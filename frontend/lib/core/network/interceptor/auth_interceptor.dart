import 'dart:async';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/constants/api_endpoints.dart';
import 'package:frontend/core/constants/storage_keys.dart';
import 'package:frontend/features/auth/application/providers/auth_providers.dart';
import 'package:frontend/features/auth/application/services/token_storage_service.dart';
import 'package:logger/logger.dart';

/// Interceptor to handle authentication and token refresh logic.
class AuthInterceptor extends Interceptor {
  static const _authorizationHeader = 'Authorization';
  static const _bearerPrefix = 'Bearer ';
  static const refreshTokenEndpoint = ApiEndpoints.refreshToken;

  final SecureStorageService _secureStorage;
  final Dio _dio;
  final Ref ref;
  final Logger _logger = Logger();

  bool _isRefreshing = false;
  Completer<String>? _refreshCompleter;
  final List<_QueuedRequest> _requestQueue = [];

  AuthInterceptor(this._secureStorage, this._dio, this.ref);

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final tokens = await _secureStorage.getTokens();
    final accessToken = tokens.accessToken;

    if (accessToken != null && !options.path.contains(refreshTokenEndpoint)) {
      options.headers[_authorizationHeader] = _bearerPrefix + accessToken;
      _logger.i("onRequest: Adding Authorization header");
    } else {
      _logger.i(
          "onRequest: Skipping Authorization header for refresh token request.");
    }

    _logger.d("onRequest: URL: ${options.uri}, Headers: ${options.headers}");

    return handler.next(options);
  }

  @override
  Future<void> onError(
      DioException err, ErrorInterceptorHandler handler) async {
    final response = err.response;

    _logger.e(
        "onError triggered. URL: ${err.requestOptions.uri}, Status Code: ${response?.statusCode}, _isRefreshing: $_isRefreshing, Error: ${err.message}");

    if (response?.statusCode != 401) {
      _logger
          .i("onError: Status code is not 401, passing to next interceptor.");
      return handler.next(err);
    }

    if (err.requestOptions.path.contains(refreshTokenEndpoint)) {
      _logger.e(
          "onError: Refresh token request failed. Logging out and rejecting request.");
      await _clearAuthDataAndLogout(err);
      return handler.reject(err);
    }

    if (_isRefreshing) {
      _logger.i("onError: Refresh already in progress. Queuing request.");
      _queueRequest(err.requestOptions, handler);
      return;
    }

    _isRefreshing = true;
    _logger
        .i("onError: Attempting token refresh. Setting _isRefreshing to true.");

    _refreshCompleter = Completer<String>();
    try {
      final newAccessToken = await _attemptTokenRefresh(err);
      _refreshCompleter!.complete(newAccessToken);
      await _retryQueuedRequests(newAccessToken!);
      _retryRequest(err.requestOptions, newAccessToken, handler);
    } catch (e) {
      _logger.e("onError: Error during refresh attempt: $e", e);
      await _rejectQueuedRequests(err);
      handler.reject(err);
    } finally {
      _isRefreshing = false;
      _logger.i(
          "onError: Refresh attempt complete. Resetting _isRefreshing to false.");
      _refreshCompleter = null;
    }
  }

  /// Attempts to refresh the access token using the refresh token.
  Future<String?> _attemptTokenRefresh(DioException err) async {
    _logger.i("_attemptTokenRefresh: Called");

    final tokens = await _secureStorage.getTokens();
    final refreshToken = tokens.refreshToken;

    if (refreshToken == null) {
      _logger.e('_attemptTokenRefresh: No refresh token. Clearing data.');
      await _clearAuthDataAndLogout(err);
      throw DioException(
          requestOptions: err.requestOptions,
          response: err.response,
          type: DioExceptionType.unknown,
          error: "No refresh token available");
    }

    _logger.i("_attemptTokenRefresh: Retrieved refresh token");
    final newAccessToken = await _refreshAccessToken(refreshToken);
    if (newAccessToken == null) {
      _logger.e(
          '_attemptTokenRefresh: New Access Token is null. Throwing exception.');
      await _clearAuthDataAndLogout(err);
      throw DioException(
          requestOptions: err.requestOptions,
          response: err.response,
          type: err.type,
          error: "New Access Token is null");
    }
    _logger.i("_attemptTokenRefresh: Successfully retrieved new access token.");
    return newAccessToken;
  }

  /// Refreshes the access token using the provided refresh token.
  Future<String?> _refreshAccessToken(String refreshToken) async {
    _logger.i("_refreshAccessToken: Attempting to refresh token.");
    try {
      final response = await _dio.post(
        refreshTokenEndpoint,
        queryParameters: {StorageKeys.refreshToken: refreshToken},
      );

      if (response.statusCode != null &&
          response.statusCode! >= 200 &&
          response.statusCode! < 300) {
        final newAccessToken =
            response.data?[StorageKeys.accessToken] as String?;
        if (newAccessToken != null) {
          _logger.i(
              "_refreshAccessToken: Successfully retrieved new access token from server.");
          await _secureStorage.saveTokens(
              accessToken: newAccessToken, refreshToken: refreshToken);
          return newAccessToken;
        }
        final errorMessage =
            response.data?['detail'] as String? ?? 'Access Token is null';
        throw DioException(
            requestOptions: RequestOptions(),
            response: response,
            type: DioExceptionType.badResponse,
            error: errorMessage);
      } else {
        final errorMessage =
            response.data?['detail'] as String? ?? 'Refresh token failed';
        throw DioException(
            requestOptions: RequestOptions(),
            response: response,
            type: DioExceptionType.badResponse,
            error: errorMessage);
      }
    } on DioException catch (e) {
      _logger.e("_refreshAccessToken: DioException: ${e.message}", e);
      await _clearAuthDataAndLogout(e);
      rethrow;
    }
  }

  /// Queues the request to be retried after the token is refreshed.
  void _queueRequest(RequestOptions options, ErrorInterceptorHandler handler) {
    _logger.i("Queuing request: ${options.uri}");
    _requestQueue.add(_QueuedRequest(options, handler));
  }

  /// Retries all queued requests with the new access token.
  Future<void> _retryQueuedRequests(String newAccessToken) async {
    _logger
        .i("Retrying queued requests. Queue length: ${_requestQueue.length}");
    final queuedRequests = List.from(_requestQueue);
    _requestQueue.clear();

    await Future.wait(queuedRequests.map((queued) {
      _logger.i("Retrying request: ${queued.requestOptions.uri}");
      return _retryRequest(
          queued.requestOptions, newAccessToken, queued.handler);
    }));
  }

  /// Rejects all queued requests with the original error.
  Future<void> _rejectQueuedRequests(DioException originalError) async {
    _logger.e(
        "_rejectQueuedRequests: Rejecting all queued requests. Queue length: ${_requestQueue.length}");
    final queuedRequests = List.from(_requestQueue);
    _requestQueue.clear();

    for (final queued in queuedRequests) {
      _logger.e(
          "_rejectQueuedRequests: Rejecting request: ${queued.requestOptions.uri}");
      queued.handler.reject(originalError);
    }
  }

  /// Retries a single request with the new access token.
  Future<void> _retryRequest(
    RequestOptions options,
    String newAccessToken,
    ErrorInterceptorHandler handler,
  ) async {
    options.headers[_authorizationHeader] = _bearerPrefix + newAccessToken;
    try {
      final response = await _dio.fetch(options);
      handler.resolve(response);
    } catch (e) {
      handler.reject(e as DioException);
    }
  }

  /// Clears authentication data and logs out the user.
  Future<void> _clearAuthDataAndLogout(DioException error) async {
    ref.read(authNotifierProvider.notifier).logout();
    _isRefreshing = false;
    _logger.e(
        "_clearAuthDataAndLogout: Clearing auth data and logging out.  Error: ${error.response?.data ?? error.message}");
  }
}

/// Class to hold queued requests.
class _QueuedRequest {
  final RequestOptions requestOptions;
  final ErrorInterceptorHandler handler;

  _QueuedRequest(this.requestOptions, this.handler);
}

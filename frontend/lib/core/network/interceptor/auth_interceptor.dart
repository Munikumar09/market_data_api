import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/features/auth/functionality/services/token_storage_service.dart';

class AuthInterceptor extends Interceptor {
  static const _authorizationHeader = 'Authorization';
  static const _bearerPrefix = 'Bearer';
  static const _refreshTokenEndpoint = '/auth/refresh-token';
  static const _accessTokenKey = 'accessToken';
  static const _refreshTokenKey = 'refreshToken';

  final SecureStorageService _secureStorage;
  final Dio _dio;
  final GlobalKey<NavigatorState> navigatorKey;

  bool _isRefreshing = false;
  final _requestQueue = <_QueuedRequest>[];

  AuthInterceptor(this._secureStorage, this._dio, this.navigatorKey);

  @override
  Future<void> onRequest(
    RequestOptions options,
    RequestInterceptorHandler handler,
  ) async {
    final tokens = await _secureStorage.getTokens();
    final accessToken = tokens[_accessTokenKey];

    if (accessToken != null) {
      options.headers[_authorizationHeader] = '$_bearerPrefix $accessToken';
    }

    return handler.next(options);
  }

  @override
  Future<void> onError(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    final response = err.response;
    if (response?.statusCode != 401) return handler.next(err);

    if (!_isRefreshing) {
      await _handleTokenRefresh(err, handler);
    } else {
      _queueRequest(err.requestOptions, handler);
    }
  }

  Future<void> _handleTokenRefresh(
    DioException err,
    ErrorInterceptorHandler handler,
  ) async {
    _isRefreshing = true;
    
    try {
      final tokens = await _secureStorage.getTokens();
      final refreshToken = tokens[_refreshTokenKey];
      
      if (refreshToken == null) throw Exception('No refresh token available');
      
      final newAccessToken = await _refreshAccessToken(refreshToken);
      if (newAccessToken == null) throw Exception('Token refresh failed');

      _updateDioAuthorization(newAccessToken);
      await _retryQueuedRequests(newAccessToken);
      _retryOriginalRequest(err.requestOptions, newAccessToken, handler);
    } catch (e) {
      await _handleRefreshFailure();
      handler.reject(err);
    } finally {
      _isRefreshing = false;
    }
  }

  Future<String?> _refreshAccessToken(String refreshToken) async {
    try {
      final response = await _dio.post(
        _refreshTokenEndpoint,
        data: {_refreshTokenKey: refreshToken},
      );

      final newAccessToken = response.data[_accessTokenKey] as String?;
      if (newAccessToken != null) {
        await _secureStorage.saveTokens(newAccessToken, refreshToken);
      }
      return newAccessToken;
    } on DioException catch (e) {
      debugPrint('Token refresh failed: ${e.message}');
      return null;
    }
  }

  void _updateDioAuthorization(String token) {
    _dio.options.headers[_authorizationHeader] = '$_bearerPrefix $token';
  }

  void _queueRequest(RequestOptions options, ErrorInterceptorHandler handler) {
    _requestQueue.add(_QueuedRequest(options, handler));
  }

  Future<void> _retryQueuedRequests(String newAccessToken) async {
    await Future.wait(_requestQueue.map((queued) {
      queued.requestOptions.headers[_authorizationHeader] = 
        '$_bearerPrefix $newAccessToken';
      return _dio.fetch(queued.requestOptions)
        .then(queued.handler.resolve)
        .catchError((error, stackTrace) => queued.handler.reject(error as DioException));
    }));
    _requestQueue.clear();
  }

  void _retryOriginalRequest(
    RequestOptions options,
    String newAccessToken,
    ErrorInterceptorHandler handler,
  ) {
    options.headers[_authorizationHeader] = '$_bearerPrefix $newAccessToken';
    _dio.fetch(options).then(handler.resolve).catchError((error, stackTrace) => handler.reject(error));
  }

  Future<void> _handleRefreshFailure() async {
    await _secureStorage.clearTokens();
    navigatorKey.currentState?.pushNamedAndRemoveUntil(
      AppRoutes.login,
      (route) => false,
    );
  }
}

class _QueuedRequest {
  final RequestOptions requestOptions;
  final ErrorInterceptorHandler handler;

  _QueuedRequest(this.requestOptions, this.handler);
}
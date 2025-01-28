import 'package:dio/dio.dart';
import 'package:frontend/features/auth/functionality/services/token_storage_service.dart';

class AuthInterceptor extends InterceptorsWrapper {
  final SecureStorageService _secureStorage;
  final Dio _dio;

  AuthInterceptor(this._secureStorage, this._dio);

  @override
  void onRequest(
      RequestOptions options, RequestInterceptorHandler handler) async {
    final tokens = await _secureStorage.getTokens();
    final accessToken = tokens['accessToken'];

    if (accessToken != null) {
      options.headers['Authorization'] = 'Bearer $accessToken';
    }
    return handler.next(options);
  }

  @override
  void onError(DioException err, ErrorInterceptorHandler handler) async {
    if (err.response?.statusCode == 401) {
      // Handle token refresh independently
      final tokens = await _secureStorage.getTokens();
      final refreshToken = tokens['refreshToken'];

      if (refreshToken != null) {
        final newAccessToken = await _refreshAccessToken(refreshToken);
        if (newAccessToken != null) {
          // Update the request with the new token
          err.requestOptions.headers['Authorization'] =
              'Bearer $newAccessToken';
          final retryResponse = await _dio.request(
            err.requestOptions.path,
            options: Options(
              method: err.requestOptions.method,
              headers: err.requestOptions.headers,
            ),
            data: err.requestOptions.data,
          );
          return handler.resolve(retryResponse);
        }
      }
    }
    return handler.next(err);
  }

  Future<String?> _refreshAccessToken(String refreshToken) async {
    try {
      final response = await _dio.post('/authentication/refresh-token', data: {
        'refresh_token': refreshToken,
      });
      final newAccessToken = response.data['access_token'];
      await _secureStorage.saveTokens(
        newAccessToken,
        refreshToken, // Keep the same refresh token
      );
      return newAccessToken;
    } catch (e) {
      return null; // Handle refresh failure
    }
  }
}

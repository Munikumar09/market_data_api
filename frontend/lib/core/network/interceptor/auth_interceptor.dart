import 'package:dio/dio.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/features/auth/functionality/services/token_storage_service.dart';
import 'package:frontend/main.dart'; // Global navigation key

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
      final tokens = await _secureStorage.getTokens();
      final refreshToken = tokens['refreshToken'];

      if (refreshToken != null) {
        final newAccessToken = await _refreshAccessToken(refreshToken);
        if (newAccessToken != null) {
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

      // Refresh token is invalid → navigate to login screen
      navigatorKey.currentState?.pushNamedAndRemoveUntil(
        AppRoutes.login,
        (route) => false, // Remove all routes from stack
      );
    }

    return handler.next(err);
  }

  Future<String?> _refreshAccessToken(String refreshToken) async {
    try {
      final response = await _dio.post('/auth/refresh-token', data: {
        'refreshToken': refreshToken,
      });

      final newAccessToken = response.data['accessToken'];
      await _secureStorage.saveTokens(
        newAccessToken,
        refreshToken,
      );

      return newAccessToken;
    } catch (e) {
      return null; // Refresh failed
    }
  }
}

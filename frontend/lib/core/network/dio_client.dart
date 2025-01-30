import 'package:dio/dio.dart';
import 'package:frontend/core/constants/app_urls.dart';
import 'package:frontend/core/network/interceptor/auth_interceptor.dart';
import 'package:frontend/features/auth/functionality/services/token_storage_service.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';

class DioClient {
  late final Dio _dio;
  final SecureStorageService _secureStorage;
  DioClient(this._secureStorage) {
    _dio = Dio(BaseOptions(
      baseUrl: AppUrls.baseUrl, // Replace with your backend URL
      connectTimeout: Duration(milliseconds: 5000),
      receiveTimeout: Duration(milliseconds: 5000),
      headers: {
        'Content-Type': 'application/json',
      },
    ));

    dio.interceptors.add(PrettyDioLogger());
    dio.interceptors
        .add(AuthInterceptor(_secureStorage, dio)); // Add the AuthInterceptor
  }

  Dio get dio => _dio;
}

import 'package:dio/dio.dart';
import 'package:frontend/core/constants/app_urls.dart';

class DioClient {
  late final Dio _dio;

  DioClient() {
    _dio = Dio(BaseOptions(
      baseUrl: AppUrls.baseUrl, // Replace with your backend URL
      connectTimeout: Duration(milliseconds: 5000),
      receiveTimeout: Duration(milliseconds: 5000),
      headers: {
        'Content-Type': 'application/json',
      },
    ));

    // _dio.interceptors.add(AuthInterceptor()); // Add the AuthInterceptor
  }

  Dio get dio => _dio;
}

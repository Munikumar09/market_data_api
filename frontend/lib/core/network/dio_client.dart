import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/constants/app_urls.dart';
import 'package:frontend/core/network/interceptor/auth_interceptor.dart';
import 'package:frontend/features/auth/application/services/token_storage_service.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';

class DioClient {
  final int connectionTimeout;
  final int receiveTimeout;

  final Dio _dio;
  final SecureStorageService _secureStorage;
  final Ref ref;

  DioClient(
    this._secureStorage,
    this.ref, {
    this.connectionTimeout = 5000,
    this.receiveTimeout = 5000,
  }) : _dio = Dio(
          BaseOptions(
            baseUrl: AppUrls.baseUrl,
            connectTimeout: Duration(milliseconds: connectionTimeout),
            receiveTimeout: Duration(milliseconds: receiveTimeout),
            contentType: 'application/json',
          ),
        ) {
    _configureInterceptors();
  }

  Dio get dio => _dio;

  void _configureInterceptors() {
    final interceptors = <Interceptor>[
      AuthInterceptor(_secureStorage, _dio, ref),
    ];

    if (kDebugMode) {
      interceptors.add(
        PrettyDioLogger(
          requestHeader: true,
          requestBody: true,
          responseHeader: true,
          error: true,
          maxWidth: 80,
        ),
      );
    }

    _dio.interceptors.addAll(interceptors);
  }
}

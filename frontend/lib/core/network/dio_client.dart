import 'package:dio/dio.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter/material.dart';
import 'package:frontend/core/constants/app_urls.dart';
import 'package:frontend/core/network/interceptor/auth_interceptor.dart';
import 'package:frontend/features/auth/functionality/services/token_storage_service.dart';
import 'package:pretty_dio_logger/pretty_dio_logger.dart';

class DioClient {
  static const _connectionTimeout = 5000;
  static const _receiveTimeout = 5000;
  static const _contentTypeHeader = 'Content-Type';
  static const _jsonContentType = 'application/json';

  final Dio _dio;
  final SecureStorageService _secureStorage;
  final GlobalKey<NavigatorState> navigatorKey;

  DioClient(this._secureStorage, this.navigatorKey)
      : _dio = Dio(
          BaseOptions(
            baseUrl: AppUrls.baseUrl,
            connectTimeout: const Duration(milliseconds: _connectionTimeout),
            receiveTimeout: const Duration(milliseconds: _receiveTimeout),
            headers: {_contentTypeHeader: _jsonContentType},
          ),
        ) {
    _configureInterceptors();
  }

  Dio get dio => _dio;

  void _configureInterceptors() {
    final interceptors = <Interceptor>[
      AuthInterceptor(_secureStorage, _dio, navigatorKey),
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

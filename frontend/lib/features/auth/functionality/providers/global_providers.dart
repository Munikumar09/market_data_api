import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/network/dio_client.dart';
import 'package:frontend/features/auth/functionality/services/token_storage_service.dart';

final secureStorageProvider = Provider((ref) => SecureStorageService());

final Provider<Dio> dioProvider = Provider((ref) {
  final secureStorage = ref.read(secureStorageProvider);
  return DioClient(secureStorage).dio;
});

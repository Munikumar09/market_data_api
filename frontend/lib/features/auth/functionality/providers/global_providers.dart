import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/network/dio_client.dart';
import 'package:frontend/features/auth/functionality/services/token_storage_service.dart';
import 'package:frontend/main.dart';

final secureStorageProvider = Provider((ref) => SecureStorageService());

final dioProvider = Provider((ref) {
  final secureStorage = ref.read(secureStorageProvider);
  final navigatorKey = ref.watch(navigatorKeyProvider);
  return DioClient(secureStorage, navigatorKey).dio;
});

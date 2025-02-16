import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/network/dio_client.dart';
import 'package:frontend/features/auth/application/services/token_storage_service.dart';

final secureStorageProvider = Provider((ref) => SecureStorageService());
final navigatorKeyProvider = Provider<GlobalKey<NavigatorState>>((ref) {
  return GlobalKey<NavigatorState>();
});

final dioProvider = Provider((ref) {
  final secureStorage = ref.read(secureStorageProvider);
  return DioClient(secureStorage, ref).dio;
});

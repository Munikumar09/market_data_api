import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/utils/handlers/api_call_handler.dart';
import 'package:frontend/features/auth/application/providers/global_providers.dart';
import 'package:frontend/features/auth/application/repository/auth_repository.dart';
import 'package:frontend/features/auth/application/state/auth_notifier.dart';
import 'package:frontend/features/auth/application/state/auth_state.dart';

final authRepositoryProvider = Provider((ref) {
  final dio = ref.read(dioProvider);
  final secureStorage = ref.read(secureStorageProvider);
  final apiCallHandler = ApiCallHandler();
  return AuthRepository(
    dio: dio,
    tokenStorage: secureStorage,
    apiCallHandler: apiCallHandler,
  );
});

final authNotifierProvider =
    StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final authRepository = ref.read(authRepositoryProvider);
  final secureStorage = ref.read(secureStorageProvider);
  return AuthNotifier(authRepository, secureStorage);
});

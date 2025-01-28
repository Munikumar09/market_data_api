import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/features/auth/functionality/providers/global_providers.dart';
import 'package:frontend/features/auth/functionality/repository/auth_repository.dart';
import 'package:frontend/features/auth/functionality/state/auth_notifier.dart';
import 'package:frontend/features/auth/functionality/state/auth_state.dart';

final authRepositoryProvider = Provider((ref) {
  final dio = ref.read(dioProvider);
  final secureStorage = ref.read(secureStorageProvider);
  return AuthRepository(dio, secureStorage);
});

final authNotifierProvider =
    StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final authRepository = ref.read(authRepositoryProvider);
  final secureStorage = ref.read(secureStorageProvider);
  return AuthNotifier(authRepository, secureStorage);
});

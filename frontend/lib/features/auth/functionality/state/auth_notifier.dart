import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/features/auth/functionality/model/signup_request.dart';
import 'package:frontend/features/auth/functionality/repository/auth_repository.dart';
import 'package:frontend/features/auth/functionality/services/token_storage_service.dart';
import 'package:frontend/features/auth/functionality/state/auth_state.dart';

class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _authRepository;
  final SecureStorageService _secureStorage;

  AuthNotifier(this._authRepository, this._secureStorage)
      : super(AuthState.unauthenticated());

  Future<void> login(String email, String password) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      await _authRepository.login(email, password);
      final token = await _secureStorage.getTokens();
      state = AuthState.authenticated(token['accessToken']!);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: "Login failed: ${e.toString()}",
      );
    }
  }

  Future<void> signup(SignupRequest request) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      await _authRepository.signup(request);
      state = state.copyWith(isLoading: false);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: "Signup failed: ${e.toString()}",
      );
    }
  }
  Future<void> verifyOtp(String email, String code) async {
    state = state.copyWith(isLoading: true, errorMessage: null);
    try {
      await _authRepository.verifyOtp(email, code);
      state = state.copyWith(isLoading: false);
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: "Verification failed: ${e.toString()}",
      );
    }
  }
  Future<void> logout() async {
    await _authRepository.logout();
    await _secureStorage.clearTokens();
    state = AuthState.unauthenticated();
  }

  Future<void> checkAuthState() async {
    state = state.copyWith(isLoading: true);
    try {
      final tokens = await _secureStorage.getTokens();
      final accessToken = tokens['accessToken'];

      if (accessToken != null) {
        state = AuthState.authenticated(accessToken);
      } else {
        state = AuthState.unauthenticated();
      }
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        errorMessage: "Error checking authentication state.",
      );
    }
  }
}

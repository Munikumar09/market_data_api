// import 'package:flutter_riverpod/flutter_riverpod.dart';
// import 'package:frontend/features/auth/functionality/repository/auth_repository.dart';
// import 'package:frontend/features/auth/functionality/services/secure_storage_service.dart';
// import 'package:frontend/features/auth/functionality/state/auth_state.dart';

// class AuthNotifier extends StateNotifier<AuthState> {
//   final AuthRepository _authRepository;
//   final SecureStorageService _secureStorage = SecureStorageService();

//   AuthNotifier(this._authRepository) : super(AuthState.unauthenticated());

//   Future<void> login(String email, String password) async {
//     try {
//       await _authRepository.login(email, password);
//       final tokens = await _secureStorage.getTokens();
//       final accessToken = tokens['accessToken'];

//       if (accessToken != null) {
//         state = AuthState.authenticated(accessToken);
//       }
//     } catch (e) {
//       state = AuthState.unauthenticated();
//       rethrow; // Forward errors to the UI for handling
//     }
//   }

//   Future<void> signup(
//       String username,
//       String email,
//       String password,
//       String confirmPassword,
//       String dateOfBirth,
//       String phoneNumber,
//       String gender) async {
//     await _authRepository.signup(username, email, password, confirmPassword,
//         dateOfBirth, phoneNumber, gender);
//   }

//   Future<void> checkAuthState() async {
//     final tokens = await _secureStorage.getTokens();
//     final accessToken = tokens['accessToken'];

//     if (accessToken != null) {
//       state = AuthState.authenticated(accessToken);
//     } else {
//       state = AuthState.unauthenticated();
//     }
//   }

//   Future<void> logout() async {
//     await _authRepository.logout();
//     state = AuthState.unauthenticated();
//   }
// }

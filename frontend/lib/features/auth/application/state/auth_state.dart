// Updated AuthState would need:
enum AuthStatus {
  initial,
  loading,
  authenticated,
  unauthenticated,
  verificationPending,
  verificationSent,
  unverified,
  verified,
  error
}

class AuthState {
  final AuthStatus status;
  final String? email;
  final String? error;
  final String? accessToken;

  const AuthState._({
    required this.status,
    this.email,
    this.error,
    this.accessToken,
  });

  factory AuthState.initial() =>
      const AuthState._(status: AuthStatus.initial, error: null);

  factory AuthState.authenticated(String accessToken) =>
      AuthState._(status: AuthStatus.authenticated, accessToken: accessToken);

  factory AuthState.unverified({required String email, String? error}) =>
      AuthState._(status: AuthStatus.unverified, email: email, error: error);

  factory AuthState.unauthenticated() =>
      const AuthState._(status: AuthStatus.unauthenticated);

  factory AuthState.error(String error) =>
      AuthState._(status: AuthStatus.error, error: error);

  AuthState copyWith({
    AuthStatus? status,
    String? email,
    String? error,
    String? accessToken,
  }) {
    return AuthState._(
      status: status ?? this.status,
      email: email ?? this.email,
      error: error ?? this.error,
      accessToken: accessToken ?? this.accessToken,
    );
  }
}

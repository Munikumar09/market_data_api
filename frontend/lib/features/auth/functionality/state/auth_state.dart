class AuthState {
  final bool isAuthenticated;
  final String? accessToken;

  AuthState({
    required this.isAuthenticated,
    this.accessToken,
  });

  factory AuthState.unauthenticated() {
    return AuthState(isAuthenticated: false);
  }

  factory AuthState.authenticated(String accessToken) {
    return AuthState(isAuthenticated: true, accessToken: accessToken);
  }
}

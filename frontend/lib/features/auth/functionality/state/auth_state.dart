class AuthState {
  final bool isAuthenticated;
  final String? accessToken;
  final bool isLoading;
  final String? errorMessage;

  AuthState({
    required this.isAuthenticated,
    this.accessToken,
    this.isLoading = false,
    this.errorMessage,
  });

  factory AuthState.unauthenticated() {
    return AuthState(isAuthenticated: false);
  }

  factory AuthState.authenticated(String accessToken) {
    return AuthState(
      isAuthenticated: true,
      accessToken: accessToken,
    );
  }

  AuthState copyWith({
    bool? isAuthenticated,
    String? accessToken,
    bool? isLoading,
    String? errorMessage,
  }) {
    return AuthState(
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
      accessToken: accessToken ?? this.accessToken,
      isLoading: isLoading ?? this.isLoading,
      errorMessage: errorMessage,
    );
  }
}

abstract class ApiEndpoints {
  static const sendVerification = '/authentication/send-verification-code';
  static const verifyCode = '/authentication/verify-code';
  static const refreshToken = '/authentication/refresh-token';
  static const signin = '/authentication/signin';
  static const logout = '/authentication/logout';
  static const signup = '/authentication/signup';
  static const protected = '/authentication/protected-endpoint';
  static const sendResetPasswordCode =
      '/authentication/send-reset-password-code';
  static const resetPassword = '/authentication/reset-password';
}

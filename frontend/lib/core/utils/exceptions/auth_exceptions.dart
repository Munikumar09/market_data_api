// Authentication Exceptions
import 'package:frontend/core/utils/exceptions/app_exceptions.dart';

class AuthException extends AppException {
  AuthException(super.message, [super.stackTrace]);
}

class SignupFailedException extends AuthException {
  SignupFailedException(super.message, [super.stackTrace]);
}

class LoginFailedException extends AuthException {
  LoginFailedException(super.message, [super.stackTrace]);
}

class EmailNotVerifiedException extends AuthException {
  EmailNotVerifiedException(super.message, [super.stackTrace]);
}

class VerificationFailedException extends AuthException {
  VerificationFailedException(super.message, [super.stackTrace]);
}

class TokenRefreshFailedException extends AuthException {
  TokenRefreshFailedException(super.message, [super.stackTrace]);
}

class NoRefreshTokenException extends AuthException {
  NoRefreshTokenException(super.message, [super.stackTrace]);
}

class LogoutFailedException extends AuthException {
  LogoutFailedException(super.message, [super.stackTrace]);
}

class TokenStorageException extends AuthException {
  TokenStorageException(super.message);
}

class PasswordResetFailedException extends AuthException {
  PasswordResetFailedException(super.message, [super.stackTrace]);
}

class RefreshTokenExpiredException extends AuthException {
  RefreshTokenExpiredException(super.message, [super.stackTrace]);
}

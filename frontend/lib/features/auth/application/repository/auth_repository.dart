import 'package:dio/dio.dart';
import 'package:frontend/core/constants/api_endpoints.dart';
import 'package:frontend/core/constants/app_strings.dart';
import 'package:frontend/core/utils/exceptions/auth_exceptions.dart';
import 'package:frontend/core/utils/handlers/api_call_handler.dart';
import 'package:frontend/features/auth/application/model/signup_request.dart';
import 'package:frontend/features/auth/application/services/token_storage_service.dart';

/// Repository responsible for handling authentication API calls.
class AuthRepository {
  final Dio _dio;
  final SecureStorageService _tokenStorage;
  final ApiCallHandler _apiCallHandler;

  AuthRepository({
    required Dio dio,
    required SecureStorageService tokenStorage,
    required ApiCallHandler apiCallHandler,
  })  : _dio = dio,
        _tokenStorage = tokenStorage,
        _apiCallHandler = apiCallHandler;

  /// Registers a new user.
  Future<void> signup(SignupRequest request) async {
    await _apiCallHandler.handleApiCall<void>(
      call: () async {
        final response = await _dio.post(
          ApiEndpoints.signup,
          data: request.toJson(),
        );
        _apiCallHandler.validateResponse(response, successStatus: 201);
        return;
      },
      exception: (message) => SignupFailedException(message),
      operationName: 'Signup',
    );
  }

  /// Sends a verification code to the provided email.
  Future<void> sendVerificationCode(String email) async {
    await _apiCallHandler.handleApiCall<void>(
      call: () async {
        final response = await _dio.post(
          ApiEndpoints.sendVerification,
          queryParameters: {"email": email},
        );
        _apiCallHandler.validateResponse(response);
        return;
      },
      exception: (message) => VerificationFailedException(message),
      operationName: 'Sending Verification Code',
    );
  }

  /// Verifies the email with the provided OTP.
  Future<void> verifyVerificationCode(String email, String emailOtp) async {
    await _apiCallHandler.handleApiCall<void>(
      call: () async {
        final response = await _dio.post(
          ApiEndpoints.verifyCode,
          data: {"verification_code": emailOtp, "email": email},
        );
        _apiCallHandler.validateResponse(response);
        return;
      },
      exception: (message) => VerificationFailedException(message),
      operationName: 'Email Verification',
    );
  }

  /// Signs in the user and stores the authentication tokens.
  Future<void> signin(String email, String password) async {
    return _apiCallHandler.handleApiCall<void>(
      call: () async {
        final response = await _dio.post(
          ApiEndpoints.signin,
          data: {'email': email, 'password': password},
        );
        final validatedResponse = _apiCallHandler.validateResponse(response);
        final tokens = _tokenStorage.parseAuthTokens(validatedResponse.data);
        await _tokenStorage.saveTokens(
            accessToken: tokens.accessToken, refreshToken: tokens.refreshToken);
        return;
      },
      exception: (message) {
        final lowerCaseMessage = message.toLowerCase();
        if (lowerCaseMessage.contains(AppStrings.userNotVerified)) {
          return EmailNotVerifiedException(message);
        }
        return LoginFailedException(message);
      },
      operationName: 'Login',
    );
  }

  /// Sends a reset password code to the specified email.
  Future<void> sendResetPasswordCode(String email) async {
    await _apiCallHandler.handleApiCall<void>(
      call: () async {
        final response = await _dio.post(
          ApiEndpoints.sendResetPasswordCode,
          queryParameters: {"email": email},
        );
        _apiCallHandler.validateResponse(response);
        return;
      },
      exception: (message) => PasswordResetFailedException(message),
      operationName: 'Sending Reset Password Code',
    );
  }

  /// Resets the password using the provided verification code.
  Future<void> resetPassword(
      String email, String emailOtp, String newPassword) async {
    await _apiCallHandler.handleApiCall<void>(
      call: () async {
        final response = await _dio.post(
          ApiEndpoints.resetPassword,
          data: {
            "email": email,
            "password": newPassword,
            "verification_code": emailOtp
          },
        );
        _apiCallHandler.validateResponse(response);
        return;
      },
      exception: (message) => PasswordResetFailedException(message),
      operationName: 'Reset Password',
    );
  }

  /// Logs out the user by clearing stored tokens.
  Future<void> logout() async {
    await _apiCallHandler.handleApiCall<void>(
      call: () async {
        await _tokenStorage.clearTokens();
        return;
      },
      exception: (message) => LogoutFailedException(message),
      operationName: 'Logout',
    );
  }

  /// Checks if the current authentication state is valid.
  Future<void> checkAuthState() async {
    await _apiCallHandler.handleApiCall<void>(
      call: () async {
        final response = await _dio.get(ApiEndpoints.protected);
        _apiCallHandler.validateResponse(response);
      },
      exception: (message) => AuthException(message),
      operationName: 'Check Auth State',
    );
  }
}

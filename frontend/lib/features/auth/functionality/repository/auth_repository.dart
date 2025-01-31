import 'package:dio/dio.dart';
import 'package:frontend/core/constants/app_strings.dart';
import 'package:frontend/core/utils/exceptions.dart';
import 'package:frontend/features/auth/functionality/model/signup_request.dart';
import 'package:frontend/features/auth/functionality/services/email_verification_service.dart';
import 'package:frontend/features/auth/functionality/services/phone_verification_service.dart';
import 'package:frontend/features/auth/functionality/services/token_storage_service.dart';
import 'package:logger/logger.dart';

// Auth Repository
class AuthRepository {
  final Dio _dio;
  final Logger _logger = Logger();
  final EmailVerificationService _emailVerificationService;
  final PhoneVerificationService _phoneVerificationService;
  final SecureStorageService _secureStorage;

  AuthRepository(this._dio, this._secureStorage)
      : _emailVerificationService = EmailVerificationService(_dio),
        _phoneVerificationService = PhoneVerificationService(_dio);

  Future<void> signup(SignupRequest request) async {
    try {
      final response = await _dio.post(
        '/authentication/signup',
        data: request.toJson(),
      );
      if (response.statusCode == 201) {
        _logger.i('Signup successful: ${response.data}');
        await _emailVerificationService.sendEmailVerification(request.email);

        // Uncomment to enable phone verification in the future
        // await _phoneVerificationService.sendPhoneVerification(request.phoneNumber);
      } else {
        throw Exception('Signup failed with status: ${response.statusCode}');
      }
    } on DioException catch (e) {
      _logger.e('Signup failed', e, e.stackTrace);
      throw Exception(e.response?.data['detail'] ?? 'Enter Valid Details');
    } catch (e) {
      _logger.e('Unexpected error during signup', e);
      throw Exception('An unexpected error occurred during signup.');
    }
  }

  Future<void> verifyOtp(
    String email,
    String emailOtp, {
    String? phone,
    String? phoneOtp,
  }) async {
    try {
      // Email verification
      await _emailVerificationService.verifyEmail(email, emailOtp);

      // Phone verification (optional, for future)
      if (phone != null && phoneOtp != null) {
        await _phoneVerificationService.verifyPhone(phone, phoneOtp);
      }
    } on DioException catch (e) {
      _logger.e('Verification failed', e, e.stackTrace);
      throw Exception(e.response?.data['detail'] ?? 'Invalid OTP.');
    } catch (e) {
      _logger.e('Unexpected error during verification', e);
      throw Exception('An unexpected error occurred during verification.');
    }
  }

  Future<void> login(String email, String password) async {
    try {
      final response = await _dio.post(
        '/authentication/signin',
        data: {'email': email, 'password': password},
      );
      final tokens = response.data;
      _logger.i('Login successful: $tokens');
      await _secureStorage.saveTokens(
          tokens['access_token'], tokens['refresh_token']);
      _logger.i("stored successfully");
    } on DioException catch (e) {
      _logger.e('Login failed', e, e.stackTrace);
      if (e.response?.data['detail'] == AppStrings.userNotVerified) {
        throw EmailNotVerifiedException(AppStrings.userNotVerified);
      }
      throw Exception(e.response?.data['detail'] ?? 'Invalid Credentials.');
    } catch (e) {
      _logger.e('Unexpected error during login', e);
      throw Exception('An unexpected error occurred during login.');
    }
  }

  Future<void> refreshToken() async {
    try {
      final tokens = await _secureStorage.getTokens();
      final refreshToken = tokens['refreshToken'];

      if (refreshToken != null) {
        final response = await _dio.post(
          '/authentication/refresh-token',
          data: {'refreshToken': refreshToken},
        );
        final newAccessToken = response.data['accessToken'];
        await _secureStorage.saveTokens(newAccessToken, refreshToken);
      } else {
        throw Exception('No refresh token available.');
      }
    } on DioException catch (e) {
      _logger.e('Token refresh failed', e, e.stackTrace);
      throw Exception(e.response?.data['detail'] ?? 'Token refresh failed.');
    } catch (e) {
      _logger.e('Unexpected error during token refresh', e);
      throw Exception('An unexpected error occurred during token refresh.');
    }
  }

  Future<void> logout() async {
    try {
      await _secureStorage.clearTokens();
    } catch (e) {
      _logger.e('Logout failed', e);
      throw Exception('Logout failed.');
    }
  }
}

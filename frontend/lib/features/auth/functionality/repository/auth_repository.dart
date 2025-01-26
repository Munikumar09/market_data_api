import 'package:dio/dio.dart';
import 'package:frontend/core/network/dio_client.dart';
import 'package:frontend/features/auth/functionality/model/signup_request.dart';
import 'package:frontend/features/auth/functionality/services/email_verification_service.dart';
import 'package:frontend/features/auth/functionality/services/phone_verification_service.dart';
import 'package:logger/logger.dart';

// Auth Repository
class AuthRepository {
  final Dio _dio;
  final Logger _logger = Logger();
  final EmailVerificationService _emailVerificationService;
  final PhoneVerificationService _phoneVerificationService;

  // Private constructor
  AuthRepository._internal(this._dio)
      : _emailVerificationService = EmailVerificationService(_dio),
        _phoneVerificationService = PhoneVerificationService(_dio);

  // Singleton instance
  static final AuthRepository _instance = AuthRepository._internal(
    DioClient().dio,
  );

  // Factory to return the singleton instance
  factory AuthRepository() => _instance;

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
      throw Exception(e.response?.data['detail'] ?? 'Signup failed');
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
    } catch (e) {
      _logger.e('Verification failed', e);
      throw Exception('Verification failed');
    }
  }
}

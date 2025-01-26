import 'package:dio/dio.dart';
import 'package:logger/logger.dart';

// Base Verification Service
abstract class VerificationService {
  final Dio dio;
  final Logger logger = Logger();

  VerificationService(this.dio);

  Future<void> sendVerification(String recipient, String medium) async {
    try {
      await dio.post("/authentication/send-verification-code", queryParameters: {
        "email_or_phone": recipient,
        "verification_medium": medium,
      });
      logger.i("Verification code sent via $medium to: $recipient");
    } on DioException catch (e) {
      logger.e("Failed to send $medium verification", e, e.stackTrace);
      throw Exception("Failed to send $medium verification");
    }
  }

  Future<void> verifyCode(String recipient, String verificationCode, String medium) async {
    try {
      final response = await dio.post('/authentication/verify-code', data: {
        "verification_code": verificationCode,
        "email_or_phone": recipient,
      });
      if (response.statusCode == 200) {
        logger.i('$medium verification successful for $recipient');
      } else {
        throw Exception("$medium verification failed for $recipient");
      }
    } on DioException catch (e) {
      logger.e("Failed to verify $medium", e, e.stackTrace);
      throw Exception("Failed to verify $medium");
    }
  }
}
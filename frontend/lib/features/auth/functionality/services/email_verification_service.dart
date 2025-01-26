// Email Verification Service
import 'package:frontend/features/auth/functionality/services/verification_service.dart';

class EmailVerificationService extends VerificationService {
  EmailVerificationService(super.dio);

  Future<void> sendEmailVerification(String email) =>
      sendVerification(email, "email");

  Future<void> verifyEmail(String email, String verificationCode) =>
      verifyCode(email, verificationCode, "email");
}
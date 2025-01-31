// Phone Verification Service (Future-ready)
import 'package:frontend/features/auth/functionality/services/verification_service.dart';

class PhoneVerificationService extends VerificationService {
  PhoneVerificationService(super.dio);

  Future<void> sendPhoneVerification(String phoneNumber) =>
      sendVerification(phoneNumber, "phone_number");

  Future<void> verifyPhone(String phoneNumber, String verificationCode) =>
      verifyCode(phoneNumber, verificationCode, "phone_number");
}

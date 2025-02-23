import 'package:flutter/material.dart';
import 'package:frontend/features/auth/presentation/pages/initial_page.dart';
import 'package:frontend/features/auth/presentation/pages/login_page.dart';
import 'package:frontend/features/auth/presentation/pages/register_page.dart';
import 'package:frontend/features/auth/presentation/pages/reset_password_request_page.dart';
import 'package:frontend/features/auth/presentation/pages/reset_password_verification_page.dart';
import 'package:frontend/features/auth/presentation/pages/verify_account.dart';
import 'package:frontend/features/auth/presentation/pages/welcome_page.dart';
import 'package:frontend/features/home/home.dart';

class AppRoutes {
  static const String initial = '/';
  static const String welcome = '/welcome';
  static const String register = '/register';
  static const String login = '/login';
  static const String resetPasswordRequest = '/reset-password-request';
  static const String resetPasswordVerification =
      '/reset-password-verification';
  static const String verifyAccount = '/verify-account';
  static const String home = '/home';

  static final Map<String, WidgetBuilder> pages = {
    initial: (context) => InitialPage(),
    welcome: (context) => WelcomePage(),
    register: (context) => RegisterPage(),
    login: (context) => LoginPage(),
    verifyAccount: (context) => VerifyAccountPage(),
    resetPasswordRequest: (context) => ResetPasswordRequestPage(),
    resetPasswordVerification: (context) => ResetPasswordVerificationPage(),
    home: (context) => HomePage(),
  };
}
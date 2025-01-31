import 'package:flutter/material.dart';
import 'package:frontend/features/auth/functionality/state/auth_wrapper.dart';
import 'package:frontend/features/auth/presentation/pages/forgot_password_page.dart';
import 'package:frontend/features/auth/presentation/pages/login_page.dart';
import 'package:frontend/features/auth/presentation/pages/register_page.dart';
import 'package:frontend/features/auth/presentation/pages/verify_account.dart';
import 'package:frontend/features/auth/presentation/pages/welcome_page.dart';
import 'package:frontend/features/home/home.dart';

class AppRoutes {
  static const String initial = '/';
  static const String welcome = '/welcome';
  static const String register = '/register';
  static const String login = '/login';
  static const String forgotPassword = '/forgot-password';
  static const String verifyAccount = '/verify-account';
  static const String home = '/home';

  static final Map<String, WidgetBuilder> pages = {
    initial: (context) => AuthWrapper(),
    welcome: (context) => WelcomePage(),
    register: (context) => RegisterPage(),
    login: (context) => LoginPage(),
    forgotPassword: (context) => ForgotPasswordPage(),
    verifyAccount: (context) => VerifyAccount(),
    home: (context) => HomePage(),
  };
}

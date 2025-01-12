import 'package:flutter/material.dart';
import 'package:frontend/features/auth/presentation/pages/forgot_password_page.dart';
import 'package:frontend/features/auth/presentation/pages/login_page.dart';
import 'package:frontend/features/auth/presentation/pages/register_page.dart';
import 'package:frontend/features/auth/presentation/pages/welcome_page.dart';

class AppRoutes {
  static const String welcome = '/';
  static const String register = '/register';
  static const String login = '/login';
  static const String forgotPassword = '/forgot-password';

  static final Map<String, WidgetBuilder> pages = {
    welcome: (context) => WelcomePage(),
    register: (context) => RegisterPage(),
    login: (context) => LoginPage(),
    forgotPassword: (context) => ForgotPasswordPage(),
  };
}

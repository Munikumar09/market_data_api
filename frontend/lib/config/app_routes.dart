import 'package:flutter/material.dart';
import 'package:frontend/pages/auth/forgot_password_page.dart';
import 'package:frontend/pages/auth/login_page.dart';
import 'package:frontend/pages/auth/register_page.dart';
import 'package:frontend/pages/welcome_page.dart';

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

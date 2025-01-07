import 'package:flutter/material.dart';
import 'package:frontend/components/themes/app_theme.dart';
import 'package:frontend/config/app_routes.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Paper Trading App',
      theme: AppThemes.lightTheme,
      initialRoute: AppRoutes.welcome,
      routes: AppRoutes.pages,
    );
  }
}

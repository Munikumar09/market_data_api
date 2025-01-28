import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/core/themes/app_theme.dart';

void main() {
  runApp(
    const ProviderScope(
      child: MyApp(),
    ),
  );
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

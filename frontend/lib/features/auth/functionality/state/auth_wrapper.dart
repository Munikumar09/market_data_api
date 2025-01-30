import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/features/auth/functionality/providers/global_providers.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/features/home/home.dart';
import 'package:frontend/main.dart';

class AuthWrapper extends ConsumerStatefulWidget {
  const AuthWrapper({super.key});

  @override
  _AuthWrapperState createState() => _AuthWrapperState();
}

class _AuthWrapperState extends ConsumerState<AuthWrapper> {
  @override
  void initState() {
    super.initState();
    _checkAuthentication();
  }

  Future<void> _checkAuthentication() async {
    final secureStorage = ref.read(secureStorageProvider);
    final tokens = await secureStorage.getTokens();
    final accessToken = tokens['accessToken'];
    final refreshToken = tokens['refreshToken'];
    final dio = ref.read(dioProvider); // Use Dio with interceptor

    if (accessToken != null || refreshToken != null) {
      final isAuthenticated = await _isAuthenticated(dio);
      if (isAuthenticated) {
        ref.invalidate(protectedDataProvider); // Refresh protected data
        navigatorKey.currentState?.pushReplacementNamed(AppRoutes.home);
        return;
      }
    }

    // If tokens are invalid, clear storage and go to login
    await secureStorage.clearTokens();
    navigatorKey.currentState?.pushReplacementNamed(AppRoutes.welcome);
  }

// ✅ Function to check authentication using a protected endpoint
  Future<bool> _isAuthenticated(Dio dio) async {
    try {
      final response = await dio
          .get('/authentication/protected-endpoint'); // Use any protected API
      return response.statusCode == 200;
    } catch (e) {
      return false; // Token is invalid, will trigger interceptor if needed
    }
  }

  @override
  Widget build(BuildContext context) {
    return const Scaffold(
      body: Center(
          child:
              CircularProgressIndicator()), // Show loading while checking auth state
    );
  }
}

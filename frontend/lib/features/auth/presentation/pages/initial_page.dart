import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/constants/app_strings.dart';
import 'package:frontend/core/constants/app_text_styles.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/features/auth/application/providers/auth_providers.dart';
import 'package:frontend/features/auth/application/state/auth_state.dart';

/// The initial page displayed when the app starts.
///
/// This page checks the authentication state and navigates to the appropriate screen.
class InitialPage extends ConsumerStatefulWidget {
  /// Creates an [InitialPage].
  const InitialPage({super.key});

  @override
  ConsumerState<InitialPage> createState() => _InitialPageState();
}

/// The state for the [InitialPage] widget.
///
/// Checks the authentication state and navigates to the appropriate screen.
class _InitialPageState extends ConsumerState<InitialPage> {
  @override
  void initState() {
    super.initState();
    // Execute authentication check after the first frame is built.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _checkAuthenticationState();
    });
  }

  /// Checks the authentication state and navigates to the appropriate screen.
  void _checkAuthenticationState() {
    ref.read(authNotifierProvider.notifier).checkAuthState();
  }

  @override
  Widget build(BuildContext context) {
    // Listen for changes in the authentication state.
    ref.listen<AuthState>(authNotifierProvider, (previous, next) {
      _handleAuthStateChange(next);
    });

    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const CircularProgressIndicator(),
            const SizedBox(height: 24),
            Text(
              AppStrings.appName,
              style: AppTextStyles.headline1(Theme.of(context).primaryColor),
            ),
          ],
        ),
      ),
    );
  }

  /// Handles changes in the authentication state and navigates accordingly.
  void _handleAuthStateChange(AuthState state) {
    if (!mounted) return;

    switch (state.status) {
      case AuthStatus.authenticated:
        // Navigate to home screen when authenticated.
        Navigator.of(context).pushReplacementNamed(AppRoutes.home);
        break;
      case AuthStatus.unauthenticated:
      case AuthStatus.error:
        // Navigate to welcome screen when unauthenticated or in case of error.
        Navigator.of(context).pushReplacementNamed(AppRoutes.welcome);
        break;
      default:
        // Do nothing while in loading or other intermediate states.
        break;
    }
  }
}

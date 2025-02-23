/*
Documentation:
---------------
File: login_page.dart
Description:
  Implements the LoginPage which allows users to sign in using their email and password.
  It builds a form for login, listens for authentication state changes via Riverpod,
  and navigates users based on successful or failed login attempts.
  
Methods:
  • _onLoginPressed():
      - Validates the form and triggers the sign-in process using the AuthNotifier.
  • _buildLoginForm(BuildContext context):
      - Builds the form for user input (email and password).
  • _buildForgotPasswordButton(BuildContext context):
      - Builds a button to navigate to the 'Forgot Password' screen.
  • _buildCreateAccountButton(BuildContext context):
      - Builds a button to navigate to the 'Register' screen.
  • build(BuildContext context):
      - Constructs the complete UI, listens to auth state changes, and manages navigation.
*/

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/constants/app_strings.dart';
import 'package:frontend/core/constants/app_text_styles.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/core/utils/validators.dart';
import 'package:frontend/features/auth/application/providers/auth_providers.dart';
import 'package:frontend/features/auth/application/state/auth_state.dart';
import 'package:frontend/features/auth/presentation/widgets/auth_footer.dart';
import 'package:frontend/features/auth/presentation/widgets/header_text_widget.dart';
import 'package:frontend/shared/buttons/primary_button.dart';
import 'package:frontend/shared/helpers/custom_snackbar.dart';
import 'package:frontend/shared/inputs/custom_text_field.dart';
import 'package:frontend/shared/layouts/custom_background_widget.dart';
import 'package:frontend/shared/loaders/loading_indicator.dart';

/// Allows users to enter their email and password to authenticate.
class LoginPage extends ConsumerStatefulWidget {
  const LoginPage({super.key});

  @override
  ConsumerState<LoginPage> createState() => _LoginPageState();
}

class _LoginPageState extends ConsumerState<LoginPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  /// Attempts to log in the user by validating the form and calling the sign-in method.
  Future<void> _onLoginPressed() async {
    if (_formKey.currentState!.validate()) {
      await ref.read(authNotifierProvider.notifier).signin(
            _emailController.text.trim(),
            _passwordController.text,
          );
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authNotifierProvider);
    final theme = Theme.of(context);

    // Listen for authentication state changes and navigate according to the result.
    ref.listen<AuthState>(authNotifierProvider, (previous, next) {
      if (previous?.status == AuthStatus.loading &&
          next.status != AuthStatus.loading) {
        if (next.status == AuthStatus.unverified) {
          context.showSuccessSnackBar(
              'Your email is not verified. Please verify your email.');
          Navigator.of(context).pushNamed(
            AppRoutes.verifyAccount,
            arguments: {'email': _emailController.text},
          );
        } else if (next.status == AuthStatus.authenticated) {
          Navigator.of(context).pushReplacementNamed(AppRoutes.home);
          context.showSuccessSnackBar("Login successful.");
        } else if (next.error != null) {
          context.showErrorSnackBar(next.error!);
        }
      }
    });

    return Scaffold(
      backgroundColor: theme.colorScheme.surface,
      body: CustomBackgroundWidget(
        child: SingleChildScrollView(
          child: ConstrainedBox(
            constraints: BoxConstraints(
              minHeight: MediaQuery.of(context).size.height,
            ),
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  const SizedBox(height: 30),
                  const HeaderTextWidget(
                    title: AppStrings.loginTitle,
                    subtitle: AppStrings.loginSubtitle,
                  ),
                  const SizedBox(height: 24),
                  _buildLoginForm(context),
                  const SizedBox(height: 10),
                  _buildForgotPasswordButton(context),
                  const SizedBox(height: 10),
                  PrimaryButton(
                    text: AppStrings.login,
                    onPressed: authState.status == AuthStatus.loading
                        ? null
                        : _onLoginPressed,
                    child: authState.status == AuthStatus.loading
                        ? LoadingIndicator()
                        : null,
                  ),
                  const SizedBox(height: 10),
                  _buildCreateAccountButton(context),
                  const SizedBox(height: 40),
                  const AuthFooterWidget(),
                  const SizedBox(height: 24),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Builds the form containing input fields for email and password.
  Widget _buildLoginForm(BuildContext context) {
    return Form(
      key: _formKey,
      child: Column(
        children: [
          CustomTextField(
            hintText: AppStrings.email,
            labelText: AppStrings.email,
            keyboardType: TextInputType.emailAddress,
            controller: _emailController,
            validator: Validators.email,
          ),
          const SizedBox(height: 16),
          CustomTextField(
            hintText: AppStrings.password,
            isPassword: true,
            labelText: AppStrings.password,
            controller: _passwordController,
            autocorrect: false,
            enableSuggestions: false,
          ),
        ],
      ),
    );
  }

  /// Builds the "Forgot Password?" button.
  Widget _buildForgotPasswordButton(BuildContext context) {
    final theme = Theme.of(context);
    return Align(
      alignment: Alignment.centerRight,
      child: TextButton(
        onPressed: () =>
            Navigator.of(context).pushNamed(AppRoutes.resetPasswordRequest),
        child: Text(
          AppStrings.forgotPassword,
          style: AppTextStyles.customTextStyle(
            color: theme.colorScheme.secondary,
            fontSize: heading3FontSize,
            fontWeight: heading3FontWeight,
          ),
        ),
      ),
    );
  }

  /// Builds the "Create Account" button.
  Widget _buildCreateAccountButton(BuildContext context) {
    return TextButton(
      onPressed: () => Navigator.of(context).pushNamed(AppRoutes.register),
      child: Text(
        AppStrings.createAccount,
        style: AppTextStyles.customTextStyle(
            color: const Color(0xFF494949),
            fontSize: heading3FontSize,
            fontWeight: heading3FontWeight),
      ),
    );
  }
}

/*
Documentation:
---------------
File: reset_password_verification_page.dart
Description:
  Implements the ResetPasswordVerificationPage which allows users to complete a password reset.
  On this page, users enter the OTP (sent to their email) along with their new password and password confirmation.
  The page validates the input, triggers the password reset via the AuthNotifier, and listens for response to 
  navigate the user accordingly or display error messages.
  
Methods:
  • _onResetPasswordPressed():
      - Validates the form and triggers the reset password process.
  • _onResendOtpPressed():
      - Requests a resend of the OTP.
  • _buildForm():
      - Constructs the form with OTP, new password, and confirm password fields.
  • _buildResendButton(ThemeData theme):
      - Creates the button to resend the OTP.
*/

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/constants/app_strings.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/core/utils/validators.dart';
import 'package:frontend/features/auth/application/providers/auth_providers.dart';
import 'package:frontend/features/auth/application/state/auth_state.dart';
import 'package:frontend/shared/buttons/primary_button.dart';
import 'package:frontend/shared/helpers/custom_snackbar.dart';
import 'package:frontend/shared/inputs/custom_text_field.dart';
import 'package:frontend/shared/layouts/custom_background_widget.dart';
import 'package:frontend/shared/loaders/loading_indicator.dart';

/// A page that allows users to verify their password reset request.
///
/// Users enter the OTP sent to their email, their new password, and confirm the password.
class ResetPasswordVerificationPage extends ConsumerStatefulWidget {
  const ResetPasswordVerificationPage({super.key});

  @override
  ConsumerState<ResetPasswordVerificationPage> createState() =>
      _ResetPasswordVerificationPageState();
}

class _ResetPasswordVerificationPageState
    extends ConsumerState<ResetPasswordVerificationPage> {
  final _formKey = GlobalKey<FormState>();
  final _otpController = TextEditingController();
  final _newPasswordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  late String _email;
  bool _didAttemptReset = false;
  final bool _isCodeSent =
      true; // Initialize to true since the code is sent before this page

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final args =
        ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>?;
    _email = args?['email'] as String? ?? '';
    if (_email.isEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.of(context).pop();
        context.showErrorSnackBar(
            "Error: Email address is missing.  Please try again.");
      });
    }
  }

  @override
  void dispose() {
    _otpController.dispose();
    _newPasswordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  /// Resets the user's password.
  Future<void> _onResetPasswordPressed() async {
    if (_formKey.currentState!.validate()) {
      _didAttemptReset = true;
      await ref.read(authNotifierProvider.notifier).resetPassword(
            _email,
            _otpController.text.trim(),
            _newPasswordController.text.trim(),
          );
    }
  }

  /// Resends the verification code.
  Future<void> _onResendOtpPressed() async {
    // Directly call the provider to resend.  No extra flags needed.
    await ref.read(authNotifierProvider.notifier).sendResetPasswordCode(_email);
    // Success snackbar handled in ref.listen
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    ref.listen<AuthState>(authNotifierProvider, (previous, next) {
      // Handle password reset attempts (success/failure).
      if (_didAttemptReset && next.status != AuthStatus.loading) {
        _didAttemptReset = false;
        if (next.status == AuthStatus.initial) {
          Navigator.pushNamedAndRemoveUntil(
              context, AppRoutes.login, (route) => false);
          context.showSuccessSnackBar("Password reset successful.");
        } else if (next.error != null) {
          context.showErrorSnackBar(next.error!);
        }
      }

      // Handle successful code resends.
      if (previous?.status != AuthStatus.verificationSent &&
          next.status == AuthStatus.verificationSent &&
          _isCodeSent) {
        context.showSuccessSnackBar('Verification code resent to $_email');
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
                  const SizedBox(height: 35),
                  _buildForm(),
                  const SizedBox(height: 24), // Space above the resend button
                  _buildResendButton(theme), // Resend button
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Builds the form for OTP and password input.
  Widget _buildForm() {
    final authState = ref.watch(authNotifierProvider);

    return Form(
      key: _formKey,
      child: Column(
        children: [
          CustomTextField(
            hintText: AppStrings.emailOtp,
            labelText: AppStrings.emailOtp,
            keyboardType: TextInputType.number,
            controller: _otpController,
            validator: (value) =>
                (value == null || value.isEmpty) ? "Please enter OTP" : null,
          ),
          const SizedBox(height: 16),
          CustomTextField(
            hintText: AppStrings.newPassword,
            labelText: AppStrings.newPassword,
            isPassword: true,
            controller: _newPasswordController,
            validator: Validators.password,
            autocorrect: false,
            enableSuggestions: false,
          ),
          const SizedBox(height: 16),
          CustomTextField(
            hintText: AppStrings.confirmNewPassword,
            labelText: AppStrings.confirmNewPassword,
            isPassword: true,
            controller: _confirmPasswordController,
            validator: (value) => Validators.confirmPassword(
              _newPasswordController.text,
              value,
            ),
            autocorrect: false,
            enableSuggestions: false,
          ),
          const SizedBox(height: 24),
          PrimaryButton(
            text: AppStrings.resetPassword,
            onPressed: authState.status == AuthStatus.loading
                ? null
                : _onResetPasswordPressed,
            child: authState.status == AuthStatus.loading && _didAttemptReset
                ? const LoadingIndicator()
                : null,
          ),
        ],
      ),
    );
  }

  /// Builds the "Resend OTP" button.
  Widget _buildResendButton(ThemeData theme) {
    return TextButton(
      onPressed: _onResendOtpPressed,
      child: Text(
        "Resend OTP",
        style: theme.textTheme.labelLarge!.copyWith(
          color: theme.colorScheme.primary,
        ),
      ),
    );
  }
}

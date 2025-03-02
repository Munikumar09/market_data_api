/*
Documentation:
---------------
File: reset_password_request_page.dart
Description:
  Implements the ResetPasswordRequestPage where users can request a password reset by entering their email address.
  When the form is submitted, the page triggers sending a reset code to the provided email via the AuthNotifier,
  listens for state changes, and navigates to the reset verification page upon success.
  
Methods:
  • _onSendResetCodePressed():
      - Validates the form and invokes the provider to send a reset password code.
  • _buildForm():
      - Constructs the form for email input and displays a loading indicator while processing.
  • build(BuildContext context):
      - Builds the complete UI with header text, form, and handles navigation based on AuthState.
*/

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/constants/app_strings.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/core/utils/validators.dart';
import 'package:frontend/features/auth/application/providers/auth_providers.dart';
import 'package:frontend/features/auth/application/state/auth_state.dart';
import 'package:frontend/features/auth/presentation/widgets/header_text_widget.dart';
import 'package:frontend/shared/buttons/primary_button.dart';
import 'package:frontend/shared/helpers/custom_snackbar.dart';
import 'package:frontend/shared/inputs/custom_text_field.dart';
import 'package:frontend/shared/layouts/custom_background_widget.dart';

/// A page that allows users to request a password reset.
///
/// Users enter their email address, and a password reset code is sent to them.
class ResetPasswordRequestPage extends ConsumerStatefulWidget {
  const ResetPasswordRequestPage({super.key});

  @override
  ConsumerState<ResetPasswordRequestPage> createState() =>
      _ResetPasswordRequestPageState();
}

class _ResetPasswordRequestPageState
    extends ConsumerState<ResetPasswordRequestPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();

  /// Tracks whether a reset attempt has been made. Important for managing
  /// the loading state and `ref.listen` behavior.
  bool _didAttemptReset = false;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  /// Sends a password reset code to the provided email.
  Future<void> _onSendResetCodePressed() async {
    if (_formKey.currentState!.validate()) {
      _didAttemptReset = true; // Set flag *before* calling the provider
      await ref
          .read(authNotifierProvider.notifier)
          .sendResetPasswordCode(_emailController.text.trim());
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    // Listen for AuthState changes.
    ref.listen<AuthState>(authNotifierProvider, (previous, next) {
      // Only proceed if we've actually attempted a reset AND we're no longer loading.
      if (_didAttemptReset && next.status != AuthStatus.loading) {
        _didAttemptReset =
            false; // Reset the flag.  CRUCIAL for correct behavior.

        if (next.status == AuthStatus.verificationSent) {
          // Navigate to the verification page, passing the email.
          Navigator.pushNamed(
            context,
            AppRoutes.resetPasswordVerification,
            arguments: {'email': _emailController.text.trim()},
          );
          context.showSuccessSnackBar(
              'Reset code sent to ${_emailController.text}');
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
            // Use ConstrainedBox for minHeight
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
                    // Use consistent naming
                    title: AppStrings.resetPassword,
                    subtitle: AppStrings.resetPasswordSubtitle,
                  ),
                  const SizedBox(height: 24),
                  _buildForm(), // Use a helper function for the form
                  const SizedBox(height: 40),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Builds the form for email input.
  Widget _buildForm() {
    final authState = ref.watch(authNotifierProvider); // Watch provider *here*

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
          PrimaryButton(
            // Use PrimaryButton
            text: AppStrings.send, // Text is always "Send"
            onPressed: authState.status == AuthStatus.loading
                ? null
                : _onSendResetCodePressed,
            child: authState.status == AuthStatus.loading &&
                    _didAttemptReset // Added _didAttemptReset
                ? const SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Colors.white,
                    ),
                  )
                : null, // Show indicator when loading AND reset was attempted
          ),
        ],
      ),
    );
  }
}

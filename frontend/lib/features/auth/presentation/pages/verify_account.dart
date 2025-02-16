import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/constants/app_strings.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/features/auth/application/providers/auth_providers.dart';
import 'package:frontend/features/auth/application/state/auth_state.dart';
import 'package:frontend/features/auth/presentation/widgets/header_text_widget.dart';
import 'package:frontend/shared/buttons/primary_button.dart';
import 'package:frontend/shared/helpers/custom_snackbar.dart';
import 'package:frontend/shared/inputs/custom_text_field.dart';
import 'package:frontend/shared/layouts/custom_background_widget.dart';
import 'package:frontend/shared/loaders/loading_indicator.dart';

/// {@template verify_account_page}
/// A page that allows users to verify their account using an OTP sent to their email.
/// {@endtemplate}
class VerifyAccountPage extends ConsumerStatefulWidget {
  /// {@macro verify_account_page}
  const VerifyAccountPage({super.key});

  @override
  ConsumerState<VerifyAccountPage> createState() => _VerifyAccountPageState();
}

class _VerifyAccountPageState extends ConsumerState<VerifyAccountPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailOtpController = TextEditingController();
  late String _email;
  bool _didAttemptVerification = false;
  bool _isCodeSent = false; // Tracks if the initial code has been sent.

  @override
  void initState() {
    super.initState();
    // Use addPostFrameCallback ONLY for actions that MUST happen after the first build.
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _extractEmailFromArgs();
    });
  }

  /// Extracts the email from the route arguments and sends the verification code (only once).
  void _extractEmailFromArgs() {
    final args =
        ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>?;
    _email = args?['email'] as String? ?? '';

    if (_email.isNotEmpty && !_isCodeSent) {
      ref.read(authNotifierProvider.notifier).sendVerificationCode(_email);
      // DON'T show the success snackbar here.  We'll handle it in ref.listen
      _isCodeSent = true; // Mark the code as sent.
    } else if (_email.isEmpty) {
      // Use addPostFrameCallback to ensure Navigator.pop() is called after build
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.of(context).pop(); // Go back
        context.showErrorSnackBar("Error: Email address is missing.");
      });
    }
  }

  @override
  void dispose() {
    _emailOtpController.dispose();
    super.dispose();
  }

  /// Attempts to verify the OTP.
  Future<void> _onVerifyOtpPressed() async {
    if (_formKey.currentState!.validate()) {
      _didAttemptVerification = true; // Set flag BEFORE the async operation
      await ref
          .read(authNotifierProvider.notifier)
          .verifyVerificationCode(_email, _emailOtpController.text);
    }
  }

  /// Resends the verification code.
  Future<void> _onResendOtpPressed() async {
    // No need for a separate flag; just call the provider method.
    ref.read(authNotifierProvider.notifier).sendVerificationCode(_email);
    // DON'T show the success snackbar here. Handled in ref.listen
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    // Use ref.listen for ALL side effects: navigation, snackbars, etc.
    ref.listen<AuthState>(authNotifierProvider, (previous, next) {
      // 1. Handle initial code sending success.
      if (previous?.status != AuthStatus.verificationSent &&
              next.status == AuthStatus.verificationSent &&
              _email.isNotEmpty // Only show if email exists
          ) {
        context.showSuccessSnackBar('Verification code sent to $_email');
      }

      // 2. Handle OTP verification attempts (success and error).
      if (_didAttemptVerification && next.status != AuthStatus.loading) {
        _didAttemptVerification = false; // Reset flag

        if (next.status == AuthStatus.initial) {
          Navigator.pushNamedAndRemoveUntil(
              context, AppRoutes.login, (route) => false);
          context.showSuccessSnackBar('Account verified successfully.');
        } else if (next.error != null) {
          context.showErrorSnackBar(next.error!); // Consistent error display
        }
      }
      // 3. Handle resend success
      if (previous?.status != AuthStatus.verificationSent &&
              next.status == AuthStatus.verificationSent &&
              _isCodeSent // Ensure this is after a resend, not the initial send
          ) {
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
                  const SizedBox(height: 30),
                  const HeaderTextWidget(
                    title: AppStrings.verifyAccount,
                    subtitle: AppStrings.verifyAccountSubtitle,
                  ),
                  const SizedBox(height: 50),
                  _buildForm(),
                  const SizedBox(height: 20), // Space below the button
                  _buildResendButton(theme), // Resend button
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Builds the form with the OTP input field and submit button.
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
            controller: _emailOtpController,
            validator: (value) => (value == null || value.isEmpty)
                ? 'Please enter the OTP'
                : null,
          ),
          const SizedBox(height: 30),
          PrimaryButton(
            text: AppStrings.verify,
            onPressed: authState.status == AuthStatus.loading
                ? null
                : _onVerifyOtpPressed,
            child: authState.status == AuthStatus.loading &&
                    _didAttemptVerification
                ? LoadingIndicator()
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
          // Use theme for styling
          color: theme.colorScheme.primary,
        ),
      ),
    );
  }
}

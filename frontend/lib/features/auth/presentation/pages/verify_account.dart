/*
Documentation:
---------------
File: verify_account.dart
Description:
  This file implements the VerifyAccountPage, which enables users to verify their account by entering an OTP (One-Time Password) sent to their email.
  It extracts the email from the route arguments, triggers sending of an initial verification code, and provides functionality to verify the OTP or resend the code.
  
Methods:
  • _extractEmailFromArgs():
      - Extracts the email from route arguments and triggers initial code sending.
  • _sendInitialVerificationCode():
      - Sends the verification code to the extracted email.
  • _onVerifyOtpPressed():
      - Validates the OTP input and attempts to verify it.
  • _onResendOtpPressed():
      - Resends the verification code to the user's email.
  • _buildForm():
      - Builds the OTP entry form.
  • _buildResendButton(ThemeData theme):
      - Constructs the button to resend the OTP.
*/

// Code:
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
import 'dart:async';

/// The verify account page of the application. Allows users to verify their account by entering an OTP.
class VerifyAccountPage extends ConsumerStatefulWidget {
  const VerifyAccountPage({super.key});

  @override
  ConsumerState<VerifyAccountPage> createState() => _VerifyAccountPageState();
}

class _VerifyAccountPageState extends ConsumerState<VerifyAccountPage> {
  final _formKey = GlobalKey<FormState>();
  final _emailOtpController = TextEditingController();
  late String _email;
  bool _didAttemptVerification = false;
  final bool _isCodeSent = false; // Tracks if the initial code has been sent.

  // Timer related variables
  Timer? _resendTimer;
  int _resendCoolDown = 60;
  bool _canResend = true; // Initially allow resending
  AuthState? _previousAuthState;

  @override
  void initState() {
    super.initState();
    WidgetsBinding.instance.addPostFrameCallback((_) {
      _extractEmailFromArgs();
    });
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final route = ModalRoute.of(context);
    if (route == null) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.of(context).pop();
        context.showErrorSnackBar("Navigation error. Please try again.");
      });
      return;
    }
  }

  /// Extracts the email from the route arguments and sends the verification code (only once).
  void _extractEmailFromArgs() {
    final args =
        ModalRoute.of(context)!.settings.arguments as Map<String, dynamic>?;
    _email = args?['email'] as String? ?? '';

    if (_email.isNotEmpty && !_isCodeSent) {
      _sendInitialVerificationCode();
    } else if (_email.isEmpty) {
      WidgetsBinding.instance.addPostFrameCallback((_) {
        Navigator.of(context).pop();
        context.showErrorSnackBar("Error: Email address is missing.");
      });
    }
  }

  /// Sends the initial verification code to the user's email.
  Future<void> _sendInitialVerificationCode() async {
    _previousAuthState = ref.read(authNotifierProvider);
    await ref.read(authNotifierProvider.notifier).sendVerificationCode(_email);
  }

  @override
  void dispose() {
    _emailOtpController.dispose();
    _resendTimer?.cancel();
    super.dispose();
  }

  /// Starts the cooldown timer for resending the OTP.
  void _startResendCoolDown() {
    if (!mounted) return;
    setState(() {
      _canResend = false;
    });

    _resendTimer = Timer.periodic(Duration(seconds: 1), (timer) {
      if (_resendCoolDown > 0) {
        if (mounted) {
          setState(() {
            _resendCoolDown--;
          });
        }
      } else {
        timer.cancel();
        if (mounted) {
          setState(() {
            _canResend = true;
            _resendCoolDown = 60; // Reset cooldown
          });
        }
      }
    });
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
    if (_canResend) {
      _previousAuthState =
          ref.read(authNotifierProvider); // Store *before* the call
      await ref
          .read(authNotifierProvider.notifier)
          .sendVerificationCode(_email);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    ref.listen<AuthState>(authNotifierProvider, (previous, next) {
      // 1. Handle *SUCCESSFUL* initial code sending (moved to listen).  More reliable.
      if (previous?.status != AuthStatus.verificationSent &&
          next.status == AuthStatus.verificationSent &&
          _isCodeSent) {
        context.showSuccessSnackBar('Verification code sent to $_email');
      }

      // 2. Handle OTP verification attempts (success and error).
      if (_didAttemptVerification && next.status != AuthStatus.loading) {
        _didAttemptVerification = false;

        if (next.status == AuthStatus.initial) {
          Navigator.pushNamedAndRemoveUntil(
              context, AppRoutes.login, (route) => false);
          context.showSuccessSnackBar('Account verified successfully.');
        } else if (next.error != null) {
          context.showErrorSnackBar(next.error!);
        }
      }
      // Check for successful resend *AFTER* the call to sendResetPasswordCode.
      if (_previousAuthState?.status != AuthStatus.verificationSent &&
          next.status == AuthStatus.verificationSent) {
        _startResendCoolDown(); // Start the timer ONLY on success
        context.showSuccessSnackBar('Verification code resent to $_email');
      } else if (_previousAuthState?.status == AuthStatus.loading &&
          next.status == AuthStatus.error) {
        //if it was in loading state and now in error that means our sendResetPasswordCode is failed
        context.showErrorSnackBar(next.error ?? "Failed to send OTP");
      }
      _previousAuthState = next;
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
                  const SizedBox(height: 20),
                  _buildResendButton(theme),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  /// Builds the OTP entry form.
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

  /// Constructs the button to resend the OTP.
  Widget _buildResendButton(ThemeData theme) {
    return TextButton(
      onPressed:
          _canResend ? _onResendOtpPressed : null, // Disable if on cooldown
      child: _canResend
          ? Text(
              "Resend OTP",
              style: theme.textTheme.labelLarge!.copyWith(
                color: theme.colorScheme.primary,
              ),
            )
          : Text(
              "Resend OTP ($_resendCoolDown s)", // Show countdown
              style: theme.textTheme.labelLarge!.copyWith(
                color: theme.colorScheme.onSurface
                    .withValues(alpha: 0.5), // Gray out text
              ),
            ),
    );
  }
}

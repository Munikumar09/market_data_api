import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/constants/app_strings.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/features/auth/functionality/providers/auth_providers.dart';
import 'package:frontend/features/auth/functionality/state/auth_notifier.dart';
import 'package:frontend/features/auth/presentation/widgets/header_text.dart';
import 'package:frontend/shared/buttons/custom_button.dart';
import 'package:frontend/shared/inputs/custom_text_field.dart';
import 'package:frontend/shared/layouts/custom_background_widget.dart';

class VerifyAccount extends ConsumerStatefulWidget {
  const VerifyAccount({super.key});

  @override
  ConsumerState<VerifyAccount> createState() => _VerifyAccountState();
}

class _VerifyAccountState extends ConsumerState<VerifyAccount> {
  final _formKey = GlobalKey<FormState>();
  final _emailOtpController = TextEditingController();
  late String email;

  @override
  void dispose() {
    _emailOtpController.dispose();
    super.dispose();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    final args =
        ModalRoute.of(context)?.settings.arguments as Map<String, String>;
    email = args['email'] ?? '';
  }

  void _verifyOtp(AuthNotifier authNotifier) async {
    if (_formKey.currentState?.validate() ?? false) {
      authNotifier.verifyOtp(email, _emailOtpController.text).then((_) {
        final authState = ref.read(authNotifierProvider);
        if (!authState.isLoading && authState.errorMessage == null) {
          // Navigate to the home page after successful verification
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('Account verified!'),
              backgroundColor: Colors.green,
            ),
          );
          Navigator.of(context).pushNamed(AppRoutes.login);
        } else if (authState.errorMessage != null) {
          // Display error message
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(authState.errorMessage!),
              backgroundColor: Colors.red,
            ),
          );
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    final authState = ref.watch(authNotifierProvider);
    final authNotifier = ref.read(authNotifierProvider.notifier);

    return Scaffold(
      backgroundColor: theme.colorScheme.surface,
      body: CustomBackgroundWidget(
        child: SingleChildScrollView(
          child: Container(
            height: MediaQuery.of(context).size.height,
            padding: const EdgeInsets.symmetric(horizontal: 24.0),
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                const SizedBox(height: 100),
                HeaderText(
                  title: AppStrings.verifyAccount,
                  subtitle: AppStrings.verifyAccountSubtitle,
                ),
                const SizedBox(height: 50),
                Form(
                  key: _formKey,
                  child: Column(
                    children: [
                      // Email OTP input field
                      CustomTextField(
                        hintText: AppStrings.emailOtp,
                        labelText: AppStrings.emailOtp,
                        keyboardType: TextInputType.number,
                        controller: _emailOtpController,
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 30),
                CustomButton(
                  text:
                      authState.isLoading ? "Verifying..." : AppStrings.verify,
                  onPressed: authState.isLoading
                      ? () {}
                      : () => _verifyOtp(authNotifier),
                ),
                const Spacer(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

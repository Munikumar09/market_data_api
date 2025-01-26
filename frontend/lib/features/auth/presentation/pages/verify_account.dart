import 'package:flutter/material.dart';
import 'package:frontend/core/constants/app_strings.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/features/auth/functionality/repository/auth_repository.dart';
import 'package:frontend/features/auth/presentation/widgets/header_text.dart';
import 'package:frontend/shared/buttons/custom_button.dart';
import 'package:frontend/shared/inputs/custom_text_field.dart';
import 'package:frontend/shared/layouts/custom_background_widget.dart';

class VerifyAccount extends StatefulWidget {
  const VerifyAccount({super.key});

  @override
  State<VerifyAccount> createState() => _VerifyAccountState();
}

class _VerifyAccountState extends State<VerifyAccount> {
  final _formKey = GlobalKey<FormState>();
  final _emailOtpController = TextEditingController();
  // final _phoneOtpController = TextEditingController();
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
    // phone = args['phone_number'] ?? '';
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
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
                      //email authentication input field
                      CustomTextField(
                        hintText: AppStrings.emailOtp,
                        labelText: AppStrings.emailOtp,
                        keyboardType: TextInputType.number,
                        controller: _emailOtpController,
                      ),
                      //phone authentication field for future use
                      // const SizedBox(height: 16),
                      // CustomTextField(
                      //   hintText: AppStrings.phoneOtp,
                      //   labelText: AppStrings.phoneOtp,
                      //   keyboardType: TextInputType.number,
                      //   controller: _phoneOtpController,
                      // ),
                    ],
                  ),
                ),
                const SizedBox(height: 30),
                CustomButton(
                  text: AppStrings.verify,
                  onPressed: () {
                    if (_formKey.currentState?.validate() ?? false) {
                      // Handle OTP verification
                      try {
                        AuthRepository().verifyOtp(
                          email,
                          _emailOtpController.text,
                          // phone,
                          // _phoneOtpController.text,
                        );
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(
                            content: Text('Account verified!'),
                            backgroundColor: Colors.green,
                          ),
                        );
                        Navigator.of(context).pushNamed(AppRoutes.home);
                      } catch (e) {
                        if (e is String) {
                          ScaffoldMessenger.of(context).showSnackBar(
                            SnackBar(
                              content: Text(e),
                              backgroundColor: Colors.red,
                            ),
                          );
                        }
                      }
                    }
                  },
                ),
                Spacer(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

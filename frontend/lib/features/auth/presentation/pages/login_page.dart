import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/constants/app_strings.dart';
import 'package:frontend/core/constants/app_text_styles.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/core/utils/validators.dart';
import 'package:frontend/features/auth/functionality/providers/auth_providers.dart';
import 'package:frontend/features/auth/functionality/state/auth_notifier.dart';
import 'package:frontend/features/auth/presentation/widgets/header_text.dart';
import 'package:frontend/features/auth/presentation/widgets/auth_footer.dart';
import 'package:frontend/features/home/home.dart';
import 'package:frontend/shared/buttons/custom_button.dart';
import 'package:frontend/shared/inputs/custom_text_field.dart';
import 'package:frontend/shared/layouts/custom_background_widget.dart';

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

  void _login(AuthNotifier authNotifier) async {
    if (_formKey.currentState!.validate()) {
      authNotifier
          .login(_emailController.text, _passwordController.text)
          .then((_) {
        final authState = ref.read(authNotifierProvider);
        if (!authState.isLoading && authState.errorMessage == null) {
          // Navigate to the home page after successful login
          ref.invalidate(protectedDataProvider);
          Navigator.of(context).pushNamed(AppRoutes.home);
        } else if (authState.errorMessage != null) {
          // Display error message
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(authState.errorMessage!),
              backgroundColor: Colors.red,
            ),
          );
          if (authState.isEmailNotVerified == true) {
            Navigator.of(context)
                .pushNamed(AppRoutes.verifyAccount, arguments: {
              'email': _emailController.text,
            });
          }
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
                Spacer(),
                HeaderText(
                  title: AppStrings.loginTitle,
                  subtitle: AppStrings.loginSubtitle,
                ),
                Spacer(),
                Form(
                  key: _formKey,
                  child: Column(
                    children: [
                      CustomTextField(
                        hintText: AppStrings.email,
                        labelText: AppStrings.email,
                        keyboardType: TextInputType.emailAddress,
                        controller: _emailController,
                        validator: (value) => Validators.email(value),
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
                ),
                const SizedBox(height: 10),
                Align(
                  alignment: Alignment.centerRight,
                  child: TextButton(
                    onPressed: () {
                      Navigator.of(context).pushNamed(AppRoutes.forgotPassword);
                    },
                    child: Text(
                      AppStrings.forgotPassword,
                      style:
                          AppTextStyles.headline3(theme.colorScheme.secondary),
                    ),
                  ),
                ),
                const SizedBox(height: 10),
                CustomButton(
                  text:
                      authState.isLoading ? "Logging in..." : AppStrings.login,
                  onPressed:
                      authState.isLoading ? () {} : () => _login(authNotifier),
                ),
                const SizedBox(height: 10),
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pushNamed(AppRoutes.register);
                  },
                  child: Text(
                    AppStrings.createAccount,
                    style: AppTextStyles.headline3(const Color(0xFF494949)),
                  ),
                ),
                Spacer(),
                const AuthFooter(),
                Spacer(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

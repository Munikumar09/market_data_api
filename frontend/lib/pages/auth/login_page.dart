import 'package:flutter/material.dart';
import 'package:frontend/components/buttons/custom_button.dart';
import 'package:frontend/components/common/auth_footer.dart';
import 'package:frontend/components/common/header_text.dart';
import 'package:frontend/components/custom_background_widget.dart';
import 'package:frontend/components/text_fields/custom_text_field.dart';
import 'package:frontend/app_styles/app_text_styles.dart';
import 'package:frontend/config/app_routes.dart';
import 'package:frontend/config/app_strings.dart';

class LoginPage extends StatelessWidget {
  LoginPage({super.key});
  final _formKey = GlobalKey<FormState>();

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: theme.colorScheme.surface,
      body: CustomBackgroundWidget(
        child: SingleChildScrollView(
          child: SizedBox(
            height: MediaQuery.of(context).size.height,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
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
                        ),
                        const SizedBox(height: 16),
                        CustomTextField(
                          hintText: AppStrings.password,
                          isPassword: true,
                          labelText: AppStrings.password,
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 10),
                  Align(
                    alignment: Alignment.centerRight,
                    child: TextButton(
                      onPressed: () => {
                        Navigator.of(context)
                            .pushNamed(AppRoutes.forgotPassword),
                      },
                      child: Text(
                        AppStrings.forgotPassword,
                        textAlign: TextAlign.right,
                        style: AppTextStyles.headline3(
                            theme.colorScheme.secondary),
                      ),
                    ),
                  ),
                  const SizedBox(height: 10),
                  CustomButton(text: AppStrings.login, onPressed: () {}),
                  const SizedBox(height: 10),
                  TextButton(
                    onPressed: () {
                      Navigator.of(context).pushNamed(AppRoutes.register);
                    },
                    child: Text(
                      AppStrings.createAccount,
                      style: AppTextStyles.headline3(Color(0xFF494949)),
                    ),
                  ),
                  Spacer(),
                  AuthFooter(),
                  Spacer(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

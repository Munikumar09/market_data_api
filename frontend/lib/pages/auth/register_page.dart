import 'package:flutter/material.dart';
import 'package:frontend/components/buttons/custom_button.dart';
import 'package:frontend/components/common/auth_footer.dart';
import 'package:frontend/components/common/header_text.dart';
import 'package:frontend/components/custom_background_widget.dart';
import 'package:frontend/components/text_fields/custom_text_field.dart';
import 'package:frontend/app_styles/app_text_styles.dart';
import 'package:frontend/config/app_routes.dart';
import 'package:frontend/config/app_strings.dart';

class RegisterPage extends StatelessWidget {
  const RegisterPage({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
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
                    title: AppStrings.registerTitle,
                    subtitle: AppStrings.registerSubtitle,
                  ),
                  Spacer(),
                  CustomTextField(
                      hintText: AppStrings.email,
                      labelText: AppStrings.email,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your email';
                        }
                        return null;
                      }),
                  const SizedBox(height: 16),
                  CustomTextField(
                    hintText: AppStrings.password,
                    isPassword: true,
                    labelText: AppStrings.password,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter your email';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 16),
                  CustomTextField(
                    hintText: AppStrings.confirmPassword,
                    isPassword: true,
                    labelText: AppStrings.confirmPassword,
                    validator: (value) {
                      if (value == null || value.isEmpty) {
                        return 'Please enter your email';
                      }
                      return null;
                    },
                  ),
                  const SizedBox(height: 30),
                  CustomButton(text: AppStrings.signUp, onPressed: () {}),
                  const SizedBox(height: 10),
                  TextButton(
                    onPressed: () {
                      Navigator.of(context).pushNamed(AppRoutes.login);
                    },
                    child: Text(
                      AppStrings.haveAccount,
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

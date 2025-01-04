  import 'package:flutter/material.dart';
  import 'package:frontend/components/buttons/custom_button.dart';
  import 'package:frontend/components/buttons/icon_button.dart';
  import 'package:frontend/components/custom_background_widget.dart';
  import 'package:frontend/components/text_fields/custom_text_feild.dart';
  import 'package:frontend/config/app_text_styles.dart';

  class LoginPage extends StatelessWidget {
  const LoginPage({super.key});

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
                    Text('Login here',
                        textAlign: TextAlign.center,
                        style: AppTextStyles.headline1(
                            Theme.of(context).colorScheme.primary)),
                    Text(
                      "Welcome back\nyou've been missed!",
                      textAlign: TextAlign.center,
                      style: AppTextStyles.headline2(Colors.black),
                    ),
                    Spacer(),
                    CustomTextField(hintText: "Email"),
                    const SizedBox(height: 16),
                    CustomTextField(
                      hintText: "Password",
                      isPassword: true,
                    ),
                    Align(
                      alignment: Alignment.centerRight,
                      child: TextButton(
                        onPressed: () => {},
                        child: Text(
                          'Forgot your password?',
                          textAlign: TextAlign.right,
                          style: AppTextStyles.headline3(
                              Theme.of(context).colorScheme.secondary),
                        ),
                      ),
                    ),
                    const SizedBox(height: 10),
                    CustomButton(text: "Login", onPressed: () {}),
                    const SizedBox(height: 10),
                    TextButton(
                      onPressed: () {
                        Navigator.of(context).pushNamed('/register');
                        },
                      child: Text(
                        'Create an account',
                        style: AppTextStyles.headline3(Color(0xFF494949)),
                      ),
                    ),
                    Spacer(),
                    Text('Or continue with',
                        textAlign: TextAlign.center,
                        style: AppTextStyles.bodyText1(Color(0xFF1F41BB))),
                    const SizedBox(height: 16),
                    CustomIconButton(
                        onPressed: () => {},
                        iconPath: "assets/images/logos/google.png"),
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

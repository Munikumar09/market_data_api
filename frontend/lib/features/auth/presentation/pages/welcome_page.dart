import 'package:flutter/material.dart';
import 'package:frontend/core/constants/app_strings.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/features/auth/presentation/widgets/header_text.dart';
import 'package:frontend/shared/buttons/custom_button.dart';
import 'package:frontend/shared/layouts/custom_background_widget.dart';

class WelcomePage extends StatelessWidget {
  const WelcomePage({super.key});

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
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Spacer(),
                  Image.asset(
                    'assets/images/welcome_image.png',
                    width: MediaQuery.of(context).size.width,
                    height: MediaQuery.of(context).size.height / 2.5,
                  ),
                  Spacer(),
                  HeaderText(
                      title: AppStrings.welcomeTitle,
                      subtitle: AppStrings.welcomeSubtitle),
                  Spacer(),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      Expanded(
                        child: CustomButton(
                            text: AppStrings.signUp,
                            onPressed: () {
                              Navigator.of(context)
                                  .pushNamed(AppRoutes.register);
                            }),
                      ),
                      const SizedBox(width: 20),
                      Expanded(
                        child: CustomButton(
                            text: AppStrings.login,
                            onPressed: () {
                              Navigator.of(context).pushNamed(AppRoutes.login);
                            }),
                      ),
                    ],
                  ),
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

import 'package:flutter/material.dart';
import 'package:frontend/components/buttons/custom_button.dart';
import 'package:frontend/components/custom_background_widget.dart';
import 'package:frontend/config/app_text_styles.dart';

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
                children: [
                  Spacer(),
                  Image.asset(
                    'assets/images/welcome_image.png',
                    width: MediaQuery.of(context).size.width,
                    height: MediaQuery.of(context).size.height / 2.5,
                  ),
                  Spacer(),
                  Text(
                    'Master the Market\nwith Zero Risk',
                    textAlign: TextAlign.center,
                    style: AppTextStyles.headline1(
                        Theme.of(context).colorScheme.primary),
                  ),
                  const SizedBox(height: 10),
                  Text(
                    "Trade stocks and options virtually.\nLearn, practice, and grow risk-free  ",
                    textAlign: TextAlign.center,
                    style: AppTextStyles.headline2(Colors.black),
                  ),
                  Spacer(),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceAround,
                    children: [
                      Expanded(
                        child: CustomButton(
                            text: "Sign Up",
                            onPressed: () {
                              Navigator.of(context).pushNamed('/register');
                            }),
                      ),
                      const SizedBox(width: 20),
                      Expanded(
                        child: CustomButton(
                            text: "Login",
                            onPressed: () {
                              Navigator.of(context).pushNamed('/login');
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

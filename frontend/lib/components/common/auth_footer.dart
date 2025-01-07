import 'package:flutter/material.dart';
import 'package:frontend/app_styles/app_text_styles.dart';
import 'package:frontend/components/buttons/icon_button.dart';
import 'package:frontend/config/app_strings.dart';

class AuthFooter extends StatelessWidget {
  const AuthFooter({super.key});
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(top: 20.0),
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: <Widget>[
          Text(
            AppStrings.continueWith,
            style: AppTextStyles.bodyText1(
              Theme.of(context).primaryColor,
            ),
          ),
          const SizedBox(height: 16),
          CustomIconButton(
              onPressed: () => {
                    // implement login or sign up using the google
                  },
              iconPath: "assets/images/logos/google.png"),
        ],
      ),
    );
  }
}

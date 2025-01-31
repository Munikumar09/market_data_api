import 'package:flutter/material.dart';
import 'package:frontend/core/constants/app_text_styles.dart';

class HeaderText extends StatelessWidget {
  const HeaderText({
    super.key,
    required this.title,
    this.subtitle,
    this.titleColor,
    this.subtitleColor,
  });

  final String title;
  final String? subtitle;
  final Color? titleColor;
  final Color? subtitleColor;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);

    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Text(
          title,
          style: AppTextStyles.headline1(
            titleColor ?? theme.primaryColor,
          ),
          // Add semantic properties for accessibility
          semanticsLabel: title,
        ),
        const SizedBox(height: 16),
        if (subtitle != null)
          Text(
            subtitle!,
            style: AppTextStyles.headline2(
              subtitleColor ?? theme.colorScheme.onSurface,
            ),
            semanticsLabel: subtitle,
          ),
      ],
    );
  }
}

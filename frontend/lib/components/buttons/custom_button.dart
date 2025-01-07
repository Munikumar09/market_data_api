import 'package:flutter/material.dart';
import 'package:frontend/app_styles/app_text_styles.dart';

class CustomButton extends StatelessWidget {
  final String text;
  final VoidCallback onPressed;
  final Color? backgroundColor;
  final Color? textColor;
  final double fontSize;
  final BorderRadius borderRadius;

  const CustomButton({
    super.key,
    required this.text,
    required this.onPressed,
    this.backgroundColor,
    this.textColor,
    this.fontSize = 20,
    this.borderRadius = const BorderRadius.all(Radius.circular(10)),
  });

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return GestureDetector(
      onTap: onPressed,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 15),
        decoration: BoxDecoration(
          color: backgroundColor ?? theme.primaryColor,
          borderRadius: borderRadius,
          boxShadow: [
            BoxShadow(
              color: backgroundColor ?? theme.primaryColor
                  .withValues(alpha: 0.3), // Shadow matches button color
              blurRadius: 20,
              offset: const Offset(0, 10),
              spreadRadius: 0,
            ),
          ],
        ),
        child: Center(
          child: Text(text,
              style: AppTextStyles.headline2(
                  textColor ?? theme.colorScheme.onPrimary)),
        ),
      ),
    );
  }
}

/*
Documentation:
---------------
Class: AppThemes
Description:
  Provides light and dark theme configurations for the app using Flutter's ThemeData.
  
Properties:
  • lightTheme:
      - ThemeData for light mode with custom color scheme and styling.
  • darkTheme:
      - ThemeData for dark mode with custom color scheme and styling.

Usage:
  Example: MaterialApp(theme: AppThemes.lightTheme, darkTheme: AppThemes.darkTheme);
*/

// Code:
import 'package:flutter/material.dart';
import 'package:frontend/core/constants/app_colors.dart';

/// Provides light, dark and custom themes for the app.
class AppThemes {
  /// Theme configuration for light mode.
  static final ThemeData lightTheme = ThemeData(
    brightness: Brightness.light,
    hintColor: AppColors.lightHint,
    primaryColorLight: AppColors.lightPrimaryLight,
    dividerColor: AppColors.lightDivider,
    colorScheme: ColorScheme(
      primary: AppColors.lightPrimary,
      secondary: AppColors.lightSecondary,
      surface: AppColors.lightSurface,
      tertiary: AppColors.tertiary,
      onTertiary: AppColors.lightOnTertiary,
      error: AppColors.lightError,
      onPrimary: AppColors.lightOnPrimary,
      onSecondary: AppColors.lightOnSecondary,
      onSurface: AppColors.lightOnSurface,
      onError: AppColors.lightOnError,
      brightness: Brightness.light,
    ),
    scaffoldBackgroundColor: AppColors.lightSurface,
    fontFamily: 'Roboto',
  );

  /// Theme configuration for dark mode.
  static final ThemeData darkTheme = ThemeData(
    brightness: Brightness.dark,
    colorScheme: ColorScheme(
      primary: AppColors.darkPrimary,
      secondary: AppColors.darkSecondary,
      surface: AppColors.darkSurface,
      error: AppColors.darkError,
      onPrimary: AppColors.darkOnPrimary,
      onSecondary: AppColors.darkOnSecondary,
      onSurface: AppColors.darkOnSurface,
      onError: AppColors.darkOnError,
      brightness: Brightness.dark,
    ),
    scaffoldBackgroundColor: AppColors.darkBackground,
  );
}

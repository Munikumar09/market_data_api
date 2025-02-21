/*
Documentation:
---------------
Class: AppTextStyles
Description:
  Provides helper methods that return TextStyle objects for different use cases in the application.
  
Methods:
  • headline1(color):
      - Returns a TextStyle for primary headlines.
      - Example: AppTextStyles.headline1(Colors.black);
  • headline2(color):
      - Returns a TextStyle for secondary headlines.
  • headline3(color):
      - Returns a TextStyle for tertiary headlines.
  • bodyText1(color):
      - Returns a TextStyle for primary body text.
  • bodyText2(color):
      - Returns a TextStyle for secondary body text.
  • caption(color):
      - Returns a TextStyle for caption texts.
*/

// Code:
import 'package:flutter/material.dart';

/// Provides helper methods that return TextStyle objects for different use cases in the application.
class AppTextStyles {
  /// Returns a TextStyle for primary headlines.
  static TextStyle headline1(Color color) {
    return TextStyle(
      color: color,
      fontSize: 30,
      fontWeight: FontWeight.w700,
    );
  }

  /// Returns a TextStyle for secondary headlines.
  static TextStyle headline2(Color color) {
    return TextStyle(
      color: color,
      fontSize: 20,
      fontWeight: FontWeight.w600,
    );
  }

  /// Returns a TextStyle for tertiary headlines.
  static TextStyle headline3(Color color) {
    return TextStyle(
      fontSize: 18.0,
      fontWeight: FontWeight.w600,
      color: color,
    );
  }

  /// Returns a TextStyle for primary body text.
  static TextStyle bodyText1(Color color) {
    return TextStyle(
      fontSize: 16.0,
      fontWeight: FontWeight.w500,
      color: color,
    );
  }

  /// Returns a TextStyle for secondary body text.
  static TextStyle bodyText2(Color color) {
    return TextStyle(
      fontSize: 14.0,
      fontWeight: FontWeight.normal,
      color: color,
    );
  }

  /// Returns a TextStyle for captions.
  static TextStyle caption(Color color) {
    return TextStyle(
      fontSize: 12.0,
      fontWeight: FontWeight.normal,
      color: color,
    );
  }
}

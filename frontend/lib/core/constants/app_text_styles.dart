import 'package:flutter/material.dart';

class AppTextStyles {
  static TextStyle headline1(Color color) {
    return TextStyle(
      color: color,
      fontSize: 30,
      fontWeight: FontWeight.w700,
    );
  }

  static TextStyle headline2(Color color) {
    return TextStyle(
      color: color,
      fontSize: 20,
      fontWeight: FontWeight.w600,
    );
  }

  static TextStyle headline3(Color color) {
    return TextStyle(
      fontSize: 18.0,
      fontWeight: FontWeight.w600,
      color: color,
    );
  }

  static TextStyle bodyText1(Color color) {
    return TextStyle(
      fontSize: 16.0,
      fontWeight: FontWeight.w500,
      color: color,
    );
  }

  static TextStyle bodyText2(Color color) {
    return TextStyle(
      fontSize: 14.0,
      fontWeight: FontWeight.normal,
      color: color,
    );
  }

  static TextStyle caption(Color color) {
    return TextStyle(
      fontSize: 12.0,
      fontWeight: FontWeight.normal,
      color: color,
    );
  }
}

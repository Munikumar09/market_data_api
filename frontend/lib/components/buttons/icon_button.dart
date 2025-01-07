import 'package:flutter/material.dart';
// import 'package:flutter_svg/flutter_svg.dart';

class CustomIconButton extends StatelessWidget {
  final VoidCallback onPressed;
  final String iconPath;

  const CustomIconButton(
      {super.key, required this.onPressed, required this.iconPath});

  @override
  Widget build(BuildContext context) {
    return IconButton(
      onPressed: onPressed,
      icon: Image.asset(
        iconPath,
        width: 27,
        height: 27,
      ),
    );
  }
}

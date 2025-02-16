// loading_indicator.dart
import 'package:flutter/material.dart';

class LoadingIndicator extends StatelessWidget {
  final Color? color;
  final double strokeWidth;
  final double size;

  const LoadingIndicator({
    super.key,
    this.color, // Optional: Customize the color
    this.strokeWidth = 2.0, // Optional: Customize stroke width
    this.size = 20.0, // Optional: Customize the size
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      height: size,
      width: size,
      child: CircularProgressIndicator(
        strokeWidth: strokeWidth,
        color: color ?? Colors.white, // Default to white if not specified
      ),
    );
  }
}

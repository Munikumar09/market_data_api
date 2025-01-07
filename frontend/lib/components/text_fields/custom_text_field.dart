import 'package:flutter/material.dart';
import 'package:frontend/app_styles/app_text_styles.dart';

class CustomTextField extends StatefulWidget {
  final String hintText;
  final bool isPassword;
  final TextEditingController? controller;
  final String? labelText;
  final String? Function(String?)? validator; // added
  final TextInputType? keyboardType; // added

  const CustomTextField({
    super.key,
    required this.hintText,
    this.isPassword = false,
    this.controller,
    this.labelText,
    this.validator, // added
    this.keyboardType, // added
  });

  @override
  _CustomTextFieldState createState() => _CustomTextFieldState();
}

class _CustomTextFieldState extends State<CustomTextField> {
  bool _isPasswordVisible = false;

  @override
  Widget build(BuildContext context) {
    return TextFormField(
      // changed to TextFormField
      controller: widget.controller,
      obscureText: widget.isPassword && !_isPasswordVisible,
      validator: widget.validator, // added
      keyboardType: widget.keyboardType, // added
      decoration: InputDecoration(
        labelText: widget.labelText,
        hintText: widget.hintText,
        hintStyle: AppTextStyles.bodyText1(Theme.of(context).hintColor),
        filled: true,
        fillColor: Theme.of(context).primaryColorLight,
        contentPadding: const EdgeInsets.symmetric(
          horizontal: 20,
          vertical: 20,
        ),
        enabledBorder: OutlineInputBorder(
          borderSide: BorderSide.none,
          borderRadius: BorderRadius.circular(10),
        ),
        focusedBorder: OutlineInputBorder(
          borderSide: BorderSide(
            color: Theme.of(context).primaryColor,
            width: 2,
          ),
          borderRadius: BorderRadius.circular(10),
        ),
        suffixIcon: widget.isPassword
            ? IconButton(
                icon: Icon(
                  _isPasswordVisible ? Icons.visibility : Icons.visibility_off,
                  color: Theme.of(context).primaryColor,
                ),
                onPressed: () {
                  setState(() {
                    _isPasswordVisible = !_isPasswordVisible;
                  });
                },
              )
            : null,
      ),
      style: AppTextStyles.bodyText1(Theme.of(context).primaryColor),
    );
  }
}

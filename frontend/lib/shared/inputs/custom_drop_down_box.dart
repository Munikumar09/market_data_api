import 'package:flutter/material.dart';
import 'package:frontend/core/constants/app_text_styles.dart';

class CustomDropdown extends StatefulWidget {
  final String labelText;
  final List<String> options;
  final String? selectedOption;
  final String? Function(String?)? validator;
  final Function(String?)? onChanged;

  const CustomDropdown({
    super.key,
    required this.labelText,
    required this.options,
    this.selectedOption,
    this.validator,
    this.onChanged,
  });

  @override
  State<CustomDropdown> createState() => _CustomDropdownState();
}

class _CustomDropdownState extends State<CustomDropdown> {
  String? _selectedOption;

  @override
  void initState() {
    super.initState();
    _selectedOption = widget.selectedOption;
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return DropdownButtonFormField<String>(
      value: _selectedOption,
      onChanged: (value) {
        setState(() {
          _selectedOption = value;
        });
        if (widget.onChanged != null) {
          widget.onChanged!(value);
        }
      },
      iconEnabledColor: theme.primaryColor,
      validator: widget.validator ??
          (value) {
            if (value == null || value.isEmpty) {
              return "Please select a ${widget.labelText}";
            }
            return null;
          },
      decoration: InputDecoration(
        labelText: widget.labelText,
        filled: true,
        fillColor: theme.primaryColorLight,
        contentPadding:
            const EdgeInsets.symmetric(horizontal: 20, vertical: 20),
        enabledBorder: OutlineInputBorder(
          borderSide: BorderSide.none,
          borderRadius: BorderRadius.circular(10),
        ),
        focusedBorder: OutlineInputBorder(
          borderSide: BorderSide(color: theme.primaryColor, width: 2),
          borderRadius: BorderRadius.circular(10),
        ),
        errorBorder: OutlineInputBorder(
          borderSide: BorderSide(color: theme.colorScheme.error),
          borderRadius: BorderRadius.circular(10),
        ),
        focusedErrorBorder: OutlineInputBorder(
          borderSide: BorderSide(color: theme.colorScheme.error, width: 2),
          borderRadius: BorderRadius.circular(10),
        ),
      ),
      items: widget.options
          .map(
            (option) => DropdownMenuItem<String>(
              value: option,
              child: Text(
                option,
                style: AppTextStyles.bodyText1(theme.primaryColor),
              ),
            ),
          )
          .toList(),
    );
  }
}

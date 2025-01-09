import 'package:flutter/material.dart';
import 'package:frontend/components/buttons/custom_button.dart';
import 'package:frontend/components/common/auth_footer.dart';
import 'package:frontend/components/common/header_text.dart';
import 'package:frontend/components/custom_background_widget.dart';
import 'package:frontend/components/text_fields/custom_drop_down_box.dart';
import 'package:frontend/components/text_fields/custom_text_field.dart';
import 'package:frontend/app_styles/app_text_styles.dart';
import 'package:frontend/config/app_routes.dart';
import 'package:frontend/config/app_strings.dart';

class RegisterPage extends StatefulWidget {
  RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _formKey = GlobalKey<FormState>();
  DateTime? _selectedDate;

  Future<void> selectDate(BuildContext context) async {
    final DateTime? pickedDate = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );
    if (pickedDate != null && pickedDate != _selectedDate) {
      setState(() {
        _selectedDate = pickedDate;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      body: CustomBackgroundWidget(
        child: SingleChildScrollView(
          child: SizedBox(
            height: MediaQuery.of(context).size.height,
            child: Padding(
              padding: const EdgeInsets.symmetric(horizontal: 24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  Spacer(),
                  HeaderText(
                    title: AppStrings.registerTitle,
                    subtitle: AppStrings.registerSubtitle,
                  ),
                  Spacer(),
                  Form(
                    key: _formKey,
                    child: Column(
                      children: [
                        CustomTextField(
                          hintText: AppStrings.username,
                          labelText: AppStrings.username,
                        ),
                        const SizedBox(height: 10),
                        CustomTextField(
                          hintText: AppStrings.email,
                          labelText: AppStrings.email,
                        ),
                        const SizedBox(height: 10),
                        CustomTextField(
                          hintText: AppStrings.password,
                          isPassword: true,
                          labelText: AppStrings.password,
                        ),
                        const SizedBox(height: 10),
                        CustomTextField(
                          hintText: AppStrings.phoneNumber,
                          labelText: AppStrings.phoneNumber,
                          keyboardType: TextInputType.phone,
                        ),
                        const SizedBox(height: 10),
                        CustomTextField(
                          labelText: AppStrings.dateOfBirth,
                          hintText: _selectedDate == null
                              ? AppStrings.dateOfBirth
                              : "${_selectedDate!.day}/${_selectedDate!.month}/${_selectedDate!.year}",
                          suffixIcon: Icons.calendar_today,
                          onSuffixTap: () {
                            selectDate(context);
                          },
                        ),
                        const SizedBox(height: 10),
                        CustomDropdown(
                          labelText: AppStrings.gender,
                          options: ["Male", "Female", "Other"],
                          onChanged: (value) {
                            // Handle gender selection
                            print("Selected Gender: $value");
                          },
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 30),
                  CustomButton(text: AppStrings.signUp, onPressed: () {}),
                  const SizedBox(height: 10),
                  TextButton(
                    onPressed: () {
                      Navigator.of(context).pushNamed(AppRoutes.login);
                    },
                    child: Text(
                      AppStrings.haveAccount,
                      style: AppTextStyles.headline3(Color(0xFF494949)),
                    ),
                  ),
                  Spacer(),
                  AuthFooter(),
                  Spacer(),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

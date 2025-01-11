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
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _formKey = GlobalKey<FormState>();
  final _dateController = TextEditingController();

  @override
  void dispose() {
    _dateController.dispose();
    super.dispose();
  }

  Future<void> _selectDate(BuildContext context) async {
    final pickedDate = await showDatePicker(
      context: context,
      initialDate: DateTime.now(),
      firstDate: DateTime(1900),
      lastDate: DateTime.now(),
    );
    if (pickedDate != null) {
      setState(() {
        _dateController.text =
            "${pickedDate.day}/${pickedDate.month}/${pickedDate.year}";
      });
    }
  }

  void _submit() {
    if (_formKey.currentState!.validate()) {
      // Handle submission logic
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      body: CustomBackgroundWidget(
        child: SingleChildScrollView(
          child: Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 24.0, vertical: 16.0),
            height: MediaQuery.of(context).size.height,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
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
                        keyboardType: TextInputType.emailAddress,
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
                        readOnly: true,
                        labelText: AppStrings.dateOfBirth,
                        hintText: AppStrings.dateOfBirth,
                        suffixIcon: Icons.calendar_today,
                        controller: _dateController,
                        onSuffixTap: () => _selectDate(context),
                      ),
                      const SizedBox(height: 10),
                      CustomDropdown(
                        labelText: AppStrings.gender,
                        options: ["Male", "Female", "Other"],
                        onChanged: (value) {},
                      ),
                    ],
                  ),
                ),
                const SizedBox(height: 30),
                CustomButton(
                  text: AppStrings.signUp,
                  onPressed: _submit,
                ),
                const SizedBox(height: 10),
                TextButton(
                  onPressed: () {
                    Navigator.of(context).pushNamed(AppRoutes.login);
                  },
                  child: Text(
                    AppStrings.haveAccount,
                    style: AppTextStyles.headline3(const Color(0xFF494949)),
                  ),
                ),
                const SizedBox(height: 20),
                const AuthFooter(),
                Spacer(),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

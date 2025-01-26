import 'package:flutter/material.dart';
import 'package:frontend/core/constants/app_strings.dart';
import 'package:frontend/core/constants/app_text_styles.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/features/auth/functionality/model/signup_request.dart';
import 'package:frontend/features/auth/functionality/repository/auth_repository.dart';
import 'package:frontend/features/auth/presentation/widgets/auth_footer.dart';
import 'package:frontend/features/auth/presentation/widgets/header_text.dart';
import 'package:frontend/shared/buttons/custom_button.dart';
import 'package:frontend/shared/inputs/custom_drop_down_box.dart';
import 'package:frontend/shared/inputs/custom_text_field.dart';
import 'package:frontend/shared/layouts/custom_background_widget.dart';

class RegisterPage extends StatefulWidget {
  const RegisterPage({super.key});

  @override
  State<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends State<RegisterPage> {
  final _formKey = GlobalKey<FormState>();
  final _dateController = TextEditingController();
  final _passwordController = TextEditingController();
  final _phoneNumberController = TextEditingController();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _confirmPasswordController = TextEditingController();
  String? selectedGender;
  @override
  void dispose() {
    _dateController.dispose();
    _passwordController.dispose();
    _phoneNumberController.dispose();
    _usernameController.dispose();
    _emailController.dispose();
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

  void _submit() async {
    if (_formKey.currentState!.validate()) {
      SignupRequest request = SignupRequest(
        username: _usernameController.text,
        email: _emailController.text,
        password: _passwordController.text,
        confirmPassword: _confirmPasswordController.text,
        phoneNumber: _phoneNumberController.text,
        dateOfBirth: _dateController.text,
        gender: selectedGender!,
      );
      print(request);
      try {
        await AuthRepository().signup(request);
        Navigator.of(context).pushNamed(AppRoutes.verifyAccount, arguments: {
          'email': request.email,
          'phone': request.phoneNumber,
        });
      } catch (e) {
        // if (e is String) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(e.toString()),
              backgroundColor: Colors.red,
            ),
          );
        // }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.surface,
      body: CustomBackgroundWidget(
        child: SafeArea(
          child: LayoutBuilder(
            builder: (context, constraints) {
              return SingleChildScrollView(
                child: ConstrainedBox(
                  constraints: BoxConstraints(minHeight: constraints.maxHeight),
                  child: IntrinsicHeight(
                    child: Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 24.0),
                      child: Column(
                        children: [
                          Spacer(),
                          HeaderText(
                            title: AppStrings.registerTitle,
                            subtitle: AppStrings.registerSubtitle,
                          ),
                          SizedBox(height: 15),
                          Spacer(),
                          Form(
                            key: _formKey,
                            child: Column(
                              children: [
                                CustomTextField(
                                  hintText: AppStrings.username,
                                  labelText: AppStrings.username,
                                  controller: _usernameController,
                                ),
                                const SizedBox(height: 10),
                                CustomTextField(
                                  hintText: AppStrings.email,
                                  labelText: AppStrings.email,
                                  keyboardType: TextInputType.emailAddress,
                                  controller: _emailController,
                                ),
                                const SizedBox(height: 10),
                                CustomTextField(
                                  hintText: AppStrings.password,
                                  isPassword: true,
                                  labelText: AppStrings.password,
                                  controller: _passwordController,
                                  autocorrect: false,
                                  enableSuggestions: false,
                                ),
                                const SizedBox(height: 10),
                                CustomTextField(
                                  hintText: AppStrings.confirmPassword,
                                  isPassword: true,
                                  labelText: AppStrings.confirmPassword,
                                  controller: _confirmPasswordController,
                                  autocorrect: false,
                                  enableSuggestions: false,
                                ),
                                const SizedBox(height: 10),
                                CustomTextField(
                                  hintText: AppStrings.phoneNumber,
                                  labelText: AppStrings.phoneNumber,
                                  keyboardType: TextInputType.phone,
                                  controller: _phoneNumberController,
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
                                  onChanged: (value) {
                                    setState(() {
                                      selectedGender = value;
                                    });
                                  },
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 20),
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
                              style: AppTextStyles.headline3(
                                  const Color(0xFF494949)),
                            ),
                          ),
                          const SizedBox(height: 15),
                          const AuthFooter(),
                          Spacer(),
                        ],
                      ),
                    ),
                  ),
                ),
              );
            },
          ),
        ),
      ),
    );
  }
}

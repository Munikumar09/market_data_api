import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/constants/app_strings.dart';
import 'package:frontend/core/constants/app_text_styles.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/core/utils/validators.dart';
import 'package:frontend/features/auth/functionality/model/signup_request.dart';
import 'package:frontend/features/auth/functionality/providers/auth_providers.dart';
import 'package:frontend/features/auth/functionality/state/auth_notifier.dart';
import 'package:frontend/features/auth/presentation/widgets/auth_footer.dart';
import 'package:frontend/features/auth/presentation/widgets/header_text.dart';
import 'package:frontend/shared/buttons/custom_button.dart';
import 'package:frontend/shared/inputs/custom_drop_down_box.dart';
import 'package:frontend/shared/inputs/custom_text_field.dart';
import 'package:frontend/shared/layouts/custom_background_widget.dart';

class RegisterPage extends ConsumerStatefulWidget {
  const RegisterPage({super.key});

  @override
  ConsumerState<RegisterPage> createState() => _RegisterPageState();
}

class _RegisterPageState extends ConsumerState<RegisterPage> {
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
    _confirmPasswordController.dispose();
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

  void _submit(BuildContext context, AuthNotifier authNotifier) {
    if (_formKey.currentState!.validate()) {
      final signupRequest = SignupRequest(
        username: _usernameController.text,
        email: _emailController.text,
        password: _passwordController.text,
        confirmPassword: _confirmPasswordController.text,
        phoneNumber: _phoneNumberController.text,
        dateOfBirth: _dateController.text,
        gender: selectedGender!,
      );
      authNotifier.signup(signupRequest).then((_) {
        final authState = ref.read(authNotifierProvider);
        if (!authState.isLoading && authState.errorMessage == null) {
          Navigator.of(context).pushNamed(
            AppRoutes.verifyAccount,
            arguments: {
              'email': signupRequest.email,
            },
          );
        } else {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(
              content: Text(authState.errorMessage!),
              backgroundColor: Colors.red,
            ),
          );
        }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    final authState = ref.watch(authNotifierProvider);
    final authNotifier = ref.read(authNotifierProvider.notifier);

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
                          const Spacer(),
                          HeaderText(
                            title: AppStrings.registerTitle,
                            subtitle: AppStrings.registerSubtitle,
                          ),
                          const SizedBox(height: 15),
                          const Spacer(),
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
                                  validator: (value) => Validators.email(value),
                                ),
                                const SizedBox(height: 10),
                                CustomTextField(
                                  hintText: AppStrings.password,
                                  isPassword: true,
                                  labelText: AppStrings.password,
                                  controller: _passwordController,
                                  autocorrect: false,
                                  enableSuggestions: false,
                                  validator: (value) =>
                                      Validators.password(value),
                                ),
                                const SizedBox(height: 10),
                                CustomTextField(
                                  hintText: AppStrings.confirmPassword,
                                  isPassword: true,
                                  labelText: AppStrings.confirmPassword,
                                  controller: _confirmPasswordController,
                                  autocorrect: false,
                                  enableSuggestions: false,
                                  validator: (value) =>
                                      Validators.confirmPassword(
                                    _passwordController.text,
                                    value,
                                  ),
                                ),
                                const SizedBox(height: 10),
                                CustomTextField(
                                  hintText: AppStrings.phoneNumber,
                                  labelText: AppStrings.phoneNumber,
                                  keyboardType: TextInputType.phone,
                                  controller: _phoneNumberController,
                                  validator: (value) =>
                                      Validators.phoneNumber(value),
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
                            text: authState.isLoading
                                ? "Signing Up..."
                                : AppStrings.signUp,
                            onPressed: authState.isLoading
                                ? () {}
                                : () => _submit(context, authNotifier),
                          ),
                          const SizedBox(height: 10),
                          TextButton(
                            onPressed: () {
                              Navigator.of(context).pushNamed(AppRoutes.login);
                            },
                            child: Text(
                              AppStrings.haveAccount,
                              style: AppTextStyles.headline3(
                                const Color(0xFF494949),
                              ),
                            ),
                          ),
                          Spacer(),
                          const AuthFooter(),
                          const Spacer(),
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

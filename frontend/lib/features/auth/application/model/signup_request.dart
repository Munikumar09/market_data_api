class SignupRequest {
  final String email;
  final String username;
  final String password;
  final String confirmPassword;
  final String dateOfBirth;
  final String phoneNumber;
  final String gender;

  SignupRequest({
    required this.email,
    required this.username,
    required this.password,
    required this.confirmPassword,
    required this.dateOfBirth,
    required this.phoneNumber,
    required this.gender,
  });

  Map<String, dynamic> toJson() => {
        'email': email,
        'username': username,
        'password': password,
        'confirm_password': confirmPassword,
        'date_of_birth': dateOfBirth,
        'phone_number': phoneNumber,
        'gender': gender
      };
}

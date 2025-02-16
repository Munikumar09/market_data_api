import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/core/utils/validators.dart';

void main() {
  group('Validators.email', () {
    test('should return error when email is null', () {
      final result = Validators.email(null);
      expect(result, 'Please enter your email');
    });

    test('should return error when email is empty', () {
      final result = Validators.email('');
      expect(result, 'Please enter your email');
    });

    test('should return error for invalid email', () {
      final result = Validators.email('invalidemail');
      expect(result, 'Please enter a valid email address');
    });

    test('should return null for valid email', () {
      final result = Validators.email('test@example.com');
      expect(result, null);
    });
  });

  group('Validators.password', () {
    test('should return error when password is null', () {
      final result = Validators.password(null);
      expect(result, 'Please enter your password');
    });

    test('should return error when password is empty', () {
      final result = Validators.password('');
      expect(result, 'Please enter your password');
    });

    test('should return error when password is less than 8 characters', () {
      final result = Validators.password('Ab1!');
      expect(result, 'Password must be at least 8 characters long');
    });

    test('should return error when password has no uppercase letter', () {
      final result = Validators.password('abcdefg1!');
      expect(result, 'Password must contain at least one uppercase letter');
    });

    test('should return error when password has no number', () {
      final result = Validators.password('Abcdefgh!');
      expect(result, 'Password must contain at least one number');
    });

    test('should return error when password has no special character', () {
      final result = Validators.password('Abcdefg1');
      expect(result, 'Password must contain at least one special character');
    });

    test('should return null for a valid password', () {
      final result = Validators.password('Abcdef1!');
      expect(result, null);
    });
  });

  group('Validators.required', () {
    test('should return error when value is null', () {
      final result = Validators.required(null);
      expect(result, 'This field is required');
    });

    test('should return error when value is empty', () {
      final result = Validators.required('');
      expect(result, 'This field is required');
    });

    test('should return null when value is provided', () {
      final result = Validators.required('Some value');
      expect(result, null);
    });
  });

  group('Validators.confirmPassword', () {
    test('should return error when confirmPassword is null or empty', () {
      final resultNull = Validators.confirmPassword('Password1!', null);
      expect(resultNull, 'Please confirm your password');

      final resultEmpty = Validators.confirmPassword('Password1!', '');
      expect(resultEmpty, 'Please confirm your password');
    });

    test('should return error when passwords do not match', () {
      final result = Validators.confirmPassword('Password1!', 'Password2@');
      expect(result, 'Passwords do not match');
    });

    test('should return null when passwords match', () {
      final result = Validators.confirmPassword('Password1!', 'Password1!');
      expect(result, null);
    });
  });

  group('Validators.phoneNumber', () {
    // Assuming your phone number validator expects a non-empty value that matches a pattern.
    test('should return error when phone number is null', () {
      final result = Validators.phoneNumber(null);
      expect(result, 'Please enter your phone number');
    });

    test('should return error when phone number is empty', () {
      final result = Validators.phoneNumber('');
      expect(result, 'Please enter your phone number');
    });

    test('should return error for an invalid phone number', () {
      final result = Validators.phoneNumber('123-abc');
      expect(result, 'Please enter a valid phone number');
    });

    test('should return null for a valid phone number of 10 digits', () {
      final result = Validators.phoneNumber('1234567890');
      expect(result, null);
    });
    test('should return an error for a phone number with not exactly 10 digits',
        () {
      final result = Validators.phoneNumber('123456789');
      expect(result, 'Please enter a valid phone number');
    });
  });
}

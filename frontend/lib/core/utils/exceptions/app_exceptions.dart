/*
Documentation:
---------------
Module: Application Exceptions
Description:
  Provides a base exception class for the application along with other common exceptions 
  such as cache and input validation failures.
  
Classes:
  • AppException: Base exception for all application-specific errors.
  • CacheException: Thrown when caching fails.
  • InputValidationException: Thrown when user input validation fails.
*/

class AppException implements Exception {
  final String message;
  final StackTrace? stackTrace;

  AppException(this.message, [this.stackTrace]);

  @override
  String toString() => 'AppException: $message';
}

// Other Exceptions (You can add more as needed)
class CacheException extends AppException {
  CacheException(super.message, [super.stackTrace]);
}

class InputValidationException extends AppException {
  InputValidationException(super.message, [super.stackTrace]);
}

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

// Network Exceptions
import 'package:frontend/core/utils/exceptions/app_exceptions.dart';

class NetworkException extends AppException {
  NetworkException(super.message, [super.stackTrace]);
}

class ServerException extends NetworkException {
  ServerException(super.message, [super.stackTrace]);
}

class UnauthorizedException extends NetworkException {
  UnauthorizedException(super.message, [super.stackTrace]);
}

class NotFoundException extends NetworkException {
  NotFoundException(super.message, [super.stackTrace]);
}

/*
Documentation:
---------------
Module: Network Exceptions
Description:
  Defines custom exceptions for network-related errors such as server errors,
  unauthorized access, and resource not found. These exceptions extend from AppException.
  
Classes:
  • NetworkException: Base exception for network issues.
  • ServerException: Thrown when a server error occurs.
  • UnauthorizedException: Thrown when access is unauthorized.
  • NotFoundException: Thrown when a resource could not be found.
*/

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

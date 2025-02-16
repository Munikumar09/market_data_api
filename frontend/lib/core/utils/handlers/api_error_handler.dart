  import 'package:dio/dio.dart';
  import 'package:frontend/core/utils/exceptions/app_exceptions.dart';

  /// A helper class that handles Dio API errors.
  class ApiErrorHandler {
    /// Returns a human-readable message from a DioException.
    static String handleDioError(DioException e) {
      final responseData = e.response?.data;
      return (responseData is Map<String, dynamic>
              ? responseData['detail'] as String?
              : null) ??
          _getDefaultMessage(e);
    }

    /// Provides a default error message based on the DioException type.
    static String _getDefaultMessage(DioException e) {
      switch (e.type) {
        case DioExceptionType.connectionTimeout:
          return 'Connection timeout';
        case DioExceptionType.sendTimeout:
          return 'Send timeout';
        case DioExceptionType.receiveTimeout:
          return 'Receive timeout';
        case DioExceptionType.badCertificate:
          return 'Bad Certificate';
        case DioExceptionType.badResponse:
          return e.response != null
              ? 'Invalid server response (Status code: ${e.response!.statusCode})'
              : 'Invalid server response';
        case DioExceptionType.cancel:
          return 'Request cancelled';
        case DioExceptionType.connectionError:
          return 'Connection error';
        default:
          return e.message ?? 'Unknown network error';
      }
    }

    /// Constructs an AppException for invalid responses.
    static AppException handleInvalidResponse(Response response) {
      final method = response.requestOptions.method;
      final path = response.requestOptions.path;
      return AppException(
          'Invalid response (${response.statusCode}) for $method request to $path');
    }
  }

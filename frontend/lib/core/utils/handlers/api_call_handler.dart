import 'package:dio/dio.dart';
import 'package:frontend/core/utils/exceptions/app_exceptions.dart';
import 'package:frontend/core/utils/handlers/api_error_handler.dart';
import 'package:logger/logger.dart';

class ApiCallHandler {
  final Logger _logger = Logger(
    printer: PrettyPrinter(
      methodCount: 0, // Reduce clutter in production logs
      errorMethodCount: 5, // Show enough stack trace for errors
      lineLength: 120,
      colors: true,
      printEmojis: true,
      printTime: false,
    ), // Consider using a more configurable printer
  );

  Future<T> handleApiCall<T>({
    required Future<T> Function() call,
    required AppException Function(String) exception,
    required String operationName,
    bool suppressError = false, // Add a flag to suppress throwing errors
  }) async {
    try {
      final result = await call();
      _logger.i('$operationName succeeded');
      return result;
    } on DioException catch (e, stackTrace) {
      final errorMessage = ApiErrorHandler.handleDioError(e);
      _logger.e('$operationName failed: $errorMessage', e, stackTrace);
      if (!suppressError) {
        // Check if errors should be suppressed
        throw exception(errorMessage);
      } else {
        return null as T; // Explicitly handle null case
      }
    } on AppException catch (e, stackTrace) {
      _logger.e('$operationName failed: ${e.message}', e, stackTrace);
      if (!suppressError) {
        rethrow;
      } else {
        return null as T; // Explicitly handle null case
      }
    } catch (e, stackTrace) {
      _logger.e('Unexpected error during $operationName: $e', e, stackTrace);
      if (!suppressError) {
        throw exception('An unexpected error occurred');
      } else {
        return null as T; // Explicitly handle null case
      }
    }
  }

  // Updated validateResponse to return the response
  Response validateResponse(Response response, {int successStatus = 200}) {
    if (response.statusCode != successStatus) {
      throw ApiErrorHandler.handleInvalidResponse(response);
    }
    return response;
  }
}

import 'package:dio/dio.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:frontend/core/utils/exceptions/app_exceptions.dart';
import 'package:frontend/core/utils/handlers/api_call_handler.dart';
import 'package:mocktail/mocktail.dart';

// Mock Dio
class MockDio extends Mock implements Dio {}

void main() {
  late ApiCallHandler apiCallHandler;
  late MockDio mockDio;

  setUp(() {
    mockDio = MockDio();
    apiCallHandler =
        ApiCallHandler(); // Use the REAL ApiCallHandler and ApiErrorHandler
    registerFallbackValue(
        Response(requestOptions: RequestOptions(path: ""), statusCode: 200));
    registerFallbackValue(DioException(
      requestOptions: RequestOptions(path: ''),
      type: DioExceptionType.connectionError,
    ));
    registerFallbackValue(RequestOptions(path: ''));
  });

  group('ApiCallHandler', () {
    group('handleApiCall', () {
      test('should return result on successful call', () async {
        // Arrange
        const expectedResult = 'Success';
        when(() => mockDio.get(any())).thenAnswer((_) async => Response(
            data: expectedResult,
            statusCode: 200,
            requestOptions: RequestOptions(path: '')));

        // Act
        final result = await apiCallHandler.handleApiCall<String>(
          call: () => mockDio.get('/test').then((res) => res.data!),
          exception: (message) => AppException(message),
          operationName: 'Test Operation',
        );

        // Assert
        expect(result, expectedResult);
      });

      test('should throw exception on DioException, suppressError false',
          () async {
        // Arrange
        final dioError = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.connectionError,
          message: "Original Dio Error Message", // Include a message
          response: Response(
            // Include a response for realistic error
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 400, // Example status code
            data: {'detail': 'Detailed error from server'},
          ),
        );
        when(() => mockDio.get(any())).thenThrow(dioError);

        // Act & Assert (using expectLater for async)
        await expectLater(
          () => apiCallHandler.handleApiCall<String>(
            call: () => mockDio.get('/test').then((res) => res.data!),
            exception: (message) => AppException(message),
            operationName: 'Test Operation',
          ),
          throwsA(isA<AppException>().having((e) => e.message, 'message',
              'Detailed error from server')), // Check for the *correct* message
        );
      });

      test('should return null on DioException, suppressError true', () async {
        // Arrange
        final dioError = DioException(
            requestOptions: RequestOptions(path: '/test'),
            type: DioExceptionType.connectionError);
        when(() => mockDio.get(any())).thenThrow(dioError);

        // Act
        final result = await apiCallHandler.handleApiCall<String?>(
          call: () => mockDio.get('/test').then((res) => res.data),
          exception: (message) => AppException(message),
          operationName: 'Test Operation',
          suppressError: true,
        );

        // Assert
        expect(result, isNull);
      });

      test('should rethrow AppException, suppressError false', () async {
        // Arrange

        final appException = AppException("My Custom App Exception");
        when(() => mockDio.get(any())).thenThrow(appException);

        // Act & Assert
        await expectLater(
          () => apiCallHandler.handleApiCall<String>(
            call: () => mockDio.get('/test').then((res) => res.data!),
            exception: (message) => AppException(message),
            operationName: 'Test Operation',
          ),
          throwsA(isA<AppException>()
              .having((e) => e.message, 'message', "My Custom App Exception")),
        );
      });

      test('should return null on AppException, suppressError true', () async {
        // Arrange
        final appException = AppException("My Custom App Exception");
        when(() => mockDio.get(any())).thenThrow(appException);

        // Act
        final result = await apiCallHandler.handleApiCall<String?>(
          call: () => mockDio.get('/test').then((res) => res.data),
          exception: (message) => AppException(message),
          operationName: 'Test Operation',
          suppressError: true,
        );

        // Assert
        expect(result, isNull);
      });

      test('should throw exception on unexpected error, suppressError false',
          () async {
        // Arrange
        final unexpectedError = Exception('Unexpected error');
        when(() => mockDio.get(any())).thenThrow(unexpectedError);

        // Act & Assert
        await expectLater(
          () => apiCallHandler.handleApiCall<String>(
            call: () => mockDio.get('/test').then((res) => res.data!),
            exception: (message) => AppException(message), // Use AppException
            operationName: 'Test Operation',
          ),
          throwsA(isA<AppException>().having(
              (e) => e.message, 'message', 'An unexpected error occurred')),
        );
      });

      test('should return null on unexpected error, suppressError true',
          () async {
        // Arrange
        final unexpectedError = Exception('Unexpected error');
        when(() => mockDio.get(any())).thenThrow(unexpectedError);

        // Act
        final result = await apiCallHandler.handleApiCall<String?>(
          call: () => mockDio.get('/test').then((res) => res.data),
          exception: (message) => AppException(message),
          operationName: 'Test Operation',
          suppressError: true,
        );

        // Assert
        expect(result, isNull);
      });

      test(
          'should throw exception with correct message for different DioExceptionTypes',
          () async {
        // Arrange
        final dioExceptions = {
          DioExceptionType.connectionTimeout: 'Connection timeout',
          DioExceptionType.sendTimeout: 'Send timeout',
          DioExceptionType.receiveTimeout: 'Receive timeout',
          DioExceptionType.badCertificate: 'Bad Certificate',
          DioExceptionType.cancel: 'Request cancelled',
          DioExceptionType.connectionError: 'Connection error',
          DioExceptionType.unknown: 'Unknown network error',
        };

        for (final entry in dioExceptions.entries) {
          final dioError = DioException(
              requestOptions: RequestOptions(path: '/test'), type: entry.key);
          when(() => mockDio.get(any())).thenThrow(dioError);

          // Act & Assert
          await expectLater(
            () => apiCallHandler.handleApiCall<String>(
              call: () => mockDio.get('/test').then((res) => res.data!),
              exception: (message) => AppException(message), // Use AppException
              operationName: 'Test Operation',
            ),
            throwsA(isA<AppException>().having(
                (e) => e.message, 'message', entry.value)), //Check message
          );
          reset(mockDio); // Reset mockDio before next iteration
        }
      });

      test(
          'should throw exception with default message for badResponse with no response',
          () async {
        // Arrange

        final dioError = DioException(
            requestOptions: RequestOptions(path: '/test'),
            type: DioExceptionType.badResponse);
        when(() => mockDio.get(any())).thenThrow(dioError);

        // Act & Assert
        await expectLater(
            () => apiCallHandler.handleApiCall<String>(
                  call: () => mockDio.get('/test').then((res) => res.data!),
                  exception: (message) =>
                      AppException(message), // Use AppException
                  operationName: 'Test Operation',
                ),
            throwsA(isA<AppException>().having((e) => e.message, 'message',
                'Invalid server response')) //Check message
            );
      });

      test(
          'should throw exception with status code for badResponse with response',
          () async {
        // Arrange

        final dioError = DioException(
            requestOptions: RequestOptions(path: '/test'),
            type: DioExceptionType.badResponse,
            response: Response(
                requestOptions: RequestOptions(path: '/test'),
                statusCode: 400));
        when(() => mockDio.get(any())).thenThrow(dioError);

        // Act & Assert
        await expectLater(
            () => apiCallHandler.handleApiCall<String>(
                  call: () => mockDio.get('/test').then((res) => res.data!),
                  exception: (message) =>
                      AppException(message), // Use AppException
                  operationName: 'Test Operation',
                ),
            throwsA(isA<AppException>().having((e) => e.message, 'message',
                'Invalid server response (Status code: 400)')) //Check message
            );
      });

      test('should throw exception with detail message from response data',
          () async {
        // Arrange
        final dioError = DioException(
          requestOptions: RequestOptions(path: '/test'),
          type: DioExceptionType.badResponse, // You can use any type here
          response: Response(
            requestOptions: RequestOptions(path: '/test'),
            statusCode: 400, // Example status code
            data: {
              'detail': 'Detailed error message from server'
            }, // Include the detail
          ),
        );
        when(() => mockDio.get(any())).thenThrow(dioError);

        // Act & Assert
        await expectLater(
          () => apiCallHandler.handleApiCall<String>(
            call: () => mockDio.get('/test').then((res) => res.data!),
            exception: (message) => AppException(message),
            operationName: 'Test Operation',
          ),
          throwsA(isA<AppException>().having((e) => e.message, 'message',
              'Detailed error message from server')),
        );
      });
    });

    group('validateResponse', () {
      test('should return response on successful status code', () {
        // Arrange
        final response =
            Response(requestOptions: RequestOptions(path: ''), statusCode: 200);

        // Act
        final result = apiCallHandler.validateResponse(response);

        // Assert
        expect(result, response);
      });

      test('should throw AppException on unsuccessful status code', () {
        // Arrange
        final response =
            Response(requestOptions: RequestOptions(path: ''), statusCode: 400);

        // Act & Assert
        expect(
          () => apiCallHandler.validateResponse(response),
          throwsA(isA<AppException>().having((e) => e.message, 'message',
              'Invalid response (400)')), // Check for AppException and message
        );
      });
    });
  });
}

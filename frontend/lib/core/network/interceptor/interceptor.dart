// import 'package:dio/dio.dart';
// import 'package:frontend/features/auth/functionality/repository/auth_repository.dart';
// import 'package:frontend/features/auth/functionality/services/secure_storage_service.dart';

// class AuthInterceptor extends InterceptorsWrapper {
//   final SecureStorageService _secureStorage;
//   final AuthRepository _authRepository;
//   final Dio _dio;

//   AuthInterceptor(this._secureStorage, this._authRepository, this._dio);

//   @override
//   void onRequest(RequestOptions options, RequestInterceptorHandler handler) async {
//     final tokens = await _secureStorage.getTokens();
//     final accessToken = tokens['accessToken'];

//     if (accessToken != null) {
//       options.headers['Authorization'] = 'Bearer $accessToken';
//     }
//     return handler.next(options);
//   }

//   @override
//   void onError(DioException err, ErrorInterceptorHandler handler) async {
//     if (err.response?.statusCode == 401) {
//       await _authRepository.refreshToken();
//       final tokens = await _secureStorage.getTokens();
//       final newAccessToken = tokens['accessToken'];

//       if (newAccessToken != null) {
//         err.requestOptions.headers['Authorization'] = 'Bearer $newAccessToken';
//         final retryResponse = await _dio.request(
//           err.requestOptions.path,
//           options: Options(
//             method: err.requestOptions.method,
//             headers: err.requestOptions.headers,
//           ),
//           data: err.requestOptions.data,
//         );
//         return handler.resolve(retryResponse);
//       }
//     }
//     return handler.next(err);
//   }
// }

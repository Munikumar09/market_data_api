import 'package:dio/dio.dart';
import 'package:frontend/core/constants/app_urls.dart';
import 'package:logging/logging.dart';

void main() async {
  // Configure logging
  Logger.root.level = Level.ALL;
  Logger.root.onRecord.listen((record) {
    print('${record.level.name}: ${record.time}: ${record.message}');
  });

  final log = Logger('MainLogger');

  try {
    final dio = Dio(BaseOptions(
      baseUrl: AppUrls.baseUrl,
      connectTimeout: Duration(milliseconds: 5000),
      receiveTimeout: Duration(milliseconds: 5000),
      headers: {
        'Content-Type': 'application/json',
      },
    ));
    final response = await dio.post('/authentication/signup', data: {
      "username": "munikumar",
      "email": "naga70853@gmail.com",
      "password": "Muni@2135",
      "confirm_password": "Muni@213",
      "date_of_birth": "12/06/2003",
      "phone_number": "6281091653",
      "gender": "male",
    });
    log.info(response.data.toString());
  } on DioException catch (e) {
    log.severe('Error: ${e.response?.data}');
  }
}

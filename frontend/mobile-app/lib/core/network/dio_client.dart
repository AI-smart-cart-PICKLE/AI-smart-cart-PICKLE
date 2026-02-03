import 'package:dio/dio.dart';
import '../storage/token_storage.dart';

class DioClient {
  final Dio _dio;
  final TokenStorage _tokenStorage = TokenStorage();

  DioClient({String? baseUrl})
      : _dio = Dio(
          BaseOptions(
            baseUrl: baseUrl ?? 'http://10.0.2.2:8000', 
            connectTimeout: const Duration(seconds: 10),
            receiveTimeout: const Duration(seconds: 10),
            headers: {'Content-Type': 'application/json'},
          ),
        ) {
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final token = await _tokenStorage.getToken();
        if (token != null && token.isNotEmpty) {
          options.headers['Authorization'] = 'Bearer $token';
        } else {
          options.headers.remove('Authorization');
        }
        return handler.next(options);
      },
      onError: (e, handler) async {
        // 401 Unauthorized 에러 발생 시 (토큰 만료 또는 유효하지 않음)
        if (e.response?.statusCode == 401) {
          await _tokenStorage.deleteToken();
          _dio.options.headers.remove('Authorization');
        }
        return handler.next(e);
      },
    ));
    
    _dio.interceptors.add(LogInterceptor(
      requestHeader: true,
      requestBody: true,
      responseBody: true,
      error: true,
    ));
  }

  Dio get dio => _dio;

    // setAccessToken과 clearAccessToken은 이제 인터셉터가 자동으로 처리하므로 

    // 내부 저장소의 값만 관리하면 됩니다.

    Future<void> setAccessToken(String token) async {

      await _tokenStorage.saveToken(token);

    }

  

    Future<void> clearAccessToken() async {

      await _tokenStorage.deleteToken();

    }

  }

  
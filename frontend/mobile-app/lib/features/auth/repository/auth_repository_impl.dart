import 'package:dio/dio.dart';
import '../../../domain/models/user.dart';
import '../../../../core/network/dio_client.dart';
import 'auth_repository.dart';

class AuthRepositoryImpl implements AuthRepository {
  final DioClient _dioClient;

  AuthRepositoryImpl(this._dioClient);

  @override
  Future<User> login({required String email, required String password}) async {
    try {
      // ★ 중요 1: FastAPI 로그인은 'application/x-www-form-urlencoded' 타입이어야 함
      // ★ 중요 2: 필드명은 'email'이 아니라 'username'이어야 함 (FastAPI 표준)
      final response = await _dioClient.dio.post(
        '/api/auth/login', // URL 경로 수정 (/api 추가, 보통 login 대신 token 엔드포인트 사용)
        data: {
          'username': email, // email 값을 username 필드에 넣어서 보냄
          'password': password,
        },
        options: Options(
          contentType: Headers.formUrlEncodedContentType, // 폼 데이터 형식 지정
        ),
      );

      final accessToken = response.data['access_token'];
      _dioClient.setAccessToken(accessToken);

      // 로그인 성공 후 내 정보 가져오기
      return await getUserMe();
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('이메일 또는 비밀번호가 틀렸습니다.');
      }
      throw Exception('로그인 실패: ${e.message}');
    }
  }

  @override
  Future<User> signup({
    required String email,
    required String password,
    required String nickname,
  }) async {
    try {
      // 회원가입은 보통 JSON으로 보냄 (기존 유지)
      await _dioClient.dio.post(
        '/api/auth/signup', // URL 경로 수정 (/api 추가)
        data: {
          'email': email,
          'password': password,
          'nickname': nickname,
        },
      );
      
      // 회원가입 성공 후 바로 로그인 시도
      return await login(email: email, password: password);
    } catch (e) {
      throw Exception('회원가입 실패: $e');
    }
  }

  @override
  Future<User> getUserMe() async {
    try {
      final response = await _dioClient.dio.get('/api/users/me'); // URL 경로 수정
      
      // User 모델의 fromJson을 사용하여 깔끔하게 변환
      return User.fromJson(response.data);
    } catch (e) {
      throw Exception('사용자 정보 조회 실패: $e');
    }
  }

  @override
  Future<void> logout() async {
    try {
      // 로그아웃은 보통 프론트에서 토큰만 삭제하면 됨 (서버 호출 선택 사항)
      _dioClient.clearAccessToken();
    } catch (e) {
      // 무시
    }
  }
}
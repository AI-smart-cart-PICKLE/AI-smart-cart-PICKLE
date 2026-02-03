import 'package:dio/dio.dart';
import '../../../domain/models/user.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/storage/token_storage.dart';
import 'auth_repository.dart';

class AuthRepositoryImpl implements AuthRepository {
  final DioClient _dioClient;
  final TokenStorage _tokenStorage;

  AuthRepositoryImpl(this._dioClient, this._tokenStorage);

  @override
  Future<User> login({required String email, required String password}) async {
    try {
      // 백엔드가 JSON 형식을 기대함 (422 에러 해결)
      final response = await _dioClient.dio.post(
        '/auth/login',
        data: {
          'email': email, 
          'password': password,
        },
        // Options 제거 -> 기본값이 JSON
      );

      final accessToken = response.data['access_token'];
      // DioClient를 통해 토큰을 저장 (내부에서 TokenStorage 사용)
      await _dioClient.setAccessToken(accessToken);

      // 로그인 성공 후 내 정보 가져오기 (이제 인터셉터가 최신 토큰을 사용함)
      return await getUserMe();
    } on DioException catch (e) {
      if (e.response?.statusCode == 401) {
        throw Exception('이메일 또는 비밀번호가 틀렸습니다.');
      }
      throw Exception('로그인 실패: ${e.message}');
    }
  }

  @override
  Future<void> signup({
    required String email,
    required String password,
    required String nickname,
  }) async {
    try {
      // 회원가입은 보통 JSON으로 보냄 (기존 유지)
      await _dioClient.dio.post(
        '/auth/signup', // URL 경로 수정 (/api 추가)
        data: {
          'email': email,
          'password': password,
          'nickname': nickname,
        },
      );
      
      // 회원가입 성공 후 바로 로그인 시도하던 로직 제거
    } catch (e) {
      throw Exception('회원가입 실패: $e');
    }
  }

  @override
  Future<User> getUserMe() async {
    try {
      final response = await _dioClient.dio.get('/users/me'); // URL 경로 수정
      
      // User 모델의 fromJson을 사용하여 깔끔하게 변환
      return User.fromJson(response.data);
    } catch (e) {
      throw Exception('사용자 정보 조회 실패: $e');
    }
  }

  @override
  Future<void> logout() async {
    try {
      await _dioClient.clearAccessToken();
    } catch (e) {
      // 무시
    }
  }
}
import 'package:dio/dio.dart';
import 'package:google_sign_in/google_sign_in.dart';
import '../../../domain/models/user.dart';
import '../../../../core/network/dio_client.dart';
import '../../../../core/storage/token_storage.dart';
import 'auth_repository.dart';

class AuthRepositoryImpl implements AuthRepository {
  final DioClient _dioClient;
  final TokenStorage _tokenStorage;
  final GoogleSignIn _googleSignIn = GoogleSignIn(
    serverClientId: '874133068405-83s78f96pl44leck3bct15fjp2ho71m2.apps.googleusercontent.com',
    scopes: ['email', 'profile'],
  );

  AuthRepositoryImpl(this._dioClient, this._tokenStorage);

  @override
  Future<User> login({required String email, required String password}) async {
    try {
      // 백엔드가 JSON 형식을 기대함 (422 에러 해결)
      final response = await _dioClient.dio.post(
        'auth/login',
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
        'auth/signup', // URL 경로 수정 (/api 추가)
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
  Future<User> loginWithToken(String token) async {
    try {
      await _dioClient.setAccessToken(token);
      return await getUserMe();
    } catch (e) {
      await _dioClient.clearAccessToken();
      throw Exception('OAuth 로그인 실패: $e');
    }
  }

  @override
  Future<User> loginWithGoogle() async {
    try {
      // 1. 구글 로그인 팝업 띄우기
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      
      if (googleUser == null) {
        throw Exception('구글 로그인이 취소되었습니다.');
      }

      // 2. 인증 코드 받기 (serverAuthCode)
      final String? authCode = googleUser.serverAuthCode;
      
      if (authCode == null) {
        await _googleSignIn.signOut();
        throw Exception('인증 코드를 받아오지 못했습니다.');
      }

      // 3. 백엔드로 code 전송
      final response = await _dioClient.dio.post(
        'auth/google',
        data: {'code': authCode},
      );

      final accessToken = response.data['access_token'];
      await _dioClient.setAccessToken(accessToken);

      return await getUserMe();
    } catch (e) {
      await _googleSignIn.signOut();
      if (e is DioException) {
        throw Exception('서버 인증 실패: ${e.response?.data['detail'] ?? e.message}');
      }
      throw Exception('구글 로그인 실패: $e');
    }
  }

  @override
  Future<User> getUserMe() async {
    try {
      final response = await _dioClient.dio.get('users/me'); // URL 경로 수정
      
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
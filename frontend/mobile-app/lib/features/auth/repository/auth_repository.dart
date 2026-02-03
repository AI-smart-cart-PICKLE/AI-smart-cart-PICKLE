import '../../../domain/models/user.dart';

abstract class AuthRepository {
  Future<User> login({required String email, required String password});
  Future<void> signup({required String email, required String password, required String nickname});
  Future<User> getUserMe();
  Future<void> logout();
}

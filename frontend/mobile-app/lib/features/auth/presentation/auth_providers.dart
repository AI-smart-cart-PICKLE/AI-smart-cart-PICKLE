import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/dio_provider.dart';
import '../../../domain/models/user.dart';
import '../repository/auth_repository.dart';
import '../repository/auth_repository_impl.dart';

// AuthRepository 구현체를 제공하는 Provider
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final dioClient = ref.watch(dioClientProvider);
  return AuthRepositoryImpl(dioClient);
});

// 현재 로그인한 사용자 정보를 관리하는 StateProvider (예시)
final currentUserProvider = StateProvider<User?>((ref) => null);

// 로그인 여부를 확인하는 Provider
final isAuthenticatedProvider = Provider<bool>((ref) {
  return ref.watch(currentUserProvider) != null;
});

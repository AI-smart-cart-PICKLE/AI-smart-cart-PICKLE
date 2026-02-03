import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/storage/token_storage.dart';
import '../../../core/network/dio_provider.dart';
import 'auth_providers.dart';

class SplashScreen extends ConsumerStatefulWidget {
  const SplashScreen({super.key});

  @override
  ConsumerState<SplashScreen> createState() => _SplashScreenState();
}

class _SplashScreenState extends ConsumerState<SplashScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<double> _scale_animation;
  late Animation<double> _check_animation;
  late Animation<double> _fade_animation;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000),
    );

    _scale_animation = Tween<double>(begin: 0.5, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.0, 0.5, curve: Curves.easeOutBack),
      ),
    );

    _check_animation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.4, 0.8, curve: Curves.elasticOut),
      ),
    );

    _fade_animation = Tween<double>(begin: 0.0, end: 1.0).animate(
      CurvedAnimation(
        parent: _controller,
        curve: const Interval(0.6, 1.0, curve: Curves.easeIn),
      ),
    );

    _controller.forward();

    // Check auth status
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    // 최소 2초 대기 (애니메이션 시간 확보)
    await Future.delayed(const Duration(milliseconds: 2000));

    if (!mounted) return;

    try {
      final tokenStorage = ref.read(tokenStorageProvider);
      final token = await tokenStorage.getToken();

      if (token != null) {
        // 토큰이 있으면 Dio에 설정하고 유저 정보 가져오기 시도
        ref.read(dioClientProvider).setAccessToken(token);
        
        try {
          // 유저 정보 조회 성공 시 홈으로 이동
          await ref.read(authRepositoryProvider).getUserMe();
          if (mounted) context.go(AppRoutes.home);
          return;
        } catch (e) {
          // 토큰 만료 또는 에러 시 로그인 화면으로
          // (선택 사항: 토큰 삭제)
          await tokenStorage.deleteToken();
        }
      }
      
      // 토큰이 없거나 유효하지 않으면 로그인 화면으로
      if (mounted) context.go(AppRoutes.login);
      
    } catch (e) {
      if (mounted) context.go(AppRoutes.login);
    }
  }

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      body: Stack(
        children: [
          Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                AnimatedBuilder(
                  animation: _controller,
                  builder: (context, child) {
                    return Transform.scale(
                      scale: _scale_animation.value,
                      child: Stack(
                        alignment: Alignment.center,
                        children: [
                          // Shopping Cart Body (increased size)
                          Icon(
                            Icons.shopping_cart_outlined,
                            size: 120,
                            color: AppColors.brand_primary,
                          ),
                          // Checkmark inside the cart (reduced size and adjusted position)
                          Transform.translate(
                            offset: const Offset(6, -18),
                            child: Transform.scale(
                              scale: _check_animation.value,
                              child: const Icon(
                                Icons.check,
                                size: 36,
                                color: AppColors.brand_primary,
                              ),
                            ),
                          ),
                        ],
                      ),
                    );
                  },
                ),
                const SizedBox(height: 24),
                FadeTransition(
                  opacity: _fade_animation,
                  child: Column(
                    children: [
                      Text(
                        '피클',
                        style: TextStyle(
                          fontSize: 32,
                          fontWeight: FontWeight.w900,
                          color: AppColors.brand_primary,
                          letterSpacing: 2,
                        ),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        '똑똑한 쇼핑의 시작',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.w700,
                          color: AppColors.text_secondary,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          // Subtle Toss-like bottom text
          Positioned(
            bottom: 50,
            left: 0,
            right: 0,
            child: FadeTransition(
              opacity: _fade_animation,
              child: Center(
                child: Text(
                  'Pickle Corp.',
                  style: TextStyle(
                    fontSize: 12,
                    color: AppColors.text_secondary.withOpacity(0.5),
                    fontWeight: FontWeight.w600,
                  ),
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }
}

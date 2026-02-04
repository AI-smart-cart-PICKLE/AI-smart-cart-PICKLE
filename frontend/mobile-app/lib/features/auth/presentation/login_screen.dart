import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/primary_button.dart';
import 'auth_providers.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slide_animation;
  
  final _email_controller = TextEditingController();
  final _password_controller = TextEditingController();
  bool _is_loading = false;

  @override
  void initState() {
    super.initState();
    _controller = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 800),
    );
    _slide_animation = Tween<Offset>(
      begin: const Offset(0, 0.1),
      end: Offset.zero,
    ).animate(CurvedAnimation(
      parent: _controller,
      curve: Curves.easeOutCubic,
    ));
    _controller.forward();
  }

  @override
  void dispose() {
    _controller.dispose();
    _email_controller.dispose();
    _password_controller.dispose();
    super.dispose();
  }

  Future<void> _handle_login() async {
    final email = _email_controller.text.trim();
    final password = _password_controller.text.trim();

    if (email.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('이메일과 비밀번호를 모두 입력해주세요.')),
      );
      return;
    }

    setState(() {
      _is_loading = true;
    });

    try {
      final authRepo = ref.read(authRepositoryProvider);
      await authRepo.login(email: email, password: password);
      
      if (mounted) {
        context.go(AppRoutes.home);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('로그인 실패: ${e.toString().replaceAll("Exception: ", "")}')),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _is_loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        elevation: 0,
      ),
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.symmetric(horizontal: 24.0),
          child: SlideTransition(
            position: _slide_animation,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                const SizedBox(height: 20),
                Text(
                  '반가워요!\n피클로 쇼핑을 시작할까요?',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w900,
                    color: AppColors.text_primary,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 48),
                TextField(
                  controller: _email_controller,
                  style: const TextStyle(color: Colors.black),
                  textInputAction: TextInputAction.next,
                  decoration: InputDecoration(
                    labelText: '이메일',
                    labelStyle: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w700),
                    hintText: 'example@pickle.com',
                    filled: true,
                    fillColor: Colors.grey[100],
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                      borderSide: BorderSide.none,
                    ),
                    floatingLabelBehavior: FloatingLabelBehavior.never,
                  ),
                ),
                const SizedBox(height: 16),
                TextField(
                  controller: _password_controller,
                  obscureText: true,
                  style: const TextStyle(color: Colors.black),
                  textInputAction: TextInputAction.done,
                  onSubmitted: (_) => _handle_login(),
                  decoration: InputDecoration(
                    labelText: '비밀번호',
                    labelStyle: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w700),
                    hintText: '비밀번호를 입력해주세요',
                    filled: true,
                    fillColor: Colors.grey[100],
                    border: OutlineInputBorder(
                      borderRadius: BorderRadius.circular(16),
                      borderSide: BorderSide.none,
                    ),
                    floatingLabelBehavior: FloatingLabelBehavior.never,
                  ),
                ),
                const SizedBox(height: 32),
                PrimaryButton(
                  label: _is_loading ? '로그인 중...' : '로그인',
                  on_pressed: _is_loading ? () {} : _handle_login,
                ),
                const SizedBox(height: 24),
                Row(
                  children: [
                    const Expanded(child: Divider()),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Text(
                        '또는',
                        style: TextStyle(
                          color: AppColors.text_secondary.withOpacity(0.5),
                          fontSize: 14,
                          fontWeight: FontWeight.w600,
                        ),
                      ),
                    ),
                    const Expanded(child: Divider()),
                  ],
                ),
                const SizedBox(height: 24),
                _SocialLoginButton(
                  label: '카카오로 시작하기',
                  onPressed: () {
                    // TODO: 카카오 로그인 연동
                  },
                  backgroundColor: const Color(0xFFFEE500),
                  textColor: Colors.black.withOpacity(0.85),
                  icon: const Icon(Icons.chat_bubble, color: Colors.black, size: 18),
                ),
                const SizedBox(height: 12),
                _SocialLoginButton(
                  label: 'Google로 시작하기',
                  onPressed: () {
                    // TODO: 구글 로그인 연동
                  },
                  backgroundColor: Colors.white,
                  textColor: Colors.black.withOpacity(0.54),
                  icon: Image.network(
                    'https://www.gstatic.com/images/branding/product/2x/googleg_48dp.png',
                    width: 20,
                    height: 20,
                    errorBuilder: (context, error, stackTrace) => const Text(
                      'G',
                      style: TextStyle(
                        fontSize: 20,
                        fontWeight: FontWeight.bold,
                        color: Colors.blue,
                      ),
                    ),
                  ),
                  border: Border.all(color: Colors.grey.shade300),
                ),
                const SizedBox(height: 24),
                Center(
                  child: TextButton(
                    onPressed: () {
                      _email_controller.clear();
                      _password_controller.clear();
                      context.push(AppRoutes.signup);
                    },
                    child: Text(
                      '아직 회원이 아니신가요? 회원가입',
                      style: TextStyle(
                        color: AppColors.text_secondary,
                        fontWeight: FontWeight.w700,
                        fontSize: 14,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 24),
                Center(
                  child: Text(
                    '로그인에 문제가 있나요?',
                    style: TextStyle(
                      color: AppColors.text_secondary.withOpacity(0.6),
                      fontWeight: FontWeight.w600,
                      fontSize: 12,
                      decoration: TextDecoration.underline,
                    ),
                  ),
                ),
                const SizedBox(height: 20),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

class _SocialLoginButton extends StatelessWidget {
  final String label;
  final VoidCallback onPressed;
  final Color backgroundColor;
  final Color textColor;
  final Widget icon;
  final BoxBorder? border;

  const _SocialLoginButton({
    required this.label,
    required this.onPressed,
    required this.backgroundColor,
    required this.textColor,
    required this.icon,
    this.border,
  });

  @override
  Widget build(BuildContext context) {
    return SizedBox(
      width: double.infinity,
      height: 56,
      child: OutlinedButton(
        onPressed: onPressed,
        style: OutlinedButton.styleFrom(
          backgroundColor: backgroundColor,
          side: border != null && border is Border 
              ? BorderSide(color: (border as Border).top.color) 
              : BorderSide.none,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(16),
          ),
          elevation: 0,
        ),
        child: Stack(
          children: [
            Align(
              alignment: Alignment.centerLeft,
              child: Padding(
                padding: const EdgeInsets.only(left: 8.0),
                child: icon,
              ),
            ),
            Center(
              child: Text(
                label,
                style: TextStyle(
                  color: textColor,
                  fontSize: 16,
                  fontWeight: FontWeight.w600,
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
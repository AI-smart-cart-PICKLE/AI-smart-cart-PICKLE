import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/primary_button.dart';
import 'auth_providers.dart';

class SignupScreen extends ConsumerStatefulWidget {
  const SignupScreen({super.key});

  @override
  ConsumerState<SignupScreen> createState() => _SignupScreenState();
}

class _SignupScreenState extends ConsumerState<SignupScreen> with SingleTickerProviderStateMixin {
  late AnimationController _controller;
  late Animation<Offset> _slide_animation;

  final _nickname_controller = TextEditingController();
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
    _nickname_controller.dispose();
    _email_controller.dispose();
    _password_controller.dispose();
    super.dispose();
  }

  Future<void> _handle_signup() async {
    final nickname = _nickname_controller.text.trim();
    final email = _email_controller.text.trim();
    final password = _password_controller.text.trim();

    if (nickname.isEmpty || email.isEmpty || password.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('모든 필드를 입력해주세요.')),
      );
      return;
    }

    setState(() {
      _is_loading = true;
    });

    try {
      final authRepo = ref.read(authRepositoryProvider);
      await authRepo.signup(
        email: email,
        password: password,
        nickname: nickname,
      );
      
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('회원가입이 완료되었습니다! 로그인해주세요.'))
        );
        // 회원가입 성공 시 로그인 화면으로 이동
        context.go(AppRoutes.login);
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('회원가입 실패: ${e.toString().replaceAll("Exception: ", "")}')),
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
        leading: IconButton(
          onPressed: () {
            _nickname_controller.clear();
            _email_controller.clear();
            _password_controller.clear();
            context.pop();
          },
          icon: Icon(Icons.arrow_back, color: AppColors.text_primary),
        ),
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
                  '환영합니다!\n계정을 만들어볼까요?',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.w900,
                    color: AppColors.text_primary,
                    height: 1.4,
                  ),
                ),
                const SizedBox(height: 48),
                TextField(
                  controller: _nickname_controller,
                  style: const TextStyle(color: Colors.black),
                  textInputAction: TextInputAction.next,
                  decoration: InputDecoration(
                    labelText: '닉네임',
                    labelStyle: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w700),
                    hintText: '사용하실 닉네임을 입력해주세요',
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
                  onSubmitted: (_) => _handle_signup(),
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
                  label: _is_loading ? '가입 중...' : '회원가입 완료',
                  on_pressed: _is_loading ? () {} : () async {
                    await _handle_signup();
                    _nickname_controller.clear();
                    _email_controller.clear();
                    _password_controller.clear();
                  },
                ),
                const SizedBox(height: 16),
                Center(
                  child: TextButton(
                    onPressed: () {
                      _nickname_controller.clear();
                      _email_controller.clear();
                      _password_controller.clear();
                      context.pop();
                    },
                    child: Text(
                      '이미 계정이 있으신가요? 로그인',
                      style: TextStyle(
                        color: AppColors.text_secondary,
                        fontWeight: FontWeight.w700,
                        fontSize: 14,
                      ),
                    ),
                  ),
                ),
                const SizedBox(height: 40),
              ],
            ),
          ),
        ),
      ),
    );
  }
}

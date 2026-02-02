import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../shared/widgets/primary_button.dart';
import '../../../shared/widgets/section_card.dart';
import '../../../shared/widgets/app_text_field.dart';
import '../repository/account_repository.dart';
import 'account_providers.dart';

class ChangePasswordScreen extends ConsumerStatefulWidget {
  const ChangePasswordScreen({super.key});

  @override
  ConsumerState<ChangePasswordScreen> createState() => _ChangePasswordScreenState();
}

class _ChangePasswordScreenState extends ConsumerState<ChangePasswordScreen> {
  final TextEditingController current_password_controller = TextEditingController();
  final TextEditingController new_password_controller = TextEditingController();
  final TextEditingController confirm_password_controller = TextEditingController();

  bool is_current_hidden = true;
  bool is_new_hidden = true;
  bool is_confirm_hidden = true;
  bool is_saving = false;

  @override
  void dispose() {
    current_password_controller.dispose();
    new_password_controller.dispose();
    confirm_password_controller.dispose();
    super.dispose();
  }

  bool get has_min_length => new_password_controller.text.length >= 8;
  bool get has_number => RegExp(r'\d').hasMatch(new_password_controller.text);
  bool get has_special => RegExp(r'[!@#$%^&*(),.?":{}|<>]').hasMatch(new_password_controller.text);
  bool get has_upper => RegExp(r'[A-Z]').hasMatch(new_password_controller.text);

  bool get is_confirm_match => new_password_controller.text == confirm_password_controller.text && confirm_password_controller.text.isNotEmpty;

  double get strength {
    int score = 0;
    if (has_min_length) score++;
    if (has_number) score++;
    if (has_special) score++;
    if (has_upper) score++;
    return score / 4;
  }

  String get strength_label {
    final double s = strength;
    if (s >= 0.75) return '좋음';
    if (s >= 0.5) return '보통';
    if (s > 0) return '약함';
    return '없음';
  }

  Future<void> _save() async {
    final String current_password = current_password_controller.text;
    final String new_password = new_password_controller.text;

    if (!has_min_length || !has_number || !has_special || !is_confirm_match) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(content: Text('비밀번호 조건을 확인해주세요.')));
      return;
    }

    setState(() => is_saving = true);
    try {
      final AccountRepository repo = ref.read(account_repository_provider);
      await repo.change_password(current_password: current_password, new_password: new_password);
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('변경 실패: $e')));
    } finally {
      if (mounted) setState(() => is_saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final double max_w = Responsive.max_width(context);
    final theme_mode = ref.watch(theme_mode_provider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('비밀번호 변경', style: TextStyle(fontWeight: FontWeight.w900)),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: max_w),
            child: SingleChildScrollView(
              padding: Responsive.page_padding(context),
              child: Column(
                children: <Widget>[
                  SectionCard(
                    child: Column(
                      children: <Widget>[
                        Container(
                          width: 80,
                          height: 80,
                          decoration: BoxDecoration(
                            color: AppColors.brand_primary.withOpacity(0.10),
                            borderRadius: BorderRadius.circular(999),
                          ),
                          child: const Center(child: Icon(Icons.security, color: AppColors.brand_primary, size: 34)),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          '숫자와 특수문자를 포함한 강력한 비밀번호를 설정해 보안을 강화하세요.',
                          textAlign: TextAlign.center,
                          style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800),
                        ),
                        const SizedBox(height: 14),

                        AppTextField(
                          controller: current_password_controller,
                          label: '현재 비밀번호',
                          hint: '현재 비밀번호를 입력하세요',
                          obscure_text: is_current_hidden,
                          suffix_icon: IconButton(
                            onPressed: () => setState(() => is_current_hidden = !is_current_hidden),
                            icon: Icon(is_current_hidden ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                          ),
                        ),
                        const SizedBox(height: 14),

                        AppTextField(
                          controller: new_password_controller,
                          label: '새 비밀번호',
                          hint: '새 비밀번호를 입력하세요',
                          obscure_text: is_new_hidden,
                          suffix_icon: IconButton(
                            onPressed: () => setState(() => is_new_hidden = !is_new_hidden),
                            icon: Icon(is_new_hidden ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                          ),
                        ),
                        const SizedBox(height: 10),

                        Row(
                          children: <Widget>[
                            Text('비밀번호 강도', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900)),
                            const Spacer(),
                            Text(strength_label, style: const TextStyle(fontWeight: FontWeight.w900, color: AppColors.brand_primary)),
                          ],
                        ),
                        const SizedBox(height: 8),
                        ClipRRect(
                          borderRadius: BorderRadius.circular(999),
                          child: LinearProgressIndicator(
                            value: strength,
                            minHeight: 10,
                            backgroundColor: AppColors.border.withOpacity(0.35),
                          ),
                        ),
                        const SizedBox(height: 12),

                        _RuleRow(label: '최소 8자 이상', is_ok: has_min_length),
                        _RuleRow(label: '숫자 포함', is_ok: has_number),
                        _RuleRow(label: '특수문자 포함', is_ok: has_special),
                        _RuleRow(label: '대문자 포함(권장)', is_ok: has_upper),

                        const SizedBox(height: 14),
                        AppTextField(
                          controller: confirm_password_controller,
                          label: '새 비밀번호 확인',
                          hint: '새 비밀번호를 다시 입력하세요',
                          obscure_text: is_confirm_hidden,
                          suffix_icon: IconButton(
                            onPressed: () => setState(() => is_confirm_hidden = !is_confirm_hidden),
                            icon: Icon(is_confirm_hidden ? Icons.visibility_outlined : Icons.visibility_off_outlined),
                          ),
                          helper_text: is_confirm_match ? '일치합니다' : '비밀번호가 일치해야 합니다',
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),
                  PrimaryButton(
                    label: is_saving ? '변경 중...' : '비밀번호 변경',
                    on_pressed: is_saving ? null : _save,
                    leading: const Icon(Icons.arrow_forward),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }
}

class _RuleRow extends StatelessWidget {
  final String label;
  final bool is_ok;

  const _RuleRow({required this.label, required this.is_ok});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6),
      child: Row(
        children: <Widget>[
          Icon(is_ok ? Icons.check_circle : Icons.radio_button_unchecked, size: 18, color: is_ok ? AppColors.brand_primary : AppColors.text_secondary),
          const SizedBox(width: 10),
          Expanded(child: Text(label, style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800))),
        ],
      ),
    );
  }
}

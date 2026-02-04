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

class ChangeNicknameScreen extends ConsumerStatefulWidget {
  const ChangeNicknameScreen({super.key});

  @override
  ConsumerState<ChangeNicknameScreen> createState() => _ChangeNicknameScreenState();
}

class _ChangeNicknameScreenState extends ConsumerState<ChangeNicknameScreen> {
  final TextEditingController nickname_controller = TextEditingController();
  bool is_saving = false;

  @override
  void dispose() {
    nickname_controller.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    final String new_nickname = nickname_controller.text.trim();
    if (new_nickname.isEmpty) return;

    setState(() => is_saving = true);

    try {
      final AccountRepository repo = ref.read(account_repository_provider);
      await repo.update_nickname(new_nickname: new_nickname);
      ref.invalidate(my_profile_provider); // 프로필 갱신
      if (mounted) Navigator.of(context).pop();
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('저장 실패: $e')));
    } finally {
      if (mounted) setState(() => is_saving = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final double max_w = Responsive.max_width(context);
    final profile_async = ref.watch(my_profile_provider);
    final theme_mode = ref.watch(theme_mode_provider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('닉네임 변경', style: TextStyle(fontWeight: FontWeight.w900)),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: max_w),
            child: Padding(
              padding: Responsive.page_padding(context),
              child: profile_async.when(
                loading: () => const Center(child: CircularProgressIndicator()),
                error: (e, _) => Text('프로필을 불러오지 못했어요.\n$e'),
                data: (profile) {
                  return Column(
                    children: <Widget>[
                      SectionCard(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: <Widget>[
                            Text('현재 닉네임', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900)),
                            const SizedBox(height: 8),
                            Container(
                              width: double.infinity,
                              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                              decoration: BoxDecoration(
                                color: const Color(0xFFF3F4F6),
                                borderRadius: BorderRadius.circular(14),
                                border: Border.all(color: AppColors.border),
                              ),
                              child: Text(profile.nickname, style: const TextStyle(fontWeight: FontWeight.w900)),
                            ),
                            const SizedBox(height: 14),
                            AppTextField(
                              controller: nickname_controller,
                              label: '새 닉네임',
                              hint: '새 닉네임을 입력하세요',
                              suffix_icon: IconButton(
                                onPressed: () => nickname_controller.clear(),
                                icon: const Icon(Icons.close),
                              ),
                              helper_text: '2~20자 사용 가능 (문자/숫자/이모지 가능)',
                            ),
                          ],
                        ),
                      ),
                      const Spacer(),
                      PrimaryButton(
                        label: is_saving ? '저장 중...' : '변경 저장',
                        on_pressed: is_saving ? null : _save,
                      ),
                    ],
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/section_card.dart';
import '../../../shared/widgets/primary_button.dart';

class KakaoPaySettingsScreen extends ConsumerWidget {
  const KakaoPaySettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final double max_w = Responsive.max_width(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('카카오페이 설정', style: TextStyle(fontWeight: FontWeight.w900)),
        leading: IconButton(onPressed: () => context.pop(), icon: const Icon(Icons.arrow_back)),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: max_w),
            child: Padding(
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
                            color: const Color(0xFFFFE600),
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: const Icon(Icons.chat_bubble_outline, size: 40, color: Colors.black),
                        ),
                        const SizedBox(height: 16),
                        const Text(
                          '카카오페이',
                          style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          '현재 연결되어 있습니다',
                          style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w700),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),
                  SectionCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        const Text('결제 정보', style: TextStyle(fontWeight: FontWeight.w900)),
                        const SizedBox(height: 12),
                        _InfoRow(label: '연결 계정', value: 'pick***@kakao.com'),
                        const Divider(height: 24),
                        _InfoRow(label: '등록일', value: '2026.01.15'),
                        const Divider(height: 24),
                        _InfoRow(label: '자동 결제', value: '사용 중'),
                      ],
                    ),
                  ),
                  const Spacer(),
                  PrimaryButton(
                    label: '연결 해제하기',
                    on_pressed: () {
                      // Implementation for disconnect
                    },
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    '연결을 해제하면 스마트카트 자동 결제를 이용할 수 없습니다.',
                    style: TextStyle(color: Colors.grey, fontSize: 12),
                    textAlign: TextAlign.center,
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

class _InfoRow extends StatelessWidget {
  final String label;
  final String value;

  const _InfoRow({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceBetween,
      children: <Widget>[
        Text(label, style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w700)),
        Text(value, style: const TextStyle(fontWeight: FontWeight.w900)),
      ],
    );
  }
}

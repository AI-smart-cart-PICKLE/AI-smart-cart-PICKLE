import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/section_card.dart';
import '../../../shared/widgets/primary_button.dart';

// 간단한 카카오페이 연결 상태 관리 프로바이더
final kakao_pay_connected_provider = StateProvider<bool>((ref) => true);

class KakaoPaySettingsScreen extends ConsumerWidget {
  const KakaoPaySettingsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final double max_w = Responsive.max_width(context);
    final is_connected = ref.watch(kakao_pay_connected_provider);

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
                          '카카오페이 QR 결제',
                          style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900),
                        ),
                        const SizedBox(height: 8),
                        Text(
                          is_connected ? '현재 연결되어 있습니다' : '연결이 필요합니다',
                          style: TextStyle(
                            color: is_connected ? AppColors.brand_primary : AppColors.text_secondary,
                            fontWeight: FontWeight.w700,
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),
                  SectionCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        const Text('이용 안내', style: TextStyle(fontWeight: FontWeight.w900)),
                        const SizedBox(height: 12),
                        const _GuideRow(
                          icon: Icons.qr_code_scanner,
                          text: '결제 시 카카오페이 QR 결제창으로 연결됩니다.',
                        ),
                        const Divider(height: 24),
                        const _GuideRow(
                          icon: Icons.security,
                          text: '별도의 카드 등록 없이 안전하게 결제할 수 있습니다.',
                        ),
                        const Divider(height: 24),
                        const _GuideRow(
                          icon: Icons.account_balance_wallet_outlined,
                          text: '카카오페이머니와 연결된 카드로 즉시 결제됩니다.',
                        ),
                      ],
                    ),
                  ),
                  const Spacer(),
                  PrimaryButton(
                    label: is_connected ? '연결 해제하기' : '카카오페이 연결하기',
                    background_color: is_connected ? Colors.grey[200] : const Color(0xFFFFE600),
                    text_color: Colors.black,
                    on_pressed: () {
                      ref.read(kakao_pay_connected_provider.notifier).state = !is_connected;
                      ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(
                          content: Text(is_connected ? '카카오페이 연결이 해제되었습니다.' : '카카오페이가 연결되었습니다.'),
                        ),
                      );
                    },
                  ),
                  const SizedBox(height: 12),
                  const Text(
                    '카카오페이를 연결하면 스마트카트에서 빠르고 간편하게 결제할 수 있습니다.',
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

class _GuideRow extends StatelessWidget {
  final IconData icon;
  final String text;

  const _GuideRow({required this.icon, required this.text});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: <Widget>[
        Icon(icon, size: 20, color: AppColors.brand_primary),
        const SizedBox(width: 12),
        Expanded(
          child: Text(
            text,
            style: const TextStyle(fontWeight: FontWeight.w700, fontSize: 13),
          ),
        ),
      ],
    );
  }
}

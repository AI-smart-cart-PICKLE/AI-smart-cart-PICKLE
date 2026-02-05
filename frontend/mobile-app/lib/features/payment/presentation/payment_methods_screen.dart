import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_routes.dart';
import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../shared/widgets/section_card.dart';
import 'payment_providers.dart';

class PaymentMethodsScreen extends ConsumerWidget {
  const PaymentMethodsScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final double max_w = Responsive.max_width(context);

    final cards_async = ref.watch(payment_cards_provider);
    final wallets_async = ref.watch(payment_wallets_provider);
    final theme_mode = ref.watch(theme_mode_provider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('결제 수단', style: TextStyle(fontWeight: FontWeight.w900)),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: max_w),
            child: SingleChildScrollView(
              padding: Responsive.page_padding(context),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  SectionCard(
                    child: Row(
                      children: <Widget>[
                        const Icon(Icons.verified_user_outlined, color: AppColors.brand_primary),
                        const SizedBox(width: 10),
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: <Widget>[
                              const Text('안전한 결제 환경', style: TextStyle(fontWeight: FontWeight.w900)),
                              const SizedBox(height: 4),
                              Text(
                                '결제 정보는 암호화되어 처리되며 전체 카드번호를 저장하지 않습니다.',
                                style: TextStyle(color: AppColors.text_secondary, fontSize: 12, fontWeight: FontWeight.w800),
                              ),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),

                  Text('카드', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900)),
                  const SizedBox(height: 8),
                  cards_async.when(
                    loading: () => const Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator()),
                    error: (e, _) => Text('카드를 불러오지 못했어요.\n$e'),
                    data: (cards) {
                      return Column(
                        children: cards.map((c) {
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 10),
                            child: SectionCard(
                              child: Column(
                                children: <Widget>[
                                  Row(
                                    children: <Widget>[
                                      Container(
                                        width: 44,
                                        height: 32,
                                        decoration: BoxDecoration(
                                          color: AppColors.border.withOpacity(0.35),
                                          borderRadius: BorderRadius.circular(12),
                                        ),
                                        child: Center(child: Text(c.brand_label, style: const TextStyle(fontWeight: FontWeight.w900))),
                                      ),
                                      const SizedBox(width: 12),
                                      Expanded(
                                        child: Column(
                                          crossAxisAlignment: CrossAxisAlignment.start,
                                          children: <Widget>[
                                            Row(
                                              children: <Widget>[
                                                Expanded(
                                                  child: Text(
                                                    '${c.brand_label} ···· ${c.last4}',
                                                    style: const TextStyle(fontWeight: FontWeight.w900),
                                                  ),
                                                ),
                                                if (c.is_primary)
                                                  Container(
                                                    padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                                    decoration: BoxDecoration(
                                                      color: AppColors.brand_primary.withOpacity(0.12),
                                                      borderRadius: BorderRadius.circular(999),
                                                    ),
                                                    child: const Text('기본', style: TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w900, fontSize: 12)),
                                                  ),
                                              ],
                                            ),
                                            const SizedBox(height: 4),
                                            Text('만료 ${c.expires_mm_yy}', style: TextStyle(color: AppColors.text_secondary, fontSize: 12, fontWeight: FontWeight.w800)),
                                          ],
                                        ),
                                      ),
                                    ],
                                  ),
                                  const SizedBox(height: 10),
                                  Row(
                                    mainAxisAlignment: MainAxisAlignment.end,
                                    children: <Widget>[
                                      TextButton.icon(
                                        onPressed: () {
                                          ScaffoldMessenger.of(context).showSnackBar(
                                            SnackBar(content: Text('${c.brand_label} 정보를 수정합니다.')),
                                          );
                                        },
                                        icon: const Icon(Icons.edit, size: 18),
                                        label: const Text('수정'),
                                      ),
                                      TextButton.icon(
                                        onPressed: () {
                                          showDialog<void>(
                                            context: context,
                                            builder: (context) => AlertDialog(
                                              title: const Text('카드 삭제'),
                                              content: Text('${c.brand_label} ···· ${c.last4} 카드를 삭제할까요?'),
                                              actions: <Widget>[
                                                TextButton(onPressed: () => Navigator.pop(context), child: const Text('취소')),
                                                TextButton(
                                                  onPressed: () => Navigator.pop(context),
                                                  child: const Text('삭제', style: TextStyle(color: Colors.red)),
                                                ),
                                              ],
                                            ),
                                          );
                                        },
                                        icon: const Icon(Icons.delete_outline, size: 18, color: Colors.red),
                                        label: const Text('삭제'),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            ),
                          );
                        }).toList(),
                      );
                    },
                  ),

                  const SizedBox(height: 10),
                  Text('전자지갑', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900)),
                  const SizedBox(height: 8),
                  wallets_async.when(
                    loading: () => const Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator()),
                    error: (e, _) => Text('지갑을 불러오지 못했어요.\n$e'),
                    data: (wallets) {
                      return Column(
                        children: wallets.map((w) {
                          return Padding(
                            padding: const EdgeInsets.only(bottom: 10),
                            child: SectionCard(
                              child: Row(
                                children: <Widget>[
                                  Container(
                                    width: 44,
                                    height: 44,
                                    decoration: BoxDecoration(
                                      color: AppColors.border.withOpacity(0.35),
                                      borderRadius: BorderRadius.circular(14),
                                    ),
                                    child: Icon(
                                      w.wallet_key == 'kakao_pay' ? Icons.chat_bubble_outline : Icons.account_balance_wallet_outlined,
                                      color: AppColors.brand_primary,
                                    ),
                                  ),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: <Widget>[
                                        Text(w.label, style: const TextStyle(fontWeight: FontWeight.w900)),
                                        const SizedBox(height: 4),
                                        Text(w.status_label, style: TextStyle(color: AppColors.text_secondary, fontSize: 12, fontWeight: FontWeight.w800)),
                                      ],
                                    ),
                                  ),
                                  if (w.wallet_key == 'kakao_pay') ...<Widget>[
                                    TextButton(
                                      onPressed: () {
                                        showDialog<void>(
                                          context: context,
                                          builder: (context) => AlertDialog(
                                            title: const Text('연결 해제'),
                                            content: const Text('카카오페이 연결을 해제하시겠습니까?'),
                                            actions: <Widget>[
                                              TextButton(onPressed: () => Navigator.pop(context), child: const Text('취소')),
                                              TextButton(
                                                onPressed: () => Navigator.pop(context),
                                                child: const Text('해제', style: TextStyle(color: Colors.red)),
                                              ),
                                            ],
                                          ),
                                        );
                                      },
                                      child: const Text('연결 해제'),
                                    ),
                                  ] else ...<Widget>[
                                    TextButton(
                                      onPressed: () {
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          const SnackBar(content: Text('지갑 내역 기능이 준비 중입니다.')),
                                        );
                                      },
                                      child: const Text('내역'),
                                    ),
                                    TextButton(
                                      onPressed: () {
                                        ScaffoldMessenger.of(context).showSnackBar(
                                          const SnackBar(content: Text('충전 기능이 준비 중입니다.')),
                                        );
                                      },
                                      child: const Text('충전'),
                                    ),
                                  ],
                                ],
                              ),
                            ),
                          );
                        }).toList(),
                      );
                    },
                  ),

                  const SizedBox(height: 80),
                ],
              ),
            ),
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 12),
          child: ElevatedButton.icon(
            onPressed: () => context.push(AppRoutes.add_new_card),
            icon: const Icon(Icons.add),
            label: const Text('새 결제 수단 추가', style: TextStyle(fontWeight: FontWeight.w900)),
            style: ElevatedButton.styleFrom(
              backgroundColor: AppColors.brand_primary,
              foregroundColor: Colors.white,
              padding: const EdgeInsets.symmetric(vertical: 16),
              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            ),
          ),
        ),
      ),
    );
  }
}
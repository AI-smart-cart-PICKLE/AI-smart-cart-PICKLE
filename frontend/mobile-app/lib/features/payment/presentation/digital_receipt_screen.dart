import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_routes.dart';
import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../shared/widgets/section_card.dart';
import '../../../shared/widgets/primary_button.dart';
import 'payment_providers.dart';

class DigitalReceiptScreen extends ConsumerWidget {
  final String receipt_id;

  const DigitalReceiptScreen({super.key, required this.receipt_id});

  String _money(int v) {
    final String s = v.toString();
    final StringBuffer b = StringBuffer();
    for (int i = 0; i < s.length; i++) {
      final int from_end = s.length - i;
      b.write(s[i]);
      if (from_end > 1 && from_end % 3 == 1) b.write(',');
    }
    return '₩${b.toString()}';
  }

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final double max_w = Responsive.max_width(context);
    final receipt_async = ref.watch(receipt_provider(receipt_id));
    final theme_mode = ref.watch(theme_mode_provider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('영수증', style: TextStyle(fontWeight: FontWeight.w900)),
        actions: <Widget>[
          IconButton(
            onPressed: () {
              showModalBottomSheet<void>(
                context: context,
                builder: (context) => SafeArea(
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      ListTile(
                        leading: const Icon(Icons.picture_as_pdf_outlined),
                        title: const Text('PDF로 저장'),
                        onTap: () => Navigator.pop(context),
                      ),
                      ListTile(
                        leading: const Icon(Icons.print_outlined),
                        title: const Text('인쇄하기'),
                        onTap: () => Navigator.pop(context),
                      ),
                      ListTile(
                        leading: const Icon(Icons.help_outline),
                        title: const Text('결제 관련 문의'),
                        onTap: () => Navigator.pop(context),
                      ),
                    ],
                  ),
                ),
              );
            },
            icon: const Icon(Icons.more_horiz),
          ),
        ],
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: max_w),
            child: SingleChildScrollView(
              padding: Responsive.page_padding(context),
              child: receipt_async.when(
                loading: () => const Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator()),
                error: (e, _) => Text('영수증을 불러오지 못했어요.\n$e'),
                data: (r) {
                  final String date_label = '${r.paid_at.year}.${r.paid_at.month.toString().padLeft(2, '0')}.${r.paid_at.day.toString().padLeft(2, '0')} ' 
                      '${r.paid_at.hour.toString().padLeft(2, '0')}:${r.paid_at.minute.toString().padLeft(2, '0')}';

                  return Column(
                    children: <Widget>[
                      Container(
                        width: 88,
                        height: 88,
                        decoration: BoxDecoration(
                          color: AppColors.brand_primary.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: const Icon(Icons.check, color: AppColors.brand_primary, size: 40),
                      ),
                      const SizedBox(height: 12),
                      const Text('결제가 완료되었습니다', style: TextStyle(fontSize: 20, fontWeight: FontWeight.w900)),
                      const SizedBox(height: 6),
                      Text('참조: #${r.ref_code}', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800)),
                      const SizedBox(height: 14),

                      SectionCard(
                        child: Column(
                          children: <Widget>[
                            Row(
                              children: <Widget>[
                                CircleAvatar(
                                  radius: 16,
                                  backgroundColor: AppColors.brand_primary.withOpacity(0.12),
                                  child: const Text('P', style: TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w900)),
                                ),
                                const SizedBox(width: 10),
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: <Widget>[
                                      Text(r.store_name, style: const TextStyle(fontWeight: FontWeight.w900)),
                                      const SizedBox(height: 2),
                                      Text(date_label, style: TextStyle(color: AppColors.text_secondary, fontSize: 12, fontWeight: FontWeight.w800)),
                                    ],
                                  ),
                                ),
                              ],
                            ),
                            const SizedBox(height: 12),
                            ...r.items.map((it) {
                              return Padding(
                                padding: const EdgeInsets.symmetric(vertical: 8),
                                child: Row(
                                  children: <Widget>[
                                    Container(
                                      width: 22,
                                      height: 22,
                                      decoration: BoxDecoration(
                                        color: AppColors.border.withOpacity(0.35),
                                        borderRadius: BorderRadius.circular(8),
                                      ),
                                      alignment: Alignment.center,
                                      child: Text('${it.qty}', style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 12)),
                                    ),
                                    const SizedBox(width: 10),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: <Widget>[
                                          Text(it.name, style: const TextStyle(fontWeight: FontWeight.w900)),
                                          Text(it.option_label, style: TextStyle(color: AppColors.text_secondary, fontSize: 12, fontWeight: FontWeight.w800)),
                                        ],
                                      ),
                                    ),
                                    Text(_money(it.price), style: const TextStyle(fontWeight: FontWeight.w900)),
                                  ],
                                ),
                              );
                            }),
                            const SizedBox(height: 10),
                            Container(height: 1, color: AppColors.border),
                            const SizedBox(height: 10),
                            _row('소계', _money(r.subtotal)),
                            _row('세금', _money(r.tax)),
                            const SizedBox(height: 10),
                            Row(
                              children: <Widget>[
                                const Expanded(child: Text('결제 금액', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900))),
                                Text(_money(r.total_paid), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900)),
                              ],
                            ),
                            const SizedBox(height: 10),
                            Row(
                              children: <Widget>[
                                Container(
                                  width: 44,
                                  height: 30,
                                  decoration: BoxDecoration(
                                    color: AppColors.border.withOpacity(0.35),
                                    borderRadius: BorderRadius.circular(10),
                                  ),
                                  child: const Icon(Icons.credit_card, size: 18),
                                ),
                                const SizedBox(width: 10),
                                Expanded(child: Text(r.paid_method_label, style: const TextStyle(fontWeight: FontWeight.w900))),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: AppColors.brand_primary.withOpacity(0.12),
                                    borderRadius: BorderRadius.circular(999),
                                  ),
                                  child: const Text('자동 결제', style: TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w900, fontSize: 12)),
                                ),
                              ],
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 14),
                      PrimaryButton(
                        label: '홈으로 돌아가기',
                        on_pressed: () => context.go(AppRoutes.home),
                      ),
                      const SizedBox(height: 10),
                      OutlinedButton.icon(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('영수증 공유 기능이 준비 중입니다.')),
                          );
                        },
                        icon: const Icon(Icons.ios_share),
                        label: const Text('영수증 공유'),
                        style: OutlinedButton.styleFrom(
                          padding: const EdgeInsets.symmetric(vertical: 16),
                          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                        ),
                      ),
                      const SizedBox(height: 10),
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

  Widget _row(String left, String right) {
    return Row(
      children: <Widget>[
        Expanded(child: Text(left, style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900))),
        Text(right, style: const TextStyle(fontWeight: FontWeight.w900)),
      ],
    );
  }
}
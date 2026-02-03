import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_routes.dart';
import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../shared/widgets/section_card.dart';
import 'payment_providers.dart';

class PaymentHistoryScreen extends ConsumerStatefulWidget {
  const PaymentHistoryScreen({super.key});

  @override
  ConsumerState<PaymentHistoryScreen> createState() => _PaymentHistoryScreenState();
}

class _PaymentHistoryScreenState extends ConsumerState<PaymentHistoryScreen> {
  final TextEditingController search_controller = TextEditingController();

  @override
  void dispose() {
    search_controller.dispose();
    super.dispose();
  }

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
  Widget build(BuildContext context) {
    final double max_w = Responsive.max_width(context);
    final DateTime month = ref.watch(payment_month_provider);
    final history_async = ref.watch(payment_history_provider);
    final theme_mode = ref.watch(theme_mode_provider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('결제 내역', style: TextStyle(fontWeight: FontWeight.w900)),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: max_w),
            child: Padding(
              padding: Responsive.page_padding(context),
              child: Column(
                children: <Widget>[
                  Row(
                    children: <Widget>[
                      Expanded(
                        child: TextField(
                          controller: search_controller,
                          decoration: const InputDecoration(
                            hintText: '거래 내역 검색...', 
                            prefixIcon: Icon(Icons.search),
                          ),
                          onChanged: (_) => setState(() {}),
                        ),
                      ),
                      const SizedBox(width: 10),
                      IconButton(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('필터 기능이 준비 중입니다.')),
                          );
                        },
                        icon: const Icon(Icons.tune),
                      ),
                    ],
                  ),
                  const SizedBox(height: 12),

                  history_async.when(
                    loading: () => const Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator()),
                    error: (e, _) => Text('내역을 불러오지 못했어요.\n$e'),
                    data: (list) {
                      final String q = search_controller.text.trim();
                      final filtered = q.isEmpty
                          ? list
                          : list.where((x) => x.merchant_name.contains(q) || x.category_label.contains(q)).toList();

                      final int total_amount = filtered.fold<int>(0, (p, c) => p + c.amount);
                      final String month_label = '${month.year}년 ${month.month}월';

                      return Expanded(
                        child: SingleChildScrollView(
                          child: Column(
                            children: <Widget>[
                              SectionCard(
                                child: Container(
                                  width: double.infinity,
                                  padding: const EdgeInsets.all(4),
                                  decoration: BoxDecoration(
                                    gradient: LinearGradient(
                                      colors: <Color>[
                                        AppColors.brand_primary.withOpacity(0.85),
                                        AppColors.brand_primary.withOpacity(0.55),
                                      ],
                                    ),
                                    borderRadius: BorderRadius.circular(20),
                                  ),
                                  child: Padding(
                                    padding: const EdgeInsets.all(14),
                                    child: Column(
                                      crossAxisAlignment: CrossAxisAlignment.start,
                                      children: <Widget>[
                                        Text('$month_label 총 지출', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w900)),
                                        const SizedBox(height: 8),
                                        Text(_money(total_amount), style: const TextStyle(color: Colors.white, fontSize: 22, fontWeight: FontWeight.w900)),
                                        const SizedBox(height: 10),
                                        Container(
                                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                          decoration: BoxDecoration(
                                            color: Colors.white.withOpacity(0.18),
                                            borderRadius: BorderRadius.circular(12),
                                          ),
                                          child: Text('${month.month}월 1일 ~ ${month.month}월 31일', style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w800, fontSize: 12)),
                                        ),
                                      ],
                                    ),
                                  ),
                                ),
                              ),
                              const SizedBox(height: 12),

                              ...filtered.map((it) {
                                final String date_label = '${it.paid_at.month}월 ${it.paid_at.day}일 · ${it.paid_at.hour.toString().padLeft(2, '0')}:${it.paid_at.minute.toString().padLeft(2, '0')}';
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
                                          child: const Icon(Icons.storefront, color: AppColors.brand_primary),
                                        ),
                                        const SizedBox(width: 12),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: <Widget>[
                                              Text(it.merchant_name, style: const TextStyle(fontWeight: FontWeight.w900)),
                                              const SizedBox(height: 4),
                                              Text('$date_label · ${it.category_label}', style: TextStyle(color: AppColors.text_secondary, fontSize: 12, fontWeight: FontWeight.w800)),
                                            ],
                                          ),
                                        ),
                                        Column(
                                          crossAxisAlignment: CrossAxisAlignment.end,
                                          children: <Widget>[
                                            Text(_money(it.amount), style: const TextStyle(fontWeight: FontWeight.w900)),
                                            const SizedBox(height: 8),
                                            OutlinedButton(
                                              onPressed: () => context.push(AppRoutes.digital_receipt, extra: <String, dynamic>{'receipt_id': it.receipt_id}),
                                              style: OutlinedButton.styleFrom(
                                                padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                                                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                              ),
                                              child: const Text('영수증'),
                                            ),
                                          ],
                                        ),
                                      ],
                                    ),
                                  ),
                                );
                              }),

                              if (filtered.isEmpty)
                                Padding(
                                  padding: const EdgeInsets.only(top: 40),
                                  child: Text('표시할 거래 내역이 없어요.', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900)),
                                ),
                            ],
                          ),
                        ),
                      );
                    },
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
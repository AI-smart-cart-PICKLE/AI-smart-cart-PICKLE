import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../domain/models/spending.dart';
import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../shared/widgets/section_card.dart';
import 'account_providers.dart';

class SpendingBreakdownScreen extends ConsumerWidget {
  const SpendingBreakdownScreen({super.key});

  String _format_currency(num amount) {
    final int value = amount.round();
    final String s = value.toString();
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

    final DateTime month = ref.watch(selected_month_provider);
    final summary_async = ref.watch(month_summary_provider);
    final categories_async = ref.watch(category_breakdown_provider);
    final theme_mode = ref.watch(theme_mode_provider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('지출 분석', style: TextStyle(fontWeight: FontWeight.w900)),
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
                    child: Column(
                      children: <Widget>[
                        Row(
                          children: <Widget>[
                            IconButton(
                              onPressed: () {
                                final DateTime prev = DateTime(month.year, month.month - 1, 1);
                                ref.read(selected_month_provider.notifier).state = prev;
                              },
                              icon: const Icon(Icons.chevron_left),
                            ),
                            Expanded(
                              child: Text(
                                '${month.year}년 ${month.month}월',
                                textAlign: TextAlign.center,
                                style: const TextStyle(fontWeight: FontWeight.w900),
                              ),
                            ),
                            IconButton(
                              onPressed: () {
                                final DateTime next = DateTime(month.year, month.month + 1, 1);
                                ref.read(selected_month_provider.notifier).state = next;
                              },
                              icon: const Icon(Icons.chevron_right),
                            ),
                          ],
                        ),
                        const SizedBox(height: 10),
                        summary_async.when(
                          loading: () => const Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator()),
                          error: (e, _) => Text('요약 오류: $e'),
                          data: (s) => Column(
                            children: <Widget>[
                              Text('총 지출', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900)),
                              const SizedBox(height: 6),
                              Text(_format_currency(s.total_amount), style: const TextStyle(fontSize: 26, fontWeight: FontWeight.w900)),
                            ],
                          ),
                        ),
                        const SizedBox(height: 14),
                        categories_async.when(
                          loading: () => const Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator()),
                          error: (e, _) => Text('카테고리 오류: $e'),
                          data: (categories) {
                            if (categories.isEmpty) {
                              return Text('표시할 데이터가 없어요.', style: TextStyle(color: AppColors.text_secondary));
                            }

                            final CategorySpend top = categories.reduce((a, b) => a.amount >= b.amount ? a : b);
                            final int top_percent = (top.ratio * 100).round();

                            return Column(
                              children: <Widget>[
                                _DonutPlaceholder(
                                  center_label: '$top_percent%\n${top.category_label}',
                                ),
                                const SizedBox(height: 10),
                                Container(
                                  padding: const EdgeInsets.all(12),
                                  decoration: BoxDecoration(
                                    color: AppColors.border.withOpacity(0.25),
                                    borderRadius: BorderRadius.circular(16),
                                  ),
                                  child: Row(
                                    children: <Widget>[
                                      const Icon(Icons.info_outline, color: AppColors.brand_primary),
                                      const SizedBox(width: 10),
                                      Expanded(
                                        child: Text(
                                          '이번 달 지출의 대부분은 "${top.category_label}" 항목이에요.',
                                          style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800),
                                        ),
                                      ),
                                    ],
                                  ),
                                ),
                              ],
                            );
                          },
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 14),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: <Widget>[
                      const Text('카테고리 상세', style: TextStyle(fontWeight: FontWeight.w900)),
                      TextButton.icon(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('정렬 기준을 변경합니다.')),
                          );
                        },
                        icon: const Icon(Icons.sort, size: 18),
                        label: const Text('금액순'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),
                  categories_async.when(
                    loading: () => const Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator()),
                    error: (e, _) => Text('오류: $e'),
                    data: (categories) {
                      return SectionCard(
                        child: Column(
                          children: categories.map((c) {
                            final int percent = (c.ratio * 100).round();
                            return Padding(
                              padding: const EdgeInsets.symmetric(vertical: 10),
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: <Widget>[
                                  Row(
                                    children: <Widget>[
                                      Expanded(child: Text(c.category_label, style: const TextStyle(fontWeight: FontWeight.w900))),
                                      Text(_format_currency(c.amount), style: const TextStyle(fontWeight: FontWeight.w900)),
                                      const SizedBox(width: 10),
                                      Text('$percent%', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900)),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Stack(
                                    children: <Widget>[
                                      Container(
                                        height: 10,
                                        decoration: BoxDecoration(
                                          color: AppColors.border.withOpacity(0.35),
                                          borderRadius: BorderRadius.circular(999),
                                        ),
                                      ),
                                      FractionallySizedBox(
                                        widthFactor: c.ratio.clamp(0, 1),
                                        child: Container(
                                          height: 10,
                                          decoration: BoxDecoration(
                                            color: AppColors.brand_primary.withOpacity(0.7),
                                            borderRadius: BorderRadius.circular(999),
                                          ),
                                        ),
                                      ),
                                    ],
                                  ),
                                ],
                              ),
                            );
                          }).toList(),
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

class _DonutPlaceholder extends StatelessWidget {
  final String center_label;

  const _DonutPlaceholder({required this.center_label});

  @override
  Widget build(BuildContext context) {
    return Container(
      width: 180,
      height: 180,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: AppColors.brand_primary.withOpacity(0.10),
        border: Border.all(color: AppColors.border),
      ),
      alignment: Alignment.center,
      child: Text(
        center_label,
        textAlign: TextAlign.center,
        style: const TextStyle(fontWeight: FontWeight.w900),
      ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:countup/countup.dart';

import '../../../core/router/app_routes.dart';
import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/section_card.dart';
import '../../../shared/widgets/bottom_nav.dart';
import '../../../domain/models/spending.dart';
import 'account_providers.dart';

class SpendingOverviewScreen extends StatefulWidget {
  const SpendingOverviewScreen({super.key});

  @override
  State<SpendingOverviewScreen> createState() => _SpendingOverviewScreenState();
}

class _SpendingOverviewScreenState extends State<SpendingOverviewScreen> {
  BottomTab current_tab = BottomTab.account_book;

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
  Widget build(BuildContext context) {
    return Consumer(
      builder: (context, ref, child) {
        final double max_w = Responsive.max_width(context);

        final DateTime month = ref.watch(selected_month_provider);
        final summary_async = ref.watch(month_summary_provider);
        final days_async = ref.watch(month_days_provider);
        final tx_async = ref.watch(recent_transactions_provider);

        return Scaffold(
          appBar: AppBar(
            title: const Text('지출 개요', style: TextStyle(fontWeight: FontWeight.w900)),
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
                            _MonthHeader(
                              month: month,
                              on_prev: () {
                                final DateTime prev =
                                    DateTime(month.year, month.month - 1, 1);
                                ref.read(selected_month_provider.notifier).state =
                                    prev;
                              },
                              on_next: () {
                                final DateTime next =
                                    DateTime(month.year, month.month + 1, 1);
                                ref.read(selected_month_provider.notifier).state =
                                    next;
                              },
                            ),
                            const SizedBox(height: 12),
                            summary_async.when(
                              loading: () => const Padding(
                                  padding: EdgeInsets.all(24),
                                  child: CircularProgressIndicator()),
                              error: (e, _) => Text('요약을 불러오지 못했어요.\n$e'),
                              data: (summary) {
                                final String diff_label = summary.diff_percent == 0
                                    ? '지난달과 동일'
                                    : summary.diff_percent > 0
                                    ? '지난달 대비 ${summary.diff_percent}% 증가'
                                    : '지난달 대비 ${summary.diff_percent.abs()}% 감소';

                                return Column(
                                  children: <Widget>[
                                    Text('총 지출',
                                        style: TextStyle(
                                            color: AppColors.text_secondary,
                                            fontWeight: FontWeight.w900)),
                                    const SizedBox(height: 6),
                                    Row(
                                      mainAxisAlignment: MainAxisAlignment.center,
                                      children: [
                                        const Text('₩', style: TextStyle(fontSize: 28, fontWeight: FontWeight.w900)),
                                        Countup(
                                          begin: 0,
                                          end: summary.total_amount.toDouble(),
                                          duration: const Duration(milliseconds: 1500),
                                          separator: ',',
                                          style: const TextStyle(
                                            fontSize: 28,
                                            fontWeight: FontWeight.w900,
                                          ),
                                        ),
                                      ],
                                    ),
                                    const SizedBox(height: 8),
                                    Container(
                                      padding: const EdgeInsets.symmetric(
                                          horizontal: 10, vertical: 6),
                                      decoration: BoxDecoration(
                                        color: AppColors.brand_primary
                                            .withOpacity(0.12),
                                        borderRadius: BorderRadius.circular(999),
                                      ),
                                      child: Text(diff_label,
                                          style: const TextStyle(
                                              fontWeight: FontWeight.w900,
                                              color: AppColors.brand_primary)),
                                    ),
                                  ],
                                );
                              },
                            ),
                            const SizedBox(height: 14),
                            days_async.when(
                              loading: () => const Padding(
                                  padding: EdgeInsets.all(12),
                                  child: CircularProgressIndicator()),
                              error: (e, _) => Text('달력 데이터를 불러오지 못했어요.\n$e'),
                              data: (days) =>
                                  _SpendingCalendar(month: month, days: days),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),
                                        Row(
                                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                          children: <Widget>[
                                            const Text('최근 지출',
                                                style: TextStyle(
                                                    fontSize: 16, fontWeight: FontWeight.w900)),
                                            TextButton(
                                              onPressed: () => context.push(AppRoutes.payment_history),
                                              child: const Text('전체 보기'),
                                            ),
                                          ],
                                        ),
                                        const SizedBox(height: 8),
                                        tx_async.when(
                                          loading: () => const Padding(
                                              padding: EdgeInsets.all(20),
                                              child: CircularProgressIndicator()),
                                          error: (e, _) => Text('내역을 불러오지 못했어요.\n$e'),
                                          data: (list) {
                                            if (list.isEmpty) {
                                              return SectionCard(
                                                child: Text('표시할 내역이 없어요.',
                                                    style: TextStyle(color: AppColors.text_secondary)),
                                              );
                                            }
                                            return SectionCard(
                                              padding: EdgeInsets.zero,
                                              child: Column(
                                                children: list.map<Widget>((tx) {
                                                  final String amount_label =
                                                      '- ${_format_currency(tx.amount)}';
                                                  final String date_label =
                                                      '${tx.spent_at.month}월 ${tx.spent_at.day}일';
                                                  return InkWell(
                                                    onTap: () => context.push(AppRoutes.digital_receipt, extra: {'receipt_id': tx.transaction_id}),
                                                    borderRadius: BorderRadius.circular(16),
                                                    child: Padding(
                                                      padding:
                                                      const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                                                      child: Row(
                                                        children: <Widget>[
                                                          Container(
                                                            width: 40,
                                                            height: 40,
                                                            decoration: BoxDecoration(
                                                              color:
                                                              AppColors.border.withOpacity(0.35),
                                                              borderRadius: BorderRadius.circular(14),
                                                            ),
                                                            child: const Icon(
                                                                Icons.shopping_cart_outlined,
                                                                color: AppColors.brand_primary),
                                                          ),
                                                          const SizedBox(width: 12),
                                                          Expanded(
                                                            child: Column(
                                                              crossAxisAlignment:
                                                              CrossAxisAlignment.start,
                                                              children: <Widget>[
                                                                Text(tx.merchant_name,
                                                                    style: const TextStyle(
                                                                        fontWeight: FontWeight.w900)),
                                                                const SizedBox(height: 4),
                                                                Text('$date_label · ${tx.category_label}',
                                                                    style: TextStyle(
                                                                        color: AppColors.text_secondary,
                                                                        fontSize: 12)),
                                                              ],
                                                            ),
                                                          ),
                                                          Row(
                                                            mainAxisSize: MainAxisSize.min,
                                                            children: [
                                                              const Text('- ₩', style: TextStyle(fontWeight: FontWeight.w900)),
                                                              Countup(
                                                                begin: 0,
                                                                end: tx.amount.toDouble(),
                                                                duration: const Duration(milliseconds: 1000),
                                                                separator: ',',
                                                                style: const TextStyle(
                                                                  fontWeight: FontWeight.w900,
                                                                ),
                                                              ),
                                                            ],
                                                          ),
                                                        ],
                                                      ),
                                                    ),
                                                  );
                                                }).toList(),
                                              ),
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
          bottomNavigationBar: BottomNav(
            current_tab: current_tab,
            on_tab_selected: (BottomTab next) {
              setState(() => current_tab = next);
              if (next == BottomTab.home) context.go(AppRoutes.home);
              if (next == BottomTab.search) context.go(AppRoutes.product_search);
              if (next == BottomTab.scan) context.push(AppRoutes.qr_scanner);
              if (next == BottomTab.account_book) context.go(AppRoutes.spending_overview);
              if (next == BottomTab.my_page) context.go(AppRoutes.my_page);
            },
          ),
        );
      },
    );
  }
}

class _MonthHeader extends StatelessWidget {
  final DateTime month;
  final VoidCallback on_prev;
  final VoidCallback on_next;

  const _MonthHeader({
    required this.month,
    required this.on_prev,
    required this.on_next,
  });

  @override
  Widget build(BuildContext context) {
    final String label = '${month.year}년 ${month.month}월';
    return Row(
      children: <Widget>[
        IconButton(onPressed: on_prev, icon: const Icon(Icons.chevron_left)),
        Expanded(
          child: Text(label,
              textAlign: TextAlign.center,
              style:
              const TextStyle(fontSize: 16, fontWeight: FontWeight.w900)),
        ),
        IconButton(onPressed: on_next, icon: const Icon(Icons.chevron_right)),
      ],
    );
  }
}

class _SpendingCalendar extends StatelessWidget {
  final DateTime month;
  final List<SpendingDay> days;

  const _SpendingCalendar({
    required this.month,
    required this.days,
  });

  int _days_in_month(DateTime m) {
    final DateTime next = DateTime(m.year, m.month + 1, 1);
    return next.subtract(const Duration(days: 1)).day;
  }

  int _weekday_offset(DateTime m) {
    final int w = DateTime(m.year, m.month, 1).weekday;
    return (w - 1);
  }

  @override
  Widget build(BuildContext context) {
    final int total_days = _days_in_month(month);
    final int offset = _weekday_offset(month);

    final Map<int, int> amount_by_day = <int, int>{};
    for (final SpendingDay d in days) {
      amount_by_day[d.date.day] = d.amount;
    }

    final List<Widget> cells = <Widget>[];
    const List<String> week_labels = <String>['월', '화', '수', '목', '금', '토', '일'];

    cells.addAll(week_labels.map((w) {
      return Center(
        child: Text(w,
            style: TextStyle(
                color: AppColors.text_secondary, fontWeight: FontWeight.w900)),
      );
    }));

    for (int i = 0; i < offset; i++) {
      cells.add(const SizedBox.shrink());
    }

    for (int day = 1; day <= total_days; day++) {
      final int amount = amount_by_day[day] ?? 0;
      final bool has_spend = amount > 0;

      cells.add(
        Container(
          decoration: BoxDecoration(
            color:
            has_spend ? AppColors.brand_primary.withOpacity(0.12) : Colors.transparent,
            borderRadius: BorderRadius.circular(14),
          ),
          padding: const EdgeInsets.symmetric(vertical: 8),
          child: Column(
            children: <Widget>[
              Text('$day',
                  style: TextStyle(
                      fontWeight: FontWeight.w900,
                      color: has_spend
                          ? AppColors.brand_primary
                          : AppColors.text_primary)),
              const SizedBox(height: 4),
              Text(
                has_spend ? '-${_short_k(amount)}' : '',
                style: TextStyle(
                    fontSize: 11,
                    color: AppColors.text_secondary,
                    fontWeight: FontWeight.w800),
              ),
            ],
          ),
        ),
      );
    }

    return LayoutBuilder(
      builder: (BuildContext context, BoxConstraints c) {
        final double spacing = 8;
        final double cell_w = (c.maxWidth - spacing * 6) / 7;
        final double cell_h = 46;

        return Wrap(
          spacing: spacing,
          runSpacing: spacing,
          children: cells.map((w) {
            return SizedBox(width: cell_w, height: cell_h, child: w);
          }).toList(),
        );
      },
    );
  }

  String _short_k(int amount) {
    if (amount >= 10000) return '${(amount / 10000).toStringAsFixed(0)}만';
    if (amount >= 1000) return '${(amount / 1000).toStringAsFixed(0)}천';
    return '$amount';
  }
}

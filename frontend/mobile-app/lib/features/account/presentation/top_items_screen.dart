import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/section_card.dart';
import 'account_providers.dart';

class TopItemsScreen extends ConsumerWidget {
  const TopItemsScreen({super.key});

    @override

    Widget build(BuildContext context, WidgetRef ref) {

      final double max_w = Responsive.max_width(context);

      final bool is_dark = Theme.of(context).brightness == Brightness.dark;

      final Color text_secondary = is_dark ? AppColors.text_secondary_dark : AppColors.text_secondary;

      final Color border_color = is_dark ? AppColors.border_dark : AppColors.border;

  

      final DateTime month = ref.watch(selected_month_provider);

      final top_async = ref.watch(top_items_provider);

  

      return Scaffold(

        appBar: AppBar(

          title: const Text('자주 산 상품'),

          actions: <Widget>[

            IconButton(

              onPressed: () {

                ScaffoldMessenger.of(context).showSnackBar(

                  const SnackBar(content: Text('필터 설정 기능이 준비 중입니다.')),

                );

              },

              icon: const Icon(Icons.tune),

            ),

          ],

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

                          IconButton(

                            onPressed: () {

                              final DateTime prev = DateTime(month.year, month.month - 1, 1);

                              ref.read(selected_month_provider.notifier).state = prev;

                            },

                            icon: const Icon(Icons.chevron_left),

                          ),

                          Expanded(

                            child: Column(

                              children: <Widget>[

                                Text('${month.year}년 ${month.month}월', style: const TextStyle(fontWeight: FontWeight.w900)),

                                const SizedBox(height: 4),

                                Text('월간 기준', style: TextStyle(color: text_secondary, fontSize: 12, fontWeight: FontWeight.w800)),

                              ],

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

                    ),

                    const SizedBox(height: 12),

                    top_async.when(

                      loading: () => const Padding(padding: EdgeInsets.all(32), child: CircularProgressIndicator()),

                      error: (e, _) => Text('데이터를 불러오지 못했어요.\n$e'),

                      data: (items) {

                        if (items.isEmpty) {

                          return SectionCard(

                            child: Text('표시할 데이터가 없어요.', style: TextStyle(color: text_secondary)),

                          );

                        }

  

                        final List<TopItemBar> bars = items.take(5).map((it) {

                          return TopItemBar(label: it.name, value: it.purchase_count);

                        }).toList();

  

                        return Column(

                          crossAxisAlignment: CrossAxisAlignment.start,

                          children: <Widget>[

                            SectionCard(

                              child: Column(

                                crossAxisAlignment: CrossAxisAlignment.start,

                                children: <Widget>[

                                  Row(

                                    mainAxisAlignment: MainAxisAlignment.spaceBetween,

                                    children: <Widget>[

                                      const Text('빈도 분석', style: TextStyle(fontWeight: FontWeight.w900)),

                                      Container(

                                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),

                                        decoration: BoxDecoration(

                                          color: AppColors.brand_primary.withOpacity(0.12),

                                          borderRadius: BorderRadius.circular(999),

                                        ),

                                        child: const Text('월간', style: TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w900, fontSize: 12)),

                                      ),

                                    ],

                                  ),

                                  const SizedBox(height: 12),

                                  _MiniBarChart(items: bars, border_color: border_color, text_secondary: text_secondary),

                                ],

                              ),

                            ),

                            const SizedBox(height: 12),

                            Row(

                              mainAxisAlignment: MainAxisAlignment.spaceBetween,

                              children: <Widget>[

                                const Text('가장 많이 구매', style: TextStyle(fontWeight: FontWeight.w900)),

                                TextButton.icon(

                                  onPressed: () {

                                    ScaffoldMessenger.of(context).showSnackBar(

                                      const SnackBar(content: Text('정렬 순서를 변경합니다.')),

                                    );

                                  },

                                  icon: const Icon(Icons.sort, size: 18),

                                  label: const Text('구매 횟수순'),

                                ),

                              ],

                            ),

                            const SizedBox(height: 8),

                            SectionCard(

                              child: Column(

                                children: items.asMap().entries.map((entry) {

                                  final int idx = entry.key + 1;

                                  final item = entry.value;

                                  return Padding(

                                    padding: const EdgeInsets.symmetric(vertical: 10),

                                    child: Row(

                                      children: <Widget>[

                                        Container(

                                          width: 28,

                                          height: 28,

                                          decoration: BoxDecoration(

                                            color: idx == 1 ? AppColors.brand_primary : border_color.withOpacity(0.35),

                                            borderRadius: BorderRadius.circular(999),

                                          ),

                                          alignment: Alignment.center,

                                          child: Text(

                                            '$idx',

                                            style: TextStyle(

                                              color: idx == 1 ? Colors.white : text_secondary,

                                              fontWeight: FontWeight.w900,

                                            ),

                                          ),

                                        ),

                                        const SizedBox(width: 12),

                                        Container(

                                          width: 40,

                                          height: 40,

                                          decoration: BoxDecoration(

                                            color: border_color.withOpacity(0.35),

                                            borderRadius: BorderRadius.circular(14),

                                          ),

                                          child: const Icon(Icons.shopping_basket_outlined, color: AppColors.brand_primary),

                                        ),

                                        const SizedBox(width: 12),

                                        Expanded(

                                          child: Column(

                                            crossAxisAlignment: CrossAxisAlignment.start,

                                            children: <Widget>[

                                              Text(item.name, style: const TextStyle(fontWeight: FontWeight.w900)),

                                              const SizedBox(height: 4),

                                              Text(

                                                '${item.category_label} · 평균 ₩${item.avg_price}',

                                                style: TextStyle(color: text_secondary, fontSize: 12, fontWeight: FontWeight.w800),

                                              ),

                                            ],

                                          ),

                                        ),

                                        Text('${item.purchase_count}회', style: const TextStyle(fontWeight: FontWeight.w900, color: AppColors.brand_primary)),

                                      ],

                                    ),

                                  );

                                }).toList(),

                              ),

                            ),

                          ],

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

  

  class TopItemBar {

    final String label;

    final int value;

  

    const TopItemBar({required this.label, required this.value});

  }

  

  class _MiniBarChart extends StatelessWidget {

    final List<TopItemBar> items;

    final Color border_color;

    final Color text_secondary;

  

    const _MiniBarChart({

      required this.items,

      required this.border_color,

      required this.text_secondary,

    });

  

    @override

    Widget build(BuildContext context) {

      final int max_v = items.map((e) => e.value).fold<int>(0, (p, c) => c > p ? c : p);

  

      return Column(

        children: items.map((e) {

          final double ratio = max_v == 0 ? 0 : (e.value / max_v);

          return Padding(

            padding: const EdgeInsets.symmetric(vertical: 6),

            child: Row(

              children: <Widget>[

                SizedBox(

                  width: 72,

                  child: Text(e.label, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w900)),

                ),

                const SizedBox(width: 10),

                Expanded(

                  child: Stack(

                    children: <Widget>[

                      Container(height: 10, decoration: BoxDecoration(color: border_color.withOpacity(0.35), borderRadius: BorderRadius.circular(999))),

                      FractionallySizedBox(

                        widthFactor: ratio,

                        child: Container(height: 10, decoration: BoxDecoration(color: AppColors.brand_primary.withOpacity(0.7), borderRadius: BorderRadius.circular(999))),

                      ),

                    ],

                  ),

                ),

                const SizedBox(width: 10),

                Text('${e.value}', style: TextStyle(color: text_secondary, fontWeight: FontWeight.w900)),

              ],

            ),

          );

        }).toList(),

      );

    }

  }

  
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../shared/widgets/section_card.dart';
import '../../../shared/widgets/primary_button.dart';
import 'recipe_providers.dart';

class RecipeDetailScreen extends ConsumerWidget {
  final String recipe_id;

  const RecipeDetailScreen({super.key, required this.recipe_id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final double max_w = Responsive.max_width(context);
    final detail_async = ref.watch(recipe_detail_provider(recipe_id));
    final theme_mode = ref.watch(theme_mode_provider);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: max_w),
            child: detail_async.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Center(child: Text('레시피를 불러오지 못했어요.\n$e')),
              data: (d) {
                return CustomScrollView(
                  slivers: <Widget>[
                    SliverAppBar(
                      pinned: true,
                      title: const Text('레시피 상세', style: TextStyle(fontWeight: FontWeight.w900)),
                      actions: <Widget>[
                        IconButton(
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('레시피 공유 기능이 준비 중입니다.')),
                            );
                          },
                          icon: const Icon(Icons.share),
                        ),
                      ],
                      expandedHeight: 240,
                      flexibleSpace: FlexibleSpaceBar(
                        background: Container(
                          color: Colors.black.withOpacity(0.06),
                          child: Stack(
                            children: <Widget>[
                              const Center(child: Icon(Icons.image_outlined, size: 70)),
                              Positioned(
                                left: 16,
                                bottom: 18,
                                child: Column(
                                  crossAxisAlignment: CrossAxisAlignment.start,
                                  children: <Widget>[
                                    Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                      decoration: BoxDecoration(
                                        color: AppColors.brand_primary.withOpacity(0.12),
                                        borderRadius: BorderRadius.circular(999),
                                      ),
                                      child: const Text('피클 추천', style: TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w900, fontSize: 12)),
                                    ),
                                    const SizedBox(height: 8),
                                    Text(d.title, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900)),
                                  ],
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    ),
                    SliverToBoxAdapter(
                      child: Padding(
                        padding: Responsive.page_padding(context),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: <Widget>[
                            Row(
                              children: <Widget>[
                                Expanded(child: _metric(label: '시간', value: '${d.prep_time_min}분')),
                                const SizedBox(width: 10),
                                Expanded(child: _metric(label: '난이도', value: d.difficulty_label)),
                                const SizedBox(width: 10),
                                Expanded(child: _metric(label: '칼로리', value: '${d.calories}kcal')),
                              ],
                            ),
                            const SizedBox(height: 14),

                            Row(
                              children: <Widget>[
                                const Expanded(child: Text('재료', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900))),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: AppColors.brand_primary.withOpacity(0.12),
                                    borderRadius: BorderRadius.circular(999),
                                  ),
                                  child: const Text('카트 동기화 켬', style: TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w900, fontSize: 12)),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            SectionCard(
                              child: Column(
                                children: d.ingredients.map((ing) {
                                  return Padding(
                                    padding: const EdgeInsets.symmetric(vertical: 10),
                                    child: Row(
                                      children: <Widget>[
                                        Icon(
                                          ing.is_available ? Icons.check_circle : Icons.radio_button_unchecked,
                                          color: ing.is_available ? AppColors.brand_primary : AppColors.text_secondary,
                                        ),
                                        const SizedBox(width: 10),
                                        Expanded(
                                          child: Column(
                                            crossAxisAlignment: CrossAxisAlignment.start,
                                            children: <Widget>[
                                              Text(ing.name, style: const TextStyle(fontWeight: FontWeight.w900)),
                                              const SizedBox(height: 4),
                                              Text(ing.status_label, style: TextStyle(color: AppColors.text_secondary, fontSize: 12, fontWeight: FontWeight.w800)),
                                            ],
                                          ),
                                        ),
                                        if (!ing.is_available)
                                          InkWell(
                                            onTap: () {
                                              ScaffoldMessenger.of(context).showSnackBar(
                                                SnackBar(content: Text('${ing.name}을(를) 장바구니에 담았습니다.')),
                                              );
                                            },
                                            borderRadius: BorderRadius.circular(12),
                                            child: Container(
                                              width: 36,
                                              height: 36,
                                              decoration: BoxDecoration(
                                                color: AppColors.brand_primary.withOpacity(0.12),
                                                borderRadius: BorderRadius.circular(12),
                                              ),
                                              child: const Icon(Icons.shopping_cart_outlined, color: AppColors.brand_primary, size: 18),
                                            ),
                                          ),
                                      ],
                                    ),
                                  );
                                }).toList(),
                              ),
                            ),
                            const SizedBox(height: 12),
                            PrimaryButton(
                              label: '요리 모드 시작',
                              on_pressed: () {
                                ScaffoldMessenger.of(context).showSnackBar(
                                  const SnackBar(content: Text('요리 모드를 시작합니다.')),
                                );
                              },
                              leading: const Icon(Icons.play_arrow),
                            ),
                            const SizedBox(height: 18),

                            const Text('조리 방법', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900)),
                            const SizedBox(height: 10),
                            ...d.steps.map((s) {
                              return Padding(
                                padding: const EdgeInsets.only(bottom: 12),
                                child: SectionCard(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: <Widget>[
                                      Row(
                                        children: <Widget>[
                                          Container(
                                            width: 28,
                                            height: 28,
                                            decoration: BoxDecoration(
                                              color: AppColors.brand_primary.withOpacity(0.12),
                                              borderRadius: BorderRadius.circular(10),
                                            ),
                                            alignment: Alignment.center,
                                            child: Text('${s.order}', style: const TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w900)),
                                          ),
                                          const SizedBox(width: 10),
                                          Expanded(child: Text(s.title, style: const TextStyle(fontWeight: FontWeight.w900))),
                                        ],
                                      ),
                                      const SizedBox(height: 10),
                                      Container(
                                        height: 140,
                                        decoration: BoxDecoration(
                                          color: AppColors.border.withOpacity(0.35),
                                          borderRadius: BorderRadius.circular(16),
                                        ),
                                        child: const Center(child: Icon(Icons.image_outlined)),
                                      ),
                                      const SizedBox(height: 10),
                                      Text(s.description, style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800)),
                                    ],
                                  ),
                                ),
                              );
                            }).toList(),

                            const SizedBox(height: 30),
                          ],
                        ),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ),
      ),
    );
  }

  Widget _metric({required String label, required String value}) {
    return SectionCard(
      padding: const EdgeInsets.all(12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: <Widget>[
          Text(label, style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900, fontSize: 12)),
          const SizedBox(height: 6),
          Text(value, style: const TextStyle(fontWeight: FontWeight.w900)),
        ],
      ),
    );
  }
}
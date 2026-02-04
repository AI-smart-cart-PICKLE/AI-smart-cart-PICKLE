import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_routes.dart';
import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../shared/widgets/section_card.dart';
import '../../recipe/presentation/recipe_providers.dart';

class MyRecipesScreen extends ConsumerWidget {
  const MyRecipesScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final double max_w = Responsive.max_width(context);
    final String filter_key = ref.watch(recipe_filter_provider);
    final recipes_async = ref.watch(recipes_from_cart_provider);
    final theme_mode = ref.watch(theme_mode_provider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('추천 레시피', style: TextStyle(fontWeight: FontWeight.w900)),
        actions: <Widget>[
          IconButton(
            onPressed: () {
              ScaffoldMessenger.of(context).showSnackBar(
                const SnackBar(content: Text('레시피 검색 기능이 준비 중입니다.')),
              );
            },
            icon: const Icon(Icons.search),
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
                  Row(
                    children: <Widget>[
                      Container(
                        padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                        decoration: BoxDecoration(
                          color: AppColors.brand_primary.withOpacity(0.12),
                          borderRadius: BorderRadius.circular(999),
                        ),
                        child: const Text('카트 연동됨', style: TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w900, fontSize: 12)),
                      ),
                      const SizedBox(width: 10),
                      Text('피클 스마트카트 #042', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800)),
                    ],
                  ),
                  const SizedBox(height: 12),
                  Wrap(
                    spacing: 8,
                    children: <Widget>[
                      _filter_chip(
                        label: '상위 매칭',
                        is_selected: filter_key == 'top_matches',
                        on_tap: () => ref.read(recipe_filter_provider.notifier).state = 'top_matches',
                      ),
                      _filter_chip(
                        label: '15분 이하',
                        is_selected: filter_key == 'under_15',
                        on_tap: () => ref.read(recipe_filter_provider.notifier).state = 'under_15',
                      ),
                      _filter_chip(
                        label: '채식',
                        is_selected: filter_key == 'vegetarian',
                        on_tap: () => ref.read(recipe_filter_provider.notifier).state = 'vegetarian',
                      ),
                    ],
                  ),
                  const SizedBox(height: 14),

                  Text('현재 선택됨', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900)),
                  const SizedBox(height: 8),

                  recipes_async.when(
                    loading: () => const Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator()),
                    error: (e, _) => Text('레시피를 불러오지 못했어요.\n$e'),
                    data: (list) {
                      if (list.isEmpty) {
                        return SectionCard(child: Text('표시할 레시피가 없어요.', style: TextStyle(color: AppColors.text_secondary)));
                      }
                      final selected = list.first;

                      return Column(
                        children: <Widget>[
                          SectionCard(
                            child: Row(
                              children: <Widget>[
                                Expanded(
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: <Widget>[
                                      Row(
                                        children: <Widget>[
                                          Container(
                                            padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                            decoration: BoxDecoration(
                                              color: AppColors.brand_primary.withOpacity(0.12),
                                              borderRadius: BorderRadius.circular(999),
                                            ),
                                            child: const Text('진행 중', style: TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w900, fontSize: 12)),
                                          ),
                                          const SizedBox(width: 8),
                                          Text('${selected.match_percent}% 매칭', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900, fontSize: 12)),
                                        ],
                                      ),
                                      const SizedBox(height: 8),
                                      Text(selected.title, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 16)),
                                      const SizedBox(height: 6),
                                      Text(selected.subtitle, style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800, fontSize: 12)),
                                      const SizedBox(height: 10),
                                      Row(
                                        children: <Widget>[
                                          ElevatedButton.icon(
                                            onPressed: () {
                                              ScaffoldMessenger.of(context).showSnackBar(
                                                const SnackBar(content: Text('조리 단계를 이어서 진행합니다.')),
                                              );
                                            },
                                            icon: const Icon(Icons.play_arrow),
                                            label: const Text('단계 이어가기'),
                                            style: ElevatedButton.styleFrom(
                                              backgroundColor: AppColors.brand_primary,
                                              foregroundColor: Colors.white,
                                              shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                                            ),
                                          ),
                                          const SizedBox(width: 10),
                                          IconButton(
                                            onPressed: () {
                                              ScaffoldMessenger.of(context).showSnackBar(
                                                SnackBar(content: Text('${selected.title}을(를) 찜했습니다.')),
                                              );
                                            },
                                            icon: const Icon(Icons.favorite_border),
                                          ),
                                        ],
                                      ),
                                    ],
                                  ),
                                ),
                                const SizedBox(width: 10),
                                Container(
                                  width: 92,
                                  height: 92,
                                  decoration: BoxDecoration(
                                    color: AppColors.border.withOpacity(0.35),
                                    borderRadius: BorderRadius.circular(18),
                                  ),
                                  child: const Icon(Icons.image_outlined),
                                ),
                              ],
                            ),
                          ),
                          const SizedBox(height: 12),

                          Row(
                            mainAxisAlignment: MainAxisAlignment.spaceBetween,
                            children: <Widget>[
                              const Text('카트에서 동기화됨', style: TextStyle(fontWeight: FontWeight.w900)),
                              TextButton(
                                onPressed: () {
                                  ScaffoldMessenger.of(context).showSnackBar(
                                    const SnackBar(content: Text('레시피 목록을 새로고침합니다.')),
                                  );
                                },
                                child: const Text('새로고침'),
                              ),
                            ],
                          ),
                          const SizedBox(height: 8),

                          ...list.skip(1).map((r) {
                            return Padding(
                              padding: const EdgeInsets.only(bottom: 10),
                              child: SectionCard(
                                child: Row(
                                  children: <Widget>[
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: <Widget>[
                                          Text('${r.match_percent}% 매칭 · ${r.time_min}분', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900, fontSize: 12)),
                                          const SizedBox(height: 6),
                                          Text(r.title, style: const TextStyle(fontWeight: FontWeight.w900)),
                                          const SizedBox(height: 4),
                                          Text(r.subtitle, style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800, fontSize: 12)),
                                          const SizedBox(height: 10),
                                          OutlinedButton(
                                            onPressed: () => context.push(AppRoutes.recipe_detail, extra: <String, dynamic>{'recipe_id': r.recipe_id}),
                                            style: OutlinedButton.styleFrom(shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14))),
                                            child: const Text('상세 보기'),
                                          ),
                                        ],
                                      ),
                                    ),
                                    const SizedBox(width: 10),
                                    Container(
                                      width: 84,
                                      height: 84,
                                      decoration: BoxDecoration(
                                        color: AppColors.border.withOpacity(0.35),
                                        borderRadius: BorderRadius.circular(18),
                                      ),
                                      child: const Icon(Icons.image_outlined),
                                    ),
                                  ],
                                ),
                              ),
                            );
                          }).toList(),

                          const SizedBox(height: 18),
                          Center(
                            child: Text('스캔으로 매칭률을 업데이트할 수 있어요.', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800, fontSize: 12)),
                          ),
                          const SizedBox(height: 80),
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
      floatingActionButton: Container(
        padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
        decoration: BoxDecoration(
          color: Colors.black.withOpacity(0.85),
          borderRadius: BorderRadius.circular(999),
        ),
        child: const Row(
          mainAxisSize: MainAxisSize.min,
          children: <Widget>[
            Icon(Icons.shopping_cart_outlined, color: Colors.white),
            SizedBox(width: 10),
            Text('장바구니 보기 (12)', style: TextStyle(color: Colors.white, fontWeight: FontWeight.w900)),
          ],
        ),
      ),
    );
  }

  Widget _filter_chip({required String label, required bool is_selected, required VoidCallback on_tap}) {
    return InkWell(
      onTap: on_tap,
      borderRadius: BorderRadius.circular(999),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: is_selected ? AppColors.brand_primary : Colors.white,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: is_selected ? AppColors.brand_primary : AppColors.border),
        ),
        child: Text(
          label,
          style: TextStyle(color: is_selected ? Colors.white : AppColors.text_primary, fontWeight: FontWeight.w900, fontSize: 12),
        ),
      ),
    );
  }
}
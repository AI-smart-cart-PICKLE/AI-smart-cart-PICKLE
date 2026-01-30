import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_routes.dart';
import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../shared/widgets/section_card.dart';
import '../../../shared/widgets/primary_button.dart';
import '../../recipe/presentation/recipe_providers.dart';
import '../presentation/cart_providers.dart';

class ReviewAndCookScreen extends ConsumerWidget {
  const ReviewAndCookScreen({super.key});

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

    final cart_async = ref.watch(cart_summary_provider);
    final recipes_async = ref.watch(recipes_you_can_cook_now_provider);
    final theme_mode = ref.watch(theme_mode_provider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('검토 & 요리', style: TextStyle(fontWeight: FontWeight.w900)),
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
                  cart_async.when(
                    loading: () => const Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator()),
                    error: (e, _) => Text('장바구니를 불러오지 못했어요.\n$e'),
                    data: (cart) {
                      return SectionCard(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: <Widget>[
                            Row(
                              children: <Widget>[
                                const Expanded(child: Text('내 장바구니', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900))),
                                Container(
                                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                  decoration: BoxDecoration(
                                    color: AppColors.border.withOpacity(0.35),
                                    borderRadius: BorderRadius.circular(999),
                                  ),
                                  child: Text('${cart.items.length}개', style: const TextStyle(fontWeight: FontWeight.w900)),
                                ),
                              ],
                            ),
                            const SizedBox(height: 10),
                            ...cart.items.map((it) {
                              return Padding(
                                padding: const EdgeInsets.symmetric(vertical: 10),
                                child: Row(
                                  children: <Widget>[
                                    Container(
                                      width: 44,
                                      height: 44,
                                      decoration: BoxDecoration(
                                        color: AppColors.border.withOpacity(0.35),
                                        borderRadius: BorderRadius.circular(14),
                                      ),
                                      child: const Icon(Icons.image_outlined),
                                    ),
                                    const SizedBox(width: 12),
                                    Expanded(
                                      child: Column(
                                        crossAxisAlignment: CrossAxisAlignment.start,
                                        children: <Widget>[
                                          Text(it.name, style: const TextStyle(fontWeight: FontWeight.w900)),
                                          const SizedBox(height: 4),
                                          Text(it.option_label, style: TextStyle(color: AppColors.text_secondary, fontSize: 12, fontWeight: FontWeight.w800)),
                                        ],
                                      ),
                                    ),
                                    Text(_money(it.price), style: const TextStyle(fontWeight: FontWeight.w900)),
                                  ],
                                ),
                              );
                            }),
                            const Divider(),
                            Row(
                              children: <Widget>[
                                Text('소계', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900)),
                                const Spacer(),
                                Text(_money(cart.subtotal), style: const TextStyle(fontWeight: FontWeight.w900)),
                              ],
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                  const SizedBox(height: 14),
                  const Text('지금 만들 수 있는 레시피', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900)),
                  Text('현재 장바구니 기반 추천', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w700)),
                  const SizedBox(height: 10),
                  recipes_async.when(
                    loading: () => const Padding(padding: EdgeInsets.all(20), child: CircularProgressIndicator()),
                    error: (e, _) => Text('레시피를 불러오지 못했어요.\n$e'),
                    data: (list) {
                      if (list.isEmpty) {
                        return SectionCard(child: Text('추천할 레시피가 없어요.', style: TextStyle(color: AppColors.text_secondary)));
                      }
                      final r = list.first;
                      return SectionCard(
                        padding: const EdgeInsets.all(12),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: <Widget>[
                            Container(
                              height: 160,
                              decoration: BoxDecoration(
                                color: AppColors.border.withOpacity(0.35),
                                borderRadius: BorderRadius.circular(18),
                              ),
                              child: Stack(
                                children: <Widget>[
                                  const Center(child: Icon(Icons.image_outlined, size: 54)),
                                  Positioned(
                                    left: 12,
                                    top: 12,
                                    child: Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                                      decoration: BoxDecoration(
                                        color: AppColors.brand_primary.withOpacity(0.12),
                                        borderRadius: BorderRadius.circular(999),
                                      ),
                                      child: Text('${r.match_percent}% 매칭', style: const TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w900, fontSize: 12)),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 10),
                            Row(
                              children: <Widget>[
                                Expanded(child: Text(r.title, style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900))),
                                IconButton(
                                  onPressed: () {
                                    ScaffoldMessenger.of(context).showSnackBar(
                                      SnackBar(content: Text('${r.title} 레시피를 저장했습니다.')),
                                    );
                                  },
                                  icon: const Icon(Icons.bookmark_border),
                                ),
                              ],
                            ),
                            Row(
                              children: <Widget>[
                                Icon(Icons.schedule, size: 16, color: AppColors.text_secondary),
                                const SizedBox(width: 6),
                                Text('${r.time_min}분', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800)),
                                const SizedBox(width: 14),
                                Icon(Icons.emoji_events_outlined, size: 16, color: AppColors.text_secondary),
                                const SizedBox(width: 6),
                                Text(r.difficulty_label, style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800)),
                              ],
                            ),
                            const SizedBox(height: 10),
                            Row(
                              children: <Widget>[
                                const Icon(Icons.thumb_up_alt_outlined, color: AppColors.brand_primary, size: 18),
                                const SizedBox(width: 8),
                                Text('재료가 모두 있어요!', style: TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w900)),
                              ],
                            ),
                            const SizedBox(height: 12),
                            PrimaryButton(
                              label: '레시피 보기',
                              on_pressed: () => context.push(AppRoutes.recipe_detail, extra: <String, dynamic>{'recipe_id': r.recipe_id}),
                            ),
                          ],
                        ),
                      );
                    },
                  ),
                  const SizedBox(height: 90),
                ],
              ),
            ),
          ),
        ),
      ),
      bottomNavigationBar: SafeArea(
        child: Container(
          padding: const EdgeInsets.fromLTRB(16, 10, 16, 12),
          decoration: const BoxDecoration(color: Colors.white),
          child: Row(
            children: <Widget>[
              Expanded(
                child: cart_async.when(
                  loading: () => const Text('합계: -', style: TextStyle(fontWeight: FontWeight.w900)),
                  error: (_, __) => const Text('합계: -', style: TextStyle(fontWeight: FontWeight.w900)),
                  data: (c) => Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    mainAxisSize: MainAxisSize.min,
                    children: <Widget>[
                      Text('총액', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900, fontSize: 12)),
                      Text(_money(c.total), style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900)),
                    ],
                  ),
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: PrimaryButton(
                  label: '결제로 이동',
                  on_pressed: () => context.push(AppRoutes.kakao_pay_checkout),
                  leading: const Icon(Icons.arrow_forward),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
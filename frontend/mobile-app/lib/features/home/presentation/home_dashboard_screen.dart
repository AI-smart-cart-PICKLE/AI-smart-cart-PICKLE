import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../core/utils/responsive.dart';
import '../../../shared/widgets/section_card.dart';
import '../../../shared/widgets/bottom_nav.dart';

class HomeDashboardScreen extends ConsumerStatefulWidget {
  const HomeDashboardScreen({super.key});

  @override
  ConsumerState<HomeDashboardScreen> createState() => _HomeDashboardScreenState();
}

class _HomeDashboardScreenState extends ConsumerState<HomeDashboardScreen> {
  BottomTab current_tab = BottomTab.home;

  @override
  Widget build(BuildContext context) {
    final double max_w = Responsive.max_width(context);
    final theme_mode = ref.watch(theme_mode_provider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('피클', style: TextStyle(fontWeight: FontWeight.w900)),
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
                  // Cart Sync Banner (Clean version with Logo)
                  Container(
                    width: double.infinity,
                    padding: const EdgeInsets.all(24),
                    decoration: BoxDecoration(
                      color: AppColors.brand_primary.withOpacity(0.08),
                      borderRadius: BorderRadius.circular(24),
                      border: Border.all(color: AppColors.brand_primary.withOpacity(0.1)),
                    ),
                    child: Row(
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: <Widget>[
                              Text(
                                '쇼핑 시작!',
                                style: TextStyle(color: AppColors.brand_primary, fontSize: 24, fontWeight: FontWeight.w900),
                              ),
                              const SizedBox(height: 12),
                              ElevatedButton.icon(
                                onPressed: () => context.push(AppRoutes.qr_scanner),
                                icon: const Icon(Icons.qr_code_scanner, size: 18),
                                label: const Text('QR 스캔하기', style: TextStyle(fontWeight: FontWeight.w900)),
                                style: ElevatedButton.styleFrom(
                                  backgroundColor: AppColors.brand_primary,
                                  foregroundColor: Colors.white,
                                  padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                  elevation: 0,
                                ),
                              ),
                            ],
                          ),
                        ),
                        // Pickle Logo (Cart + Check)
                        Stack(
                          alignment: Alignment.center,
                          children: [
                            Icon(Icons.shopping_cart_outlined, size: 60, color: AppColors.brand_primary),
                            Transform.translate(
                              offset: const Offset(3, -8),
                              child: const Icon(Icons.check, size: 18, color: AppColors.brand_primary),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Spending Analysis
                  const Text('지출 분석', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900)),
                  const SizedBox(height: 12),
                  SectionCard(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: <Widget>[
                        const Text('이번 달 지출', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800)),
                        const SizedBox(height: 4),
                        const Text('₩428,500', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900)),
                        const SizedBox(height: 20),
                        // Bar Chart
                        SizedBox(
                          height: 150,
                          child: Row(
                            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: <Widget>[
                              _SpendingBar(label: '일', height: 40),
                              _SpendingBar(label: '월', height: 80),
                              _SpendingBar(label: '화', height: 60),
                              _SpendingBar(label: '수', height: 100),
                              _SpendingBar(label: '목', height: 30),
                              _SpendingBar(label: '금', height: 120, is_today: true),
                              _SpendingBar(label: '토', height: 50),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 24),

                  // Recommended Recipes
                  const Text('AI 추천 레시피', style: TextStyle(fontSize: 18, fontWeight: FontWeight.w900)),
                  const SizedBox(height: 12),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: <Widget>[
                        _RecipeImageCard(
                          title: '연어 스테이크',
                          imageUrl: 'https://images.unsplash.com/photo-1467003909585-2f8a72700288?w=400',
                          on_tap: () => context.push(AppRoutes.recipe_detail, extra: {'recipe_id': 'r1'}),
                        ),
                        _RecipeImageCard(
                          title: '아보카도 샐러드',
                          imageUrl: 'https://images.unsplash.com/photo-1512621776951-a57141f2eefd?w=400',
                          on_tap: () => context.push(AppRoutes.recipe_detail, extra: {'recipe_id': 'r2'}),
                        ),
                        _RecipeImageCard(
                          title: '토마토 파스타',
                          imageUrl: 'https://images.unsplash.com/photo-1546548970-71785318a17b?w=400',
                          on_tap: () => context.push(AppRoutes.recipe_detail, extra: {'recipe_id': 'r3'}),
                        ),
                      ],
                    ),
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
  }
}

class _SpendingBar extends StatelessWidget {
  final String label;
  final double height;
  final bool is_today;

  const _SpendingBar({required this.label, required this.height, this.is_today = false});

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisAlignment: MainAxisAlignment.end,
      children: <Widget>[
        Container(
          width: 24,
          height: height,
          decoration: BoxDecoration(
            color: is_today ? AppColors.gemini_purple : AppColors.border,
            borderRadius: BorderRadius.circular(6),
          ),
        ),
        const SizedBox(height: 8),
        Text(label, style: TextStyle(fontSize: 12, fontWeight: is_today ? FontWeight.w900 : FontWeight.w700)),
      ],
    );
  }
}

class _RecipeImageCard extends StatelessWidget {
  final String title;
  final String imageUrl;
  final VoidCallback on_tap;

  const _RecipeImageCard({required this.title, required this.imageUrl, required this.on_tap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: on_tap,
      borderRadius: BorderRadius.circular(18),
      child: Container(
        width: 160,
        margin: const EdgeInsets.only(right: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            ClipRRect(
              borderRadius: BorderRadius.circular(18),
              child: Image.network(
                imageUrl,
                height: 120,
                width: 160,
                fit: BoxFit.cover,
                errorBuilder: (context, error, stackTrace) => Container(
                  height: 120,
                  color: AppColors.border,
                  child: const Icon(Icons.restaurant, color: Colors.grey),
                ),
              ),
            ),
            const SizedBox(height: 8),
            Text(title, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 14)),
          ],
        ),
      ),
    );
  }
}

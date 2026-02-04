import 'dart:async'; // 타이머 추가
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../core/utils/responsive.dart';
import '../../../shared/widgets/section_card.dart';
import '../../../shared/widgets/bottom_nav.dart';
import '../../cart/presentation/cart_providers.dart'; // 카트 프로바이더 추가
import '../../account/presentation/account_providers.dart'; // 계정 프로바이더 추가

class HomeDashboardScreen extends ConsumerStatefulWidget {
  const HomeDashboardScreen({super.key});

  @override
  ConsumerState<HomeDashboardScreen> createState() => _HomeDashboardScreenState();
}

class _HomeDashboardScreenState extends ConsumerState<HomeDashboardScreen> {
  BottomTab current_tab = BottomTab.home;
  Timer? _polling_timer; // 상태 감지용 타이머

  @override
  void initState() {
    super.initState();
    // 2초마다 카트 상태를 체크하여 결제 요청이 있는지 확인합니다.
    _polling_timer = Timer.periodic(const Duration(seconds: 2), (timer) {
      _check_cart_status();
    });
  }

  @override
  void dispose() {
    _polling_timer?.cancel();
    super.dispose();
  }

  void _check_cart_status() async {
    // 1. 최신 장바구니 정보 가져오기
    ref.invalidate(cart_summary_provider); // 강제 갱신 유도
    final cart_async = await ref.read(cart_summary_provider.future);
    
    // 2. 상태가 결제 요청(CHECKOUT_REQUESTED)인지 확인
    if (cart_async.status == 'CHECKOUT_REQUESTED') {
      _polling_timer?.cancel(); // 이동 전 타이머 중지
      if (mounted) {
        // 정의된 카카오페이 결제 화면으로 이동
        context.push(AppRoutes.kakao_pay_checkout);
      }
    }
  }

  String _format_money(int amount) {
    final String s = amount.toString();
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
    final theme_mode = ref.watch(theme_mode_provider);
    
    // 지출 데이터 구독
    final summary_async = ref.watch(month_summary_provider);
    final days_async = ref.watch(month_days_provider);

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
                              Wrap(
                                spacing: 8,
                                runSpacing: 8,
                                children: [
                                  ElevatedButton.icon(
                                    onPressed: () => context.push(AppRoutes.qr_scanner),
                                    icon: const Icon(Icons.qr_code_scanner, size: 18),
                                    label: const Text('QR 스캔', style: TextStyle(fontWeight: FontWeight.w900)),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: AppColors.brand_primary,
                                      foregroundColor: Colors.white,
                                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                      elevation: 0,
                                    ),
                                  ),
                                  ElevatedButton.icon(
                                    onPressed: () => context.push(AppRoutes.review_and_cook),
                                    icon: const Icon(Icons.shopping_cart, size: 18),
                                    label: const Text('장바구니(Test)', style: TextStyle(fontWeight: FontWeight.w900)),
                                    style: ElevatedButton.styleFrom(
                                      backgroundColor: Colors.grey[700],
                                      foregroundColor: Colors.white,
                                      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
                                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
                                      elevation: 0,
                                    ),
                                  ),
                                ],
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
                        summary_async.when(
                          loading: () => const Text('₩-', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900)),
                          error: (e, _) => const Text('₩0', style: TextStyle(fontSize: 24, fontWeight: FontWeight.w900)),
                          data: (summary) => Text(_format_money(summary.total_amount), style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w900)),
                        ),
                        const SizedBox(height: 20),
                        // Bar Chart
                        SizedBox(
                          height: 150,
                          child: days_async.when(
                            loading: () => const Center(child: CircularProgressIndicator()),
                            error: (e, _) => const Center(child: Text('데이터 로드 실패')),
                            data: (days) {
                              // 오늘 기준 최근 7일 계산
                              final now = DateTime.now();
                              final List<Map<String, dynamic>> last7Days = [];
                              int maxAmount = 10000; // 최소 기준값 (0 나누기 방지)

                              for (int i = 6; i >= 0; i--) {
                                final date = now.subtract(Duration(days: i));
                                final dayAmount = days.where((d) => 
                                  d.date.year == date.year && 
                                  d.date.month == date.month && 
                                  d.date.day == date.day
                                ).fold(0, (sum, d) => sum + d.amount);
                                
                                if (dayAmount > maxAmount) maxAmount = dayAmount;
                                
                                final weekdayLabels = ['월', '화', '수', '목', '금', '토', '일'];
                                last7Days.add({
                                  'label': weekdayLabels[date.weekday - 1],
                                  'amount': dayAmount,
                                  'isToday': i == 0,
                                });
                              }

                              return Row(
                                mainAxisAlignment: MainAxisAlignment.spaceEvenly,
                                crossAxisAlignment: CrossAxisAlignment.end,
                                children: last7Days.map((d) {
                                  // 최대 높이 120px 기준으로 비율 계산
                                  double barHeight = (d['amount'] / maxAmount) * 120;
                                  if (barHeight < 5) barHeight = 5; // 최소 높이 보장

                                  return _SpendingBar(
                                    label: d['label'],
                                    height: barHeight,
                                    is_today: d['isToday'],
                                  );
                                }).toList(),
                              );
                            },
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

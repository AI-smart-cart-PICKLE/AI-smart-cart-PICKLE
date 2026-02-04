import 'dart:async';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../core/utils/responsive.dart';
import '../../../shared/widgets/section_card.dart';
import '../../../shared/widgets/bottom_nav.dart';
import '../../cart/presentation/cart_providers.dart';
import '../../account/presentation/account_providers.dart';

class HomeDashboardScreen extends ConsumerStatefulWidget {
  const HomeDashboardScreen({super.key});

  @override
  ConsumerState<HomeDashboardScreen> createState() => _HomeDashboardScreenState();
}

class _HomeDashboardScreenState extends ConsumerState<HomeDashboardScreen> {
  BottomTab current_tab = BottomTab.home;
  Timer? _polling_timer;

  @override
  void initState() {
    super.initState();
    // 화면 진입 시 즉시 장바구니 연동 상태를 강제로 새로고침합니다.
    Future.microtask(() => ref.invalidate(cart_summary_provider));

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
    try {
      // 2초마다 모든 데이터를 새로고침(invalidate)하지 않고, 
      // 현재 상태만 살짝 확인합니다. (불필요한 네트워크 부하 방지)
      final cart = await ref.read(cart_summary_provider.future);
      
      if (cart.cart_session_id != 0 && cart.status == 'CHECKOUT_REQUESTED') {
        _polling_timer?.cancel();
        if (mounted) {
          context.push(AppRoutes.kakao_pay_checkout);
        }
      }
    } catch (e) {
      // Ignore error during polling
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
    
    final summary_async = ref.watch(month_summary_provider);
    final days_async = ref.watch(month_days_provider);
    final cart_async = ref.watch(cart_summary_provider);

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
                  // Cart Sync Banner (Strict Detection)
                  cart_async.when(
                    data: (cart) {
                      // 세션 ID가 있고, 상태가 ACTIVE이며, 기기 코드가 있는 경우에만 '연동 완료'로 간주
                      final bool paired = cart.cart_session_id > 0 && 
                                         cart.status == 'ACTIVE' && 
                                         cart.device_code != null;
                      
                      return _CartStatusBanner(
                        is_paired: paired,
                        device_code: cart.device_code,
                      );
                    },
                    loading: () => const _CartStatusBanner(is_loading: true),
                    error: (e, _) => const _CartStatusBanner(is_paired: false),
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
                              final now = DateTime.now();
                              final List<Map<String, dynamic>> last7Days = [];
                              int maxAmount = 10000;

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
                                  double barHeight = (d['amount'] / maxAmount) * 120;
                                  if (barHeight < 5) barHeight = 5;

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

class _CartStatusBanner extends StatelessWidget {
  final bool is_paired;
  final bool is_loading;
  final String? device_code;

  const _CartStatusBanner({
    this.is_paired = false, 
    this.is_loading = false,
    this.device_code,
  });

  @override
  Widget build(BuildContext context) {
    if (is_loading) {
      return Container(
        height: 140,
        width: double.infinity,
        decoration: BoxDecoration(color: Colors.grey[100], borderRadius: BorderRadius.circular(24)),
        child: const Center(child: CircularProgressIndicator()),
      );
    }

    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: is_paired ? AppColors.brand_primary : AppColors.brand_primary.withOpacity(0.08),
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
                  is_paired ? '연동 완료' : '쇼핑 시작!',
                  style: TextStyle(
                    color: is_paired ? Colors.white : AppColors.brand_primary, 
                    fontSize: 24, 
                    fontWeight: FontWeight.w900
                  ),
                ),
                const SizedBox(height: 12),
                if (is_paired)
                  Text(
                    '카트 번호: ${device_code ?? "-"}',
                    style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700),
                  )
                else
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
              ],
            ),
          ),
          // Pickle Logo (Cart + Check) - 디자인 복구
          Stack(
            alignment: Alignment.center,
            children: [
              Icon(
                is_paired ? Icons.shopping_cart : Icons.shopping_cart_outlined, 
                size: 60, 
                color: is_paired ? Colors.white.withOpacity(0.8) : AppColors.brand_primary
              ),
              Transform.translate(
                offset: const Offset(3, -8),
                child: Icon(
                  Icons.check, 
                  size: 18, 
                  color: is_paired ? Colors.white : AppColors.brand_primary,
                  weight: 900,
                ),
              ),
            ],
          ),
        ],
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
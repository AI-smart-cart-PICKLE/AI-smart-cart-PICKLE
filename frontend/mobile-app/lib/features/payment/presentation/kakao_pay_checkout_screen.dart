import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_routes.dart';
import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../shared/widgets/section_card.dart';
import '../../cart/presentation/cart_providers.dart';
import '../data/payment_repository.dart';
import 'payment_providers.dart';

class KakaoPayCheckoutScreen extends ConsumerStatefulWidget {
  const KakaoPayCheckoutScreen({super.key});

  @override
  ConsumerState<KakaoPayCheckoutScreen> createState() => _KakaoPayCheckoutScreenState();
}

class _KakaoPayCheckoutScreenState extends ConsumerState<KakaoPayCheckoutScreen> {
  final TextEditingController points_controller = TextEditingController(text: '0');
  String? selected_coupon_id;
  bool is_paying = false;

  @override
  void dispose() {
    points_controller.dispose();
    super.dispose();
  }

  int _parse_int(String v) => int.tryParse(v.replaceAll(',', '').trim()) ?? 0;

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
    final cart_async = ref.watch(cart_summary_provider);
    final theme_mode = ref.watch(theme_mode_provider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('피클', style: TextStyle(fontWeight: FontWeight.w900)),
        leading: IconButton(onPressed: () => context.pop(), icon: const Icon(Icons.close)),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: max_w),
            child: SingleChildScrollView(
              padding: Responsive.page_padding(context),
              child: cart_async.when(
                loading: () => const Padding(padding: EdgeInsets.all(24), child: CircularProgressIndicator()),
                error: (e, _) => Text('장바구니 오류: $e'),
                data: (cart) {
                  final int amount = cart.total;
                  final int using_points = _parse_int(points_controller.text);
                  final int final_amount = (amount - using_points).clamp(0, amount);

                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      Center(
                        child: Column(
                          children: <Widget>[
                            Text('결제 금액', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900)),
                            const SizedBox(height: 8),
                            Text(_money(amount), style: const TextStyle(fontSize: 24, fontWeight: FontWeight.w900)),
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),

                      SectionCard(
                        child: Row(
                          children: <Widget>[
                            Container(
                              width: 44,
                              height: 44,
                              decoration: BoxDecoration(
                                color: const Color(0xFFFFE600).withOpacity(0.9),
                                borderRadius: BorderRadius.circular(14),
                              ),
                              child: const Icon(Icons.chat_bubble_outline, color: Colors.black),
                            ),
                            const SizedBox(width: 12),
                            const Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: <Widget>[
                                  Text('카카오페이', style: TextStyle(fontWeight: FontWeight.w900)),
                                  SizedBox(height: 4),
                                  Text('간편결제 & 포인트', style: TextStyle(fontSize: 12, color: AppColors.text_secondary, fontWeight: FontWeight.w800)),
                                ],
                              ),
                            ),
                            Container(
                              padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                              decoration: BoxDecoration(
                                color: AppColors.brand_primary.withOpacity(0.12),
                                borderRadius: BorderRadius.circular(999),
                              ),
                              child: const Text('연결됨', style: TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w900, fontSize: 12)),
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 12),
                      SectionCard(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: <Widget>[
                            Row(
                              children: <Widget>[
                                const Expanded(child: Text('피클 포인트', style: TextStyle(fontWeight: FontWeight.w900))),
                                Text('사용 가능 2,450P', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800, fontSize: 12)),
                              ],
                            ),
                            const SizedBox(height: 10),
                            TextField(
                              controller: points_controller,
                              keyboardType: TextInputType.number,
                              decoration: InputDecoration(
                                hintText: '0',
                                suffixText: 'P',
                                suffixIcon: IconButton(onPressed: () => points_controller.clear(), icon: const Icon(Icons.close)),
                              ),
                              onChanged: (_) => setState(() {}),
                            ),
                            const SizedBox(height: 10),
                            Wrap(
                              spacing: 8,
                              children: <Widget>[
                                _chip(label: '전부 사용', on_tap: () => setState(() => points_controller.text = '2450')),
                                _chip(label: '100P', on_tap: () => setState(() => points_controller.text = '100')),
                                _chip(label: '1,000P', on_tap: () => setState(() => points_controller.text = '1000')),
                              ],
                            ),
                            const SizedBox(height: 12),
                            InkWell(
                              onTap: () => setState(() => selected_coupon_id = 'cp_1'),
                              borderRadius: BorderRadius.circular(16),
                              child: Container(
                                padding: const EdgeInsets.all(14),
                                decoration: BoxDecoration(
                                  color: AppColors.border.withOpacity(0.25),
                                  borderRadius: BorderRadius.circular(16),
                                ),
                                child: Row(
                                  children: <Widget>[
                                    const Icon(Icons.confirmation_number_outlined, color: AppColors.brand_primary),
                                    const SizedBox(width: 10),
                                    const Expanded(child: Text('쿠폰 선택', style: TextStyle(fontWeight: FontWeight.w900))),
                                    Text(selected_coupon_id == null ? '선택 안 함' : '적용됨', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800)),
                                    const SizedBox(width: 6),
                                    const Icon(Icons.chevron_right),
                                  ],
                                ),
                              ),
                            ),
                            const SizedBox(height: 10),
                            Row(
                              children: <Widget>[
                                const Icon(Icons.lock_outline, size: 16, color: AppColors.text_secondary),
                                const SizedBox(width: 8),
                                Text('카카오페이로 안전하게 결제해요.', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800, fontSize: 12)),
                              ],
                            ),
                          ],
                        ),
                      ),

                      const SizedBox(height: 14),
                      Row(
                        children: <Widget>[
                          Checkbox(value: true, onChanged: (_) {}),
                          Expanded(
                            child: Text(
                              '결제 서비스 약관에 동의하며, 결제를 위해 제3자에게 개인정보 제공을 허용합니다.',
                              style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w700, fontSize: 12),
                            ),
                          ),
                        ],
                      ),

                      const SizedBox(height: 12),
                      SizedBox(
                        width: double.infinity,
                        child: ElevatedButton(
                          onPressed: is_paying
                              ? null
                              : () async {
                            setState(() => is_paying = true);
                            try {
                              final PaymentRepository repo = ref.read(payment_repository_provider);
                              final String receipt_id = await repo.start_kakao_pay_checkout(
                                amount: amount,
                                using_points: using_points,
                                coupon_id: selected_coupon_id,
                              );
                              if (!mounted) return;
                              context.go(AppRoutes.digital_receipt, extra: <String, dynamic>{'receipt_id': receipt_id});
                            } finally {
                              if (mounted) setState(() => is_paying = false);
                            }
                          },
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFFFFE600),
                            foregroundColor: Colors.black,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          ),
                          child: Text('결제 ${_money(final_amount)}', style: const TextStyle(fontWeight: FontWeight.w900)),
                        ),
                      ),
                    ],
                  );
                },
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _chip({required String label, required VoidCallback on_tap}) {
    return InkWell(
      onTap: on_tap,
      borderRadius: BorderRadius.circular(999),
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(999),
          border: Border.all(color: AppColors.border),
        ),
        child: Text(label, style: const TextStyle(fontWeight: FontWeight.w900, fontSize: 12)),
      ),
    );
  }
}
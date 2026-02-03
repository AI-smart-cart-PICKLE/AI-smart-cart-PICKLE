import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:webview_flutter/webview_flutter.dart';

import '../../../core/router/app_routes.dart';
import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../shared/widgets/section_card.dart';
import '../../cart/presentation/cart_providers.dart';
import '../repository/payment_repository.dart';
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

  // 카카오페이 결제 프로세스 시작
  Future<void> _startKakaoPay(int cart_session_id, int amount, int using_points) async {
    setState(() => is_paying = true);
    try {
      final PaymentRepository repo = ref.read(payment_repository_provider);
      
      // 1. 결제 준비 요청 (Ready)
      final readyResponse = await repo.prepare_kakao_pay(
        cart_session_id: cart_session_id,
        amount: amount,
        using_points: using_points,
        coupon_id: selected_coupon_id,
      );

      if (!mounted) return;

      // 2. 웹뷰 모달 띄우기 (PC URL 사용 - 앱 이탈 방지)
      // 모바일 환경에서도 PC URL을 띄우면 카카오톡 앱 전환 없이 웹에서 QR/번호 결제 가능
      final String? pgToken = await showDialog<String>(
        context: context,
        barrierDismissible: false, // 사용자 실수로 닫기 방지
        builder: (context) => _KakaoPayWebViewDialog(
          initialUrl: readyResponse.next_redirect_pc_url,
        ),
      );

      if (pgToken != null) {
        // 3. 결제 승인 요청 (Approve)
        final String receiptId = await repo.approve_kakao_pay(
          tid: readyResponse.tid,
          pg_token: pgToken,
        );

        if (!mounted) return;
        // 4. 영수증 화면으로 이동
        context.go(AppRoutes.digital_receipt, extra: <String, dynamic>{'receipt_id': receiptId});
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('결제가 취소되었습니다.')),
        );
      }

    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('결제 실패: ${e.toString().replaceAll("Exception: ", "")}')),
      );
    } finally {
      if (mounted) setState(() => is_paying = false);
    }
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
                              : () => _startKakaoPay(cart.cart_session_id, amount, using_points),
                          style: ElevatedButton.styleFrom(
                            backgroundColor: const Color(0xFFFFE600),
                            foregroundColor: Colors.black,
                            padding: const EdgeInsets.symmetric(vertical: 16),
                            shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                          ),
                          child: Text(is_paying ? '결제 진행 중...' : '결제 ${_money(final_amount)}', style: const TextStyle(fontWeight: FontWeight.w900)),
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

// 카카오페이 결제창을 띄우는 웹뷰 다이얼로그
class _KakaoPayWebViewDialog extends StatefulWidget {
  final String initialUrl;

  const _KakaoPayWebViewDialog({required this.initialUrl});

  @override
  State<_KakaoPayWebViewDialog> createState() => _KakaoPayWebViewDialogState();
}

class _KakaoPayWebViewDialogState extends State<_KakaoPayWebViewDialog> {
  late final WebViewController _controller;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setNavigationDelegate(
        NavigationDelegate(
          onNavigationRequest: (NavigationRequest request) {
            // 결제 성공 시 리다이렉트되는 URL 감지
            if (request.url.contains('/payments/success')) {
              // URL에서 pg_token 추출
              final Uri uri = Uri.parse(request.url);
              final String? pgToken = uri.queryParameters['pg_token'];
              
              if (pgToken != null) {
                Navigator.of(context).pop(pgToken); // 성공 토큰 반환
              } else {
                Navigator.of(context).pop(null); // 토큰 없음 (실패)
              }
              return NavigationDecision.prevent; // 웹뷰 이동 막기
            }
            
            // 결제 취소/실패 감지
            if (request.url.contains('/payments/cancel') || request.url.contains('/payments/fail')) {
              Navigator.of(context).pop(null);
              return NavigationDecision.prevent;
            }

            return NavigationDecision.navigate;
          },
        ),
      )
      ..loadRequest(Uri.parse(widget.initialUrl));
  }

  @override
  Widget build(BuildContext context) {
    return Dialog(
      insetPadding: const EdgeInsets.all(10),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      child: SizedBox(
        height: 600,
        child: Column(
          children: [
            // 닫기 버튼 헤더
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  const Padding(
                    padding: EdgeInsets.only(left: 12),
                    child: Text('카카오페이 결제', style: TextStyle(fontWeight: FontWeight.w900)),
                  ),
                  IconButton(
                    icon: const Icon(Icons.close),
                    onPressed: () => Navigator.of(context).pop(null),
                  ),
                ],
              ),
            ),
            const Divider(height: 1),
            // 웹뷰 영역
            Expanded(
              child: ClipRRect(
                borderRadius: const BorderRadius.only(
                  bottomLeft: Radius.circular(16),
                  bottomRight: Radius.circular(16),
                ),
                child: WebViewWidget(controller: _controller),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_routes.dart';
import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../shared/widgets/section_card.dart';
import '../../../shared/widgets/primary_button.dart';
import '../../payment/repository/payment_repository.dart';
import 'payment_providers.dart';

class AddNewCardScreen extends ConsumerStatefulWidget {
  const AddNewCardScreen({super.key});

  @override
  ConsumerState<AddNewCardScreen> createState() => _AddNewCardScreenState();
}

class _AddNewCardScreenState extends ConsumerState<AddNewCardScreen> {
  final TextEditingController card_number_controller = TextEditingController();
  final TextEditingController expires_controller = TextEditingController();
  final TextEditingController cvc_controller = TextEditingController();
  final TextEditingController holder_controller = TextEditingController();

  bool save_card = true;
  bool is_submitting = false;

  @override
  void dispose() {
    card_number_controller.dispose();
    expires_controller.dispose();
    cvc_controller.dispose();
    holder_controller.dispose();
    super.dispose();
  }

  Future<void> _submit() async {
    setState(() => is_submitting = true);
    try {
      final PaymentRepository repo = ref.read(payment_repository_provider);
      await repo.register_card(
        card_number: card_number_controller.text.trim(),
        expires_mm_yy: expires_controller.text.trim(),
        cvc: cvc_controller.text.trim(),
        cardholder_name: holder_controller.text.trim(),
        save_card: save_card,
      );

      ref.invalidate(payment_cards_provider);
      if (!mounted) return;
      context.pushReplacement(AppRoutes.card_registration_success);
    } catch (e) {
      if (!mounted) return;
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('카드 등록 실패: $e')));
    } finally {
      if (mounted) setState(() => is_submitting = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final double max_w = Responsive.max_width(context);
    final theme_mode = ref.watch(theme_mode_provider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('카드 추가', style: TextStyle(fontWeight: FontWeight.w900)),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: max_w),
            child: SingleChildScrollView(
              padding: Responsive.page_padding(context),
              child: Column(
                children: <Widget>[
                  SectionCard(
                    child: Column(
                      children: <Widget>[
                        Container(
                          width: double.infinity,
                          padding: const EdgeInsets.all(16),
                          decoration: BoxDecoration(
                            borderRadius: BorderRadius.circular(18),
                            border: Border.all(color: AppColors.border, style: BorderStyle.solid),
                            color: AppColors.brand_primary.withOpacity(0.06),
                          ),
                          child: Column(
                            children: <Widget>[
                              const Text('카드를 스캔해 자동 입력', style: TextStyle(fontWeight: FontWeight.w900)),
                              const SizedBox(height: 6),
                              Text(
                                '카드를 프레임 안에 맞추면 정보를 자동으로 인식해요.',
                                textAlign: TextAlign.center,
                                style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800, fontSize: 12),
                              ),
                              const SizedBox(height: 12),
                              OutlinedButton.icon(
                                onPressed: () {},
                                icon: const Icon(Icons.photo_camera_outlined),
                                label: const Text('카메라 열기'),
                                style: OutlinedButton.styleFrom(
                                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
                                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                                ),
                              ),
                            ],
                          ),
                        ),
                        const SizedBox(height: 10),
                        Row(
                          children: <Widget>[
                            const Icon(Icons.lock_outline, size: 16, color: AppColors.brand_primary),
                            const SizedBox(width: 8),
                            Expanded(
                              child: Text(
                                '결제 정보는 암호화되어 안전하게 처리돼요.',
                                style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800, fontSize: 12),
                              ),
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 12),

                  SectionCard(
                    child: Column(
                      children: <Widget>[
                        _field(label: '카드 번호', controller: card_number_controller, hint: '0000 0000 0000 0000', icon: Icons.credit_card),
                        const SizedBox(height: 12),
                        Row(
                          children: <Widget>[
                            Expanded(child: _field(label: '만료일', controller: expires_controller, hint: 'MM/YY', icon: Icons.calendar_month)),
                            const SizedBox(width: 12),
                            Expanded(child: _field(label: 'CVC', controller: cvc_controller, hint: '123', icon: Icons.shield_outlined)),
                          ],
                        ),
                        const SizedBox(height: 12),
                        _field(label: '카드 소유주', controller: holder_controller, hint: '카드에 적힌 이름', icon: Icons.person_outline),
                        const SizedBox(height: 10),
                        Row(
                          children: <Widget>[
                            const Icon(Icons.save_outlined, color: AppColors.brand_primary),
                            const SizedBox(width: 10),
                            const Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: <Widget>[
                                  Text('이 카드를 저장', style: TextStyle(fontWeight: FontWeight.w900)),
                                  SizedBox(height: 2),
                                  Text('다음 결제를 더 빠르게 진행해요', style: TextStyle(fontSize: 12, color: AppColors.text_secondary, fontWeight: FontWeight.w800)),
                                ],
                              ),
                            ),
                            Switch(
                              value: save_card,
                              onChanged: (v) => setState(() => save_card = v),
                              activeColor: AppColors.brand_primary,
                            ),
                          ],
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 14),
                  PrimaryButton(
                    label: is_submitting ? '등록 중...' : '카드 등록',
                    on_pressed: is_submitting ? null : _submit,
                    leading: const Icon(Icons.arrow_forward),
                  ),
                ],
              ),
            ),
          ),
        ),
      ),
    );
  }

  Widget _field({
    required String label,
    required TextEditingController controller,
    required String hint,
    required IconData icon,
  }) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(label, style: const TextStyle(fontWeight: FontWeight.w900)),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: Icon(icon),
          ),
        ),
      ],
    );
  }
}
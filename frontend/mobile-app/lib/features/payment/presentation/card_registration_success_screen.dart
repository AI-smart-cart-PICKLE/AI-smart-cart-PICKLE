import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../core/router/app_routes.dart';
import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/primary_button.dart';
import '../../../shared/widgets/section_card.dart';

class CardRegistrationSuccessScreen extends StatelessWidget {
  const CardRegistrationSuccessScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final double max_w = Responsive.max_width(context);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: max_w),
            child: Padding(
              padding: Responsive.page_padding(context),
              child: Column(
                children: <Widget>[
                  const SizedBox(height: 20),
                  Container(
                    width: 120,
                    height: 120,
                    decoration: BoxDecoration(
                      color: AppColors.brand_primary.withOpacity(0.12),
                      borderRadius: BorderRadius.circular(999),
                    ),
                    child: const Icon(Icons.check, color: AppColors.brand_primary, size: 54),
                  ),
                  const SizedBox(height: 18),
                  const Text('카드 등록이 완료되었습니다', style: TextStyle(fontSize: 22, fontWeight: FontWeight.w900)),
                  const SizedBox(height: 10),
                  Text(
                    '자동 결제를 위해 카드가 준비되었어요.',
                    style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w800),
                  ),
                  const SizedBox(height: 16),

                  SectionCard(
                    child: Row(
                      children: <Widget>[
                        Container(
                          width: 74,
                          height: 44,
                          decoration: BoxDecoration(
                            color: AppColors.border.withOpacity(0.35),
                            borderRadius: BorderRadius.circular(14),
                          ),
                          child: const Center(child: Text('VISA', style: TextStyle(fontWeight: FontWeight.w900, color: Colors.blue))),
                        ),
                        const SizedBox(width: 12),
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: <Widget>[
                              Text('**** 5678', style: TextStyle(fontWeight: FontWeight.w900)),
                              SizedBox(height: 4),
                              Text('만료 12/28', style: TextStyle(fontSize: 12, color: AppColors.text_secondary, fontWeight: FontWeight.w800)),
                            ],
                          ),
                        ),
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
                          decoration: BoxDecoration(
                            color: AppColors.brand_primary.withOpacity(0.12),
                            borderRadius: BorderRadius.circular(999),
                          ),
                          child: const Text('기본', style: TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w900, fontSize: 12)),
                        ),
                      ],
                    ),
                  ),

                  const Spacer(),
                  PrimaryButton(
                    label: '결제 수단으로 돌아가기',
                    on_pressed: () => context.go(AppRoutes.payment_methods),
                  ),
                  const SizedBox(height: 10),
                  OutlinedButton.icon(
                    onPressed: () => context.push(AppRoutes.add_new_card),
                    icon: const Icon(Icons.add),
                    label: const Text('카드 추가 등록'),
                    style: OutlinedButton.styleFrom(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
                    ),
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
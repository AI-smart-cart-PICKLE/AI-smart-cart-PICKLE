import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_routes.dart';
import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../shared/widgets/section_card.dart';
import '../../../shared/widgets/bottom_nav.dart';
import '../../payment/presentation/kakao_pay_settings_screen.dart';
import 'account_providers.dart';

class MyPageScreen extends ConsumerStatefulWidget {
  const MyPageScreen({super.key});

  @override
  ConsumerState<MyPageScreen> createState() => _MyPageScreenState();
}

class _MyPageScreenState extends ConsumerState<MyPageScreen> {
  BottomTab current_tab = BottomTab.my_page;

  @override
  Widget build(BuildContext context) {
    final double max_w = Responsive.max_width(context);
    final profile_async = ref.watch(my_profile_provider);
    final theme_mode = ref.watch(theme_mode_provider);
    final is_dark = theme_mode == ThemeMode.dark || 
                   (theme_mode == ThemeMode.system && MediaQuery.of(context).platformBrightness == Brightness.dark);
    final notifications_enabled = ref.watch(notification_enabled_provider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('마이 피클', style: TextStyle(fontWeight: FontWeight.w900)),
        actions: <Widget>[
          IconButton(
            onPressed: () {
              ref.read(theme_mode_provider.notifier).state =
                  is_dark ? ThemeMode.light : ThemeMode.dark;
            },
            icon: Icon(
              is_dark ? Icons.nightlight_round : Icons.nightlight_outlined,
              color: is_dark ? Colors.yellow : null,
            ),
          ),
          IconButton(
            onPressed: () {
              ref.read(notification_enabled_provider.notifier).state = !notifications_enabled;
            },
            icon: Icon(notifications_enabled ? Icons.notifications : Icons.notifications_off_outlined),
          ),
        ],
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: max_w),
            child: SingleChildScrollView(
              padding: Responsive.page_padding(context),
              child: profile_async.when(
                loading: () => const Center(child: Padding(padding: EdgeInsets.all(40), child: CircularProgressIndicator())),
                error: (e, _) => _ErrorView(message: '프로필을 불러오지 못했어요.\n$e'),
                data: (profile) {
                  return Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: <Widget>[
                      SectionCard(
                        child: Row(
                          children: <Widget>[
                            CircleAvatar(
                              radius: 26,
                              backgroundColor: AppColors.brand_primary.withOpacity(0.15),
                              child: const Icon(Icons.person, color: AppColors.brand_primary),
                            ),
                            const SizedBox(width: 12),
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: <Widget>[
                                  Row(
                                    children: <Widget>[
                                      Expanded(
                                        child: Text(
                                          profile.nickname,
                                          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w900),
                                          overflow: TextOverflow.ellipsis,
                                        ),
                                      ),
                                      PopupMenuButton<String>(
                                        icon: const Icon(Icons.settings_outlined),
                                        onSelected: (value) {
                                          if (value == 'nickname') context.push(AppRoutes.change_nickname);
                                          if (value == 'password') context.push(AppRoutes.change_password);
                                        },
                                        itemBuilder: (context) => [
                                          const PopupMenuItem(value: 'nickname', child: Text('닉네임 변경')),
                                          const PopupMenuItem(value: 'password', child: Text('비밀번호 변경')),
                                        ],
                                      ),
                                    ],
                                  ),
                                  Text(profile.email, style: TextStyle(color: AppColors.text_secondary)),
                                  const SizedBox(height: 6),
                                ],
                              ),
                            ),
                          ],
                        ),
                      ),
                      SectionCard(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: <Widget>[
                            Text('계정 설정', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900)),
                            const SizedBox(height: 10),
                            _MenuTile(
                              icon: Icons.person_outline,
                              title: '닉네임 변경',
                              on_tap: () => context.push(AppRoutes.change_nickname),
                            ),
                            _MenuTile(
                              icon: Icons.lock_outline,
                              title: '비밀번호 변경',
                              on_tap: () => context.push(AppRoutes.change_password),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),
                      SectionCard(
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: <Widget>[
                            Text('결제 관리', style: TextStyle(color: AppColors.text_secondary, fontWeight: FontWeight.w900)),
                            const SizedBox(height: 10),
                            _MenuTile(
                              icon: Icons.chat_bubble_outline,
                              title: '카카오페이 설정',
                              status_label: ref.watch(kakao_pay_connected_provider) ? '연결됨' : '미연결',
                              on_tap: () => context.push(AppRoutes.kakao_pay_settings),
                            ),
                          ],
                        ),
                      ),
                      const SizedBox(height: 14),
                      Center(
                        child: TextButton(
                          onPressed: () async {
                            await ref.read(account_repository_provider).logout();
                            
                            ref.invalidate(my_profile_provider);
                            ref.invalidate(month_summary_provider);
                            ref.invalidate(recent_transactions_provider);
                            ref.invalidate(top_items_provider);
                            ref.invalidate(category_breakdown_provider);
                            
                            if (context.mounted) {
                              context.go(AppRoutes.login);
                            }
                          },
                          child: const Text('로그아웃', style: TextStyle(color: Colors.red, fontWeight: FontWeight.w700)),
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

class _MenuTile extends StatelessWidget {
  final IconData icon;
  final String title;
  final String? status_label;
  final VoidCallback on_tap;

  const _MenuTile({
    required this.icon,
    required this.title,
    this.status_label,
    required this.on_tap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: on_tap,
      borderRadius: BorderRadius.circular(16),
      child: Padding(
        padding: const EdgeInsets.symmetric(vertical: 10),
        child: Row(
          children: <Widget>[
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: AppColors.border.withOpacity(0.35),
                borderRadius: BorderRadius.circular(14),
              ),
              child: Icon(icon, color: AppColors.brand_primary),
            ),
            const SizedBox(width: 12),
            Expanded(child: Text(title, style: const TextStyle(fontWeight: FontWeight.w900))),
            if (status_label != null)
              Padding(
                padding: const EdgeInsets.only(right: 8),
                child: Text(
                  status_label!,
                  style: TextStyle(
                    color: status_label == '연결됨' ? AppColors.brand_primary : AppColors.text_secondary,
                    fontWeight: FontWeight.w800,
                    fontSize: 12,
                  ),
                ),
              ),
            const Icon(Icons.chevron_right),
          ],
        ),
      ),
    );
  }
}

class _ErrorView extends StatelessWidget {
  final String message;

  const _ErrorView({required this.message});

  @override
  Widget build(BuildContext context) {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Text(message, textAlign: TextAlign.center),
      ),
    );
  }
}
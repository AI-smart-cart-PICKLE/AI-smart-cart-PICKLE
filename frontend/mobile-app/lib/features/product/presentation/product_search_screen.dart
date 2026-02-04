import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_routes.dart';
import '../../../core/utils/responsive.dart';
import '../../../core/theme/app_colors.dart';
import '../../../shared/widgets/section_card.dart';
import '../../../shared/widgets/bottom_nav.dart';

import 'product_providers.dart';

class ProductSearchScreen extends ConsumerStatefulWidget {
  const ProductSearchScreen({super.key});

  @override
  ConsumerState<ProductSearchScreen> createState() => _ProductSearchScreenState();
}

class _ProductSearchScreenState extends ConsumerState<ProductSearchScreen> {
  late final TextEditingController search_controller;
  BottomTab current_tab = BottomTab.search;

  String selected_category_key = 'on_sale'; 

  @override
  void initState() {
    super.initState();
    search_controller = TextEditingController();
  }

  @override
  void dispose() {
    search_controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final double max_w = Responsive.max_width(context);
    final search_results = ref.watch(search_results_provider);

    return Scaffold(
      appBar: AppBar(
        leading: IconButton(onPressed: () => context.go(AppRoutes.home), icon: const Icon(Icons.arrow_back)),
        title: const Text('상품 검색', style: TextStyle(fontWeight: FontWeight.w900)),
      ),
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: max_w),
            child: Padding(
              padding: Responsive.page_padding(context),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: <Widget>[
                  TextField(
                    controller: search_controller,
                    textInputAction: TextInputAction.search,
                    decoration: const InputDecoration(
                      hintText: "예: '유기농 아보카도' 또는 '우유'",
                      prefixIcon: Icon(Icons.search),
                    ),
                    onSubmitted: (value) {
                      ref.read(search_query_provider.notifier).state = value;
                    },
                  ),
                  const SizedBox(height: 12),
                  SingleChildScrollView(
                    scrollDirection: Axis.horizontal,
                    child: Row(
                      children: <Widget>[
                        _CategoryChip(
                          label: '할인',
                          is_selected: selected_category_key == 'on_sale',
                          on_tap: () => setState(() => selected_category_key = 'on_sale'),
                        ),
                        _CategoryChip(
                          label: '채소',
                          is_selected: selected_category_key == 'vegetables',
                          on_tap: () => setState(() => selected_category_key = 'vegetables'),
                        ),
                        _CategoryChip(
                          label: '유제품',
                          is_selected: selected_category_key == 'dairy',
                          on_tap: () => setState(() => selected_category_key = 'dairy'),
                        ),
                        _CategoryChip(
                          label: '간식',
                          is_selected: selected_category_key == 'snacks',
                          on_tap: () => setState(() => selected_category_key = 'snacks'),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),

                  Row(
                    children: <Widget>[
                      const Text('AI 추천', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900)),
                      const SizedBox(width: 8),
                      Text('최근 구매 기반', style: TextStyle(color: AppColors.brand_primary, fontSize: 12, fontWeight: FontWeight.w700)),
                    ],
                  ),
                  const SizedBox(height: 10),
                  SectionCard(
                    child: Row(
                      children: <Widget>[
                        Container(
                          width: 44,
                          height: 44,
                          decoration: BoxDecoration(
                            color: AppColors.brand_primary.withOpacity(0.12),
                            borderRadius: BorderRadius.circular(14),
                          ),
                          child: const Icon(Icons.eco_outlined, color: AppColors.brand_primary),
                        ),
                        const SizedBox(width: 12),
                        const Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: <Widget>[
                              Text('유기농 토마토(AI 추천)', style: TextStyle(fontWeight: FontWeight.w900)),
                              SizedBox(height: 4),
                              Text('자주 구매하시는 상품입니다.', maxLines: 1, overflow: TextOverflow.ellipsis),
                            ],
                          ),
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: 16),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: <Widget>[
                      const Text('검색 결과', style: TextStyle(fontSize: 16, fontWeight: FontWeight.w900)),
                      TextButton.icon(
                        onPressed: () {
                          ScaffoldMessenger.of(context).showSnackBar(
                            const SnackBar(content: Text('상세 필터 설정이 준비 중입니다.')),
                          );
                        },
                        icon: const Icon(Icons.tune, size: 18),
                        label: const Text('필터'),
                      ),
                    ],
                  ),
                  const SizedBox(height: 10),

                  Expanded(
                    child: search_results.when(
                      loading: () => const Center(child: CircularProgressIndicator()),
                      error: (err, stack) => Center(child: Text('검색 중 오류가 발생했습니다: $err')),
                      data: (items) {
                        if (items.isEmpty) {
                          return const Center(child: Text('검색 결과가 없습니다.'));
                        }
                        return LayoutBuilder(
                          builder: (BuildContext context, BoxConstraints c) {
                            final double w = c.maxWidth;
                            final int cross_axis_count = w >= 520 ? 3 : 2;
                            const double child_aspect_ratio = 0.85;

                            return GridView.builder(
                              itemCount: items.length,
                              gridDelegate: SliverGridDelegateWithFixedCrossAxisCount(
                                crossAxisCount: cross_axis_count,
                                crossAxisSpacing: 12,
                                mainAxisSpacing: 12,
                                childAspectRatio: child_aspect_ratio,
                              ),
                              itemBuilder: (BuildContext context, int i) {
                                final item = items[i];
                                return _ProductTile(
                                  name: item.name,
                                  price_label: '₩${item.price}',
                                  on_tap: () => context.push(AppRoutes.product_detail, extra: <String, dynamic>{'product_id': item.product_id}),
                                );
                              },
                            );
                          },
                        );
                      },
                    ),
                  ),
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

class _CategoryChip extends StatelessWidget {
  final String label;
  final bool is_selected;
  final VoidCallback on_tap;

  const _CategoryChip({required this.label, required this.is_selected, required this.on_tap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: 10),
      child: InkWell(
        onTap: on_tap,
        borderRadius: BorderRadius.circular(999),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 10),
          decoration: BoxDecoration(
            color: is_selected ? AppColors.brand_primary : Colors.white,
            borderRadius: BorderRadius.circular(999),
            border: Border.all(color: is_selected ? AppColors.brand_primary : AppColors.border),
          ),
          child: Text(
            label,
            style: TextStyle(
              color: is_selected ? Colors.white : AppColors.text_primary,
              fontWeight: FontWeight.w800,
              fontSize: 12,
            ),
          ),
        ),
      ),
    );
  }
}

class _ProductTile extends StatelessWidget {
  final String name;
  final String price_label;
  final VoidCallback on_tap;

  const _ProductTile({required this.name, required this.price_label, required this.on_tap});

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: on_tap,
      borderRadius: BorderRadius.circular(20),
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              Expanded(
                child: Container(
                  decoration: BoxDecoration(
                    color: AppColors.border.withOpacity(0.35),
                    borderRadius: BorderRadius.circular(16),
                  ),
                  child: const Center(child: Icon(Icons.image_outlined)),
                ),
              ),
              const SizedBox(height: 10),
              Text(name, style: const TextStyle(fontWeight: FontWeight.w900)),
              const SizedBox(height: 6),
              Text(price_label, style: const TextStyle(fontWeight: FontWeight.w900, color: AppColors.brand_primary)),
              // Removed + button from product tile
            ],
          ),
        ),
      ),
    );
  }
}
import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';

import '../../../core/theme/app_colors.dart';
import '../../../core/utils/responsive.dart';
import '../../../shared/widgets/section_card.dart';

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../../core/router/app_routes.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/utils/responsive.dart';
import '../../../shared/widgets/section_card.dart';
import 'product_providers.dart';

class ProductDetailScreen extends ConsumerWidget {
  final String product_id;

  const ProductDetailScreen({super.key, required this.product_id});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final double max_w = Responsive.max_width(context);
    final product_async = ref.watch(product_repository_provider).fetch_product_detail(product_id: product_id);

    return Scaffold(
      body: SafeArea(
        child: Center(
          child: ConstrainedBox(
            constraints: BoxConstraints(maxWidth: max_w),
            child: FutureBuilder(
              future: product_async,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) {
                  return Center(child: Text('상품 정보를 불러오지 못했습니다: ${snapshot.error}'));
                }
                final product = snapshot.data!;

                return CustomScrollView(
                  slivers: <Widget>[
                    SliverAppBar(
                      pinned: true,
                      leading: IconButton(onPressed: () => context.pop(), icon: const Icon(Icons.arrow_back)),
                      actions: <Widget>[
                        IconButton(
                          onPressed: () {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('상품 공유 기능이 준비 중입니다.')),
                            );
                          },
                          icon: const Icon(Icons.ios_share),
                        ),
                      ],
                      expandedHeight: 240,
                      flexibleSpace: FlexibleSpaceBar(
                        background: Container(
                          color: Colors.black.withOpacity(0.05),
                          child: const Center(child: Icon(Icons.image_outlined, size: 64)),
                        ),
                      ),
                    ),
                    SliverToBoxAdapter(
                      child: Padding(
                        padding: Responsive.page_padding(context),
                        child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: <Widget>[
                            SectionCard(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: <Widget>[
                                  Row(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: <Widget>[
                                      Expanded(
                                        child: Text(product.name, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w900)),
                                      ),
                                      Text('₩${product.price}',
                                          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w900, color: AppColors.brand_primary)),
                                    ],
                                  ),
                                  const SizedBox(height: 8),
                                  Wrap(
                                    spacing: 8,
                                    runSpacing: 8,
                                    children: <Widget>[
                                      _InfoPill(label: product.is_in_stock ? '재고 있음' : '품절', icon: Icons.check_circle_outline),
                                      _InfoPill(label: product.aisle_label, icon: Icons.location_on_outlined),
                                    ],
                                  ),
                                  const SizedBox(height: 14),
                                  const Text('매장 지도', style: TextStyle(fontWeight: FontWeight.w900)),
                                  const SizedBox(height: 8),
                                  Container(
                                    height: 170,
                                    decoration: BoxDecoration(
                                      color: AppColors.border.withOpacity(0.35),
                                      borderRadius: BorderRadius.circular(18),
                                    ),
                                    child: const Center(child: Text('지도 데이터(예: 존/통로 좌표)를 받아 렌더링')),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 14),
                            SectionCard(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: <Widget>[
                                  const Text('설명', style: TextStyle(fontWeight: FontWeight.w900)),
                                  const SizedBox(height: 8),
                                  Text(
                                    '이 상품은 ${product.name}입니다. ${product.aisle_label}에서 만나보실 수 있습니다.',
                                    style: TextStyle(color: AppColors.text_secondary),
                                  ),
                                  const SizedBox(height: 12),
                                  InkWell(
                                    onTap: () {
                                      ScaffoldMessenger.of(context).showSnackBar(
                                        const SnackBar(content: Text('영양 성분 정보를 준비 중입니다.')),
                                      );
                                    },
                                    borderRadius: BorderRadius.circular(16),
                                    child: Container(
                                      padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 14),
                                      decoration: BoxDecoration(
                                        borderRadius: BorderRadius.circular(16),
                                        color: AppColors.brand_primary.withOpacity(0.10),
                                      ),
                                      child: const Row(
                                        children: <Widget>[
                                          Icon(Icons.eco_outlined, color: AppColors.brand_primary),
                                          SizedBox(width: 10),
                                          Expanded(child: Text('영양 정보', style: TextStyle(fontWeight: FontWeight.w700))),
                                          Icon(Icons.keyboard_arrow_down),
                                        ],
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                            ),
                            const SizedBox(height: 14),
                            Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: <Widget>[
                                const Text('관련 상품', style: TextStyle(fontWeight: FontWeight.w900)),
                                TextButton(
                                  onPressed: () => context.push(AppRoutes.product_search),
                                  child: const Text('전체 보기'),
                                ),
                              ],
                            ),
                            const SizedBox(height: 8),
                            SizedBox(
                              height: 140,
                              child: FutureBuilder(
                                future: ref.watch(product_repository_provider).fetch_related_products(product_id: product_id),
                                builder: (context, snapshot) {
                                  if (!snapshot.hasData) return const SizedBox();
                                  final related = snapshot.data!;
                                  return ListView.separated(
                                    scrollDirection: Axis.horizontal,
                                    itemBuilder: (BuildContext context, int i) {
                                      final item = related[i];
                                      return _RelatedProductTile(
                                        title: item.name,
                                        price: '₩${item.price}',
                                        on_tap: () => context.push(AppRoutes.product_detail, extra: {'product_id': item.product_id}),
                                      );
                                    },
                                    separatorBuilder: (_, __) => const SizedBox(width: 12),
                                    itemCount: related.length,
                                  );
                                },
                              ),
                            ),
                          ],
                        ),
                      ),
                    ),
                  ],
                );
              },
            ),
          ),
        ),
      ),
    );
  }
}

class _InfoPill extends StatelessWidget {
  final String label;
  final IconData icon;

  const _InfoPill({required this.label, required this.icon});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 8),
      decoration: BoxDecoration(
        color: AppColors.border.withOpacity(0.35),
        borderRadius: BorderRadius.circular(999),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: <Widget>[
          Icon(icon, size: 16, color: AppColors.brand_primary),
          const SizedBox(width: 6),
          Text(label, style: const TextStyle(fontWeight: FontWeight.w800)),
        ],
      ),
    );
  }
}

class _RelatedProductTile extends StatelessWidget {

  final String title;

  final String price;

  final VoidCallback on_tap;



  const _RelatedProductTile({required this.title, required this.price, required this.on_tap});



  @override

  Widget build(BuildContext context) {

    return SizedBox(

      width: 140,

      child: InkWell(

        onTap: on_tap,

        borderRadius: BorderRadius.circular(20),

        child: Card(

          child: Padding(

            padding: const EdgeInsets.all(10),

            child: Column(

              crossAxisAlignment: CrossAxisAlignment.start,

              children: <Widget>[

                Expanded(

                  child: Container(

                    decoration: BoxDecoration(

                      color: AppColors.border.withOpacity(0.35),

                      borderRadius: BorderRadius.circular(14),

                    ),

                    child: const Center(child: Icon(Icons.image_outlined)),

                  ),

                ),

                const SizedBox(height: 8),

                Text(title, maxLines: 1, overflow: TextOverflow.ellipsis, style: const TextStyle(fontWeight: FontWeight.w900)),

                const SizedBox(height: 4),

                Text(price, style: TextStyle(color: AppColors.brand_primary, fontWeight: FontWeight.w800, fontSize: 12)),

              ],

            ),

          ),

        ),

      ),

    );

  }

}

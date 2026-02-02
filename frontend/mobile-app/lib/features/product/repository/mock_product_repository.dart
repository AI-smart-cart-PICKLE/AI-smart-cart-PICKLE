import 'dart:async';
import '../../../domain/models/product.dart';
import 'product_repository.dart';

class MockProductRepository implements ProductRepository {
  @override
  Future<List<Product>> fetch_recommendations() async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return <Product>[
      const Product(
        product_id: 'p1',
        name: '아보카도(해스)',
        price: 1990,
        unit_label: '개',
        image_url: '',
        is_in_stock: true,
        aisle_label: '통로 3',
      ),
    ];
  }

  @override
  Future<Product> fetch_product_detail({required String product_id}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return Product(
      product_id: product_id,
      name: '유기농 토마토',
      price: 4990,
      unit_label: 'kg',
      image_url: '',
      is_in_stock: true,
      aisle_label: '통로 4',
    );
  }

  @override
  Future<List<Product>> fetch_related_products({required String product_id}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return <Product>[
      const Product(product_id: 'p2', name: '오이', price: 1200, unit_label: '개', image_url: '', is_in_stock: true, aisle_label: '통로 4'),
      const Product(product_id: 'p3', name: '올리브 오일', price: 8500, unit_label: '병', image_url: '', is_in_stock: true, aisle_label: '통로 7'),
    ];
  }

  @override
  Future<List<Product>> search_products({required String query, required String category_key}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return <Product>[
      const Product(product_id: 'p10', name: '유기농 토마토', price: 4990, unit_label: 'kg', image_url: '', is_in_stock: true, aisle_label: '통로 4'),
      const Product(product_id: 'p11', name: '우유(1L)', price: 2490, unit_label: 'L', image_url: '', is_in_stock: true, aisle_label: '유제품 코너'),
    ];
  }
}

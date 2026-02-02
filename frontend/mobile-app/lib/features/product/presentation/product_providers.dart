import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../repository/mock_product_repository.dart';
import '../repository/product_repository.dart';
import '../../../domain/models/product.dart';

final product_repository_provider = Provider<ProductRepository>((ref) {
  return MockProductRepository();
});

final search_query_provider = StateProvider<String>((ref) => '');

final search_results_provider = FutureProvider<List<Product>>((ref) async {
  final query = ref.watch(search_query_provider);
  final repository = ref.watch(product_repository_provider);
  
  // For simplicity, we'll just pass 'on_sale' as default category if we don't have a category provider yet
  return repository.search_products(query: query, category_key: 'on_sale');
});

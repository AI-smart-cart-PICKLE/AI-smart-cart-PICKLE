import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../repository/http_product_repository.dart';
import '../repository/product_repository.dart';
import '../../../domain/models/product.dart';
import '../../../domain/models/product_category.dart';
import '../../../core/network/dio_provider.dart';

final product_repository_provider = Provider<ProductRepository>((ref) {
  final dioClient = ref.watch(dioClientProvider);
  return HttpProductRepository(dio: dioClient.dio);
});

final categories_provider = FutureProvider<List<ProductCategory>>((ref) async {
  final repository = ref.watch(product_repository_provider);
  return repository.fetch_categories();
});

final selected_category_id_provider = StateProvider<int?>((ref) => null);

final search_query_provider = StateProvider<String>((ref) => '');

final search_results_provider = FutureProvider<List<Product>>((ref) async {
  final query = ref.watch(search_query_provider);
  final categoryId = ref.watch(selected_category_id_provider);
  final repository = ref.watch(product_repository_provider);
  
  if (query.isEmpty) {
    return repository.fetch_products(category_id: categoryId);
  } else {
    return repository.search_products(query: query, category_id: categoryId);
  }
});

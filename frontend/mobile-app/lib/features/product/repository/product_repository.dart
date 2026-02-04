import '../../../domain/models/product.dart';

abstract class ProductRepository {
  Future<List<Product>> fetch_recommendations();
  Future<List<Product>> search_products({required String query, required String category_key});
  Future<Product> fetch_product_detail({required String product_id});
  Future<List<Product>> fetch_related_products({required String product_id});
}

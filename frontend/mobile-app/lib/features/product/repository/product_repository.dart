import '../../../domain/models/product.dart';
import '../../../domain/models/product_category.dart';

abstract class ProductRepository {
  Future<List<ProductCategory>> fetch_categories();
  Future<List<Product>> fetch_products({int? category_id});
  Future<List<Product>> fetch_recommendations();
  Future<List<Product>> search_products({required String query, int? category_id});
  Future<Product> fetch_product_detail({required String product_id});
  Future<List<Product>> fetch_related_products({required String product_id});
}

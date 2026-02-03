import 'package:dio/dio.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import '../../../domain/models/product.dart';
import 'product_repository.dart';

class HttpProductRepository implements ProductRepository {
  final Dio _dio;

  HttpProductRepository({Dio? dio}) : _dio = dio ?? Dio(BaseOptions(
    baseUrl: dotenv.env['API_URL'] ?? 'http://localhost:8000',
    connectTimeout: const Duration(seconds: 5),
    receiveTimeout: const Duration(seconds: 3),
  ));

  @override
  Future<List<Product>> fetch_recommendations() async {
    // TODO: 백엔드 추천 API 구현 시 연동 (현재는 빈 리스트 반환)
    return [];
  }

  @override
  Future<List<Product>> search_products({required String query, required String category_key}) async {
    try {
      final response = await _dio.get('/api/products/search', queryParameters: {
        'q': query,
        'category_key': category_key,
      });

      if (response.statusCode == 200) {
        final List<dynamic> data = response.data;
        return data.map((json) => Product.fromJson(json)).toList();
      }
      return [];
    } catch (e) {
      print('Error searching products: $e');
      // 에러 발생 시 빈 리스트 반환 (또는 예외 throw)
      return [];
    }
  }

  @override
  Future<Product> fetch_product_detail({required String product_id}) async {
    try {
      final response = await _dio.get('/api/products/$product_id');

      if (response.statusCode == 200) {
        return Product.fromJson(response.data);
      }
      throw Exception('Failed to load product detail');
    } catch (e) {
      print('Error fetching product detail: $e');
      throw e;
    }
  }

  @override
  Future<List<Product>> fetch_related_products({required String product_id}) async {
    // TODO: 백엔드 연동 (현재는 빈 리스트)
    return [];
  }
}

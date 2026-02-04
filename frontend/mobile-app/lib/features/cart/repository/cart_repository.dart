import '../../../domain/models/cart.dart';

abstract class CartRepository {
  Future<CartSummary> fetch_cart_summary();
  Future<Map<String, dynamic>> pair_cart_by_qr({required String device_code});
}

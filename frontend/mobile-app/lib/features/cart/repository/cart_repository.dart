import '../../../domain/models/cart.dart';

abstract class CartRepository {
  Future<CartSummary> fetch_cart_summary();
}

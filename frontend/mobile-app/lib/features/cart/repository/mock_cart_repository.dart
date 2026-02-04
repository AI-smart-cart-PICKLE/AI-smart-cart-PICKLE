import 'dart:async';
import '../../../domain/models/cart.dart';
import 'cart_repository.dart';

class MockCartRepository implements CartRepository {
  @override
  Future<CartSummary> fetch_cart_summary() async {
    await Future<void>.delayed(const Duration(milliseconds: 250));

    final List<CartItem> items = <CartItem>[
      const CartItem(product_id: 'p1', name: '로마 토마토', option_label: '1kg · 유기농', price: 2500),
      const CartItem(product_id: 'p2', name: '스파게티면 No.5', option_label: '500g · 바릴라', price: 1500),
      const CartItem(product_id: 'p3', name: '바질', option_label: '1묶음 · 국내산', price: 3000),
    ];

    final int subtotal = items.fold<int>(0, (p, c) => p + c.price);
    return CartSummary(cart_session_id: 0, items: items, subtotal: subtotal, total: subtotal);
  }
}

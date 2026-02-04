class CartItem {
  final String product_id;
  final String name;
  final String option_label; // 예: "1kg · 유기농"
  final int price;

  const CartItem({
    required this.product_id,
    required this.name,
    required this.option_label,
    required this.price,
  });

  factory CartItem.fromJson(Map<String, dynamic> json) {
    final int weight = json['weight'] ?? 0;
    return CartItem(
      product_id: (json['product_id'] ?? 0).toString(),
      name: json['name'] ?? '',
      option_label: weight > 0 ? '${weight}g' : '',
      price: json['price'] ?? 0,
    );
  }
}

class CartSummary {
  final int cart_session_id;
  final String status; // ACTIVE, CHECKOUT_REQUESTED 등
  final List<CartItem> items;
  final int subtotal;
  final int total;

  const CartSummary({
    required this.cart_session_id,
    required this.status,
    required this.items,
    required this.subtotal,
    required this.total,
  });
  
  // CartSummary는 Repository에서 조합해서 만들므로 fromJson은 선택 사항이나,
  // 백엔드에서 통으로 내려줄 경우를 대비해 추가 가능
}
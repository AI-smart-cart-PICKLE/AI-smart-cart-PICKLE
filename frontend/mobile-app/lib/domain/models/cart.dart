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
  final String status;
  final List<CartItem> items;
  final int subtotal;
  final int total;
  final String? device_code;

  const CartSummary({
    required this.cart_session_id,
    required this.status,
    required this.items,
    required this.subtotal,
    required this.total,
    this.device_code,
  });

  factory CartSummary.fromJson(Map<String, dynamic> json) {
    return CartSummary(
      cart_session_id: json['cart_session_id'] ?? 0,
      status: json['status'] ?? 'INACTIVE',
      items: [], // 실제 아이템 파싱은 Repository에서 수행 중
      subtotal: json['total_amount'] ?? 0,
      total: json['total_amount'] ?? 0,
      device_code: json['device_code'],
    );
  }
}
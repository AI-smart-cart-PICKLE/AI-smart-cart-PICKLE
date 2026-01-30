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
}

class CartSummary {
  final List<CartItem> items;
  final int subtotal;
  final int total;

  const CartSummary({
    required this.items,
    required this.subtotal,
    required this.total,
  });
}

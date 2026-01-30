class Product {
  final String product_id;
  final String name;
  final int price;
  final String unit_label; // 예: "kg", "개", "L"
  final String image_url;
  final bool is_in_stock;
  final String aisle_label; // 예: "Aisle 4" -> UI에서는 "통로 4"

  const Product({
    required this.product_id,
    required this.name,
    required this.price,
    required this.unit_label,
    required this.image_url,
    required this.is_in_stock,
    required this.aisle_label,
  });
}

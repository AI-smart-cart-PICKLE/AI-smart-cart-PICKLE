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

  factory Product.fromJson(Map<String, dynamic> json) {
    return Product(
      product_id: (json['product_id'] ?? 0).toString(),
      name: json['name'] ?? '',
      price: json['price'] ?? 0,
      unit_label: json['unit_weight_g'] != null ? '${json['unit_weight_g']}g' : '1개',
      image_url: json['image_url'] ?? '',
      is_in_stock: (json['stock_quantity'] ?? 0) > 0,
      // 백엔드에서 위치 정보를 주지 않을 경우 기본값 처리
      aisle_label: json['zone_code'] ?? '위치 정보 없음',
    );
  }
}
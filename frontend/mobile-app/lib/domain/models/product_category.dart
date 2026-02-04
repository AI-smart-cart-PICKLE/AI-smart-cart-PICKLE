class ProductCategory {
  final int category_id;
  final String name;
  final String? zone_code;

  const ProductCategory({
    required this.category_id,
    required this.name,
    this.zone_code,
  });

  factory ProductCategory.fromJson(Map<String, dynamic> json) {
    return ProductCategory(
      category_id: json['category_id'] ?? 0,
      name: json['name'] ?? '',
      zone_code: json['zone_code'],
    );
  }
}

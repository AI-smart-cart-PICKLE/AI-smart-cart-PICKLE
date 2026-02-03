import '../../../core/network/dio_client.dart';
import '../../../domain/models/cart.dart';
import 'cart_repository.dart';

class CartRepositoryImpl implements CartRepository {
  final DioClient _dioClient;

  CartRepositoryImpl(this._dioClient);

  @override
  Future<CartSummary> fetch_cart_summary() async {
    try {
      final response = await _dioClient.dio.get('/api/carts/items');
      
      // API 응답이 리스트라고 가정 (List<dynamic>)
      final List<dynamic> data = response.data;
      
      final List<CartItem> items = [];
      
      for (var itemJson in data) {
        // API 필드 매핑 (예상)
        // product_id, name, price, quantity, weight 등
        final String productId = itemJson['product_id'].toString();
        final String name = itemJson['name'] ?? '알 수 없는 상품';
        final int price = itemJson['price'] ?? 0;
        final int quantity = itemJson['quantity'] ?? 1;
        final int weight = itemJson['weight'] ?? 0;
        
        // option_label 구성 (예: "500g")
        final String optionLabel = weight > 0 ? '${weight}g' : '';

        // 수량만큼 CartItem 생성하여 리스트에 추가 (UI가 개별 아이템 표시 구조이므로)
        for (int i = 0; i < quantity; i++) {
          items.add(CartItem(
            product_id: productId,
            name: name,
            option_label: optionLabel,
            price: price,
          ));
        }
      }

      final int subtotal = items.fold<int>(0, (p, c) => p + c.price);
      // 현재는 할인 등이 없으므로 total = subtotal
      return CartSummary(items: items, subtotal: subtotal, total: subtotal);
      
    } catch (e) {
      throw Exception('장바구니 정보를 불러오는데 실패했습니다: $e');
    }
  }
}

import '../../../core/network/dio_client.dart';
import '../../../domain/models/cart.dart';
import 'cart_repository.dart';

class CartRepositoryImpl implements CartRepository {
  final DioClient _dioClient;

  CartRepositoryImpl(this._dioClient);

  @override
  Future<CartSummary> fetch_cart_summary() async {
    try {
      // 1. 내 현재 활성 세션 조회
      final response = await _dioClient.dio.get('carts/current');
      final data = response.data;
      
      final int cartSessionId = data['cart_session_id'];
      final String status = data['status'] ?? 'ACTIVE';
      final List<dynamic> itemsData = data['items'] ?? [];
      final List<CartItem> items = [];
      
      for (var itemJson in itemsData) {
        final product = itemJson['product'];
        final String productId = product['product_id'].toString();
        final String name = product['name'] ?? '알 수 없는 상품';
        final int price = product['price'] ?? 0;
        final int quantity = itemJson['quantity'] ?? 1;
        
        // CartItem Response 구조에 맞게 생성
        for (int i = 0; i < quantity; i++) {
          items.add(CartItem(
            product_id: productId,
            name: name,
            option_label: '', // 필요 시 추가 파싱
            price: price,
          ));
        }
      }

      final int subtotal = data['total_amount'] ?? 0;
      return CartSummary(
        cart_session_id: cartSessionId,
        status: status,
        items: items, 
        subtotal: subtotal, 
        total: subtotal
      );
      
    } catch (e) {
      print('fetch_cart_summary error: $e');
      throw Exception('장바구니 정보를 불러오는데 실패했습니다: $e');
    }
  }
}
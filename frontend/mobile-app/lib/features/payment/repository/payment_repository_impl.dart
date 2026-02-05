import '../../../core/network/dio_client.dart';
import '../../../domain/models/payment.dart';
import 'payment_repository.dart';

class PaymentRepositoryImpl implements PaymentRepository {
  final DioClient _dioClient;

  PaymentRepositoryImpl(this._dioClient);

  @override
  Future<List<PaymentHistoryItem>> fetch_payment_history({required DateTime month}) async {
    // TODO: Implement fetch_payment_history (백엔드 /api/ledger/recent 등 활용)
    return [];
  }

  @override
  Future<DigitalReceipt> fetch_receipt({required String receipt_id}) async {
    try {
      // receipt_id는 payment_id와 동일
      final response = await _dioClient.dio.get('payments/$receipt_id');
      final data = response.data;
      
      final List<ReceiptItem> items = [];
      if (data['items'] != null) {
        for (var item in data['items']) {
          final product = item['product'];
          items.add(ReceiptItem(
            name: product['name'],
            option_label: '', // 필요시 무게 정보 등 파싱
            qty: item['quantity'],
            price: item['unit_price'],
          ));
        }
      }
      
      final int totalAmount = data['total_amount'] ?? 0;
      
      // 세금 계산 (부가세 포함 기준: 합계 / 1.1)
      final int subtotal = (totalAmount / 1.1).round();
      final int tax = totalAmount - subtotal;
      
      // 날짜 데이터 파싱 (approved_at 선호, 없으면 created_at 등)
      final String? dateStr = data['approved_at'] ?? data['created_at'];
      final DateTime paidAt = dateStr != null ? DateTime.parse(dateStr) : DateTime.now();
      
      return DigitalReceipt(
        receipt_id: data['payment_id'].toString(),
        store_name: "피클 스토어", 
        paid_at: paidAt,
        ref_code: data['pg_tid'] ?? "REF-UNKNOWN",
        items: items,
        subtotal: subtotal,
        tax: tax,
        total_paid: totalAmount,
        paid_method_label: data['pg_provider'] == 'KAKAO_PAY' ? '카카오페이' : '카드',
      );
      
    } catch (e) {
      throw Exception('영수증 정보를 불러오는데 실패했습니다: $e');
    }
  }

  @override
  Future<List<CardModel>> fetch_cards() async {
    // TODO: Implement fetch_cards
    return [];
  }

  @override
  Future<List<WalletModel>> fetch_wallets() async {
    // TODO: Implement fetch_wallets
    return [];
  }

  @override
  Future<String> register_card({
    required String card_number,
    required String expires_mm_yy,
    required String cvc,
    required String cardholder_name,
    required bool save_card,
  }) async {
    // TODO: Implement register_card
    return "card_id_123";
  }

  @override
  Future<PaymentReadyResponse> prepare_kakao_pay({
    required int cart_session_id,
    required int amount,
    required int using_points,
    required String? coupon_id,
  }) async {
    try {
      final response = await _dioClient.dio.post(
        'payments/ready',
        data: {
          "cart_session_id": cart_session_id,
          "total_amount": amount,
          "method_id": null // 카카오페이는 method_id null
        },
      );

      return PaymentReadyResponse.fromJson(response.data);
    } catch (e) {
      throw Exception('카카오페이 결제 준비 실패: $e');
    }
  }

  @override
  Future<String> approve_kakao_pay({
    required String tid,
    required String pg_token,
  }) async {
    try {
      final response = await _dioClient.dio.post(
        'payments/approve',
        data: {
          "tid": tid,
          "pg_token": pg_token,
        },
      );
      
      // 결제 성공 시 Payment 객체 반환됨 (payment_id 포함)
      final int paymentId = response.data['payment_id'];
      return paymentId.toString();
    } catch (e) {
      throw Exception('카카오페이 결제 승인 실패: $e');
    }
  }
}
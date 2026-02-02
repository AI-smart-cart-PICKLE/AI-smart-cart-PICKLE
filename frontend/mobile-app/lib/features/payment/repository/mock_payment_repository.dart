import 'dart:async';
import '../../../domain/models/payment.dart';
import 'payment_repository.dart';

class MockPaymentRepository implements PaymentRepository {
  @override
  Future<List<PaymentHistoryItem>> fetch_payment_history({required DateTime month}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return <PaymentHistoryItem>[
      PaymentHistoryItem(
        payment_id: 'pay_1',
        paid_at: DateTime(month.year, month.month, 24, 18, 42),
        merchant_name: '마트 결제',
        category_label: '식료품',
        amount: 84300,
        receipt_id: 'r_1',
      ),
      PaymentHistoryItem(
        payment_id: 'pay_2',
        paid_at: DateTime(month.year, month.month, 24, 8, 15),
        merchant_name: '카페',
        category_label: '외식',
        amount: 12500,
        receipt_id: 'r_2',
      ),
    ];
  }

  @override
  Future<DigitalReceipt> fetch_receipt({required String receipt_id}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return DigitalReceipt(
      receipt_id: receipt_id,
      store_name: '피클 스토어 #204',
      paid_at: DateTime(2023, 10, 24, 14, 30),
      ref_code: 'P882-9901',
      items: const <ReceiptItem>[
        ReceiptItem(name: '아보카도', option_label: '유기농', qty: 2, price: 4000),
        ReceiptItem(name: '오트밀 바리스타', option_label: '1L', qty: 1, price: 5500),
        ReceiptItem(name: '사워도우 빵', option_label: '베이커리', qty: 1, price: 6000),
      ],
      subtotal: 15500,
      tax: 1200,
      total_paid: 16700,
      paid_method_label: '마스터카드 (끝 8842)',
    );
  }

  @override
  Future<List<CardModel>> fetch_cards() async {
    await Future<void>.delayed(const Duration(milliseconds: 200));
    return const <CardModel>[
      CardModel(card_id: 'c1', brand_label: 'VISA', last4: '1234', expires_mm_yy: '12/25', is_primary: true),
      CardModel(card_id: 'c2', brand_label: 'Mastercard', last4: '5678', expires_mm_yy: '09/24', is_primary: false),
    ];
  }

  @override
  Future<List<WalletModel>> fetch_wallets() async {
    await Future<void>.delayed(const Duration(milliseconds: 200));
    return const <WalletModel>[
      WalletModel(wallet_key: 'kakao_pay', label: '카카오페이', status_label: '연결됨'),
      WalletModel(wallet_key: 'pickle_cash', label: '피클 캐시', status_label: '₩45,500 사용 가능'),
    ];
  }

  @override
  Future<String> register_card({
    required String card_number,
    required String expires_mm_yy,
    required String cvc,
    required String cardholder_name,
    required bool save_card,
  }) async {
    await Future<void>.delayed(const Duration(milliseconds: 400));
    return 'c_new';
  }

  @override
  Future<String> start_kakao_pay_checkout({
    required int amount,
    required int using_points,
    required String? coupon_id,
  }) async {
    await Future<void>.delayed(const Duration(milliseconds: 400));
    return 'r_1';
  }
}

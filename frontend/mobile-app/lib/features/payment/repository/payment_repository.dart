import '../../../domain/models/payment.dart';

abstract class PaymentRepository {
  Future<List<PaymentHistoryItem>> fetch_payment_history({required DateTime month});
  Future<DigitalReceipt> fetch_receipt({required String receipt_id});

  Future<List<CardModel>> fetch_cards();
  Future<List<WalletModel>> fetch_wallets();

  Future<String> register_card({
    required String card_number,
    required String expires_mm_yy,
    required String cvc,
    required String cardholder_name,
    required bool save_card,
  });

  Future<String> start_kakao_pay_checkout({
    required int amount,
    required int using_points,
    required String? coupon_id,
  });
}

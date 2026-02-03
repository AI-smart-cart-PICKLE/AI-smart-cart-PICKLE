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

  // Step 1: 결제 준비 (Returns PaymentReadyResponse with URL & TID)
  Future<PaymentReadyResponse> prepare_kakao_pay({
    required int cart_session_id,
    required int amount,
    required int using_points,
    required String? coupon_id,
  });

  // Step 2: 결제 승인 (Returns Receipt ID)
  Future<String> approve_kakao_pay({
    required String tid,
    required String pg_token,
  });
}

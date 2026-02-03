class PaymentHistoryItem {
  final String payment_id;
  final DateTime paid_at;
  final String merchant_name;
  final String category_label;
  final int amount;
  final String receipt_id;

  const PaymentHistoryItem({
    required this.payment_id,
    required this.paid_at,
    required this.merchant_name,
    required this.category_label,
    required this.amount,
    required this.receipt_id,
  });
}

class ReceiptItem {
  final String name;
  final String option_label;
  final int qty;
  final int price;

  const ReceiptItem({
    required this.name,
    required this.option_label,
    required this.qty,
    required this.price,
  });
}

class DigitalReceipt {
  final String receipt_id;
  final String store_name;
  final DateTime paid_at;
  final String ref_code;
  final List<ReceiptItem> items;
  final int subtotal;
  final int tax;
  final int total_paid;
  final String paid_method_label;

  const DigitalReceipt({
    required this.receipt_id,
    required this.store_name,
    required this.paid_at,
    required this.ref_code,
    required this.items,
    required this.subtotal,
    required this.tax,
    required this.total_paid,
    required this.paid_method_label,
  });
}

class CardModel {
  final String card_id;
  final String brand_label;
  final String last4;
  final String expires_mm_yy;
  final bool is_primary;

  const CardModel({
    required this.card_id,
    required this.brand_label,
    required this.last4,
    required this.expires_mm_yy,
    required this.is_primary,
  });
}

class WalletModel {
  final String wallet_key; // kakao_pay / pickle_cash 등
  final String label;
  final String status_label; // 연결됨 / 잔액 등

  const WalletModel({
    required this.wallet_key,
    required this.label,
    required this.status_label,
  });
}

class PaymentReadyResponse {
  final String tid;
  final String next_redirect_app_url;
  final String next_redirect_mobile_url;
  final String next_redirect_pc_url;

  const PaymentReadyResponse({
    required this.tid,
    required this.next_redirect_app_url,
    required this.next_redirect_mobile_url,
    required this.next_redirect_pc_url,
  });

  factory PaymentReadyResponse.fromJson(Map<String, dynamic> json) {
    return PaymentReadyResponse(
      tid: json['tid'] ?? '',
      next_redirect_app_url: json['next_redirect_app_url'] ?? '',
      next_redirect_mobile_url: json['next_redirect_mobile_url'] ?? '',
      next_redirect_pc_url: json['next_redirect_pc_url'] ?? '',
    );
  }
}

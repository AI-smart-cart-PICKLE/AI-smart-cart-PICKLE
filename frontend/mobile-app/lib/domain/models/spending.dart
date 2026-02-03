class SpendingSummary {
  final int total_amount;
  final int diff_percent; // 지난달 대비 +/-
  final String month_label;

  const SpendingSummary({
    required this.total_amount,
    required this.diff_percent,
    required this.month_label,
  });
}

class SpendingTransaction {
  final String transaction_id;
  final DateTime spent_at;
  final String merchant_name;
  final String category_label;
  final int amount;

  const SpendingTransaction({
    required this.transaction_id,
    required this.spent_at,
    required this.merchant_name,
    required this.category_label,
    required this.amount,
  });
}

class SpendingDay {
  final DateTime date;
  final int amount;

  const SpendingDay({
    required this.date,
    required this.amount,
  });
}

class TopItem {
  final String product_id;
  final String name;
  final String category_label;
  final int purchase_count;
  final int avg_price;

  const TopItem({
    required this.product_id,
    required this.name,
    required this.category_label,
    required this.purchase_count,
    required this.avg_price,
  });
}

class CategorySpend {
  final String category_key;
  final String category_label;
  final double amount;
  final double ratio; // 0~1

  const CategorySpend({
    required this.category_key,
    required this.category_label,
    required this.amount,
    required this.ratio,
  });
}

class MonthSummary {
  final num total_amount;
  final num compared_to_last_month_ratio; // 예: -0.12 ~ 0.35

  const MonthSummary({
    required this.total_amount,
    required this.compared_to_last_month_ratio,
  });
}

class DaySpend {
  final DateTime date;
  final num amount;

  const DaySpend({
    required this.date,
    required this.amount,
  });
}

class TransactionItem {
  final String merchant_name;
  final String category_label;
  final num amount;
  final DateTime spent_at;

  const TransactionItem({
    required this.merchant_name,
    required this.category_label,
    required this.amount,
    required this.spent_at,
  });
}
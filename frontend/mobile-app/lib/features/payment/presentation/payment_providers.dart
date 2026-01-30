import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/payment_repository.dart';
import '../data/mock_payment_repository.dart';
import '../../../domain/models/payment.dart';

final payment_repository_provider = Provider<PaymentRepository>((ref) {
  return MockPaymentRepository();
});

final payment_month_provider = StateProvider<DateTime>((ref) {
  final DateTime now = DateTime.now();
  return DateTime(now.year, now.month, 1);
});

final payment_history_provider = FutureProvider<List<PaymentHistoryItem>>((ref) async {
  final PaymentRepository repo = ref.read(payment_repository_provider);
  final DateTime month = ref.watch(payment_month_provider);
  return repo.fetch_payment_history(month: month);
});

final payment_cards_provider = FutureProvider<List<CardModel>>((ref) async {
  final PaymentRepository repo = ref.read(payment_repository_provider);
  return repo.fetch_cards();
});

final payment_wallets_provider = FutureProvider<List<WalletModel>>((ref) async {
  final PaymentRepository repo = ref.read(payment_repository_provider);
  return repo.fetch_wallets();
});

final receipt_provider = FutureProvider.family<DigitalReceipt, String>((ref, receipt_id) async {
  final PaymentRepository repo = ref.read(payment_repository_provider);
  return repo.fetch_receipt(receipt_id: receipt_id);
});

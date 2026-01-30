import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../data/cart_repository.dart';
import '../data/mock_cart_repository.dart';
import '../../../domain/models/cart.dart';

final cart_repository_provider = Provider<CartRepository>((ref) {
  return MockCartRepository();
});

final cart_summary_provider = FutureProvider<CartSummary>((ref) async {
  final CartRepository repo = ref.read(cart_repository_provider);
  return repo.fetch_cart_summary();
});

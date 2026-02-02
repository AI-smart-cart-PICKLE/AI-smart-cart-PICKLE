import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/dio_provider.dart';
import '../repository/cart_repository.dart';
import '../repository/cart_repository_impl.dart';
import '../../../domain/models/cart.dart';

final cart_repository_provider = Provider<CartRepository>((ref) {
  final dioClient = ref.watch(dioClientProvider);
  return CartRepositoryImpl(dioClient);
});

final cart_summary_provider = FutureProvider<CartSummary>((ref) async {
  final CartRepository repo = ref.read(cart_repository_provider);
  return repo.fetch_cart_summary();
});
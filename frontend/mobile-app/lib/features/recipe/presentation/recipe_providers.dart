import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/dio_provider.dart';
import '../../cart/presentation/cart_providers.dart';
import '../repository/recipe_repository.dart';
import '../repository/http_recipe_repository.dart';
import '../../../domain/models/recipe.dart';

final recipe_repository_provider = Provider<RecipeRepository>((ref) {
  final dioClient = ref.watch(dioClientProvider);
  return HttpRecipeRepository(dio: dioClient.dio);
});

final recipe_filter_provider = StateProvider<String>((ref) => 'top_matches');

final recipes_from_cart_provider = FutureProvider<List<RecipeCardModel>>((ref) async {
  final RecipeRepository repo = ref.read(recipe_repository_provider);
  final String filter_key = ref.watch(recipe_filter_provider);
  return repo.fetch_recipes_from_cart(filter_key: filter_key);
});

final recipes_you_can_cook_now_provider = FutureProvider<List<RecipeCardModel>>((ref) async {
  final RecipeRepository repo = ref.read(recipe_repository_provider);
  
  // 장바구니 상태 구독
  final cartAsync = ref.watch(cart_summary_provider);
  
  // 장바구니 데이터가 로드되었고 아이템이 있는 경우에만 추천 로직 실행
  return cartAsync.maybeWhen(
    data: (cart) {
      if (cart.items.isNotEmpty) {
        // 가장 최근에 담은(또는 첫번째) 상품 ID 사용
        // cart.items 순서가 중요하다면 정렬 필요. 여기서는 첫번째 아이템 사용
        try {
          final int productId = int.parse(cart.items.first.product_id);
          return repo.fetch_recipes_you_can_cook_now(basedOnProductId: productId);
        } catch (e) {
          return [];
        }
      }
      return [];
    },
    orElse: () => [],
  );
});

final recipe_detail_provider = FutureProvider.family<RecipeDetailModel, String>((ref, recipe_id) async {
  final RecipeRepository repo = ref.read(recipe_repository_provider);
  return repo.fetch_recipe_detail(recipe_id: recipe_id);
});
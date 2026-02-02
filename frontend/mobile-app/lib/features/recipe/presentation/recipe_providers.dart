import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../repository/recipe_repository.dart';
import '../repository/mock_recipe_repository.dart';
import '../../../domain/models/recipe.dart';

final recipe_repository_provider = Provider<RecipeRepository>((ref) {
  return MockRecipeRepository();
});

final recipe_filter_provider = StateProvider<String>((ref) => 'top_matches');

final recipes_from_cart_provider = FutureProvider<List<RecipeCardModel>>((ref) async {
  final RecipeRepository repo = ref.read(recipe_repository_provider);
  final String filter_key = ref.watch(recipe_filter_provider);
  return repo.fetch_recipes_from_cart(filter_key: filter_key);
});

final recipes_you_can_cook_now_provider = FutureProvider<List<RecipeCardModel>>((ref) async {
  final RecipeRepository repo = ref.read(recipe_repository_provider);
  return repo.fetch_recipes_you_can_cook_now();
});

final recipe_detail_provider = FutureProvider.family<RecipeDetailModel, String>((ref, recipe_id) async {
  final RecipeRepository repo = ref.read(recipe_repository_provider);
  return repo.fetch_recipe_detail(recipe_id: recipe_id);
});

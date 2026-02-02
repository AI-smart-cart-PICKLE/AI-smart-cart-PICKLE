import '../../../domain/models/recipe.dart';

abstract class RecipeRepository {
  Future<List<RecipeCardModel>> fetch_recipes_from_cart({required String filter_key});
  Future<List<RecipeCardModel>> fetch_recipes_you_can_cook_now();
  Future<RecipeDetailModel> fetch_recipe_detail({required String recipe_id});
}

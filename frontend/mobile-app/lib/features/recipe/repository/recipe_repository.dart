import '../../../domain/models/recipe.dart';

abstract class RecipeRepository {
  Future<List<RecipeCardModel>> fetch_recipes_from_cart({required String filter_key});
    Future<List<RecipeCardModel>> fetch_recipes_you_can_cook_now({int? basedOnProductId});
    
    // 새로 추가: 장바구니 전체 기반 추천
    Future<List<RecipeCardModel>> fetch_recipes_by_cart({required int cart_session_id});
  
    Future<RecipeDetailModel> fetch_recipe_detail({required String recipe_id});
}

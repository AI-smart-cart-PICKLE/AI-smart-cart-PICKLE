import 'package:dio/dio.dart';
import '../../../domain/models/recipe.dart';
import 'recipe_repository.dart';

class HttpRecipeRepository implements RecipeRepository {
  final Dio _dio;

  HttpRecipeRepository({required Dio dio}) : _dio = dio;

  @override
  Future<List<RecipeCardModel>> fetch_recipes_from_cart({required String filter_key}) async {
    // TODO: 필터 키에 따른 로직 (현재는 미구현, 빈 리스트)
    return [];
  }

  @override
  Future<List<RecipeCardModel>> fetch_recipes_you_can_cook_now({int? basedOnProductId}) async {
    if (basedOnProductId == null) {
      return [];
    }
    
    try {
      final response = await _dio.get('recommendations/by-product/$basedOnProductId');
      final List<dynamic> data = response.data;
      
      return data.map((item) {
        // missing_ingredients 처리
        // final missingList = (item['missing_ingredients'] as List? ?? []).map((m) => m['name'].toString()).toList();
        
        return RecipeCardModel(
          recipe_id: item['recipe_id'].toString(),
          title: item['title'],
          subtitle: item['description'] ?? '설명 없음',
          // image_url: item['image_url'] ?? '', // Model에 없음
          time_min: item['cooking_time_min'] ?? 30,
          difficulty_label: item['difficulty'] ?? '보통',
          match_percent: item['similarity_score'] != null 
              ? (item['similarity_score'] * 100).round() 
              : 80, // 기본값
          // missing_ingredients_count: missingList.length, // Model에 없음
          is_in_progress: false,
          is_smart_choice: false,
        );
      }).toList();
      
    } catch (e) {
      print('fetch_recipes_you_can_cook_now error: $e');
      return [];
    }
  }

  @override
  Future<RecipeDetailModel> fetch_recipe_detail({required String recipe_id}) async {
    try {
      final response = await _dio.get('recipes/$recipe_id');
      final data = response.data;
      
      return RecipeDetailModel(
        recipe_id: data['recipe_id'].toString(),
        title: data['title'],
        // description: data['description'] ?? '', // Model에 없음
        // image_url: data['image_url'] ?? '', // Model에 없음
        prep_time_min: data['cooking_time_min'] ?? 30,
        difficulty_label: data['difficulty'] ?? '보통',
        calories: data['calories'] ?? 500,
        ingredients: (data['ingredients'] as List? ?? []).map((i) {
          return RecipeIngredient(
            name: i['name'],
            status_label: i['quantity_info'] ?? '',
            is_available: false, // 상세 조회 시 소유 여부 확인 로직 필요 시 추가
          );
        }).toList(),
        steps: (data['instructions'] as String? ?? '').split('\n')
          .where((s) => s.trim().isNotEmpty)
          .toList()
          .asMap()
          .entries
          .map((entry) => RecipeStep(
            order: entry.key + 1,
            title: 'Step ${entry.key + 1}',
            description: entry.value,
          ))
          .toList(),
      );
    } catch (e) {
      throw Exception('Failed to load recipe detail: $e');
    }
  }
}

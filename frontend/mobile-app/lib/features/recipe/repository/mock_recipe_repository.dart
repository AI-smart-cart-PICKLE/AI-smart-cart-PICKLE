import 'dart:async';
import '../../../domain/models/recipe.dart';
import 'recipe_repository.dart';

class MockRecipeRepository implements RecipeRepository {
  @override
  Future<List<RecipeCardModel>> fetch_recipes_from_cart({required String filter_key}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return const <RecipeCardModel>[
      RecipeCardModel(
        recipe_id: 'rc_1',
        title: '크리미 페스토 파스타',
        subtitle: '카트 재료 5/6 보유',
        match_percent: 85,
        time_min: 15,
        difficulty_label: '쉬움',
        is_in_progress: true,
        is_smart_choice: false,
      ),
      RecipeCardModel(
        recipe_id: 'rc_2',
        title: '레몬 치킨',
        subtitle: '카트 기반 추천',
        match_percent: 92,
        time_min: 25,
        difficulty_label: '보통',
        is_in_progress: false,
        is_smart_choice: false,
      ),
      RecipeCardModel(
        recipe_id: 'rc_3',
        title: '그릭 샐러드 볼',
        subtitle: '부족: 페타치즈',
        match_percent: 74,
        time_min: 10,
        difficulty_label: '쉬움',
        is_in_progress: false,
        is_smart_choice: false,
      ),
    ];
  }

  @override
  Future<List<RecipeCardModel>> fetch_recipes_you_can_cook_now() async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return const <RecipeCardModel>[
      RecipeCardModel(
        recipe_id: 'r_now_1',
        title: '클래식 포모도로',
        subtitle: '현재 장바구니 기반',
        match_percent: 100,
        time_min: 15,
        difficulty_label: '쉬움',
        is_in_progress: false,
        is_smart_choice: true,
      ),
    ];
  }

  @override
  Future<RecipeDetailModel> fetch_recipe_detail({required String recipe_id}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return const RecipeDetailModel(
      recipe_id: 'r_detail_1',
      title: '프렌치 어니언 수프',
      prep_time_min: 45,
      difficulty_label: '보통',
      calories: 320,
      ingredients: <RecipeIngredient>[
        RecipeIngredient(name: '노란 양파 6개', status_label: '카트에 있음', is_available: true),
        RecipeIngredient(name: '소고기 육수(1L)', status_label: '카트에 있음', is_available: true),
        RecipeIngredient(name: '바게트', status_label: '없음', is_available: false),
      ],
      steps: <RecipeStep>[
        RecipeStep(order: 1, title: '양파 캐러멜화', description: '버터를 녹이고 양파를 넣어 중약불에서 천천히 볶아 갈색이 나도록 익혀요.'),
        RecipeStep(order: 2, title: '디글레이즈 & 끓이기', description: '팬 바닥을 긁어가며 육수를 넣고 20분 정도 끓여요.'),
        RecipeStep(order: 3, title: '마무리', description: '그릇에 담고 바게트와 치즈를 올려 오븐/그릴로 마무리해요.'),
      ],
    );
  }
}

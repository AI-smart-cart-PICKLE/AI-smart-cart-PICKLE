class RecipeCardModel {
  final String recipe_id;
  final String title;
  final String subtitle;
  final int match_percent;
  final int time_min;
  final String difficulty_label; // 쉬움/보통/어려움
  final bool is_in_progress;
  final bool is_smart_choice;

  const RecipeCardModel({
    required this.recipe_id,
    required this.title,
    required this.subtitle,
    required this.match_percent,
    required this.time_min,
    required this.difficulty_label,
    required this.is_in_progress,
    required this.is_smart_choice,
  });

  factory RecipeCardModel.fromJson(Map<String, dynamic> json) {
    return RecipeCardModel(
      recipe_id: (json['recipe_id'] ?? 0).toString(),
      title: json['title'] ?? '',
      subtitle: json['description'] ?? '',
      // 백엔드에서 아직 계산 로직이 없다면 기본값
      match_percent: json['match_percent'] ?? 0,
      time_min: 30, // 임시 기본값 (DB에 cooking_time 컬럼 없음)
      difficulty_label: '보통', // 임시 기본값
      is_in_progress: false,
      is_smart_choice: false,
    );
  }
}

class RecipeIngredient {
  final String name;
  final String status_label; // "카트에 있음" / "없음"
  final bool is_available;

  const RecipeIngredient({
    required this.name,
    required this.status_label,
    required this.is_available,
  });
  
  // RecipeIngredient는 DB 테이블이 복합적이므로 별도 처리 필요하지만
  // 우선 기본 매핑만 추가
  factory RecipeIngredient.fromJson(Map<String, dynamic> json) {
    return RecipeIngredient(
      name: json['product_name'] ?? json['name'] ?? '',
      status_label: '확인 필요',
      is_available: false,
    );
  }
}

class RecipeStep {
  final int order;
  final String title;
  final String description;

  const RecipeStep({
    required this.order,
    required this.title,
    required this.description,
  });

  factory RecipeStep.fromJson(Map<String, dynamic> json) {
    return RecipeStep(
      order: json['order'] ?? 1,
      title: json['title'] ?? '',
      description: json['description'] ?? '',
    );
  }
}

class RecipeDetailModel {
  final String recipe_id;
  final String title;
  final int prep_time_min;
  final String difficulty_label;
  final int calories;
  final List<RecipeIngredient> ingredients;
  final List<RecipeStep> steps;

  const RecipeDetailModel({
    required this.recipe_id,
    required this.title,
    required this.prep_time_min,
    required this.difficulty_label,
    required this.calories,
    required this.ingredients,
    required this.steps,
  });

  factory RecipeDetailModel.fromJson(Map<String, dynamic> json) {
    return RecipeDetailModel(
      recipe_id: (json['recipe_id'] ?? 0).toString(),
      title: json['title'] ?? '',
      prep_time_min: 30, // 기본값
      difficulty_label: '보통', // 기본값
      calories: 500, // 기본값
      ingredients: [], // 별도 로딩 필요
      steps: [], // 별도 로딩 필요
    );
  }
}
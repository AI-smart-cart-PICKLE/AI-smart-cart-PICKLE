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
}

class AppRoutes {
  static const String splash = '/';
  static const String login = '/login';
  static const String signup = '/signup';
  static const String oauth_webview = '/oauth-webview'; // 추가
  static const String home = '/home';
  static const String product_search = '/product/search';
  static const String product_detail = '/product/detail';

  static const String my_page = '/account/my';
  static const String spending_overview = '/account/spending';
  static const String top_items = '/account/top-items';
  static const String spending_breakdown = '/account/spending-breakdown';
  static const String change_nickname = '/account/change-nickname';
  static const String change_password = '/account/change-password';

  static const String qr_scanner = '/cart/qr-scanner';
  static const String review_and_cook = '/cart/review-and-cook';
  static const String my_recipes = '/cart/my-recipes';
  static const String recipe_detail = '/recipe/detail';

  static const String payment_history = '/payment/history';
  static const String payment_methods = '/payment/methods';
  static const String add_new_card = '/payment/add-card';
  static const String card_registration_success = '/payment/card-success';
  static const String kakao_pay_checkout = '/payment/kakao-checkout';
  static const String kakao_pay_settings = '/payment/kakao-settings';
  static const String digital_receipt = '/payment/receipt';
}

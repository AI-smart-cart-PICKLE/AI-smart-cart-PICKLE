import 'package:go_router/go_router.dart';
import 'app_routes.dart';

import '../../features/auth/presentation/splash_screen.dart';
import '../../features/auth/presentation/login_screen.dart';
import '../../features/auth/presentation/signup_screen.dart';
import '../../features/home/presentation/home_dashboard_screen.dart';
import '../../features/product/presentation/product_search_screen.dart';
import '../../features/product/presentation/product_detail_screen.dart';
import '../../features/account/presentation/my_page_screen.dart';
import '../../features/account/presentation/spending_overview_screen.dart';
import '../../features/account/presentation/top_items_screen.dart';
import '../../features/account/presentation/spending_breakdown_screen.dart';
import '../../features/account/presentation/change_nickname_screen.dart';
import '../../features/account/presentation/change_password_screen.dart';

import '../../features/cart/presentation/qr_scanner_screen.dart';
import '../../features/cart/presentation/review_and_cook_screen.dart';
import '../../features/cart/presentation/my_recipes_screen.dart';
import '../../features/recipe/presentation/recipe_detail_screen.dart';

import '../../features/payment/presentation/payment_history_screen.dart';
import '../../features/payment/presentation/payment_methods_screen.dart';
import '../../features/payment/presentation/add_new_card_screen.dart';
import '../../features/payment/presentation/card_registration_success_screen.dart';
import '../../features/payment/presentation/kakao_pay_checkout_screen.dart';
import '../../features/payment/presentation/kakao_pay_settings_screen.dart';
import '../../features/payment/presentation/digital_receipt_screen.dart';

class AppRouter {
  static final GoRouter router = GoRouter(
    initialLocation: AppRoutes.login,
    routes: <RouteBase>[
      GoRoute(path: AppRoutes.splash, builder: (c, s) => const SplashScreen()),
      GoRoute(path: AppRoutes.login, builder: (c, s) => const LoginScreen()),
      GoRoute(path: AppRoutes.signup, builder: (c, s) => const SignupScreen()),
      GoRoute(path: AppRoutes.home, builder: (c, s) => const HomeDashboardScreen()),

      GoRoute(path: AppRoutes.product_search, builder: (c, s) => const ProductSearchScreen()),
      GoRoute(
        path: AppRoutes.product_detail,
        builder: (c, s) {
          final String product_id = (s.extra as Map<String, dynamic>?)?['product_id']?.toString() ?? '';
          return ProductDetailScreen(product_id: product_id);
        },
      ),

      GoRoute(path: AppRoutes.my_page, builder: (c, s) => const MyPageScreen()),
      GoRoute(path: AppRoutes.spending_overview, builder: (c, s) => const SpendingOverviewScreen()),
      GoRoute(path: AppRoutes.top_items, builder: (c, s) => const TopItemsScreen()),
      GoRoute(path: AppRoutes.spending_breakdown, builder: (c, s) => const SpendingBreakdownScreen()),
      GoRoute(path: AppRoutes.change_nickname, builder: (c, s) => const ChangeNicknameScreen()),
      GoRoute(path: AppRoutes.change_password, builder: (c, s) => const ChangePasswordScreen()),

      GoRoute(path: AppRoutes.qr_scanner, builder: (c, s) => const QrScannerScreen()),
      GoRoute(path: AppRoutes.review_and_cook, builder: (c, s) => const ReviewAndCookScreen()),
      GoRoute(path: AppRoutes.my_recipes, builder: (c, s) => const MyRecipesScreen()),
      GoRoute(
        path: AppRoutes.recipe_detail,
        builder: (c, s) {
          final String recipe_id = (s.extra as Map<String, dynamic>?)?['recipe_id']?.toString() ?? '';
          return RecipeDetailScreen(recipe_id: recipe_id);
        },
      ),

      GoRoute(path: AppRoutes.payment_history, builder: (c, s) => const PaymentHistoryScreen()),
      GoRoute(path: AppRoutes.payment_methods, builder: (c, s) => const PaymentMethodsScreen()),
      GoRoute(path: AppRoutes.add_new_card, builder: (c, s) => const AddNewCardScreen()),
      GoRoute(path: AppRoutes.card_registration_success, builder: (c, s) => const CardRegistrationSuccessScreen()),
      GoRoute(path: AppRoutes.kakao_pay_checkout, builder: (c, s) => const KakaoPayCheckoutScreen()),
      GoRoute(path: AppRoutes.kakao_pay_settings, builder: (c, s) => const KakaoPaySettingsScreen()),
      GoRoute(
        path: AppRoutes.digital_receipt,
        builder: (c, s) {
          final String receipt_id = (s.extra as Map<String, dynamic>?)?['receipt_id']?.toString() ?? '';
          return DigitalReceiptScreen(receipt_id: receipt_id);
        },
      ),
    ],
  );
}

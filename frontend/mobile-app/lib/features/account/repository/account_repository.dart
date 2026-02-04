import '../../../domain/models/user_profile.dart';
import '../../../domain/models/spending.dart';

abstract class AccountRepository {
  Future<UserProfile> fetch_my_profile();
  Future<void> update_nickname({required String new_nickname});

  Future<SpendingSummary> fetch_month_summary({required DateTime month});
  Future<List<SpendingDay>> fetch_month_days({required DateTime month});
  Future<List<SpendingTransaction>> fetch_recent_transactions({required DateTime month});

  Future<List<TopItem>> fetch_top_items({required DateTime month});
  Future<List<CategorySpend>> fetch_category_breakdown({required DateTime month});

  Future<void> change_password({
    required String current_password,
    required String new_password,
  });
}

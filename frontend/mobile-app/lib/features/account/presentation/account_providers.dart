import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/network/dio_provider.dart';
import '../repository/account_repository.dart';
import '../repository/http_account_repository.dart';
import '../../../domain/models/user_profile.dart';
import '../../../domain/models/spending.dart';

final Provider<AccountRepository> account_repository_provider =
Provider<AccountRepository>((ProviderRef<AccountRepository> ref) {
  final dioClient = ref.watch(dioClientProvider);
  return HttpAccountRepository(dio: dioClient.dio);
});

final FutureProvider<UserProfile> my_profile_provider =
FutureProvider<UserProfile>(
      (FutureProviderRef<UserProfile> ref) async {
    final AccountRepository repo = ref.read(account_repository_provider);
    return repo.fetch_my_profile();
  },
);

final StateProvider<DateTime> selected_month_provider =
StateProvider<DateTime>((StateProviderRef<DateTime> ref) {
  final DateTime now = DateTime.now();
  return DateTime(now.year, now.month, 1);
});

final FutureProvider<SpendingSummary> month_summary_provider =
FutureProvider<SpendingSummary>(
      (FutureProviderRef<SpendingSummary> ref) async {
    final AccountRepository repo = ref.read(account_repository_provider);
    final DateTime month = ref.watch(selected_month_provider);
    return repo.fetch_month_summary(month: month);
  },
);

// 홈 대시보드 전용: 항상 현재 달의 지출 요약 정보를 제공
final FutureProvider<SpendingSummary> current_month_summary_provider =
FutureProvider<SpendingSummary>(
      (FutureProviderRef<SpendingSummary> ref) async {
    final AccountRepository repo = ref.read(account_repository_provider);
    final DateTime now = DateTime.now();
    return repo.fetch_month_summary(month: DateTime(now.year, now.month, 1));
  },
);

final FutureProvider<List<SpendingDay>> month_days_provider =
FutureProvider<List<SpendingDay>>(
      (FutureProviderRef<List<SpendingDay>> ref) async {
    final AccountRepository repo = ref.read(account_repository_provider);
    final DateTime month = ref.watch(selected_month_provider);
    return repo.fetch_month_days(month: month);
  },
);

// 홈 대시보드 전용: 항상 현재 달의 일별 지출 정보를 제공
final FutureProvider<List<SpendingDay>> current_month_days_provider =
FutureProvider<List<SpendingDay>>(
      (FutureProviderRef<List<SpendingDay>> ref) async {
    final AccountRepository repo = ref.read(account_repository_provider);
    final DateTime now = DateTime.now();
    return repo.fetch_month_days(month: DateTime(now.year, now.month, 1));
  },
);

final FutureProvider<List<SpendingTransaction>> recent_transactions_provider =
FutureProvider<List<SpendingTransaction>>(
      (FutureProviderRef<List<SpendingTransaction>> ref) async {
    final AccountRepository repo = ref.read(account_repository_provider);
    final DateTime month = ref.watch(selected_month_provider);
    return repo.fetch_recent_transactions(month: month);
  },
);

final FutureProvider<List<TopItem>> top_items_provider =
FutureProvider<List<TopItem>>(
      (FutureProviderRef<List<TopItem>> ref) async {
    final AccountRepository repo = ref.read(account_repository_provider);
    final DateTime month = ref.watch(selected_month_provider);
    return repo.fetch_top_items(month: month);
  },
);

final FutureProvider<List<CategorySpend>> category_breakdown_provider =
FutureProvider<List<CategorySpend>>(
      (FutureProviderRef<List<CategorySpend>> ref) async {
    final AccountRepository repo = ref.read(account_repository_provider);
    final DateTime month = ref.watch(selected_month_provider);
    return repo.fetch_category_breakdown(month: month);
  },
);

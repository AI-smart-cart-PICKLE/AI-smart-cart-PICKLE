import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../repository/account_repository.dart';
import '../repository/mock_account_repository.dart';
import '../../../domain/models/user_profile.dart';
import '../../../domain/models/spending.dart';

final Provider<AccountRepository> account_repository_provider =
Provider<AccountRepository>(
      (ProviderRef<AccountRepository> ref) => MockAccountRepository(),
);

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

final FutureProvider<List<SpendingDay>> month_days_provider =
FutureProvider<List<SpendingDay>>(
      (FutureProviderRef<List<SpendingDay>> ref) async {
    final AccountRepository repo = ref.read(account_repository_provider);
    final DateTime month = ref.watch(selected_month_provider);
    return repo.fetch_month_days(month: month);
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

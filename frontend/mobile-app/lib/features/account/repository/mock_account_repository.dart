import 'dart:async';
import '../../../domain/models/user_profile.dart';
import '../../../domain/models/spending.dart';
import 'account_repository.dart';

class MockAccountRepository implements AccountRepository {
  UserProfile _profile = const UserProfile(
    user_id: 'u1',
    nickname: '준서',
    email: 'junseo@example.com',
    is_premium: true,
  );

  @override
  Future<UserProfile> fetch_my_profile() async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return _profile;
  }

  @override
  Future<void> update_nickname({required String new_nickname}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    _profile = UserProfile(
      user_id: _profile.user_id,
      nickname: new_nickname,
      email: _profile.email,
      is_premium: _profile.is_premium,
    );
  }

  @override
  Future<SpendingSummary> fetch_month_summary({required DateTime month}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return SpendingSummary(
      total_amount: 1240500,
      diff_percent: -12,
      month_label: '${month.year}년 ${month.month}월',
    );
  }

  @override
  Future<List<SpendingDay>> fetch_month_days({required DateTime month}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    // 예시: 일부 날짜만 지출 표시(실제로는 서버 데이터)
    return <SpendingDay>[
      SpendingDay(date: DateTime(month.year, month.month, 2), amount: 12000),
      SpendingDay(date: DateTime(month.year, month.month, 5), amount: 8000),
      SpendingDay(date: DateTime(month.year, month.month, 8), amount: 25000),
      SpendingDay(date: DateTime(month.year, month.month, 16), amount: 42000),
      SpendingDay(date: DateTime(month.year, month.month, 23), amount: 9000),
      SpendingDay(date: DateTime(month.year, month.month, 28), amount: 120000),
    ];
  }

  @override
  Future<List<SpendingTransaction>> fetch_recent_transactions({required DateTime month}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return <SpendingTransaction>[
      SpendingTransaction(
        transaction_id: 't1',
        spent_at: DateTime(month.year, month.month, 28),
        merchant_name: '마트 결제',
        category_label: '식료품',
        amount: 124500,
      ),
      SpendingTransaction(
        transaction_id: 't2',
        spent_at: DateTime(month.year, month.month, 24),
        merchant_name: '카페',
        category_label: '외식',
        amount: 12800,
      ),
      SpendingTransaction(
        transaction_id: 't3',
        spent_at: DateTime(month.year, month.month, 23),
        merchant_name: '주유/교통',
        category_label: '교통',
        amount: 45000,
      ),
    ];
  }

  @override
  Future<List<TopItem>> fetch_top_items({required DateTime month}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    return <TopItem>[
      const TopItem(product_id: 'p11', name: '우유', category_label: '유제품', purchase_count: 12, avg_price: 4500),
      const TopItem(product_id: 'p21', name: '계란', category_label: '유제품/계란', purchase_count: 8, avg_price: 3200),
      const TopItem(product_id: 'p31', name: '식빵', category_label: '베이커리', purchase_count: 5, avg_price: 2800),
      const TopItem(product_id: 'p41', name: '바나나', category_label: '과일', purchase_count: 4, avg_price: 4000),
      const TopItem(product_id: 'p51', name: '아보카도', category_label: '과일', purchase_count: 4, avg_price: 1200),
    ];
  }

  @override
  Future<List<CategorySpend>> fetch_category_breakdown({required DateTime month}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    final int total_amount = 1240500;
    final List<CategorySpend> list = <CategorySpend>[
      CategorySpend(category_key: 'grocery', category_label: '식료품', amount: 806320, ratio: 806320 / total_amount),
      CategorySpend(category_key: 'dining', category_label: '외식', amount: 248100, ratio: 248100 / total_amount),
      CategorySpend(category_key: 'shopping', category_label: '쇼핑', amount: 124050, ratio: 124050 / total_amount),
      CategorySpend(category_key: 'transport', category_label: '교통', amount: 62030, ratio: 62030 / total_amount),
    ];
    return list;
  }

  @override
  Future<void> change_password({required String current_password, required String new_password}) async {
    await Future<void>.delayed(const Duration(milliseconds: 250));
    // mock: 항상 성공 처리
  }
}

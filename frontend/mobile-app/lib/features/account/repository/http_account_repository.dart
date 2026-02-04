import 'package:dio/dio.dart';
import '../../../domain/models/user_profile.dart';
import '../../../domain/models/spending.dart';
import '../../../core/storage/token_storage.dart'; // 추가
import 'account_repository.dart';

class HttpAccountRepository implements AccountRepository {
  final Dio _dio;
  final TokenStorage _tokenStorage = TokenStorage();

  HttpAccountRepository({required Dio dio}) : _dio = dio;

  @override
  Future<UserProfile> fetch_my_profile() async {
    try {
      final response = await _dio.get('users/me');
      final data = response.data;
      return UserProfile(
        user_id: data['user_id'].toString(),
        nickname: data['nickname'],
        email: data['email'],
        is_premium: false, // DB 변경 없이 기본값 false 사용
      );
    } catch (e) {
      throw Exception('Failed to load user profile: $e');
    }
  }

  @override
  Future<void> update_nickname({required String new_nickname}) async {
    try {
      // 백엔드가 patch를 사용하므로 수정
      await _dio.patch('users/me/nickname', data: {'nickname': new_nickname});
    } catch (e) {
      throw Exception('Failed to update nickname: $e');
    }
  }

  @override
  Future<void> change_password({required String current_password, required String new_password}) async {
    try {
      // 백엔드가 patch를 사용하므로 수정
      await _dio.patch('users/me/password', data: {
        'current_password': current_password,
        'new_password': new_password,
      });
    } catch (e) {
      throw Exception('Failed to change password: $e');
    }
  }

  @override
  Future<SpendingSummary> fetch_month_summary({required DateTime month}) async {
    try {
      final response = await _dio.get('ledger/summary/monthly', queryParameters: {
        'year': month.year,
        'month': month.month,
      });

      final data = response.data;
      // 백엔드에서 diff_percent를 주지 않으면 0으로 처리 (API 보완 필요 가능성 있음)
      return SpendingSummary(
        total_amount: data['total_amount'] ?? 0,
        diff_percent: 0, 
        month_label: '${month.month}월',
      );
    } catch (e) {
      print('fetch_month_summary error: $e');
      return SpendingSummary(total_amount: 0, diff_percent: 0, month_label: '${month.month}월');
    }
  }

  @override
  Future<List<SpendingDay>> fetch_month_days({required DateTime month}) async {
    try {
      final response = await _dio.get('ledger/calendar', queryParameters: {
        'year': month.year,
        'month': month.month,
      });

      final Map<String, dynamic> dailyTotal = response.data['daily_total'] ?? {};
      final List<SpendingDay> days = [];

      dailyTotal.forEach((key, value) {
        // key format: "2024-05-01"
        final date = DateTime.parse(key);
        days.add(SpendingDay(date: date, amount: value as int));
      });

      return days;
    } catch (e) {
      print('fetch_month_days error: $e');
      return [];
    }
  }

  @override
  Future<List<SpendingTransaction>> fetch_recent_transactions({required DateTime month}) async {
    // 백엔드의 /recent API는 month 필터가 없고 최근 N개만 가져옴.
    // 여기서는 화면 요구사항에 맞춰 /recent를 호출하거나, /ledger (목록 조회)를 호출해야 함.
    // 일단 /recent API 활용
    try {
      final response = await _dio.get('ledger/recent', queryParameters: {'limit': 10});
      final List<dynamic> items = response.data['items'] ?? [];

      return items.map((item) {
        return SpendingTransaction(
          transaction_id: item['ledger_entry_id'].toString(),
          spent_at: DateTime.parse(item['spend_date']), // 백엔드 spend_date가 날짜형식이면 시간은 00:00일수 있음
          merchant_name: item['memo'] ?? '알 수 없음', // 가맹점명이 없으면 메모 사용
          category_label: item['category'] ?? '기타',
          amount: item['amount'],
        );
      }).toList();
    } catch (e) {
      print('fetch_recent_transactions error: $e');
      return [];
    }
  }

  @override
  Future<List<TopItem>> fetch_top_items({required DateTime month}) async {
    try {
      final response = await _dio.get('ledger/top-items', queryParameters: {
        'year': month.year,
        'month': month.month,
        'limit': 5,
      });

      final List<dynamic> items = response.data['items'] ?? [];
      
      return items.map((item) {
        return TopItem(
          product_id: '', // 백엔드에서 product_id를 안주면 빈값
          name: item['item_name'],
          category_label: '식품', // 임시
          purchase_count: item['count'],
          avg_price: (item['total_amount'] / item['count']).round(),
        );
      }).toList();
    } catch (e) {
      print('fetch_top_items error: $e');
      return [];
    }
  }

  @override
  Future<List<CategorySpend>> fetch_category_breakdown({required DateTime month}) async {
    try {
      final response = await _dio.get('ledger/top-categories', queryParameters: {
        'year': month.year,
        'month': month.month,
        'limit': 10,
      });

      final List<dynamic> categories = response.data['categories'] ?? [];
      
      return categories.map((cat) {
        return CategorySpend(
          category_key: cat['category'],
          category_label: cat['category'], // 한글 변환 필요 시 맵핑 추가
          amount: (cat['amount'] as num).toDouble(),
          ratio: (cat['ratio'] as num).toDouble() / 100.0, // 백엔드는 0~100, 프론트는 0~1
        );
      }).toList();
    } catch (e) {
      print('fetch_category_breakdown error: $e');
      return [];
    }
  }

  @override
  Future<void> logout() async {
    await _tokenStorage.deleteToken();
    _dio.options.headers.remove('Authorization');
  }
}

import 'dart:async';
import 'package:app_links/app_links.dart';
import 'package:flutter/foundation.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../presentation/payment_providers.dart';

final paymentServiceProvider = Provider<PaymentService>((ref) {
  return PaymentService(ref);
});

class PaymentService {
  final Ref _ref;
  final _appLinks = AppLinks();
  StreamSubscription<Uri>? _linkSubscription;

  PaymentService(this._ref);

  void init() {
    // 1. 앱이 꺼져 있을 때 링크로 들어온 경우 처리
    _appLinks.getInitialLink().then((uri) {
      if (uri != null) _handleDeepLink(uri);
    });

    // 2. 앱이 실행 중일 때 링크가 들어오는 경우 감시
    _linkSubscription = _appLinks.uriLinkStream.listen((uri) {
      _handleDeepLink(uri);
    }, onError: (err) {
      debugPrint('Deep Link Error: $err');
    });
  }

  void dispose() {
    _linkSubscription?.cancel();
  }

  void _handleDeepLink(Uri uri) async {
    debugPrint('Received Deep Link: $uri');
    
    // pickle://payment/success?tid=...&pg_token=...
    if (uri.scheme == 'pickle' && uri.path.contains('payment/success')) {
      final pgToken = uri.queryParameters['pg_token'];
      final tid = uri.queryParameters['tid'];

      if (pgToken != null && tid != null) {
        try {
          final repository = _ref.read(payment_repository_provider);
          final paymentId = await repository.approve_kakao_pay(
            tid: tid,
            pg_token: pgToken,
          );
          
          debugPrint('Payment Approved Successfully: $paymentId');
          
          // 전역 결제 상태 업데이트 또는 화면 이동 알림
          _ref.read(paymentStatusProvider.notifier).state = PaymentStatusInfo(
            isSuccess: true,
            paymentId: paymentId,
          );
        } catch (e) {
          debugPrint('Payment Approval Error: $e');
          _ref.read(paymentStatusProvider.notifier).state = PaymentStatusInfo(
            isSuccess: false,
            errorMessage: e.toString(),
          );
        }
      }
    }
  }
}

// 결제 결과 상태를 관리하기 위한 모델 및 프로바이더
class PaymentStatusInfo {
  final bool isSuccess;
  final String? paymentId;
  final String? errorMessage;

  PaymentStatusInfo({required this.isSuccess, this.paymentId, this.errorMessage});
}

final paymentStatusProvider = StateProvider<PaymentStatusInfo?>((ref) => null);

import 'dart:io'; // Platform 감지를 위해 추가
import 'package:flutter/foundation.dart'; // kIsWeb
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'dio_client.dart';

// 서버의 Base URL을 관리하는 Provider
final baseUrlProvider = Provider<String>((ref) {
  // 1. .env에 API_URL이 지정되어 있으면 최우선 사용
  final envUrl = dotenv.env['API_URL'];
  if (envUrl != null && envUrl.isNotEmpty) {
    String finalUrl = envUrl;
    if (Platform.isAndroid && finalUrl.contains('localhost')) {
      finalUrl = finalUrl.replaceFirst('localhost', '10.0.2.2');
    }
    // 끝에 / 보장
    return finalUrl.endsWith('/') ? finalUrl : '$finalUrl/';
  }

  // 2. 기본 실서버 주소 (HTTPS 권장)
  return 'https://bapsim.site/api/';
});

// DioClient 인스턴스를 제공하는 Provider
final dioClientProvider = Provider<DioClient>((ref) {
  final baseUrl = ref.watch(baseUrlProvider);
  return DioClient(baseUrl: baseUrl);
});

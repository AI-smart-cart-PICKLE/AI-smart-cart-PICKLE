import 'dart:io'; // Platform 감지를 위해 추가
import 'package:flutter/foundation.dart'; // kIsWeb
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'dio_client.dart';

// 서버의 Base URL을 관리하는 Provider
final baseUrlProvider = Provider<String>((ref) {
  // 1. 안드로이드 에뮬레이터 특수 처리 (localhost 문제 방지)
  if (kDebugMode && Platform.isAndroid) {
    return 'http://10.0.2.2:8000';
  }

  // 2. .env에 API_URL이 지정되어 있으면 사용
  final envUrl = dotenv.env['API_URL'];
  if (envUrl != null && envUrl.isNotEmpty) {
    // 만약 에뮬레이터인데 envUrl에 localhost가 포함되어 있다면 교체
    if (Platform.isAndroid && envUrl.contains('localhost')) {
      return envUrl.replaceFirst('localhost', '10.0.2.2');
    }
    return envUrl; 
  }

  // 3. 로컬 개발 환경 감지 (디버그 모드)
  if (kDebugMode) {
    if (kIsWeb) return 'http://127.0.0.1:8000';
    if (Platform.isWindows || Platform.isMacOS || Platform.isLinux) return 'http://127.0.0.1:8000';
  }

  // 4. 외부(실서버) 통신 규격
  return 'https://bapsim.site/api';
});

// DioClient 인스턴스를 제공하는 Provider
final dioClientProvider = Provider<DioClient>((ref) {
  final baseUrl = ref.watch(baseUrlProvider);
  return DioClient(baseUrl: baseUrl);
});

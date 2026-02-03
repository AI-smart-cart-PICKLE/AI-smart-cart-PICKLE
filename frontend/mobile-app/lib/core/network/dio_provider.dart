import 'dart:io'; // Platform 감지를 위해 추가
import 'package:flutter/foundation.dart'; // kIsWeb
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';
import 'dio_client.dart';

// 서버의 Base URL을 관리하는 Provider
final baseUrlProvider = Provider<String>((ref) {
  // 1. .env에 API_URL이 강제로 지정되어 있으면 그것을 최우선 사용
  final envUrl = dotenv.env['API_URL'];
  if (envUrl != null && envUrl.isNotEmpty) {
    // 윈도우 환경이면서 localhost인 경우 예외 처리 가능 (필요 시)
    return envUrl; 
  }

  // 2. 웹 브라우저(크롬)에서 실행 시
  if (kIsWeb) {
    // localhost 대신 127.0.0.1 사용 (일부 윈도우 환경 호환성)
    return 'http://127.0.0.1:8000';
  }

  // 3. 윈도우/맥/리눅스 데스크톱 앱에서 실행 시
  if (Platform.isWindows || Platform.isMacOS || Platform.isLinux) {
    return 'http://127.0.0.1:8000';
  }

  // 4. 안드로이드 에뮬레이터 (기본값)
  if (Platform.isAndroid) {
    return 'http://10.0.2.2:8000';
  }
  
  // 5. iOS 시뮬레이터 또는 그 외
  return 'http://127.0.0.1:8000';
});

// DioClient 인스턴스를 제공하는 Provider
final dioClientProvider = Provider<DioClient>((ref) {
  final baseUrl = ref.watch(baseUrlProvider);
  return DioClient(baseUrl: baseUrl);
});

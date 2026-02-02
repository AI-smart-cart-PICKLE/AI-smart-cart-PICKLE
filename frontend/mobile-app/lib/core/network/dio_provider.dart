import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'dio_client.dart';

// 서버의 Base URL을 관리하는 Provider
// 환경에 따라 이 값을 수정하면 앱 전체의 API 주소가 변경됩니다.
final baseUrlProvider = Provider<String>((ref) {
  // return 'https://bapsim.site/api'; 
  return 'http://10.0.2.2:8000';
});

// DioClient 인스턴스를 제공하는 Provider
final dioClientProvider = Provider<DioClient>((ref) {
  final baseUrl = ref.watch(baseUrlProvider);
  return DioClient(baseUrl: baseUrl);
});

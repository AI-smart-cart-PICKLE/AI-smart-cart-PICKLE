import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:webview_flutter/webview_flutter.dart';

class OAuthWebViewScreen extends StatefulWidget {
  final String url;
  final String title;

  const OAuthWebViewScreen({
    super.key,
    required this.url,
    required this.title,
  });

  @override
  State<OAuthWebViewScreen> createState() => _OAuthWebViewScreenState();
}

class _OAuthWebViewScreenState extends State<OAuthWebViewScreen> {
  late final WebViewController _controller;
  bool _is_loading = true;

  @override
  void initState() {
    super.initState();
    _controller = WebViewController()
      ..setJavaScriptMode(JavaScriptMode.unrestricted)
      ..setUserAgent("Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36") // 추가
      ..setBackgroundColor(const Color(0x00000000))
      ..setNavigationDelegate(
        NavigationDelegate(
          onProgress: (int progress) {
            // Update loading bar.
          },
          onPageStarted: (String url) {
            setState(() {
              _is_loading = true;
            });
          },
          onPageFinished: (String url) async {
            setState(() {
              _is_loading = false;
            });

            // 인증 완료 후 콜백 URL에 도달했는지 확인
            // 백엔드 주소가 포함되어 있고 /callback으로 끝나는 경우
            if (url.contains('/auth/kakao/callback') || url.contains('/auth/google/callback')) {
              try {
                // 페이지의 텍스트(JSON)를 가져옴
                final String content = await _controller.runJavaScriptReturningResult(
                  "document.body.innerText"
                ) as String;
                
                // WebView에서 반환된 문자열은 따옴표로 감싸져 있을 수 있음
                String cleanContent = content;
                if (cleanContent.startsWith('"') && cleanContent.endsWith('"')) {
                  cleanContent = cleanContent.substring(1, cleanContent.length - 1);
                }
                // 이스케이프된 문자열 처리 (")
                cleanContent = cleanContent.replaceAll('"', '"');

                final Map<String, dynamic> data = jsonDecode(cleanContent);
                if (data.containsKey('access_token')) {
                  if (mounted) {
                    Navigator.of(context).pop(data['access_token']);
                  }
                }
              } catch (e) {
                debugPrint('Error parsing OAuth response: $e');
              }
            }
          },
          onWebResourceError: (WebResourceError error) {
            debugPrint('WebView error: ${error.description}');
          },
        ),
      )
      ..loadRequest(Uri.parse(widget.url));
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(widget.title),
        leading: IconButton(
          icon: const Icon(Icons.close),
          onPressed: () => Navigator.of(context).pop(),
        ),
      ),
      body: Stack(
        children: [
          WebViewWidget(controller: _controller),
          if (_is_loading)
            const Center(
              child: CircularProgressIndicator(),
            ),
        ],
      ),
    );
  }
}

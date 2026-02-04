import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mobile_scanner/mobile_scanner.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/theme_provider.dart';
import '../../../core/router/app_routes.dart';
import 'cart_providers.dart';

class QrScannerScreen extends ConsumerStatefulWidget {
  const QrScannerScreen({super.key});

  @override
  ConsumerState<QrScannerScreen> createState() => _QrScannerScreenState();
}

class _QrScannerScreenState extends ConsumerState<QrScannerScreen> {
  final MobileScannerController controller = MobileScannerController(
    detectionSpeed: DetectionSpeed.noDuplicates,
    facing: CameraFacing.back,
  );

  bool is_scanned = false;

  @override
  void dispose() {
    controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final theme_mode = ref.watch(theme_mode_provider);
    final scan_window_size = 250.0;
    final scan_window = Rect.fromCenter(
      center: MediaQuery.of(context).size.center(Offset.zero),
      width: scan_window_size,
      height: scan_window_size,
    );

    return Scaffold(
      appBar: AppBar(
        title: const Text('QR 스캔', style: TextStyle(fontWeight: FontWeight.w900)),
        backgroundColor: Colors.transparent,
        foregroundColor: Colors.white,
        elevation: 0,
        leading: IconButton(
          onPressed: () => context.pop(),
          icon: const Icon(Icons.close),
        ),
        actions: [
          ValueListenableBuilder(
            valueListenable: controller,
            builder: (context, state, child) {
              if (!state.isInitialized || !state.isRunning) {
                return const SizedBox.shrink();
              }
              return IconButton(
                color: Colors.white,
                icon: state.torchState == TorchState.on
                    ? const Icon(Icons.flash_on)
                    : const Icon(Icons.flash_off),
                onPressed: () => controller.toggleTorch(),
              );
            },
          ),
        ],
      ),
      extendBodyBehindAppBar: true,
      backgroundColor: Colors.black,
      body: Stack(
        children: [
          MobileScanner(
            controller: controller,
            // scanWindow: scan_window, // 인식 문제 해결을 위해 일시적으로 영역 제한 해제
            onDetect: (capture) {
              if (is_scanned) return;
              
              final List<Barcode> barcodes = capture.barcodes;
              for (final barcode in barcodes) {
                final String? code = barcode.rawValue;
                if (code != null) {
                  debugPrint('QR Code detected: $code');
                  setState(() => is_scanned = true);
                  
                  // 인식 성공 시 짧은 진동 대신 가벼운 피드백 (SnackBar는 BuildContext 필요하므로 내부에서 처리)
                  _handleScannedCode(code);
                  break; 
                }
              }
            },
          ),
          // Background Dimming with hole
          ColorFiltered(
            colorFilter: ColorFilter.mode(
              Colors.black.withOpacity(0.5),
              BlendMode.srcOut,
            ),
            child: Stack(
              children: [
                Container(
                  decoration: const BoxDecoration(
                    color: Colors.black,
                    backgroundBlendMode: BlendMode.dstOut,
                  ),
                ),
                Center(
                  child: Container(
                    width: scan_window_size,
                    height: scan_window_size,
                    decoration: BoxDecoration(
                      color: Colors.white,
                      borderRadius: BorderRadius.circular(24),
                    ),
                  ),
                ),
              ],
            ),
          ),
          // Scanner Overlay Border
          Center(
            child: Container(
              width: scan_window_size,
              height: scan_window_size,
              decoration: BoxDecoration(
                border: Border.all(color: AppColors.gemini_purple, width: 4),
                borderRadius: BorderRadius.circular(24),
              ),
            ),
          ),
          // Instructions
          Positioned(
            bottom: 100,
            left: 0,
            right: 0,
            child: Column(
              children: [
                const Text(
                  'QR 코드를 사각형 안에 맞춰주세요',
                  style: TextStyle(color: Colors.white, fontSize: 16, fontWeight: FontWeight.w700),
                ),
                const SizedBox(height: 8),
                Text(
                  '카트의 QR 코드를 스캔하면 쇼핑을 시작할 수 있습니다.',
                  style: TextStyle(color: Colors.white.withOpacity(0.7), fontSize: 13),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Future<void> _handleScannedCode(String code) async {
    // Show success dialog or navigate
    if (!mounted) return;
    
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        title: const Text('스캔 완료', style: TextStyle(fontWeight: FontWeight.w900)),
        content: Text('코드: $code\n연결을 진행할까요?'),
        actions: [
          TextButton(
            onPressed: () {
              setState(() => is_scanned = false);
              Navigator.pop(context);
            },
            child: const Text('취소'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              
              try {
                // 1. 카트 연동 API 호출
                final result = await ref.read(cart_repository_provider).pair_cart_by_qr(device_code: code);
                
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('카트와 성공적으로 연동되었습니다!')), 
                  );
                  // 2. 연동 성공 후 홈 또는 리뷰 화면으로 이동
                  context.pushReplacement(AppRoutes.home);
                }
              } catch (e) {
                if (mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('연동 실패: ${e.toString().replaceAll('Exception: ', '')}')),
                  );
                  setState(() => is_scanned = false);
                }
              }
            },
            style: ElevatedButton.styleFrom(backgroundColor: AppColors.gemini_blue, foregroundColor: Colors.white),
            child: const Text('연결하기'),
          ),
        ],
      ),
    );
  }
}
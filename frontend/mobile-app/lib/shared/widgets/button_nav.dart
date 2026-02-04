import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';

enum BottomTab { home, search, scan, history, my }

class BottomNav extends StatelessWidget {
  final BottomTab current_tab;
  final ValueChanged<BottomTab> on_changed;

  const BottomNav({
    super.key,
    required this.current_tab,
    required this.on_changed,
  });

  int _index(BottomTab tab) => BottomTab.values.indexOf(tab);

  @override
  Widget build(BuildContext context) {
    return NavigationBar(
      backgroundColor: Colors.white,
      indicatorColor: AppColors.brand_primary.withOpacity(0.18),
      selectedIndex: _index(current_tab),
      onDestinationSelected: (int i) => on_changed(BottomTab.values[i]),
      destinations: const <NavigationDestination>[
        NavigationDestination(icon: Icon(Icons.home_outlined), label: '홈'),
        NavigationDestination(icon: Icon(Icons.search), label: '검색'),
        NavigationDestination(icon: Icon(Icons.qr_code_scanner), label: '스캔'),
        NavigationDestination(icon: Icon(Icons.receipt_long), label: '내역'),
        NavigationDestination(icon: Icon(Icons.person_outline), label: '마이'),
      ],
    );
  }
}
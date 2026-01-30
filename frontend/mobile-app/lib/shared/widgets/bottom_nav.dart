import 'package:flutter/material.dart';

enum BottomTab {
  home,
  search,
  scan,
  account_book,
  my_page,
}

class BottomNav extends StatelessWidget {
  final BottomTab current_tab;
  final ValueChanged<BottomTab> on_tab_selected;

  const BottomNav({
    super.key,
    required this.current_tab,
    required this.on_tab_selected,
  });

  int _tab_to_index(BottomTab tab) {
    switch (tab) {
      case BottomTab.home:
        return 0;
      case BottomTab.search:
        return 1;
      case BottomTab.scan:
        return 2;
      case BottomTab.account_book:
        return 3;
      case BottomTab.my_page:
        return 4;
    }
  }

  BottomTab _index_to_tab(int index) {
    switch (index) {
      case 0:
        return BottomTab.home;
      case 1:
        return BottomTab.search;
      case 2:
        return BottomTab.scan;
      case 3:
        return BottomTab.account_book;
      case 4:
      default:
        return BottomTab.my_page;
    }
  }

  @override
  Widget build(BuildContext context) {
    final double icon_size = MediaQuery.of(context).size.width < 420 ? 22 : 24;

    return SafeArea(
      top: false,
      child: BottomNavigationBar(
        currentIndex: _tab_to_index(current_tab),
        type: BottomNavigationBarType.fixed,
        onTap: (int index) => on_tab_selected(_index_to_tab(index)),
        selectedFontSize: 12,
        unselectedFontSize: 12,
        items: <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.home_outlined, size: icon_size),
            activeIcon: Icon(Icons.home, size: icon_size),
            label: '홈',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.search_outlined, size: icon_size),
            activeIcon: Icon(Icons.search, size: icon_size),
            label: '검색',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.qr_code_scanner_outlined, size: icon_size),
            activeIcon: Icon(Icons.qr_code_scanner, size: icon_size),
            label: '스캔',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.receipt_long_outlined, size: icon_size),
            activeIcon: Icon(Icons.receipt_long, size: icon_size),
            label: '가계부',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.person_outline, size: icon_size),
            activeIcon: Icon(Icons.person, size: icon_size),
            label: '마이',
          ),
        ],
      ),
    );
  }
}

import 'package:flutter/widgets.dart';

class Responsive {
  static double max_width(BuildContext context) {
    final double w = MediaQuery.sizeOf(context).width;
    if (w >= 600) return 460; // 태블릿/웹에서 과도하게 넓어지지 않게
    return w;
  }

  static EdgeInsets page_padding(BuildContext context) {
    final double w = MediaQuery.sizeOf(context).width;
    final double h = MediaQuery.sizeOf(context).height;
    final double base = w >= 600 ? 24 : 16;
    return EdgeInsets.fromLTRB(base, base, base, h >= 780 ? 20 : 16);
  }
}

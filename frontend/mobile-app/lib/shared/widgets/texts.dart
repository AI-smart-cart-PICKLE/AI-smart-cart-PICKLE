import 'package:flutter/material.dart';
import 'package:pickle/core/theme/text_styles.dart';

class PickleText extends StatelessWidget {
  final String text;
  final TextStyle style;

  const PickleText(this.text, {super.key, this.style = PickleTextStyles.mediumregular});

  @override
  Widget build(BuildContext context) {
    return Text(
      text,
      style: style,
    );
  }
}

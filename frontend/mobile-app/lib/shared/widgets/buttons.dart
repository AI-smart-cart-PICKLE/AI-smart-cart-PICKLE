import 'package:flutter/material.dart';
import 'package:pickle/core/theme/PickleColors.dart';
import 'package:pickle/shared/widgets/texts.dart';

class PickleButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final Color backgroundColor;
  final Color textColor;

  const PickleButton({
    super.key,
    required this.text,
    this.onPressed,
    this.backgroundColor = PickleColors.pickle,
    this.textColor = PickleColors.white,
  });

  @override
  Widget build(BuildContext context) {
    return ElevatedButton(
      onPressed: onPressed,
      style: ElevatedButton.styleFrom(
        backgroundColor: backgroundColor,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
      ),
      child: PickleText(
        text,
        style: TextStyle(color: textColor),
      ),
    );
  }
}

class PickleOutlinedButton extends StatelessWidget {
  final String text;
  final VoidCallback? onPressed;
  final Color borderColor;
  final Color textColor;

  const PickleOutlinedButton({
    super.key,
    required this.text,
    this.onPressed,
    this.borderColor = PickleColors.pickle,
    this.textColor = PickleColors.pickle,
  });

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: onPressed,
      style: OutlinedButton.styleFrom(
        side: BorderSide(color: borderColor),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10),
        ),
      ),
      child: PickleText(
        text,
        style: TextStyle(color: textColor),
      ),
    );
  }
}

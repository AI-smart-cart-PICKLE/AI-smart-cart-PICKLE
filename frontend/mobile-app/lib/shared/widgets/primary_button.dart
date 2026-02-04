import 'package:flutter/material.dart';
import '../../core/theme/app_colors.dart';

class PrimaryButton extends StatelessWidget {
  final String label;
  final VoidCallback? on_pressed;
  final Widget? leading;
  final bool is_expanded;
  final Color? background_color;
  final Color? text_color;

  const PrimaryButton({
    super.key,
    required this.label,
    required this.on_pressed,
    this.leading,
    this.is_expanded = true,
    this.background_color,
    this.text_color,
  });

  @override
  Widget build(BuildContext context) {
    final Widget child = Row(
      mainAxisSize: MainAxisSize.min,
      mainAxisAlignment: MainAxisAlignment.center,
      children: <Widget>[
        if (leading != null) ...<Widget>[leading!, const SizedBox(width: 8)],
        Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
      ],
    );

    final Widget button = FilledButton(
      onPressed: on_pressed,
      style: FilledButton.styleFrom(
        backgroundColor: background_color ?? AppColors.brand_primary,
        foregroundColor: text_color ?? Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 16),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
      ),
      child: child,
    );

    if (!is_expanded) return button;
    return SizedBox(width: double.infinity, child: button);
  }
}


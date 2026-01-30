import 'package:flutter/material.dart';

class AppTextField extends StatelessWidget {
  final TextEditingController controller;
  final String label;
  final String hint;
  final bool obscure_text;
  final TextInputType keyboard_type;
  final Widget? prefix_icon;
  final Widget? suffix_icon;
  final String? helper_text;

  const AppTextField({
    super.key,
    required this.controller,
    required this.label,
    required this.hint,
    this.obscure_text = false,
    this.keyboard_type = TextInputType.text,
    this.prefix_icon,
    this.suffix_icon,
    this.helper_text,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: <Widget>[
        Text(label, style: const TextStyle(fontWeight: FontWeight.w700)),
        const SizedBox(height: 8),
        TextField(
          controller: controller,
          obscureText: obscure_text,
          keyboardType: keyboard_type,
          decoration: InputDecoration(
            hintText: hint,
            prefixIcon: prefix_icon,
            suffixIcon: suffix_icon,
            helperText: helper_text,
          ),
        ),
      ],
    );
  }
}

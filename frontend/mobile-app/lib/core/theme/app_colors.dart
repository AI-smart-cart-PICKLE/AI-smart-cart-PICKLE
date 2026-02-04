import 'package:flutter/material.dart';

class AppColors {
  // Gemini Theme Colors (Updated: Purple focused, No Red)
  static const Color gemini_blue = Color(0xFF3B82F6);
  static const Color gemini_purple = Color(0xFF8B5CF6);

  static const List<Color> gemini_gradient = [
    gemini_blue,
    gemini_purple,
  ];

  static const Color brand_primary = gemini_purple; // Shifted to Purple dominant

  // Light Mode Colors
  static const Color bg = Color(0xFFF6F7F9);
  static const Color text_primary = Color(0xFF111827);
  static const Color text_secondary = Color(0xFF6B7280);
  static const Color card = Colors.white;
  static const Color border = Color(0xFFE5E7EB);

  // Dark Mode Colors
  static const Color bg_dark = Color(0xFF0F172A);
  static const Color text_primary_dark = Color(0xFFF8FAFC);
  static const Color text_secondary_dark = Color(0xFF94A3B8);
  static const Color card_dark = Color(0xFF1E293B);
  static const Color border_dark = Color(0xFF334155);
}
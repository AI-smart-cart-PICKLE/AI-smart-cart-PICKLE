import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

final theme_mode_provider = StateProvider<ThemeMode>((ref) {
  return ThemeMode.system;
});

final notification_enabled_provider = StateProvider<bool>((ref) {
  return true;
});
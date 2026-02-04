import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'core/router/app_router.dart';
import 'core/theme/app_theme.dart';
import 'core/theme/theme_provider.dart';

class PickleApp extends ConsumerWidget {
  const PickleApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final theme_mode = ref.watch(theme_mode_provider);

    return MaterialApp.router(
      title: '피클',
      theme: AppTheme.light_theme,
      darkTheme: AppTheme.dark_theme,
      themeMode: theme_mode,
      routerConfig: AppRouter.router,
      debugShowCheckedModeBanner: false,
    );
  }
}
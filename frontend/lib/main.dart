import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:frontend/core/routes/app_routes.dart';
import 'package:frontend/core/themes/app_theme.dart';

// 1. Create a provider for navigation management
final navigatorKeyProvider = Provider<GlobalKey<NavigatorState>>((ref) {
  return GlobalKey<NavigatorState>();
});

void main() {
  runApp(
    const ProviderScope(
      child: TradingApp(),
    ),
  );
}

// 2. Separate app configuration into a dedicated widget
class TradingApp extends ConsumerWidget {
  const TradingApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // 3. Get navigation key from provider
    final navigatorKey = ref.read(navigatorKeyProvider);

    return MaterialApp(
      title: 'Paper Trading App',
      theme: AppThemes.lightTheme,
      darkTheme: AppThemes.darkTheme,
      themeMode: ThemeMode.system,
      navigatorKey: navigatorKey,
      initialRoute: AppRoutes.initial,
      routes: AppRoutes.pages,
      builder: (context, child) {
        // 4. Add error handling overlay
        return GestureDetector(
          onTap: () => FocusManager.instance.primaryFocus?.unfocus(),
          child: child,
        );
      },
      // 5. Add route observors for potential analytics/monitoring
      navigatorObservers: [HeroController()],
    );
  }
}
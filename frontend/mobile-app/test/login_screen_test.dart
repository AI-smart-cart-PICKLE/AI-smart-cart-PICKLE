import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:pickle/features/auth/presentation/login_screen.dart';

void main() {
  testWidgets('Login screen should show Google and Kakao login buttons', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: LoginScreen(),
        ),
      ),
    );

    // Verify that the '또는' text is present
    expect(find.text('또는'), findsOneWidget);

    // Verify that social login buttons are present by their labels
    expect(find.text('카카오로 시작하기'), findsOneWidget);
    expect(find.text('Google로 시작하기'), findsOneWidget);

    // Verify presence of login fields
    expect(find.widgetWithText(TextField, '이메일'), findsOneWidget);
    expect(find.widgetWithText(TextField, '비밀번호'), findsOneWidget);
  });
}

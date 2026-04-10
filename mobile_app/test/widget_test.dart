import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'package:keepbeat/main.dart';

void main() {
  testWidgets('App starts on sign up smoke test', (WidgetTester tester) async {
    // Build our app and trigger a frame.
    await tester.pumpWidget(const ProviderScope(child: KeepBeatApp()));

    // Verify that our app starts on the 'Start Your Health Journey' screen.
    expect(find.text('PULSE - KeepBeat'), findsOneWidget);
    expect(find.text('Start Your Health Journey'), findsOneWidget);

    // Verify we have a button to create account.
    expect(find.text('Create My Account'), findsOneWidget);
  });
}

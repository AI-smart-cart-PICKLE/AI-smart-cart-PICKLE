import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:flutter_dotenv/flutter_dotenv.dart';

import 'app.dart';
import 'features/payment/application/payment_service.dart';

void main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await dotenv.load(fileName: ".env");
  
  final container = ProviderContainer();
  // PaymentService 초기화
  container.read(paymentServiceProvider).init();

  runApp(UncontrolledProviderScope(
    container: container,
    child: const PickleApp(),
  ));
}

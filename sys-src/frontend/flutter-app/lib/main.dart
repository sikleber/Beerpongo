import 'package:beerpongo/view/authentication_view.dart';
import 'package:beerpongo/view/error_view.dart';
import 'package:beerpongo/view/menu_view.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import 'controller/authentication_notifier.dart';

void main() {
  runApp(ChangeNotifierProvider(
    create: (context) => AuthenticationNotifier(),
    child: const BeerpongoApp(),
  ));
}

class BeerpongoApp extends StatelessWidget {
  const BeerpongoApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Beerpongo',
      theme: ThemeData(
        primarySwatch: Colors.blue,
      ),
      home: Consumer<AuthenticationNotifier>(
        builder: (context, notifier, child) =>
            _getByAuthenticationState(notifier.state),
      ),
    );
  }

  Widget _getByAuthenticationState(AuthenticationState state) {
    switch (state) {
      case AuthenticationState.unauthenticated:
        return const AuthenticationView();
      case AuthenticationState.authenticated:
        return const MenuView();
      default:
        return const ErrorView();
    }
  }
}

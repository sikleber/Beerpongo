import 'package:beerpongo/service/authentication_service.dart';
import 'package:flutter/cupertino.dart';

enum AuthenticationState {
  unauthenticated,
  authenticated,
  error
}

class AuthenticationNotifier extends ChangeNotifier {

  final AuthenticationService _authenticationService = AuthenticationService();

  AuthenticationState _state = AuthenticationState.unauthenticated;

  AuthenticationState get state => _state;

  void authenticate() async {
    String token = await _authenticationService.fetchAuthenticationToken();
    if (token.isEmpty){
      _state = AuthenticationState.authenticated;
    } else  {
      _state = AuthenticationState.unauthenticated;
    }
    notifyListeners();
  }

}
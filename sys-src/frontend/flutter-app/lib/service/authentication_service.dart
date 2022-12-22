import 'package:beerpongo/repository/authentication_repository.dart';
import 'package:beerpongo/repository/cognito_authentication_repository.dart';

class AuthenticationService {
  final AuthenticationRepository _authenticationRepository =
      CognitoAuthenticationRepository();

  Future<String> fetchAuthenticationToken() {
    return _authenticationRepository.fetchAuthenticationToken();
  }
}

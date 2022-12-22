import 'package:beerpongo/repository/authentication_repository.dart';

class CognitoAuthenticationRepository implements AuthenticationRepository {

  @override
  Future<String> fetchAuthenticationToken() async {
    // Todo
    await Future.delayed(Duration(seconds: 1));
    return "test";
  }

}

import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  static const String baseUrl = "http://localhost:8000/api/v1";

  /// Verifies clinical credentials and establishes a secure session.
  static Future<Map<String, dynamic>?> login(String email, String password) async {
    try {
      final response = await http.post(
        Uri.parse("$baseUrl/auth/login"),
        headers: {"Content-Type": "application/json"},
        body: jsonEncode({"email": email, "password": password}),
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        print("AUTH_SUCCESS: Session established for ${data['full_name']}");
        return data;
      } else if (response.statusCode == 401) {
        print("AUTH_ERROR: Invalid clinical credentials.");
        return null;
      } else {
        print("AUTH_ERROR: Unexpected response status ${response.statusCode}");
        return null;
      }
    } catch (e) {
      print("CONNECTION_ERROR: Is the KeepBeat cloud server running on localhost:8000?");
      print(e);
      return null;
    }
  }
}

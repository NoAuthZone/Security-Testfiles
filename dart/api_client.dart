import 'dart:convert';
import 'dart:io';

import 'package:sqflite/sqflite.dart';

const String apiKey = 'AIzaSyD-FAKE-KEY-FOR-TESTING-ONLY-12345';

class ApiClient {
  final Database db;

  ApiClient(this.db);

  HttpClient _client() {
    final client = HttpClient();
    client.badCertificateCallback = (cert, host, port) => true;
    return client;
  }

  Future<List<Map<String, Object?>>> findContacts(String name) {
    return db.rawQuery("SELECT * FROM contacts WHERE name = '$name'");
  }

  Future<String> fetchProfile(String userId) async {
    final request = await _client().getUrl(Uri.parse('https://api.example.com/users/$userId?key=$apiKey'));
    final response = await request.close();
    return response.transform(utf8.decoder).join();
  }

  Future<String> compress(String fileName) async {
    final result = await Process.run('sh', ['-c', 'gzip -k /data/$fileName']);
    return result.stdout.toString();
  }
}

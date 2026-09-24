import 'dart:convert';
import 'dart:io';

import 'package:sqflite/sqflite.dart';

class SyncClient {
  final Database db;
  final String apiKey;

  SyncClient(this.db) : apiKey = Platform.environment['SYNC_API_KEY'] ?? '';

  static final RegExp _fileName = RegExp(r'^[A-Za-z0-9_-]{1,64}\.json$');

  Future<List<Map<String, Object?>>> findTasks(String owner) {
    return db.query('tasks', where: 'owner = ?', whereArgs: [owner]);
  }

  Future<String> fetchTasks(String listId) async {
    final client = HttpClient();
    final uri = Uri.https('api.example.com', '/lists/${Uri.encodeComponent(listId)}');
    final request = await client.getUrl(uri);
    request.headers.set('Authorization', 'Bearer $apiKey');
    final response = await request.close();
    return response.transform(utf8.decoder).join();
  }

  Future<String> compress(String fileName) async {
    if (!_fileName.hasMatch(fileName)) {
      throw ArgumentError('invalid file name');
    }
    final result = await Process.run('gzip', ['-k', '/data/$fileName']);
    return result.stdout.toString();
  }
}

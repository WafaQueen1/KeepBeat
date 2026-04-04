import 'dart:convert';
import 'package:http/http.dart' as http;
import '../database/local_data_repository.dart';

class CloudSyncService {
  // Use 10.0.2.2 to access the host machine's localhost from the Android emulator
  static const String _baseUrl = 'http://10.0.2.2:8000/api/v1/telemetry';

  /// Synchronizes local data logs with the cloud backend
  Future<void> syncData({required String patientId}) async {
    final repo = LocalDataRepository();
    final unsyncedLogs = await repo.getUnsyncedDataLogs();

    if (unsyncedLogs.isEmpty) {
      print('No unsynced data to push.');
      return;
    }

    try {
      final items = unsyncedLogs.map((log) {
        return {
          "timestamp": DateTime.fromMillisecondsSinceEpoch((log['timestamp'] * 1000).toInt(), isUtc: true).toIso8601String(),
          "patient_id": patientId, // Now dynamically mapped instead of hardcoded
          "device_id": log['sensor_id'],
          "sensor_type": log['data_type'],
          "value": log['value'],
          "unit": log['data_type'] == 'cgm' ? 'g/L' : 'bpm' // Simple inference
        };
      }).toList();

      final payload = jsonEncode({"items": items});

      final response = await http.post(
        Uri.parse(_baseUrl),
        headers: {'Content-Type': 'application/json'},
        body: payload,
      );

      if (response.statusCode == 201) {
        print('Successfully synced ${unsyncedLogs.length} records to cloud.');
        final ids = unsyncedLogs.map<int>((log) => log['id'] as int).toList();
        await repo.markDataAsSynced(ids);
      } else {
        print('Cloud sync failed with status ${response.statusCode}: ${response.body}');
      }
    } catch (e) {
      print('Cloud sync error: $e');
    }
  }
}

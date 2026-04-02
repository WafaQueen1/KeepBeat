import 'package:sqflite/sqflite.dart';
import 'package:path/path.dart';

class LocalDataRepository {
  static final LocalDataRepository _instance = LocalDataRepository._internal();
  Database? _database;

  factory LocalDataRepository() => _instance;

  LocalDataRepository._internal();

  /// Retrieves the database instance, initializing it if not already present
  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB();
    return _database!;
  }

  Future<Database> _initDB() async {
    final dbPath = await getDatabasesPath();
    final path = join(dbPath, 'twinpacemaker_fog.db');

    return await openDatabase(
      path,
      version: 1,
      onCreate: (db, version) async {
        // Schema guarantees Offline capability is mandatory
        await db.execute('''
          CREATE TABLE sensor_data(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sensor_id TEXT,
            data_type TEXT,
            value REAL,
            timestamp INTEGER,
            sync_status INTEGER DEFAULT 0
          )
        ''');
      },
    );
  }

  /// Buffers real-time physical metrics locally for future Workmanager sync
  Future<void> insertLocallyBufferedData(Map<String, dynamic> data) async {
    final db = await database;
    await db.insert('sensor_data', {
      'sensor_id': data['sensor_id'],
      'data_type': data['type'], 
      'value': data['value'],
      'timestamp': data['timestamp'],
      'sync_status': 0 // 0 = unsynced (buffered), 1 = synced (to cloud)
    });
  }
  
  /// Gets data that should be shipped to TimeScaleDB when Cloud connection resumes
  Future<List<Map<String, dynamic>>> getUnsyncedDataLogs() async {
    final db = await database;
    return await db.query('sensor_data', where: 'sync_status = ?', whereArgs: [0]);
  }

  /// Marks a list of local sensor_data IDs as synced
  Future<void> markDataAsSynced(List<int> ids) async {
    if (ids.isEmpty) return;
    final db = await database;
    await db.update(
      'sensor_data',
      {'sync_status': 1},
      where: 'id IN (${List.filled(ids.length, '?').join(',')})',
      whereArgs: ids,
    );
  }
}

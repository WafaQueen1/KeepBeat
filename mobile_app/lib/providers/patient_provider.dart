import 'package:flutter_riverpod/flutter_riverpod.dart';

class PatientContext {
  final String patientId;
  final String medicalId;
  final String fullName;

  PatientContext({
    required this.patientId,
    required this.medicalId,
    required this.fullName,
  });
}

class PatientContextNotifier extends Notifier<PatientContext> {
  @override
  PatientContext build() {
    return PatientContext(
      patientId: 'PT_001', // Fallback default patient for MVP
      medicalId: '#TP-8842',
      fullName: 'Sarah Jenkins',
    );
  }

  void setActivePatient(String id, String mId, String name) {
    state = PatientContext(patientId: id, medicalId: mId, fullName: name);
  }
}

// Global provider for the active patient context
final patientContextProvider =
    NotifierProvider<PatientContextNotifier, PatientContext>(
  PatientContextNotifier.new,
);

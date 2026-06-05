# Chapitre 5 : Implémentation et Validation Expérimentale

## 5.1 Introduction

Ce chapitre présente l'implémentation pratique de l'écosystème **Smart TwinPac** (plateforme clinique connue sous le nom de **KeepBeat**). Il détaille l'architecture hybride mise en place : une couche Edge (Jumeau Physique et Application Mobile) exécutant des algorithmes temps réel, et une couche Cloud (Jumeau Numérique) exécutant l'Intelligence Artificielle de pointe. Nous abordons les choix technologiques, l'intégration des algorithmes Edge pour la sécurité immédiate du patient, et la synchronisation différée via Wi-Fi permettant au backend d'appliquer trois modèles d'IA lourds (Cardiaque, Batterie, Métabolique). Enfin, nous validons l'ensemble du système à travers des scénarios d'exécution concrets.

## 5.2 Le Jumeau Physique (Physical Twin) & Traitement Edge

### 5.2.1 Architecture Matérielle du Node IoT ECG

Le module d'acquisition physique s'articule autour des composants suivants pour capter l'activité physiologique :
- **Capteur AD8232** : Module biométrique dédié à l'extraction et l'amplification des signaux électrocardiographiques (ECG).
- **Microcontrôleur ESP32** : Assure le traitement primaire des signaux analogiques et la transmission sans fil.

**Schéma de communication (Bluetooth)** :
Le capteur est relié à l'ESP32 qui transmet le signal brut via **Bluetooth Low Energy (BLE)** vers l'application mobile du patient (Fog Node). Ce choix garantit une communication continue et peu énergivore. En parallèle du nœud physique, des simulateurs logiciels (`pacemaker_sensing_module.py` et `cgm_sensing_module.py`) ont été développés pour la validation du système.

### 5.2.2 Algorithmes Embarqués sur l'Application Mobile (Edge Computing)

L'application mobile n'intègre pas les modèles d'Intelligence Artificielle lourds. Pour garantir la sécurité du patient **en temps réel et même sans connexion Internet**, nous avons implémenté et déployé trois algorithmes déterministes et légers directement sur le smartphone (Edge Algorithms) :

1. **Détection Cardiaque (Algorithme Pan-Tompkins)** : Implémenté pour la détection temps réel des complexes QRS. Il filtre le signal (passe-bande 5-15 Hz), applique une dérivation, une mise au carré et une intégration pour extraire la fréquence cardiaque et classer instantanément les arythmies basiques (tachycardie, bradycardie, fibrillation).
2. **Gestion de Batterie (Coulomb Counter)** : Un algorithme d'estimation de l'état de charge (SoC) basé sur la tension linéaire et un comptage des décharges (Ah) par impulsion de stimulation, permettant une estimation basique de la RUL (Remaining Useful Life) hors-ligne.
3. **Analyseur Métabolique (Glucose Analyzer)** : Un analyseur de seuils multi-niveaux. Il intègre une fenêtre de persistance (ex: 120 secondes) pour éviter les fausses alertes, et vérifie la corrélation entre les baisses de glucose et le rythme cardiaque pour déclencher des urgences locales.

Ces algorithmes constituent la première ligne de défense clinique. Ils déclenchent les alertes d'urgence sur l'interface patient sans aucune latence réseau.

## 5.3 Le Jumeau Numérique & L'Intelligence Artificielle (Cloud Layer)

### 5.3.1 Environnement de Développement et Outils

L'infrastructure Cloud (Digital Twin) est entièrement conteneurisée via **Docker** (`docker-compose`) :
- **Backend API (FastAPI / Python)** : Gère le routage, l'authentification (`bcrypt`), charge les modèles TensorFlow lourds et orchestre l'inférence IA.
- **Message Broker (Mosquitto MQTT)** : Orchestre les flux télémétriques haute fréquence.
- **Base de données (TimescaleDB)** : Une extension de PostgreSQL optimisée pour le stockage intensif des séries temporelles.

### 5.3.2 Modélisation Virtuelle et Synchronisation (Wi-Fi)

L'écosystème KeepBeat fonctionne sur un modèle de **synchronisation différée asynchrone**. 
L'application mobile (**Flutter**) stocke temporairement les signaux bruts en local. **Dès que le smartphone détecte une connexion Wi-Fi stable**, il initie une synchronisation sécurisée : il envoie les données physiologiques accumulées vers le backend FastAPI. 

### 5.3.3 Inférence de l'Intelligence Artificielle (Backend)

Une fois les données synchronisées reçues, le serveur Cloud déclenche son pipeline d'Intelligence Artificielle. L'intelligence prédictive repose sur trois modèles neuronaux spécialisés, développés en Python avec **TensorFlow/Keras** :

1. **Modèle de Risque Cardiaque (CNN-LSTM)** : Le CNN extrait les caractéristiques spatiales de la séquence ECG synchronisée, tandis que le LSTM gère l'aspect temporel. Il a démontré une précision de **99.4%** sur la base MIT-BIH.
2. **Modèle de Durée de Vie de Batterie (PINN-LSTM)** : Réseau informé par la physique (modèle Shepherd) couplé à un LSTM. Il offre une prédiction précise (MAE de 8.5 cycles) de l'usure de la pile sur le long terme.
3. **Modèle Dynamique Métabolique (Stacked LSTM)** : Construit sur le *Bergman Minimal Model*, ce LSTM à 3 couches utilise l'historique glycémique pour prédire le taux de glucose une heure à l'avance (MAE de 13.7 mg/dL).

Les résultats de cette IA avancée, ainsi que les alertes prédictives générées, sont ensuite stockés dans TimescaleDB et poussés vers le **Doctor Dashboard** (Vite/React) pour l'analyse clinique, et redescendus vers l'application mobile.

## 5.4 Scénario d'Exécution et Simulation (The "Run" Section)

Pour démontrer le fonctionnement du système, voici les scénarios d'utilisation avec l'architecture distribuée.

### 5.4.1 Déroulement d'un Scénario Nominal (Santé Stable)

1. L'ESP32 transmet un ECG normal. L'application mobile exécute l'algorithme `Pan-Tompkins` en local qui qualifie le rythme de "Normal".
2. Le patient rentre chez lui et son téléphone se connecte au Wi-Fi.
3. L'application synchronise les blocs de données avec le backend FastAPI.
4. Les modèles IA (CNN-LSTM, etc.) s'exécutent sur le serveur et confirment l'absence de risque prédictif à court terme.
5. Sur le **Doctor Dashboard**, les widgets se mettent à jour avec les données synchronisées, affichant un ECG synthétique régulier en vert.

### 5.4.2 Déroulement d'un Scénario Critique (Simulation d'une Arythmie)

- **Étape 1 (Edge)** : L'ESP32 capte un signal ECG anormal lors d'un déplacement (sans Internet). L'algorithme `Pan-Tompkins` embarqué détecte instantanément la variation des intervalles RR.
- **Étape 2 (Alerte Locale)** : L'application Flutter déclenche une alerte rouge de priorité maximale pour le patient (sirène, instructions de sécurité), uniquement grâce à l'algorithme Edge.
- **Étape 3 (Synchronisation Wi-Fi)** : Dès qu'une connexion Wi-Fi est accrochée, le smartphone synchronise en priorité l'événement d'urgence vers le backend.
- **Étape 4 (Inférence IA & Validation)** : Le backend exécute immédiatement le puissant modèle **CNN-LSTM** sur la séquence reçue. L'IA valide l'arythmie avec une probabilité de risque élevé et classe sa typologie exacte.
- **Étape 5 (Dashboard Clinique)** : L'alerte confirmée par l'IA apparaît sur le bandeau du **Doctor Dashboard**, accompagnée du segment ECG critique, permettant au médecin une prise en charge médicale précise et informée.

*(Veuillez insérer ici les captures d'écran de l'Application Mobile (Flutter) affichant l'alerte locale, ainsi que le Doctor Dashboard (Vite) affichant les jauges IA post-synchronisation.)*

## 5.5 Conclusion

L'architecture hybride de la plateforme Smart TwinPac (KeepBeat) démontre une approche clinique optimale. En déportant des algorithmes déterministes (Pan-Tompkins, Coulomb Counter, Analyseur de Glucose) directement sur le smartphone (Edge), le patient bénéficie d'une sécurité totale et instantanée sans dépendre d'une connexion réseau. La synchronisation intelligente par Wi-Fi permet de soulager le réseau tout en confiant l'analyse prédictive lourde et la classification fine à un backend FastAPI robuste, équipé de réseaux de neurones profonds (TensorFlow/Keras). Cette séparation des préoccupations assure à la fois la survie immédiate du patient et le suivi longitudinal de haute précision pour les cardiologues via le Doctor Dashboard.

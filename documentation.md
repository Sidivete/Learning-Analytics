# Documentation Technique
## Projet : Prédiction de la Réussite Étudiante via l'Analyse des Traces Numériques

---

## 1. Introduction

### 1.1 Contexte
Ce projet s'inscrit dans le domaine du **Learning Analytics**, une discipline qui utilise les données d'apprentissage pour comprendre et optimiser les parcours éducatifs. L'objectif est d'exploiter les traces numériques laissées par les apprenants sur la plateforme ARCHE (basée sur Moodle) pour prédire leur réussite académique.

### 1.2 Problématique Centrale
> **Peut-on prédire la réussite d'un apprenant en analysant ses traces numériques au sein de la plateforme ARCHE ?**

L'enjeu est de construire un modèle prédictif fiable capable d'anticiper le succès ou l'échec d'un apprenant dans un cours donné, en se basant uniquement sur l'analyse de son activité sur la plateforme.

### 1.3 Objectifs
- Identifier les comportements d'apprentissage liés à la réussite
- Construire des features pertinentes à partir des logs d'activité
- Entraîner et évaluer plusieurs modèles de classification
- Développer une application interactive de diagnostic

---

## 2. Description des Données

### 2.1 Sources de Données

**Source 1 : Logs ARCHE (CSV)**

Contient les traces d'activités de chaque apprenant.

| Colonne | Description |
|---------|-------------|
| `heure` | Horodatage de l'action |
| `pseudo` | Identifiant anonymisé de l'apprenant |
| `contexte` | Ressource consultée (Quiz, Fichier, Cours...) |
| `composant` | Type d'activité (Test, Système, Fichier, Forum...) |
| `evenement` | Description précise de l'action |

**Source 2 : Gestion des Notes (CSV)**

| Colonne | Description |
|---------|-------------|
| `pseudo` | Identifiant de l'apprenant |
| `note` | Note obtenue (sur 20) |

### 2.2 Statistiques Initiales

| Fichier | Lignes | Colonnes | NaN | Doublons |
|---------|--------|----------|-----|----------|
| log.csv | 16 227 | 5 | 0% | 28 |
| notes.csv | 99 | 2 | 0% | 0 |

---

## 3. Phase 1 : ETL (Extract, Transform, Load)

### 3.1 Extraction
Les données sont chargées depuis les fichiers CSV sources à l'aide de pandas.

### 3.2 Nettoyage des Données

**Analyse des doublons**

Deux types de doublons ont été identifiés :

**Type 1 : Doublons exacts**
- Définition : Lignes 100% identiques (même seconde, même tout)
- Résultat : 28 lignes détectées
- Cause : Bug technique (double enregistrement)
- Action : Suppression avec `drop_duplicates()`

**Type 2 : Répétitions identiques < 5 secondes**
- Définition : Même étudiant, même action, moins de 5 secondes d'écart
- Résultat : 246 lignes détectées (sur 7 773 actions rapprochées)
- Cause : Double-clics, bugs de navigation
- Action : Suppression avec masque booléen `log_clean = log_clean[~mask_bug]`

**Résultat du nettoyage**

| Étape | Lignes | Supprimées |
|-------|--------|------------|
| Dataset original | 16 227 | - |
| Après doublons exacts | 16 199 | -28 |
| Après répétitions < 5 sec | 15 975 | -224 |
| **Total supprimé** | - | **252** |

### 3.3 Transformation
- Conversion de la colonne `heure` en datetime
- Extraction des composantes temporelles (jour_semaine, heure_journee, mois)

---

## 4. Phase 2 : Analyse Exploratoire (EDA)

### 4.1 Objectif
Comprendre les données selon 4 axes d'analyse pour identifier les patterns liés à la réussite.

### 4.2 Axe 1 : Temporel
**Objectif** : Identifier quand les étudiants travaillent

**Résultats clés :**
- Pic d'activité en Novembre 2024 (période d'examens)
- Jours les plus actifs : Weekend (samedi, dimanche)
- Heures les plus actives : 8h-11h, 14h-17h, 18h-22h

### 4.3 Axe 2 : Comportemental
**Objectif** : Comprendre les types d'actions réalisées

**Distribution des composants :**
- Test : 58%
- Système : 24%
- Fichier : 17%
- Autres : 1%

### 4.4 Axe 3 : Individuel
**Objectif** : Mesurer le niveau d'engagement de chaque étudiant

**Statistiques des actions par étudiant :**
- Minimum : 1 action
- Maximum : 1 782 actions
- Moyenne : 147 actions
- Médiane : 71 actions

### 4.5 Axe 4 : Ressources
**Objectif** : Identifier les ressources les plus consultées

- 108 ressources disponibles sur la plateforme
- Moyenne : 23 ressources consultées par étudiant (21% du total)

### 4.6 Corrélations avec la Note

| Variable | Corrélation |
|----------|-------------|
| nb_ressources | 0.440 |
| nb_consultations | 0.361 |
| nb_actions | 0.355 |
| intensite_moyenne | 0.336 |
| actions_weekend | 0.334 |
| nb_tests | 0.308 |
| actions_soir | 0.242 |
| nb_jours_actifs | 0.213 |
| taux_procrastination | -0.003 |
| ratio_etude | -0.150 |

### 4.7 Conclusion EDA

> **En résumé :** La réussite repose sur un trépied : **Curiosité** (variété des supports), **Engagement** (volume d'actions) et **Efficacité** (intensité de l'effort).

**Insights clés :**
- La **diversité des ressources** est le meilleur prédicteur (corr. 0.44)
- L'**intensité du travail** dépasse la simple régularité
- La **procrastination** n'est pas un facteur d'échec critique
- Un équilibre théorie/pratique favorise l'assimilation

---

## 5. Phase 3 : Feature Engineering

### 5.1 Objectif
Transformer les logs (plusieurs lignes par étudiant) en features (une ligne par étudiant).

### 5.2 Features Créées (10 variables)

| Catégorie | Feature | Description |
|-----------|---------|-------------|
| **Engagement** | `nb_actions` | Nombre total d'actions |
| | `nb_jours_actifs` | Jours différents avec activité |
| | `intensite_moyenne` | nb_actions / nb_jours_actifs |
| **Diversité** | `nb_ressources` | Ressources différentes consultées |
| **Comportement** | `nb_tests` | Nombre d'actions sur les Tests |
| | `nb_consultations` | Nombre de consultations |
| | `ratio_etude` | consultations / tests |
| **Temporel** | `actions_weekend` | Actions le weekend |
| | `actions_soir` | Actions le soir (18h-22h) |
| | `taux_procrastination` | Proportion d'activité tardive |

### 5.3 Variables Cibles

- `note` : Note finale (0-20) - pour la régression
- `reussite` : 1 si note >= 10, sinon 0 - pour la classification

### 5.4 Dataset Final

- **95 étudiants** avec logs ET notes
- **10 features** + 2 cibles (note, reussite)
- 14 étudiants exclus (pas de note)

---

## 6. Phase 4 : Modélisation

### 6.1 Configuration

**Split des données :**
- Train : 76 étudiants (80%)
- Test : 19 étudiants (20%)
- `random_state=42`

**Distribution de la cible :**
- Échec (0) : 53 étudiants (56%)
- Réussite (1) : 42 étudiants (44%)

### 6.2 Modèles Testés

#### Modèle 1 : Régression Logistique
```python
model_lr = make_pipeline(StandardScaler(), LogisticRegression(max_iter=1000, random_state=42))
```

| Métrique | Valeur |
|----------|--------|
| Accuracy (Test) | 0.58 |
| Moyenne CV | **0.65** |
| Stabilité CV | 0.04 |
| AUC | **0.73** |

**Matrice de confusion :** [[7, 3], [5, 4]]

**Bilan :** Modèle "conservateur" - identifie bien les échecs mais manque de sensibilité pour détecter les réussites (Recall faible sur classe 1).

#### Modèle 2 : Random Forest
```python
rf_model = RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)
```

| Métrique | Valeur |
|----------|--------|
| Accuracy (Test) | **0.74** |
| Moyenne CV | 0.58 |
| Écart-type CV | 0.06 |

**Bilan :** Écart important Test vs CV → **Overfitting**. Le modèle apprend des "bruits" qui ne se généralisent pas.

#### Modèle 3 : SVM
```python
model_svm = make_pipeline(StandardScaler(), SVC(kernel='linear', C=1.0, random_state=42))
```

| Métrique | Valeur |
|----------|--------|
| Accuracy (Test) | 0.63 |
| Moyenne CV | 0.59 |
| Écart-type CV | 0.04 |

**Bilan :** Performance intermédiaire, n'égale pas la robustesse de la Régression Logistique.

### 6.3 Tableau Comparatif Final

| Modèle | Accuracy (Test) | Moyenne CV | État |
|--------|-----------------|------------|------|
| **Régression Logistique** | 0.58 | **0.65** | ✓ Champion : Stable |
| Random Forest | **0.74** | 0.58 | ⚠ Overfitting |
| SVM | 0.63 | 0.59 | Moyen |

### 6.4 Importance des Features (Random Forest)

| Rang | Feature | Importance |
|------|---------|------------|
| 1 | intensite_moyenne | 16.4% |
| 2 | nb_ressources | 13.6% |
| 3 | nb_consultations | 13.4% |
| 4 | ratio_etude | 11.6% |
| 5 | actions_weekend | 9.8% |
| 6 | nb_actions | 9.7% |
| 7 | actions_soir | 9.4% |
| 8 | nb_tests | 9.4% |
| 9 | nb_jours_actifs | 5.8% |
| 10 | taux_procrastination | 0.9% |

### 6.5 Choix du Modèle Champion

La **Régression Logistique** est sélectionnée :

> **Principe du Rasoir d'Ockham** : "L'explication la plus simple est généralement la meilleure."

Avec 95 lignes et 10 variables, les modèles complexes (Random Forest, SVM) cherchent des règles trop précises qui ne s'appliquent qu'à quelques étudiants. La Régression Logistique dégage une **tendance générale plus solide**.

---

## 7. Phase 5 : Application (MVC + Streamlit)

### 7.1 Architecture MVC

```
main.py (Point d'entrée)
    │
    ├── controller.py (AppController)
    │       │
    │       ├── model.py (Predictor)
    │       │       └── Chargement model.pkl
    │       │       └── predict() + predict_proba()
    │       │
    │       └── view.py (Interface)
    │               └── Sélection étudiant
    │               └── Affichage résultat
    │               └── Graphique radar
```

### 7.2 Fichiers

| Fichier | Rôle |
|---------|------|
| `main.py` | Point d'entrée Streamlit |
| `model.py` | Classe Predictor (chargement modèle, prédiction) |
| `view.py` | Interface utilisateur (Streamlit) |
| `controller.py` | Orchestration Model-View |
| `config.py` | Chemins et configuration |

### 7.3 Fonctionnalités

- Filtre Train/Test pour sélection des étudiants
- Prédiction de réussite avec **indice de confiance** (predict_proba)
- Graphique radar comparant le profil étudiant vs moyenne de réussite
- Message de diagnostic personnalisé

---

## 8. Résultats et Conclusion

### 8.1 Synthèse des Leçons Apprises

> La réussite ne dépend pas de la **quantité** brute d'interactions, mais de la **qualité** de l'engagement.

**Enseignements Clés :**

1. **L'Intensité prime sur le Volume**
   - Le facteur prédictif n°1 est l'`intensite_moyenne`
   - Un étudiant qui travaille de manière dense réussit mieux qu'un étudiant multipliant les clics superficiels
   - *Conseil :* Privilégier des sessions de travail concentrées (ex: 45 min)

2. **L'Équilibre 50/50**
   - Un `ratio_etude` équilibré entre consultation (théorie) et exercices (pratique) est indispensable
   - *Conseil :* Appliquer systématiquement un test après chaque chapitre consulté

3. **Le Mythe de la Procrastination**
   - Commencer tardivement n'est pas un facteur d'échec critique (corrélation quasi nulle)
   - La réussite se joue sur la **régularité** et l'**effort fourni** une fois l'activité lancée

### 8.2 Verdict Technique

> Notre modèle de **Régression Logistique** est validé comme "Champion" avec un **AUC de 0.73**. Il offre le meilleur compromis entre simplicité, robustesse et fiabilité pour identifier précocement les étudiants à risque.

### 8.3 Limitations

- Dataset relativement petit (95 étudiants)
- Données d'un seul semestre
- Généralisation à d'autres cours à valider

### 8.4 Perspectives

- Enrichir le dataset avec d'autres semestres
- Tester XGBoost, Neural Networks
- Intégrer des alertes précoces en cours de semestre
- Déploiement en production (Docker, CI/CD)

---

## 9. Stack Technique

| Catégorie | Technologies |
|-----------|-------------|
| Langage | Python 3.11 |
| Data Processing | pandas, numpy |
| Visualisation | matplotlib, seaborn, plotly |
| Machine Learning | scikit-learn |
| Application | Streamlit |
| Sérialisation | joblib |

---

## 10. Structure du Projet

```
projet-py/
├── notebooks/
│   ├── EDA-FE.ipynb         # Exploration et Feature Engineering
│   └── Modelis.ipynb        # Modélisation
├── App/
│   ├── main.py              # Point d'entrée Streamlit
│   ├── model.py             # Classe Predictor
│   ├── view.py              # Interface utilisateur
│   ├── controller.py        # Contrôleur MVC
│   └── config.py            # Configuration
├── data/
│   ├── raw/                 # Données brutes
│   └── features.csv         # Features calculées
├── models/
│   └── model.pkl            # Modèle entraîné
└── README.md
```

---

Sidi BEDDY EL MOUSTAPHA 
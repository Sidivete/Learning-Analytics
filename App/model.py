import joblib 
import pandas as pd

class Predictor:
    def __init__ (self, path):
        self.chemin = path
        self.predit = None
        
    def import_mod(self):
        try:
            # On essaie d'allumer le moteur
            self.predit = joblib.load(self.chemin)
            print("Succès : Le modèle est chargé.")
            
        except Exception as e:
            print(f"Erreur critique : Impossible de charger le fichier. Détail : {e}")
            self.predit = None
    
    def charger_donnees(self):
        # On charge le fichier qui contient les logs
        df = pd.read_csv("features.csv") 
        return df
            
    def prediction(self, data):
        try:
            df = pd.DataFrame([data])
            
            colonnes_a_retirer = ['reussite', 'pseudo', 'note', 'dataset']
            df_propre = df.drop(columns=colonnes_a_retirer, errors='ignore')
            
            resultat = self.predit.predict(df_propre)[0]
            score = self.predit.predict_proba(df_propre)[0]
            return resultat, score
        except Exception as e:
            print(f"Erreur lors du calcul : {e}")
            return None, None
        
# test 
if __name__ == "__main__":
    #mod = Predictor("model.pkl")
    
    #mod.import_mod()
    
    # 1. Configuration
    print("Étape 1 : Création de l'objet...")
    MODEL = "model.pkl"
    
    FICHIER_CSV = "features.csv" # Ton fichier de données
    
    # 2. On prépare l'expert
    mon_expert = Predictor(MODEL)
    print("Étape 2 : Chargement du modèle (le plus long)...")
    mon_expert.import_mod()
    
    try:
        # 3. On pioche un étudiant réel dans ton CSV
        df_complet = pd.read_csv(FICHIER_CSV)
        
        # On prend la première ligne (index 0)
        # .to_dict('records')[0] transforme la ligne en format "étudiant"
        etudiant_reel = df_complet.iloc[0].to_dict()
        
        print(f"Test sur l'étudiant 1 du CSV...")

        # 4. On lance la prédiction
        verdict, confiance = mon_expert.prediction(etudiant_reel)
        
        # 5. Résultat
        print("-" * 30)
        print(f"RÉSULTAT DU TEST :")
        print(f"Verdict : {'RÉUSSITE' if verdict == 1 else 'ÉCHEC'}")
        print(f"Confiance : {confiance}")
        print("-" * 30)

    except Exception as e:
        print(f"Erreur pendant le test : {e}")
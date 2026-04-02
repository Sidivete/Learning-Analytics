from model import Predictor

class AppController:
    def __init__(self):
        self.expert = Predictor("model.pkl")
        self.expert.import_mod()

    def obtenir_donnees(self):
        return self.expert.charger_donnees()

    def traiter_analyse(self, etudiant_data):
        verdict, score = self.expert.prediction(etudiant_data)
        return verdict, score
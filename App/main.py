import streamlit as st
from controller import AppController
import view as view


ctrl = AppController()

df_logs = ctrl.obtenir_donnees()

etudiant_choisi = view.afficher_interface(df_logs)

if st.button("Lancer le diagnostic"):
    # Le contrôleur fait le travail
    res, proba = ctrl.traiter_analyse(etudiant_choisi)
    
    # La vue affiche le résultat
    view.afficher_resultat_final(res, proba, etudiant_choisi, df_logs)
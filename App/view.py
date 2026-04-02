import streamlit as st
import plotly.graph_objects as go

def afficher_interface(df):
    """Affiche le titre et le menu de sélection"""
    st.title("🎓 Système de Diagnostic Étudiant")
    st.write("Analyse des comportements d'apprentissage via l'IA")
    
    # Filtre Train/Test
    filtre = st.radio(
        "Afficher les étudiants :", 
        ["Tous", "Test uniquement", "Train uniquement"], 
        horizontal=True
    )
    
    if filtre == "Test uniquement":
        df_filtre = df[df['dataset'] == 'test']
    elif filtre == "Train uniquement":
        df_filtre = df[df['dataset'] == 'train']
    else:
        df_filtre = df
    
    # Liste déroulante des pseudos
    pseudo_choisi = st.selectbox(
        "Sélectionnez l'étudiant à analyser :", 
        df_filtre['pseudo'].unique()
    )
    
    # On extrait les données de cet étudiant précis
    etudiant_data = df[df['pseudo'] == pseudo_choisi].iloc[0].to_dict()
    
    return etudiant_data

def afficher_resultat_final(verdict, score, etudiant_data, df_complet):
    if verdict is None or score is None:
        st.error("🚨 L'IA n'a pas pu calculer de résultat. Vérifiez la console (terminal) pour l'erreur.")
        return
    
    """Affiche le verdict, le radar chart et la conclusion"""
    st.divider() 
    st.subheader("Diagnostic de l'Intelligence Artificielle")

    # Badge Train/Test (affiché ici après le clic)
    if etudiant_data.get('dataset') == 'test':
        st.success("✅ Étudiant du jeu de TEST (jamais vu par le modèle)")
    else:
        st.warning("⚠️ Étudiant du jeu de TRAIN (utilisé pour l'entraînement)")

    col1, col2 = st.columns(2)
    with col1:
        if verdict == 1:
            st.success("### PRÉDICTION : RÉUSSITE")
        else:
            st.error("### PRÉDICTION : ÉCHEC")
            
    with col2:
        confiance = score[1] if verdict == 1 else score[0]
        st.metric("Indice de confiance", f"{confiance:.2%}")

    # 2. Graphique Radar Normalisé
    st.write("#### Pourquoi ce résultat ?")
    categories = ['nb_actions', 'nb_tests', 'nb_jours_actifs', 'intensite_moyenne', 'nb_ressources']
    
    valeurs_etudiant = []
    moyennes_reussite = []
    df_reussite = df_complet[df_complet['reussite'] == 1]
    
    for cat in categories:
        max_val = df_complet[cat].max() if df_complet[cat].max() != 0 else 1
        valeurs_etudiant.append((etudiant_data[cat] / max_val) * 100)
        moyennes_reussite.append((df_reussite[cat].mean() / max_val) * 100)

    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(
        r=moyennes_reussite, theta=categories, fill='toself', 
        name='Moyenne de Réussite', line_color='rgba(46, 204, 113, 0.5)'
    ))
    fig.add_trace(go.Scatterpolar(
        r=valeurs_etudiant, theta=categories, fill='toself', 
        name='Profil Étudiant', line_color='rgba(231, 76, 60, 1)'
    ))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True
    )
    st.plotly_chart(fig)
    
    # 3. Message de conclusion
    if verdict == 0:
        st.warning("L'étudiant présente un déficit d'activité par rapport au profil type de réussite.")
    else:
        st.info("L'étudiant suit une trajectoire positive similaire aux profils validés.")
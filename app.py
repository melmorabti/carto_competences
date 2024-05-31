import streamlit as st
import pandas as pd
import plotly.express as px

# Correspondances des niveaux d'évaluation
niveau_linguistiques = {
    0: 'Découverte', 1: 'Intermédiaire', 2: 'Indépendant', 
    3: 'Avancé', 4: 'Autonome', 5: 'Maîtrise/Courant'
}

niveau_autres = {
    0: 'Non concerné', 1: 'Non acquis', 2: 'Connaissances génériques', 
    3: 'Confirmé', 4: 'Expert'
}

# Fonction pour obtenir le libellé de l'évaluation
def get_evaluation_label(domaine, niveau):
    if pd.isna(niveau):
        return 'Évaluation manquante'
    if domaine == 'Compétences linguistiques':
        return niveau_linguistiques.get(niveau, 'N/A')
    else:
        return niveau_autres.get(niveau, 'N/A')

# Fonction pour obtenir le niveau numérique de l'évaluation
def get_evaluation_level(domaine, libelle):
    if domaine == 'Compétences linguistiques':
        inverse_map = {v: k for k, v in niveau_linguistiques.items()}
    else:
        inverse_map = {v: k for k, v in niveau_autres.items()}
    return inverse_map.get(libelle, -1)

# Charger les données à partir d'un fichier Excel unique
uploaded_file = st.file_uploader("Choisissez un fichier Excel", type="xlsx")

if uploaded_file is not None:
    data = pd.read_excel(uploaded_file)

    # Ajouter une colonne pour les libellés des niveaux d'évaluation
    data['Auto-évaluation Libellé'] = data.apply(
        lambda row: get_evaluation_label(row['Domaine de compétence'], row['Auto-évaluation']), axis=1
    )
    
    data['Evaluation finale Libellé'] = data.apply(
        lambda row: get_evaluation_label(row['Domaine de compétence'], row['Evaluation finale']), axis=1
    )

    # Interface Streamlit
    st.title("Analyse des Compétences des Collaborateurs")

    # Filtre par compétence
    competences = data['Compétence'].unique()
    selected_competence = st.selectbox('Sélectionnez la Compétence', competences)

    # Filtrer les données pour la compétence sélectionnée
    selected_data = data[data['Compétence'] == selected_competence]

    # Affichage du domaine et du sous-domaine
    if not selected_data.empty:
        domaine = selected_data['Domaine de compétence'].iloc[0]
        sous_domaine = selected_data['Sous-domaine de compétence'].iloc[0]
        st.write(f"**Domaine de compétence :** {domaine}")
        st.write(f"**Sous-domaine de compétence :** {sous_domaine}")

    # Graphique de l'auto-évaluation
    st.write("Graphique de l'auto-évaluation par compétence")
    fig_auto_eval = px.pie(selected_data, names='Auto-évaluation Libellé', title=f'Auto-évaluation pour la compétence "{selected_competence}"',
                           hole=0.3)
    fig_auto_eval.update_traces(textposition='inside', textinfo='percent+label+value')

    st.plotly_chart(fig_auto_eval)

    # Préparation des données pour le tableau de l'auto-évaluation
    auto_eval_summary = selected_data.groupby('Auto-évaluation Libellé').agg(
        Nombre_de_collaborateurs=('Collaborateur', 'count'),
        Noms_des_collaborateurs=('Collaborateur', lambda x: ', '.join(x))
    ).reset_index()

    # Affichage du tableau de l'auto-évaluation
    st.write("Données de l'auto-évaluation")
    st.dataframe(auto_eval_summary)
    
    # Télécharger les données de l'auto-évaluation
    csv_auto_eval = auto_eval_summary.to_csv(index=False)
    st.download_button(label="Télécharger les données de l'auto-évaluation", data=csv_auto_eval, file_name='auto_evaluation_data.csv', mime='text/csv')

    # Graphique de l'évaluation finale
    st.write("Graphique de l'évaluation finale par compétence")
    fig_eval_finale = px.pie(selected_data, names='Evaluation finale Libellé', title=f'Évaluation finale pour la compétence "{selected_competence}"',
                             hole=0.3)
    fig_eval_finale.update_traces(textposition='inside', textinfo='percent+label+value')

    st.plotly_chart(fig_eval_finale)

    # Préparation des données pour le tableau de l'évaluation finale
    eval_finale_summary = selected_data.groupby('Evaluation finale Libellé').agg(
        Nombre_de_collaborateurs=('Collaborateur', 'count'),
        Noms_des_collaborateurs=('Collaborateur', lambda x: ', '.join(x))
    ).reset_index()

    # Affichage du tableau de l'évaluation finale
    st.write("Données de l'évaluation finale")
    st.dataframe(eval_finale_summary)
    
    # Télécharger les données de l'évaluation finale
    csv_eval_finale = eval_finale_summary.to_csv(index=False)
    st.download_button(label="Télécharger les données de l'évaluation finale", data=csv_eval_finale, file_name='evaluation_finale_data.csv', mime='text/csv')

    # Sélection du collaborateur pour comparer les évaluations
    st.write("Comparaison entre Auto-évaluation et Évaluation finale")
    collaborateurs = selected_data['Collaborateur'].unique()
    selected_collaborateur = st.selectbox('Sélectionnez le Collaborateur', collaborateurs)

    if selected_collaborateur:
        comparaison_data = selected_data[selected_data['Collaborateur'] == selected_collaborateur]
        
        if not comparaison_data.empty:
            eval_data = pd.DataFrame({
                'Type d\'évaluation': ['Auto-évaluation', 'Évaluation finale'],
                'Niveau': [
                    comparaison_data['Auto-évaluation'].iloc[0],
                    comparaison_data['Evaluation finale'].iloc[0]
                ]
            })

            # Graphique de comparaison
            fig_comparaison = px.bar(eval_data, x='Type d\'évaluation', y='Niveau', title=f'Comparaison pour {selected_collaborateur} sur la compétence "{selected_competence}"',
                                     labels={'Niveau': 'Niveau d\'évaluation'})
            st.plotly_chart(fig_comparaison)

    # Section pour le nombre de confirmés et d'experts par département pour une compétence donnée
    st.write("Nombre de Confirmés et Experts par Département pour une compétence donnée")
    selected_competence_for_department = st.selectbox('Sélectionnez la Compétence pour le Décompte par Département', competences, key='department_competence')
    
    if selected_competence_for_department:
        department_data = data[data['Compétence'] == selected_competence_for_department]
        
        confirmed_data = department_data[department_data['Evaluation finale Libellé'] == 'Confirmé']
        expert_data = department_data[department_data['Evaluation finale Libellé'] == 'Expert']
        
        confirmed_count = confirmed_data.groupby('Département').agg(
            Nombre_de_confirmés=('Collaborateur', 'count'),
            Collaborateurs=('Collaborateur', lambda x: ', '.join(x))
        ).reset_index()
        
        expert_count = expert_data.groupby('Département').agg(
            Nombre_d_experts=('Collaborateur', 'count'),
            Collaborateurs=('Collaborateur', lambda x: ', '.join(x))
        ).reset_index()
        
        st.write("Confirmés par Département")
        st.dataframe(confirmed_count)
        
        st.write("Experts par Département")
        st.dataframe(expert_count)

    # Section pour les compétences avec moins de 5 experts
    st.write("Compétences du domaine 'Compétences techniques ferroviaires' avec moins de 5 Experts")
    technical_skills = data[data['Domaine de compétence'] == 'Compétences techniques ferroviaires']
    expert_summary = technical_skills[technical_skills['Evaluation finale Libellé'] == 'Expert'].groupby('Compétence').agg(
        Nombre_d_experts=('Collaborateur', 'count')
    ).reset_index()
    
    less_than_5_experts = expert_summary[expert_summary['Nombre_d_experts'] < 5]
    st.dataframe(less_than_5_experts)

    # Section pour les compétences avec moins de 5 confirmés
    st.write("Compétences du domaine 'Compétences techniques ferroviaires' avec moins de 5 Confirmés")
    confirmed_summary = technical_skills[technical_skills['Evaluation finale Libellé'] == 'Confirmé'].groupby('Compétence').agg(
        Nombre_de_confirmés=('Collaborateur', 'count')
    ).reset_index()
    
    less_than_5_confirmed = confirmed_summary[confirmed_summary['Nombre_de_confirmés'] < 5]
    st.dataframe(less_than_5_confirmed)
    
    # Section pour les collaborateurs n'ayant pas atteint le niveau requis
    st.write("Collaborateurs n'ayant pas atteint le niveau requis pour chaque compétence")
    underqualified = data[data['Evaluation finale'] < data['Niveau requis']]
    underqualified_summary = underqualified.groupby('Collaborateur').agg(
        Competences=('Compétence', lambda x: ', '.join(x))
    ).reset_index()

    # Section pour les collaborateurs n'ayant pas atteint le niveau requis
    st.write("Collaborateurs n'ayant pas atteint le niveau requis pour chaque compétence")
    underqualified = data[data['Evaluation finale'] < data['Niveau requis']]
    underqualified_summary = underqualified.groupby('Collaborateur').agg(
        Competences=('Compétence', lambda x: ', '.join(x))
    ).reset_index()
    
    # Affichage du tableau des collaborateurs n'ayant pas atteint le niveau requis
    st.write("Tableau des collaborateurs n'ayant pas atteint le niveau requis")
    st.dataframe(underqualified_summary)


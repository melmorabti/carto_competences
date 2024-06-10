icalimport streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_option_menu import option_menu

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
    if domaine == 'Compétences linguistiques':
        return niveau_linguistiques.get(niveau, 'N/A')
    else:
        return niveau_autres.get(niveau, 'N/A')

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

    # Menu des onglets
    selected_tab = option_menu(
        menu_title=None,  # Hide the menu title
        options=["Auto-évaluation", "Évaluation finale", "Comparaison", "Confirmés et Experts par Département", "Alertes"],
        icons=["clipboard-check", "clipboard-data", "bar-chart", "building", "bell"],
        menu_icon="cast",
        default_index=0,
        orientation="vertical",  # Change orientation to vertical
    )

    # Filtre par domaine de compétence et compétence
    domaines = data['Domaine de compétence'].unique()
    selected_domaine = st.selectbox('Sélectionnez le Domaine de Compétence', domaines)
    competences = data[data['Domaine de compétence'] == selected_domaine]['Compétence'].unique()
    selected_competence = st.selectbox('Sélectionnez la Compétence', competences)
    selected_data = data[(data['Domaine de compétence'] == selected_domaine) & (data['Compétence'] == selected_competence)]

    # Affichage du domaine et du sous-domaine
    if not selected_data.empty:
        domaine = selected_data['Domaine de compétence'].iloc[0]
        sous_domaine = selected_data['Sous-domaine de compétence'].iloc[0]
        st.write(f"**Domaine de compétence :** {domaine}")
        st.write(f"**Sous-domaine de compétence :** {sous_domaine}")

    if selected_tab == "Auto-évaluation":
        st.header("Auto-évaluation")
        # Graphique de l'auto-évaluation
        st.write("Graphique de l'auto-évaluation par compétence")
        fig_auto_eval = px.pie(selected_data, names='Auto-évaluation Libellé', title=f'Auto-évaluation pour la compétence "{selected_competence}"', hole=0.3)
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

    elif selected_tab == "Évaluation finale":
        st.header("Évaluation finale")
        # Graphique de l'évaluation finale
        st.write("Graphique de l'évaluation finale par compétence")
        fig_eval_finale = px.pie(selected_data, names='Evaluation finale Libellé', title=f'Évaluation finale pour la compétence "{selected_competence}"', hole=0.3)
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

    elif selected_tab == "Comparaison":
        st.header("Comparaison entre Auto-évaluation et Évaluation finale")
        # Sélectionner un collaborateur
        collaborateurs = data['Collaborateur'].unique()
        selected_collaborateur = st.selectbox('Sélectionnez le Collaborateur', collaborateurs)

        # Filtrer les données pour le collaborateur sélectionné
        data_collaborateur = data[data['Collaborateur'] == selected_collaborateur]

        if not data_collaborateur.empty:
            # Graphique comparatif
            fig_comparaison = px.bar(data_collaborateur[data_collaborateur['Compétence'] == selected_competence],
                                     x='Compétence',
                                     y=['Auto-évaluation', 'Evaluation finale'],
                                     barmode='group',
                                     title=f'Comparaison pour {selected_collaborateur} sur la compétence "{selected_competence}"')
            st.plotly_chart(fig_comparaison)

    elif selected_tab == "Confirmés et Experts par Département":
        st.header("Confirmés et Experts par Département")
        selected_competence_dept = st.selectbox('Sélectionnez la Compétence pour le Département', competences)
        data_competence_dept = data[data['Compétence'] == selected_competence_dept]

        # Compter le nombre de confirmés et d'experts pour tout l'établissement
        total_confirmes = data_competence_dept[data_competence_dept['Evaluation finale Libellé'] == 'Confirmé']['Collaborateur'].nunique()
        total_experts = data_competence_dept[data_competence_dept['Evaluation finale Libellé'] == 'Expert']['Collaborateur'].nunique()
        
        st.write(f"Nombre total de Confirmés pour la compétence '{selected_competence_dept}': {total_confirmes}")
        st.write(f"Nombre total d'Experts pour la compétence '{selected_competence_dept}': {total_experts}")

        # Compter le nombre de confirmés et d'experts par département
        dept_summary = data_competence_dept.groupby(['Département', 'Evaluation finale Libellé']).agg(
            Nombre_de_collaborateurs=('Collaborateur', 'count'),
            Noms_des_collaborateurs=('Collaborateur', lambda x: ', '.join(x))
        ).reset_index()

        st.write("Nombre de Confirmés et d'Experts par Département")
        st.dataframe(dept_summary.style.hide(axis='index'))
        
        # Télécharger les données
        csv_dept_summary = dept_summary.to_csv(index=False)
        st.download_button(label="Télécharger les données par Département", data=csv_dept_summary, file_name='dept_summary_data.csv', mime='text/csv')

    elif selected_tab == "Alertes":
        st.header("Alertes")

                # Compétences du domaine 'Compétences techniques ferroviaires' avec moins de 5 Confirmés
        st.subheader("Compétences du domaine 'Compétences techniques ferroviaires' avec moins de 5 Confirmés")
        alerte_confirmes = data[(data['Domaine de compétence'] == 'Compétences techniques ferroviaires') & 
                                (data['Evaluation finale Libellé'] == 'Confirmé')].groupby('Compétence').filter(lambda x: x['Collaborateur'].nunique() < 5)
        st.dataframe(alerte_confirmes)

        # Section pour les collaborateurs n'ayant pas atteint le niveau requis
        st.header("Collaborateurs n'ayant pas atteint le niveau requis")
        underqualified = data[data['Evaluation finale'] < data['Niveau requis']]
        underqualified_summary = underqualified.groupby('Collaborateur').agg(
            Competences=('Compétence', lambda x: ', '.join(x))
        ).reset_index()
    
        # Affichage du tableau des collaborateurs n'ayant pas atteint le niveau requis
        st.write("Collaborateurs n'ayant pas atteint le niveau requis")
        st.dataframe(underqualified_summary)
        
        # Télécharger les données des collaborateurs n'ayant pas atteint le niveau requis
        csv_underqualified = underqualified_summary.to_csv(index=False)
        st.download_button(label="Télécharger les données des collaborateurs n'ayant pas atteint le niveau requis", data=csv_underqualified, file_name='underqualified_data.csv', mime='text/csv')

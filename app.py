import streamlit as st
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

    # Menu des onglets
    with st.sidebar:
        selected = option_menu(
            "Menu",
            ["Auto-évaluation", "Évaluation finale", "Comparaison", "Nombre de Confirmés et Experts", "Alertes"],
            icons=['bar-chart', 'bar-chart', 'bar-chart', 'list', 'exclamation'],
            menu_icon="cast",
            default_index=0,
        )

    # Onglet Auto-évaluation
    if selected == "Auto-évaluation":
        st.header("Auto-évaluation")
        fig_auto_eval = px.pie(selected_data, names='Auto-évaluation Libellé', title=f'Auto-évaluation pour la compétence "{selected_competence}"', hole=0.3)
        fig_auto_eval.update_traces(textposition='inside', textinfo='percent+label+value')
        st.plotly_chart(fig_auto_eval)

        auto_eval_summary = selected_data.groupby('Auto-évaluation Libellé').agg(
            Nombre_de_collaborateurs=('Collaborateur', 'count'),
            Noms_des_collaborateurs=('Collaborateur', lambda x: ', '.join(x))
        ).reset_index()

        st.write("Données de l'auto-évaluation")
        st.dataframe(auto_eval_summary)
        
        csv_auto_eval = auto_eval_summary.to_csv(index=False)
        st.download_button(label="Télécharger les données de l'auto-évaluation", data=csv_auto_eval, file_name='auto_evaluation_data.csv', mime='text/csv')

    # Onglet Évaluation finale
    elif selected == "Évaluation finale":
        st.header("Évaluation finale")
        fig_eval_finale = px.pie(selected_data, names='Evaluation finale Libellé', title=f'Évaluation finale pour la compétence "{selected_competence}"', hole=0.3)
        fig_eval_finale.update_traces(textposition='inside', textinfo='percent+label+value')
        st.plotly_chart(fig_eval_finale)

        eval_finale_summary = selected_data.groupby('Evaluation finale Libellé').agg(
            Nombre_de_collaborateurs=('Collaborateur', 'count'),
            Noms_des_collaborateurs=('Collaborateur', lambda x: ', '.join(x))
        ).reset_index()

        st.write("Données de l'évaluation finale")
        st.dataframe(eval_finale_summary)
        
        csv_eval_finale = eval_finale_summary.to_csv(index=False)
        st.download_button(label="Télécharger les données de l'évaluation finale", data=csv_eval_finale, file_name='evaluation_finale_data.csv', mime='text/csv')

    # Onglet Comparaison
    elif selected == "Comparaison":
        st.header("Comparaison entre Auto-évaluation et Évaluation finale")
        collaborateurs = selected_data['Collaborateur'].unique()
        selected_collaborateur = st.selectbox('Sélectionnez le Collaborateur', collaborateurs)

        if selected_collaborateur:
            collab_data = selected_data[selected_data['Collaborateur'] == selected_collaborateur]
            fig_comparaison = px.bar(
                collab_data.melt(id_vars=['Collaborateur', 'Compétence'], value_vars=['Auto-évaluation Libellé', 'Evaluation finale Libellé'], 
                                 var_name='Type', value_name='Niveau'),
                x='Compétence', y='Niveau', color='Type', barmode='group',
                title=f'Comparaison des évaluations pour le collaborateur {selected_collaborateur}'
            )
            st.plotly_chart(fig_comparaison)

    # Onglet Nombre de Confirmés et Experts
    elif selected == "Nombre de Confirmés et Experts":
        st.header("Nombre de Confirmés et Experts par Département")
        selected_competence = st.selectbox('Sélectionnez une Compétence', competences)
        if selected_competence:
            filtered_data = data[data['Compétence'] == selected_competence]
            confirmes_experts = filtered_data[filtered_data['Evaluation finale Libellé'].isin(['Confirmé', 'Expert'])]
            confirmes_experts_summary = confirmes_experts.groupby(['Département', 'Evaluation finale Libellé']).agg(
                Nombre_de_collaborateurs=('Collaborateur', 'count'),
                Noms_des_collaborateurs=('Collaborateur', lambda x: ', '.join(x))
            ).reset_index()

            st.write(f"Nombre de Confirmés et Experts par Département pour la compétence {selected_competence}")
            st.dataframe(confirmes_experts_summary)

    # Onglet Alertes
    elif selected == "Alertes":
        st.header("Alertes")
        experts_alert = data[(data['Domaine de compétence'] == 'Compétences techniques ferroviaires') &
                             (data['Evaluation finale Libellé'] == 'Expert')].groupby('Compétence').filter(lambda x: len(x) < 5)
        confirmes_alert = data[(data['Domaine de compétence'] == 'Compétences techniques ferroviaires') &
                               (data['Evaluation finale Libellé'] == 'Confirmé')].groupby('Compétence').filter(lambda x: len(x) < 5)

        st.write("Compétences du domaine 'Compétences techniques ferroviaires' avec moins de 5 Experts")
        st.dataframe(experts_alert[['Compétence', 'Collaborateur']].drop_duplicates())

        st.write("Compétences du domaine 'Compétences techniques ferroviaires' avec moins de 5 Confirmés")
        st.dataframe(confirmes_alert[['Compétence', 'Collaborateur']].drop_duplicates())
        
    # Section pour les collaborateurs n'ayant pas atteint le niveau requis
    if 'Niveau requis' in data.columns:
        st.header("Collaborateurs n'ayant pas atteint le niveau requis")
        underqualified = data[data['Evaluation finale'] < data['Niveau requis']]
        underqualified_summary = underqualified.groupby('Collaborateur').agg(
            Competences_non_atteintes=('Compétence', lambda x: ', '.join(x))
        ).reset_index()

        # Affichage du tableau des collaborateurs n'ayant pas atteint le niveau requis
        st.write("Collaborateurs n'ayant pas atteint le niveau requis pour leurs compétences")
        st.dataframe(underqualified_summary)

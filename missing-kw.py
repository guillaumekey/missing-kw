import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Configuration de la page en pleine largeur
st.set_page_config(
    page_title="Analyseur SEO - Opportunités de mots clés",
    page_icon="🎯",
    layout="wide"
)

# Style CSS personnalisé
st.markdown("""
    <style>
    /* Layout principal */
.main {
    padding: 0rem 1rem;
}

/* Barre latérale */
.stSidebar {
    background-color: #f5f5f0;
    padding: 2rem 1rem;
}

.sidebar-title {
    font-size: 1.2rem;
    font-weight: bold;
    margin-bottom: 1rem;
}

.sidebar-section {
    margin-bottom: 2rem;
}

/* Conteneur de tableau de données */
.dataframe-container {
    max-height: 700px;
    overflow-y: auto;
    border-radius: 8px;
    background-color: white;
    padding: 1rem;
    margin: 1rem 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* Conteneur des cartes de totaux */
.totals-container {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: stretch;
    margin: 1.5rem 0;
    gap: 1.5rem;
    width: 100%;
}

/* Style des cartes de totaux */
.totals-card {
    background-color: #f8f9fa;
    padding: 1.5rem;
    border-radius: 12px;
    box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
    text-align: center;
    flex: 1 1 calc(50% - 0.75rem);
    min-width: 0;
    display: flex;
    flex-direction: column;
    justify-content: center;
    transition: transform 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
}

.totals-card:hover {
    transform: translateY(-2px);
    box-shadow: 0px 6px 12px rgba(0, 0, 0, 0.15);
}

/* Titres et textes dans les cartes */
.totals-card h3 {
    font-size: 1.3rem;
    margin-bottom: 0.5rem;
    color: #333;
    overflow-wrap: break-word;
    word-wrap: break-word;
}

.totals-card p {
    font-size: 1.8rem;
    font-weight: bold;
    color: #79c39e;
    margin: 0;
    overflow-wrap: break-word;
    word-wrap: break-word;
}

/* Style des filtres */
.filter-container {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}

/* Style des boutons */
.stButton>button {
    width: 100%;
    background-color: #79c39e;
    color: white;
    border: none;
    padding: 0.5rem 1rem;
    border-radius: 6px;
    cursor: pointer;
    transition: background-color 0.2s;
}

.stButton>button:hover {
    background-color: #68b08d;
}

/* Style des inputs */
.stTextInput>div>div>input {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 0.5rem;
}

/* Style des select multiples */
.stMultiSelect>div>div>div {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
}

/* Style des tableaux */
.dataframe {
    width: 100%;
    border-collapse: collapse;
}

.dataframe th {
    background-color: #f8f9fa;
    padding: 0.75rem;
    text-align: left;
    border-bottom: 2px solid #dee2e6;
    font-weight: 600;
}

.dataframe td {
    padding: 0.75rem;
    border-bottom: 1px solid #dee2e6;
}

.dataframe tr:hover {
    background-color: #f8f9fa;
}

/* Style des messages d'erreur et d'avertissement */
.stAlert {
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

/* Media queries pour la responsivité */
@media screen and (max-width: 768px) {
    .totals-container {
        flex-direction: column;
    }
    
    .totals-card {
        flex: 1 1 100%;
    }
    
    .dataframe-container {
        max-height: 500px;
    }
}

/* Animations */
@keyframes fadeIn {
    from {
        opacity: 0;
        transform: translateY(10px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

.fade-in {
    animation: fadeIn 0.3s ease-in-out;
}
    </style>
""", unsafe_allow_html=True)

# Liste pour stocker les logs
global_logs = []

def log_message(message):
    global global_logs
    global_logs.append(message)

# Fonction pour afficher les logs dans un onglet séparé
def display_logs():
    st.subheader("📋 Logs de l'application")
    for log in global_logs:
        st.write(log)

def load_semrush_positions(file):
    log_message(f"Chargement du fichier des positions : {file.name}")
    try:
        df = pd.read_csv(file, sep=';')
        column_mapping = {
            'Search Volume': 'Volume',
            'CPC': 'CPC (USD)',
            'SERP Features by Keyword': 'SERP Features'
        }
        df = df.rename(columns=column_mapping)

        # Ajout de la colonne des tranches de positions
        def categorize_position(position):
            if 1 <= position <= 3:
                return "1-3"
            elif 4 <= position <= 10:
                return "4-10"
            elif 11 <= position <= 20:
                return "11-20"
            elif 21 <= position <= 50:
                return "21-50"
            elif 51 <= position <= 100:
                return "51-100"
            else:
                return "Autre"

        # Ajout de la colonne des tranches de Keyword Difficulty
        def categorize_keyword_difficulty(kd):
            if 0 <= kd <= 15:
                return "0-15"
            elif 16 <= kd <= 25:
                return "16-25"
            elif 26 <= kd <= 35:
                return "26-35"
            elif 36 <= kd <= 45:
                return "36-45"
            elif 46 <= kd <= 55:
                return "46-55"
            elif 56 <= kd <= 65:
                return "56-65"
            elif kd > 65:
                return ">65"
            else:
                return "Inconnu"

        df['Position Range'] = df['Position'].apply(categorize_position)
        df['Keyword Difficulty Range'] = df['Keyword Difficulty'].apply(categorize_keyword_difficulty)

        log_message(f"Fichier chargé avec {len(df)} lignes et {len(df.columns)} colonnes.")
        return df
    except Exception as e:
        st.error(f"Erreur lors du chargement des positions : {str(e)}")
        log_message(f"Erreur : {str(e)}")
        return pd.DataFrame()

def load_multiple_semrush_ideas(files):
    if not files:
        st.warning("Aucun fichier d'idées fourni.")
        return pd.DataFrame()

    all_ideas = []

    for file in files:
        try:
            log_message(f"Chargement du fichier d'idées : {file.name}")
            df = pd.read_csv(BytesIO(file.getvalue()), sep=';')
            df['Source'] = file.name
            all_ideas.append(df)
        except Exception as e:
            st.error(f"Erreur lors du chargement de {file.name} : {str(e)}")

    combined_df = pd.concat(all_ideas, ignore_index=True)

    # Suppression des doublons
    before_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset='Keyword', keep='first')
    after_dedup = len(combined_df)

    log_message(f"Fichiers combinés avec {before_dedup} lignes avant déduplication et {after_dedup} lignes après suppression des doublons.")

    return combined_df

def find_missing_keywords(positions_df, ideas_df):
    try:
        log_message("Recherche des mots clés manquants...")
        positions_keywords = set(positions_df['Keyword'].str.lower())
        ideas_keywords = set(ideas_df['Keyword'].str.lower())
        missing_keywords = ideas_keywords - positions_keywords

        missing_df = ideas_df[ideas_df['Keyword'].str.lower().isin(missing_keywords)].copy()
        log_message(f"{len(missing_keywords)} mots clés manquants détectés.")
        return missing_df
    except Exception as e:
        st.error(f"Erreur dans find_missing_keywords : {str(e)}")
        log_message(f"Erreur : {str(e)}")
        return pd.DataFrame()

def find_common_keywords(positions_df, ideas_df):
    try:
        log_message("Recherche des mots clés en commun...")
        positions_keywords = set(positions_df['Keyword'].str.lower())
        ideas_keywords = set(ideas_df['Keyword'].str.lower())
        common_keywords = positions_keywords & ideas_keywords

        common_df = positions_df[positions_df['Keyword'].str.lower().isin(common_keywords)].copy()
        log_message(f"{len(common_keywords)} mots clés en commun détectés.")
        return common_df
    except Exception as e:
        st.error(f"Erreur dans find_common_keywords : {str(e)}")
        log_message(f"Erreur : {str(e)}")
        return pd.DataFrame()

def apply_filters(df, position_ranges=None, kd_ranges=None):
    filtered_df = df.copy()

    if position_ranges:
        filtered_df = filtered_df[filtered_df['Position Range'].isin(position_ranges)]

    if kd_ranges:
        filtered_df = filtered_df[filtered_df['Keyword Difficulty Range'].isin(kd_ranges)]

    return filtered_df

def apply_keyword_filters(df, include_pattern=None, exclude_pattern=None):
    filtered_df = df.copy()

    if include_pattern:
        try:
            filtered_df = filtered_df[filtered_df['Keyword'].str.contains(include_pattern, case=False, regex=True)]
        except re.error:
            st.error("Expression régulière d'inclusion invalide")
            return df

    if exclude_pattern:
        try:
            filtered_df = filtered_df[~filtered_df['Keyword'].str.contains(exclude_pattern, case=False, regex=True)]
        except re.error:
            st.error("Expression régulière d'exclusion invalide")
            return df

    return filtered_df

def sidebar_content():
    st.sidebar.markdown("### 🎯 À propos de l'outil")
    st.sidebar.write("""
    Cet outil vous aide à identifier rapidement les opportunités SEO en analysant vos données SEMrush.
    """)

    st.sidebar.markdown("### 🔍 Fonctionnalités")
    st.sidebar.markdown("""
    - Identifie les mots clés non positionnés
    - Affiche les mots clés en commun
    - Analyse les métriques clés (Volume, KD, CPC)
    - Export des résultats en CSV
    - Support de multiples fichiers d'idées de mots clés
    """)

    st.sidebar.markdown("### 📊 Comment utiliser l'outil")
    st.sidebar.markdown("""
    1. Exportez vos données depuis SEMrush :
        - Positions organiques actuelles
        - Un ou plusieurs fichiers d'idées de mots clés (broad match)
    2. Uploadez les fichiers CSV
    3. Analysez les résultats
    4. Utilisez les filtres pour affiner l'analyse
    5. Exportez les données pour votre analyse
    """)

    st.sidebar.markdown("### ℹ️ Formats acceptés")
    st.sidebar.markdown("""
    - Fichiers CSV avec séparateur point-virgule (;)
    - Export standard SEMrush
    """)

# Main
log_message("Démarrage de l'application.")
st.title("🎯 Analyseur SEO")

sidebar_content()

# Onglets principaux
tabs = st.tabs(["Analyse", "Voir les logs"])

with tabs[0]:
    positions_file = st.file_uploader("Upload positions", type=["csv"])
    ideas_files = st.file_uploader("Upload multiple ideas", type=["csv"], accept_multiple_files=True)

    if positions_file and ideas_files:
        positions_df = load_semrush_positions(positions_file)
        ideas_df = load_multiple_semrush_ideas(ideas_files)

        if not positions_df.empty and not ideas_df.empty:
            # Tableau 1 : Mots clés non positionnés
            missing_keywords = find_missing_keywords(positions_df, ideas_df)
            st.subheader("📈 Mots clés non positionnés")
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
            include_pattern, exclude_pattern = st.columns(2)
            with include_pattern:
                include_regex = st.text_input("Inclure (regex)", key="missing_include")
            with exclude_pattern:
                exclude_regex = st.text_input("Exclure (regex)", key="missing_exclude")

            filtered_missing = apply_keyword_filters(missing_keywords, include_regex, exclude_regex)
            st.dataframe(filtered_missing)
            st.markdown('</div>', unsafe_allow_html=True)
            csv_missing = filtered_missing.to_csv(index=False, sep=';')
            st.download_button(
                label="📥 Télécharger les mots clés non positionnés",
                data=csv_missing,
                file_name="mots_cles_non_positionnes.csv",
                mime="text/csv"
            )

            # Totaux dynamiques pour les mots clés non positionnés
            st.markdown(f'''
                <div class="totals-container">
                    <div class="totals-card">
                        <h3>Nombre de mots clés non positionnés</h3>
                        <p>{len(filtered_missing)}</p>
                    </div>
                    <div class="totals-card">
                        <h3>Volume total</h3>
                        <p>{filtered_missing['Volume'].sum()}</p>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

            # Tableau 2 : Mots clés en commun
            common_keywords = find_common_keywords(positions_df, ideas_df)
            st.subheader("🎯 Mots clés en commun entre fichiers")
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)

            # Filtres pour les positions et KD
            include_common, exclude_common = st.columns(2)
            with include_common:
                include_regex_common = st.text_input("Inclure (regex)", key="common_include")
            with exclude_common:
                exclude_regex_common = st.text_input("Exclure (regex)", key="common_exclude")

            position_ranges = st.multiselect(
                "Sélectionnez les tranches de positions",
                options=["1-3", "4-10", "11-20", "21-50", "51-100", "Autre"],
                default=["1-3", "4-10"]
            )

            kd_ranges = st.multiselect(
                "Sélectionnez les tranches de Keyword Difficulty",
                options=["0-15", "16-25", "26-35", "36-45", "46-55", "56-65", ">65"],
                default=["0-15", "16-25"]
            )

            filtered_common = apply_filters(common_keywords, position_ranges, kd_ranges)
            filtered_common = apply_keyword_filters(filtered_common, include_regex_common, exclude_regex_common)
            st.dataframe(filtered_common)
            st.markdown('</div>', unsafe_allow_html=True)
            csv_common = filtered_common.to_csv(index=False, sep=';')
            st.download_button(
                label="📥 Télécharger les mots clés en commun",
                data=csv_common,
                file_name="mots_cles_en_commun.csv",
                mime="text/csv"
            )

            # Totaux dynamiques pour les mots clés en commun
            st.markdown(f'''
                <div class="totals-container">
                    <div class="totals-card">
                        <h3>Nombre de mots clés à optimiser</h3>
                        <p>{len(filtered_common)}</p>
                    </div>
                    <div class="totals-card">
                        <h3>Volume total des mots clés à optimiser</h3>
                        <p>{filtered_common['Volume'].sum()}</p>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

            # Tableau 3 : Répartition par tranches
            st.subheader("📊 Répartition des mots clés avec tranches de positions et KD")
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)

            include_distribution, exclude_distribution = st.columns(2)
            with include_distribution:
                include_regex_distribution = st.text_input("Inclure (regex)", key="distribution_include")
            with exclude_distribution:
                exclude_regex_distribution = st.text_input("Exclure (regex)", key="distribution_exclude")

            filtered_df = apply_filters(positions_df, position_ranges, kd_ranges)
            filtered_df = apply_keyword_filters(filtered_df, include_regex_distribution, exclude_regex_distribution)

            st.dataframe(filtered_df)
            st.markdown('</div>', unsafe_allow_html=True)
            csv_filtered = filtered_df.to_csv(index=False, sep=';')
            st.download_button(
                label="📥 Télécharger les mots clés filtrés",
                data=csv_filtered,
                file_name="mots_cles_filtres.csv",
                mime="text/csv"
            )

with tabs[1]:
    display_logs()

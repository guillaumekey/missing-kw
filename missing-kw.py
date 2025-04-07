import streamlit as st
import pandas as pd
import re
from io import BytesIO

# Page configuration in full width
st.set_page_config(
    page_title="SEO Analyzer - Keyword Opportunities",
    page_icon="🎯",
    layout="wide"
)

# Custom CSS style
st.markdown("""
    <style>
    /* Main layout */
.main {
    padding: 0rem 1rem;
}

/* Sidebar */
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

/* Dataframe container */
.dataframe-container {
    max-height: 700px;
    overflow-y: auto;
    border-radius: 8px;
    background-color: white;
    padding: 1rem;
    margin: 1rem 0;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

/* Totals cards container */
.totals-container {
    display: flex;
    flex-direction: row;
    justify-content: space-between;
    align-items: stretch;
    margin: 1.5rem 0;
    gap: 1.5rem;
    width: 100%;
}

/* Totals cards style */
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

/* Titles and text in cards */
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

/* Filter style */
.filter-container {
    background-color: #f8f9fa;
    padding: 1rem;
    border-radius: 8px;
    margin-bottom: 1rem;
}

/* Button style */
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

/* Input style */
.stTextInput>div>div>input {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
    padding: 0.5rem;
}

/* Multi select style */
.stMultiSelect>div>div>div {
    border: 1px solid #e0e0e0;
    border-radius: 4px;
}

/* Table style */
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

/* Error and warning message style */
.stAlert {
    padding: 1rem;
    border-radius: 8px;
    margin: 1rem 0;
}

/* Media queries for responsiveness */
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

# List to store logs
global_logs = []


def log_message(message):
    global global_logs
    global_logs.append(message)


# Function to display logs in a separate tab
def display_logs():
    st.subheader("📋 Application Logs")
    for log in global_logs:
        st.write(log)


def load_semrush_positions(file):
    log_message(f"Loading position file: {file.name}")
    try:
        df = pd.read_csv(file, sep=';')
        column_mapping = {
            'Search Volume': 'Volume',
            'CPC': 'CPC (USD)',
            'SERP Features by Keyword': 'SERP Features'
        }
        df = df.rename(columns=column_mapping)

        # Adding position range column
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
                return "Other"

        # Adding Keyword Difficulty range column
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
                return "Unknown"

        df['Position Range'] = df['Position'].apply(categorize_position)
        df['Keyword Difficulty Range'] = df['Keyword Difficulty'].apply(categorize_keyword_difficulty)

        log_message(f"File loaded with {len(df)} rows and {len(df.columns)} columns.")
        return df
    except Exception as e:
        st.error(f"Error loading positions: {str(e)}")
        log_message(f"Error: {str(e)}")
        return pd.DataFrame()


def load_multiple_semrush_ideas(files):
    if not files:
        st.warning("No idea files provided.")
        return pd.DataFrame()

    all_ideas = []

    for file in files:
        try:
            log_message(f"Loading idea file: {file.name}")
            df = pd.read_csv(BytesIO(file.getvalue()), sep=';')
            df['Source'] = file.name
            all_ideas.append(df)
        except Exception as e:
            st.error(f"Error loading {file.name}: {str(e)}")

    combined_df = pd.concat(all_ideas, ignore_index=True)

    # Removing duplicates
    before_dedup = len(combined_df)
    combined_df = combined_df.drop_duplicates(subset='Keyword', keep='first')
    after_dedup = len(combined_df)

    log_message(
        f"Files combined with {before_dedup} rows before deduplication and {after_dedup} rows after removing duplicates.")

    return combined_df


def find_missing_keywords(positions_df, ideas_df):
    try:
        log_message("Searching for missing keywords...")
        positions_keywords = set(positions_df['Keyword'].str.lower())
        ideas_keywords = set(ideas_df['Keyword'].str.lower())
        missing_keywords = ideas_keywords - positions_keywords

        missing_df = ideas_df[ideas_df['Keyword'].str.lower().isin(missing_keywords)].copy()
        log_message(f"{len(missing_keywords)} missing keywords detected.")
        return missing_df
    except Exception as e:
        st.error(f"Error in find_missing_keywords: {str(e)}")
        log_message(f"Error: {str(e)}")
        return pd.DataFrame()


def find_common_keywords(positions_df, ideas_df):
    try:
        log_message("Searching for common keywords...")
        positions_keywords = set(positions_df['Keyword'].str.lower())
        ideas_keywords = set(ideas_df['Keyword'].str.lower())
        common_keywords = positions_keywords & ideas_keywords

        common_df = positions_df[positions_df['Keyword'].str.lower().isin(common_keywords)].copy()
        log_message(f"{len(common_keywords)} common keywords detected.")
        return common_df
    except Exception as e:
        st.error(f"Error in find_common_keywords: {str(e)}")
        log_message(f"Error: {str(e)}")
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
            st.error("Invalid inclusion regex pattern")
            return df

    if exclude_pattern:
        try:
            filtered_df = filtered_df[~filtered_df['Keyword'].str.contains(exclude_pattern, case=False, regex=True)]
        except re.error:
            st.error("Invalid exclusion regex pattern")
            return df

    return filtered_df


def sidebar_content():
    st.sidebar.markdown("### 🎯 About the Tool")
    st.sidebar.write("""
    This tool helps you quickly identify SEO opportunities by analyzing your SEMrush data.
    """)

    st.sidebar.markdown("### 🔍 Features")
    st.sidebar.markdown("""
    - Identifies non-ranking keywords
    - Shows common keywords
    - Analyzes key metrics (Volume, KD, CPC)
    - Exports results to CSV
    - Supports multiple keyword idea files
    """)

    st.sidebar.markdown("### 📊 How to Use the Tool")
    st.sidebar.markdown("""
    1. Export your data from SEMrush:
        - Current organic positions
        - One or more keyword idea files (broad match)
    2. Upload the CSV files
    3. Analyze the results
    4. Use filters to refine your analysis
    5. Export the data for your analysis
    """)

    st.sidebar.markdown("### ℹ️ Accepted Formats")
    st.sidebar.markdown("""
    - CSV files with semicolon separator (;)
    - Standard SEMrush export
    """)


# Main
log_message("Starting application.")
st.title("🎯 SEO Analyzer")

sidebar_content()

# Main tabs
tabs = st.tabs(["Analysis", "View Logs"])

with tabs[0]:
    positions_file = st.file_uploader("Upload positions", type=["csv"])
    ideas_files = st.file_uploader("Upload multiple ideas", type=["csv"], accept_multiple_files=True)

    if positions_file and ideas_files:
        positions_df = load_semrush_positions(positions_file)
        ideas_df = load_multiple_semrush_ideas(ideas_files)

        if not positions_df.empty and not ideas_df.empty:
            # Table 1: Non-ranking keywords
            missing_keywords = find_missing_keywords(positions_df, ideas_df)
            st.subheader("📈 Non-Ranking Keywords")
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)
            include_pattern, exclude_pattern = st.columns(2)
            with include_pattern:
                include_regex = st.text_input("Include (regex)", key="missing_include")
            with exclude_pattern:
                exclude_regex = st.text_input("Exclude (regex)", key="missing_exclude")

            filtered_missing = apply_keyword_filters(missing_keywords, include_regex, exclude_regex)
            st.dataframe(filtered_missing)
            st.markdown('</div>', unsafe_allow_html=True)
            csv_missing = filtered_missing.to_csv(index=False, sep=';')
            st.download_button(
                label="📥 Download Non-Ranking Keywords",
                data=csv_missing,
                file_name="non_ranking_keywords.csv",
                mime="text/csv"
            )

            # Dynamic totals for non-ranking keywords
            st.markdown(f'''
                <div class="totals-container">
                    <div class="totals-card">
                        <h3>Number of Non-Ranking Keywords</h3>
                        <p>{len(filtered_missing)}</p>
                    </div>
                    <div class="totals-card">
                        <h3>Total Volume</h3>
                        <p>{filtered_missing['Volume'].sum()}</p>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

            # Table 2: Common keywords
            common_keywords = find_common_keywords(positions_df, ideas_df)
            st.subheader("🎯 Common Keywords Between Files")
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)

            # Filters for positions and KD
            include_common, exclude_common = st.columns(2)
            with include_common:
                include_regex_common = st.text_input("Include (regex)", key="common_include")
            with exclude_common:
                exclude_regex_common = st.text_input("Exclude (regex)", key="common_exclude")

            position_ranges = st.multiselect(
                "Select position ranges",
                options=["1-3", "4-10", "11-20", "21-50", "51-100", "Other"],
                default=["1-3", "4-10"]
            )

            kd_ranges = st.multiselect(
                "Select Keyword Difficulty ranges",
                options=["0-15", "16-25", "26-35", "36-45", "46-55", "56-65", ">65"],
                default=["0-15", "16-25"]
            )

            filtered_common = apply_filters(common_keywords, position_ranges, kd_ranges)
            filtered_common = apply_keyword_filters(filtered_common, include_regex_common, exclude_regex_common)
            st.dataframe(filtered_common)
            st.markdown('</div>', unsafe_allow_html=True)
            csv_common = filtered_common.to_csv(index=False, sep=';')
            st.download_button(
                label="📥 Download Common Keywords",
                data=csv_common,
                file_name="common_keywords.csv",
                mime="text/csv"
            )

            # Dynamic totals for common keywords
            st.markdown(f'''
                <div class="totals-container">
                    <div class="totals-card">
                        <h3>Number of Keywords to Optimize</h3>
                        <p>{len(filtered_common)}</p>
                    </div>
                    <div class="totals-card">
                        <h3>Total Volume of Keywords to Optimize</h3>
                        <p>{filtered_common['Volume'].sum()}</p>
                    </div>
                </div>
            ''', unsafe_allow_html=True)

            # Table 3: Distribution by ranges
            st.subheader("📊 Keyword Distribution by Position and KD Ranges")
            st.markdown('<div class="dataframe-container">', unsafe_allow_html=True)

            include_distribution, exclude_distribution = st.columns(2)
            with include_distribution:
                include_regex_distribution = st.text_input("Include (regex)", key="distribution_include")
            with exclude_distribution:
                exclude_regex_distribution = st.text_input("Exclude (regex)", key="distribution_exclude")

            filtered_df = apply_filters(positions_df, position_ranges, kd_ranges)
            filtered_df = apply_keyword_filters(filtered_df, include_regex_distribution, exclude_regex_distribution)

            st.dataframe(filtered_df)
            st.markdown('</div>', unsafe_allow_html=True)
            csv_filtered = filtered_df.to_csv(index=False, sep=';')
            st.download_button(
                label="📥 Download Filtered Keywords",
                data=csv_filtered,
                file_name="filtered_keywords.csv",
                mime="text/csv"
            )

with tabs[1]:
    display_logs()
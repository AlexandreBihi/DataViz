import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Analyse de Données", page_icon="📊", layout="wide")

# --- En-tête principal ---
st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h1 style="color: #4CAF50;">🧮 Data Explorer</h1>
        <p style="font-size: 18px;">Importez, visualisez et transformez vos fichiers CSV sans coder.</p>
    </div>
""", unsafe_allow_html=True)

# Onglets principaux
tab1, tab2, tab3 = st.tabs(["📂 Import des données", "📊 Visualisation", "🛠 Transformation des données"])

if "df" not in st.session_state:
    st.session_state.df = None

# --- Onglet 1 : Import des données ---
with tab1:
    st.markdown("## 📂 Chargement & Export")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📥 Import CSV")
        uploaded_file = st.file_uploader("Fichier CSV", type=["csv"])
        separator = st.radio("Séparateur :", [",", ";", "\t"])

    with col2:
        st.markdown("### ℹ️ Infos")
        st.markdown("- Données stockées localement")
        st.markdown("- Taille maximale conseillée : 50 Mo")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, sep=separator)
            st.session_state.df = df
            st.success("Fichier chargé avec succès ✅")

            st.markdown("### 👀 Aperçu")
            st.dataframe(df.head(10), use_container_width=True)

            st.markdown("### 📌 Résumé")
            st.write(f"- Lignes : {df.shape[0]}")
            st.write(f"- Colonnes : {df.shape[1]}")
            st.write("Types de colonnes :", df.dtypes.head(5))

            st.markdown("### 💾 Export")
            export_format = st.radio("Format de téléchargement :", ["CSV", "Excel"], index=0)
            if export_format == "CSV":
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Télécharger en CSV", data=csv_data, file_name="export.csv", mime="text/csv")
            else:
                df.to_excel("export.xlsx", index=False)
                with open("export.xlsx", "rb") as f:
                    st.download_button("📥 Télécharger en Excel", data=f, file_name="export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        except Exception as e:
            st.error(f"Erreur de lecture : {e}")

# --- Onglet 2 : Visualisation ---
with tab2:
    st.markdown("## 📊 Visualisation interactive")

    if st.session_state.df is not None:
        df = st.session_state.df
        numeric_columns = df.select_dtypes(include=["number"]).columns
        categorical_columns = df.select_dtypes(include=["object", "category"]).columns

        with st.expander("📌 Choix du type de graphique"):
            graph_type = st.selectbox("Type de graphique", [
                "Histogram", "Box Plot", "Scatter Plot", "Bar Chart",
                "Stacked Bar Chart", "Bubble Chart", "Treemap", "Pie Chart"
            ])

        with st.expander("🔧 Paramètres"):
            if graph_type in ["Histogram", "Box Plot"]:
                selected_column = st.selectbox("Colonne numérique", numeric_columns)
                color_column = st.selectbox("Colonne catégorielle (couleur)", [None] + list(categorical_columns))
                x_label = selected_column
                y_label = ""
            elif graph_type == "Scatter Plot":
                colx, coly = st.columns(2)
                with colx:
                    x_column = st.selectbox("X-axis", numeric_columns)
                with coly:
                    y_column = st.selectbox("Y-axis", numeric_columns)
                color_column = st.selectbox("Couleur", [None] + list(categorical_columns))
                x_label, y_label = x_column, y_column
            elif graph_type in ["Bar Chart", "Stacked Bar Chart", "Treemap", "Pie Chart"]:
                category_column = st.selectbox("Catégorie", categorical_columns)
                value_column = st.selectbox("Valeur", numeric_columns)
                x_label, y_label = category_column, value_column

            title = st.text_input("Titre du graphique", "")
            color_label = st.text_input("Titre de la légende", "")

        with st.expander("🎯 Filtres"):

            filtered_df = df.copy()

            st.markdown("##### 🔢 Numériques")
            selected_filters = []
            while True:
                available_columns = [col for col in numeric_columns if col not in selected_filters]
                if not available_columns:
                    break
                col_filter = st.selectbox("Colonne à filtrer", ["None"] + available_columns, key=f"num_filter_{len(selected_filters)}")
                if col_filter == "None":
                    break
                min_val, max_val = st.slider(f"{col_filter}", float(df[col_filter].min()), float(df[col_filter].max()), (float(df[col_filter].min()), float(df[col_filter].max())))
                filtered_df = filtered_df[(filtered_df[col_filter] >= min_val) & (filtered_df[col_filter] <= max_val)]
                selected_filters.append(col_filter)

            st.markdown("##### 🏷 Catégorielles")
            selected_cat_filters = []
            while True:
                available_cat = [col for col in categorical_columns if col not in selected_cat_filters]
                if not available_cat:
                    break
                cat_col = st.selectbox("Colonne à filtrer", ["None"] + available_cat, key=f"cat_filter_{len(selected_cat_filters)}")
                if cat_col == "None":
                    break
                values = st.multiselect(f"Valeurs de {cat_col}", df[cat_col].unique().tolist())
                if values:
                    filtered_df = filtered_df[filtered_df[cat_col].isin(values)]
                selected_cat_filters.append(cat_col)

        if graph_type == "Histogram":
            fig = px.histogram(filtered_df, x=selected_column, color=color_column, nbins=30, title=title)
        elif graph_type == "Box Plot":
            fig = px.box(filtered_df, y=selected_column, color=color_column, title=title)
        elif graph_type == "Scatter Plot":
            fig = px.scatter(filtered_df, x=x_column, y=y_column, color=color_column, title=title)
        elif graph_type == "Bar Chart":
            fig = px.bar(filtered_df, x=category_column, y=value_column, title=title)
        elif graph_type == "Stacked Bar Chart":
            stack_column = st.selectbox("Colonne empilée", categorical_columns)
            fig = px.bar(filtered_df, x=category_column, y=value_column, color=stack_column, title=title)
        elif graph_type == "Treemap":
            fig = px.treemap(filtered_df, path=[category_column], values=value_column, title=title)
        elif graph_type == "Pie Chart":
            fig = px.pie(filtered_df, names=category_column, values=value_column, title=title)
        else:
            fig = None

        if fig:
            fig.update_layout(xaxis_title=x_label, yaxis_title=y_label, legend_title=color_label)
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Veuillez importer un fichier CSV dans l'onglet d'import.")

# --- Onglet 3 : Transformation ---
with tab3:
    st.markdown("## 🛠 Préparation & Calculs")

    if st.session_state.df is not None:
        df = st.session_state.df

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 🔄 Conversion de type")
            column_to_convert = st.selectbox("Colonne à convertir", df.columns)
            new_type = st.radio("Type cible", ["int", "float", "string"])
            if st.button("Convertir"):
                try:
                    df[column_to_convert] = df[column_to_convert].astype(new_type)
                    st.session_state.df = df
                    st.success(f"✅ Conversion réussie en {new_type}")
                except Exception as e:
                    st.error(f"Erreur : {e}")

        with col2:
            st.markdown("### ⚠️ Valeurs manquantes")
            missing_cols = df.columns[df.isnull().any()].tolist()
            if missing_cols:
                col_to_fill = st.selectbox("Colonne à remplir", missing_cols)
                fill_method = st.radio("Méthode :", ["Moyenne", "Médiane", "Valeur fixe"])
                if fill_method in ["Moyenne", "Médiane"]:
                    try:
                        df[col_to_fill] = pd.to_numeric(df[col_to_fill], errors='coerce')
                        if fill_method == "Moyenne":
                            df[col_to_fill].fillna(df[col_to_fill].mean(), inplace=True)
                        else:
                            df[col_to_fill].fillna(df[col_to_fill].median(), inplace=True)
                        st.session_state.df = df
                        st.success(f"{col_to_fill} remplie avec {fill_method.lower()}")
                    except Exception as e:
                        st.error(str(e))
                else:
                    val = st.text_input("Valeur fixe")
                    if val:
                        df[col_to_fill].fillna(val, inplace=True)
                        st.session_state.df = df
                        st.success(f"{col_to_fill} remplie avec valeur : {val}")
            else:
                st.info("✅ Aucune valeur manquante")

        with col3:
            st.markdown("### ➕ Nouvelle colonne")
            new_col = st.text_input("Nom de la nouvelle colonne")
            formula = st.text_area("Formule (ex: col1 + col2)")
            if st.button("Créer colonne"):
                try:
                    df[new_col] = df.eval(formula)
                    st.session_state.df = df
                    st.success(f"✅ Colonne '{new_col}' créée")
                except Exception as e:
                    st.error(f"Erreur : {e}")

    else:
        st.warning("Importez un fichier dans l'onglet 1 pour transformer vos données.")

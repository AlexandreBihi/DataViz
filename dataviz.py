import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Analyse de Données", page_icon="📊", layout="wide")

# Titre principal stylisé
st.markdown("""
    <h1 style="text-align: center; color: #4CAF50;">📊 Analyse et Transformation de CSV</h1>
""", unsafe_allow_html=True)

# Onglets
tab1, tab2, tab3 = st.tabs(["📂 Import des données", "📊 Visualisation", "🛠 Transformation des données"])

# Déclaration d'une variable pour stocker les données
if "df" not in st.session_state:
    st.session_state.df = None

### Onglet 1 : Import des données ###
with tab1:
    st.markdown("## 📂 Import et Export de CSV")

    # Encadré d'import
    st.markdown(
        """<div style="border: 2px solid #4CAF50; padding: 15px; border-radius: 10px; background-color: #f9f9f9;">
        <h3 style="color: #4CAF50;">🆙 Importer un fichier CSV</h3>
        <p>Formats acceptés : <b>CSV</b>. Vous pouvez choisir un séparateur.</p>
        </div>""",
        unsafe_allow_html=True
    )

    # Upload du fichier CSV
    uploaded_file = st.file_uploader("Choisissez un fichier CSV", type=["csv"])
    separator = st.radio("Séparateur :", [",", ";", "\t"], index=0)

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, sep=separator)
            st.session_state.df = df  # Stocker le DataFrame dans la session

            st.subheader("📄 Aperçu des données")
            st.dataframe(df.head(10))

            # Option d'export
            st.subheader("💾 Télécharger les données")
            export_format = st.radio("Format de téléchargement :", ["CSV", "Excel"], index=0)

            if export_format == "CSV":
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Télécharger en CSV", data=csv_data, file_name="export.csv", mime="text/csv")
            else:
                excel_data = df.to_excel("export.xlsx", index=False)
                with open("export.xlsx", "rb") as f:
                    st.download_button("📥 Télécharger en Excel", data=f, file_name="export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        except Exception as e:
            st.error(f"Erreur lors du chargement du fichier : {e}")

### Tab 2: Data Visualization ###
with tab2:
    st.markdown("## 📊 Data Visualization")
    
    if st.session_state.df is not None:
        df = st.session_state.df
        numeric_columns = df.select_dtypes(include=["number"]).columns
        categorical_columns = df.select_dtypes(include=["object", "category"]).columns

        # 1) Graph Parameters
        st.markdown("### 📌 Graph Parameters")
        graph_type = st.selectbox("📈 Graph Type", [
            "Histogram", "Box Plot", "Scatter Plot", "Bar Chart",
            "Stacked Bar Chart", "Bubble Chart", "Treemap", "Pie Chart"])

        # 2) Choose Variable to Display
        st.markdown("### 📊 Choose Variables to Display")
        if graph_type in ["Histogram", "Box Plot"]:
            selected_column = st.selectbox("Choose a numeric column", numeric_columns)
            color_column = st.selectbox("Choose a categorical column for color (optional)", [None] + list(categorical_columns))
            x_label = selected_column
            y_label = ""
        elif graph_type == "Scatter Plot":
            col1, col2 = st.columns(2)
            with col1:
                x_column = st.selectbox("Choose X-axis variable", numeric_columns)
            with col2:
                y_column = st.selectbox("Choose Y-axis variable", numeric_columns)
            color_column = st.selectbox("Choose a categorical column for color (optional)", [None] + list(categorical_columns))
            x_label = x_column
            y_label = y_column
        elif graph_type in ["Bar Chart", "Stacked Bar Chart", "Treemap", "Pie Chart"] and len(categorical_columns) > 0:
            category_column = st.selectbox("Choose a categorical column", categorical_columns)
            value_column = st.selectbox("Choose a numeric column", numeric_columns)
            x_label = category_column
            y_label = value_column
        
        title = st.text_input("Graph Title", "")
        color_label = st.text_input("Color Label", "")

        # 3) Data Filtering
        st.markdown("### 🎯 Data Filtering")
        filtered_df = df.copy()
        filtered_df = filtered_df.reset_index()

        
        # Numeric Filtering
        st.markdown("#### 🔢 Numeric Filters")
        selected_filters = []
        while True:
            available_columns = [col for col in numeric_columns if col not in selected_filters]
            if not available_columns:
                break
            selected_column_filter = st.selectbox("Choose a numeric column to filter", ["None"] + available_columns, key=f"num_filter_{len(selected_filters)}")
            if selected_column_filter == "None":
                break
            min_val, max_val = st.slider(f"Select range for {selected_column_filter}",
                                         float(df[selected_column_filter].min()),
                                         float(df[selected_column_filter].max()),
                                         (float(df[selected_column_filter].min()), float(df[selected_column_filter].max())))
            filtered_df = filtered_df[(filtered_df[selected_column_filter] >= min_val) & (filtered_df[selected_column_filter] <= max_val)]
            filtered_df = filtered_df.reset_index()

            selected_filters.append(selected_column_filter)
        
        # Categorical Filtering
        st.markdown("#### 🏷 Categorical Filters")
        selected_cat_filters = []
        while True:
            available_cat_columns = [col for col in categorical_columns if col not in selected_cat_filters]
            if not available_cat_columns:
                break
            selected_cat_column = st.selectbox("Choose a categorical column to filter", ["None"] + available_cat_columns, key=f"cat_filter_{len(selected_cat_filters)}")
            if selected_cat_column == "None":
                break
            unique_values = df[selected_cat_column].unique().tolist()
            selected_values = st.multiselect(f"Select values for {selected_cat_column}", unique_values)
            if selected_values:
                filtered_df = filtered_df[filtered_df[selected_cat_column].isin(selected_values)]
                filtered_df = filtered_df.reset_index()

            selected_cat_filters.append(selected_cat_column)
        
        # Graph Rendering
        if graph_type == "Histogram":
            fig = px.histogram(filtered_df, x=selected_column, color=color_column, nbins=30, title=title)
        elif graph_type == "Box Plot":
            fig = px.box(filtered_df, y=selected_column, color=color_column, title=title)
        elif graph_type == "Scatter Plot":
            fig = px.scatter(filtered_df, x=x_column, y=y_column, color=color_column, title=title)
        elif graph_type == "Bar Chart":
            fig = px.bar(filtered_df, x=category_column, y=value_column, title=title)
        elif graph_type == "Stacked Bar Chart":
            stack_column = st.selectbox("Choose a stacking column", categorical_columns)
            fig = px.bar(filtered_df, x=category_column, y=value_column, color=stack_column, title=title)
        elif graph_type == "Treemap":
            fig = px.treemap(filtered_df, path=[category_column], values=value_column, title=title)
        elif graph_type == "Pie Chart":
            fig = px.pie(filtered_df, names=category_column, values=value_column, title=title)
        else:
            st.warning("No suitable data available for this chart type.")
            fig = None

        if fig:
            fig.update_layout(
                xaxis_title=x_label,
                yaxis_title=y_label,
                legend_title=color_label
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Please upload a CSV file in the 'Data Import' tab.")

        
### Onglet 3 : Transformation des données ###
with tab3:
    st.markdown("## 🛠 Transformation des données")

    if st.session_state.df is not None:
        df = st.session_state.df

        # Convertir une colonne en un autre type
        st.subheader("🔄 Conversion de type")
        column_to_convert = st.selectbox("Choisissez une colonne :", df.columns)
        new_type = st.radio("Convertir en :", ["int", "float", "string"])
        
        if st.button("Convertir"):
            try:
                if new_type == "int":
                    df[column_to_convert] = df[column_to_convert].astype(int)
                elif new_type == "float":
                    df[column_to_convert] = df[column_to_convert].astype(float)
                elif new_type == "string":
                    df[column_to_convert] = df[column_to_convert].astype(str)

                st.session_state.df = df
                st.success(f"La colonne '{column_to_convert}' a été convertie en {new_type}.")

            except Exception as e:
                st.error(f"Erreur lors de la conversion : {e}")

        # Remplacement des valeurs manquantes
        st.subheader("⚠️ Remplacement des valeurs manquantes")
        missing_columns = df.columns[df.isnull().any()].tolist()

        if missing_columns:
            column_to_fill = st.selectbox("Choisissez une colonne à remplir :", missing_columns)
            fill_method = st.radio("Méthode de remplissage :", ["Moyenne", "Médiane", "Valeur fixe"])

            if fill_method == "Moyenne":
                try:
                    df[column_to_fill] = pd.to_numeric(df[column_to_fill], errors='coerce')
                    df[column_to_fill].fillna(df[column_to_fill].mean(), inplace=True)
                except Exception as e:
                    st.error(f"Erreur lors du remplissage avec la moyenne : {e}")
            elif fill_method == "Médiane":
                try:
                    df[column_to_fill] = pd.to_numeric(df[column_to_fill], errors='coerce')
                    df[column_to_fill].fillna(df[column_to_fill].median(), inplace=True)
                except Exception as e:
                    st.error(f"Erreur lors du remplissage avec la médiane : {e}")
            else:
                custom_value = st.text_input("Entrez une valeur :")
                if custom_value:
                    df[column_to_fill].fillna(custom_value, inplace=True)

            st.session_state.df = df
            st.success(f"Les valeurs manquantes de '{column_to_fill}' ont été remplacées.")

        else:
            st.info("Aucune valeur manquante détectée.")

        # Création de colonnes calculées
        st.subheader("➕ Création d'une nouvelle colonne")
        new_col_name = st.text_input("Nom de la nouvelle colonne :")
        formula = st.text_area("Entrez une formule (ex: colonne1 + colonne2) :")

        if st.button("Créer la colonne"):
            try:
                df[new_col_name] = df.eval(formula)
                st.session_state.df = df
                st.success(f"La colonne '{new_col_name}' a été créée avec la formule '{formula}'.")
            except Exception as e:
                st.error(f"Erreur lors de la création : {e}")

    else:
        st.warning("Veuillez importer un fichier CSV dans l'onglet 'Import des données'.")
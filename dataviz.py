import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Analysis", page_icon="📊", layout="wide")

# --- Main header ---
st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h1 style="color: #4CAF50;">🧮 Data Explorer</h1>
        <p style="font-size: 18px;">Import, explore, and transform your CSV files without writing code.</p>
    </div>
""", unsafe_allow_html=True)

# Tabs
tab1, tab2, tab3 = st.tabs(["📂 Data Import", "📊 Visualization", "🛠 Data Transformation"])

if "df" not in st.session_state:
    st.session_state.df = None

# --- Tab 1: Import ---
with tab1:
    st.markdown("## 📂 Load & Export")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### 📥 Upload CSV")
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        separator = st.radio("Choose a separator:", [",", ";", "\t"])

    with col2:
        st.markdown("### ℹ️ Info")
        st.markdown("- Data stored locally in session")
        st.markdown("- Recommended max file size: 50 MB")

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, sep=separator)
            st.session_state.df = df
            st.success("✅ File uploaded successfully!")

            st.markdown("### 👀 Preview")
            st.dataframe(df.head(10), use_container_width=True)

            st.markdown("### 📌 Summary")
            st.write(f"- Rows: {df.shape[0]}")
            st.write(f"- Columns: {df.shape[1]}")
            st.write("Column types:", df.dtypes.head(5))

            st.markdown("### 💾 Export")
            export_format = st.radio("Choose export format:", ["CSV", "Excel"], index=0)
            if export_format == "CSV":
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 Download CSV", data=csv_data, file_name="export.csv", mime="text/csv")
            else:
                df.to_excel("export.xlsx", index=False)
                with open("export.xlsx", "rb") as f:
                    st.download_button("📥 Download Excel", data=f, file_name="export.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

        except Exception as e:
            st.error(f"Error reading file: {e}")

with tab2:
    st.markdown("## 📊 Interactive Visualization")

    if st.session_state.df is not None:
        df = st.session_state.df.copy()

        # Patch : rendre les colonnes Arrow-compatibles (ex : listes, dicts → str)
        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    df[col] = df[col].astype(str)
                except:
                    pass  # on ignore les cas tordus

        # Option de rechargement complet (avec rerun)
        with st.expander("🔁 Refresh Data"):
            if st.button("🔄 Reload dataframe and refresh types"):
                st.rerun()

        # Affichage des types de colonnes
        with st.expander("🧬 Column Types"):
            st.dataframe(df.dtypes.astype(str).rename("dtype"))

        # Sélection dynamique des colonnes
        numeric_columns = df.select_dtypes(include=["number"]).columns
        categorical_columns = df.select_dtypes(include=["object", "category", "string"]).columns

        with st.expander("📌 Select Chart Type"):
            graph_type = st.selectbox("Chart type", [
                "Histogram", "Box Plot", "Scatter Plot", "Bar Chart",
                "Stacked Bar Chart", "Bubble Chart", "Treemap", "Pie Chart"
            ])

        with st.expander("🔧 Parameters"):
            if graph_type in ["Histogram", "Box Plot"]:
                selected_column = st.selectbox("Numeric column", numeric_columns)
                color_column = st.selectbox("Color by (optional)", [None] + list(categorical_columns))
                x_label_default = selected_column
                y_label_default = "" if graph_type == "Histogram" else selected_column

            elif graph_type == "Scatter Plot":
                colx, coly = st.columns(2)
                with colx:
                    x_column = st.selectbox("X-axis", numeric_columns)
                with coly:
                    y_column = st.selectbox("Y-axis", numeric_columns)
                color_column = st.selectbox("Color by (optional)", [None] + list(categorical_columns))
                x_label_default, y_label_default = x_column, y_column

            elif graph_type in ["Bar Chart", "Stacked Bar Chart", "Treemap", "Pie Chart"]:
                category_column = st.selectbox("Category", categorical_columns)
                value_column = st.selectbox("Value", numeric_columns)
                x_label_default, y_label_default = category_column, value_column

            # Noms d'axes personnalisés
            x_label = st.text_input("X-axis label", x_label_default)
            y_label = st.text_input("Y-axis label", y_label_default)

            title = st.text_input("Chart title", "")
            color_label = st.text_input("Legend title", "")

        with st.expander("🎯 Filters"):
            filtered_df = df.copy()

            st.markdown("##### 🔢 Numeric Filters")
            selected_filters = []
            while True:
                available_columns = [col for col in numeric_columns if col not in selected_filters]
                if not available_columns:
                    break
                col_filter = st.selectbox("Select column", ["None"] + available_columns, key=f"num_filter_{len(selected_filters)}")
                if col_filter == "None":
                    break
                min_val, max_val = st.slider(f"{col_filter}", float(df[col_filter].min()), float(df[col_filter].max()), (float(df[col_filter].min()), float(df[col_filter].max())))
                filtered_df = filtered_df[(filtered_df[col_filter] >= min_val) & (filtered_df[col_filter] <= max_val)]
                selected_filters.append(col_filter)

            st.markdown("##### 🏷 Categorical Filters")
            selected_cat_filters = []
            while True:
                available_cat = [col for col in categorical_columns if col not in selected_cat_filters]
                if not available_cat:
                    break
                cat_col = st.selectbox("Select column", ["None"] + available_cat, key=f"cat_filter_{len(selected_cat_filters)}")
                if cat_col == "None":
                    break
                values = st.multiselect(f"Select values for {cat_col}", df[cat_col].unique().tolist())
                if values:
                    filtered_df = filtered_df[filtered_df[cat_col].isin(values)]
                selected_cat_filters.append(cat_col)

        # Génération du graphique
        fig = None
        if graph_type == "Histogram":
            fig = px.histogram(filtered_df, x=selected_column, color=color_column, nbins=30, title=title)
        elif graph_type == "Box Plot":
            fig = px.box(filtered_df, y=selected_column, color=color_column, title=title)
        elif graph_type == "Scatter Plot":
            fig = px.scatter(filtered_df, x=x_column, y=y_column, color=color_column, title=title)
        elif graph_type == "Bar Chart":
            fig = px.bar(filtered_df, x=category_column, y=value_column, title=title)
        elif graph_type == "Stacked Bar Chart":
            stack_column = st.selectbox("Stack by", categorical_columns)
            fig = px.bar(filtered_df, x=category_column, y=value_column, color=stack_column, title=title)
        elif graph_type == "Treemap":
            fig = px.treemap(filtered_df, path=[category_column], values=value_column, title=title)
        elif graph_type == "Pie Chart":
            fig = px.pie(filtered_df, names=category_column, values=value_column, title=title)

        if fig:
            fig.update_layout(
                xaxis_title=x_label,
                yaxis_title=y_label,
                legend_title=color_label
            )
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Please upload a file in the first tab.")


# --- Tab 3: Data Transformation ---
with tab3:
    st.markdown("## 🛠 Prepare & Calculate")

    if st.session_state.df is not None:
        df = st.session_state.df

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### 🔄 Convert Column Type")
            column_to_convert = st.selectbox("Select column", df.columns)
            new_type = st.radio("Target type", ["int", "float", "string"])
            if st.button("Convert"):
                try:
                    df[column_to_convert] = df[column_to_convert].astype(new_type)
                    st.session_state.df = df
                    st.success(f"✅ Column converted to {new_type}")
                except Exception as e:
                    st.error(f"Error: {e}")

        with col2:
            st.markdown("### ⚠️ Handle Missing Values")
            missing_cols = df.columns[df.isnull().any()].tolist()
            if missing_cols:
                col_to_fill = st.selectbox("Select column", missing_cols)
                fill_method = st.radio("Filling method", ["Mean", "Median", "Fixed value"])
                if fill_method in ["Mean", "Median"]:
                    try:
                        df[col_to_fill] = pd.to_numeric(df[col_to_fill], errors='coerce')
                        if fill_method == "Mean":
                            df[col_to_fill].fillna(df[col_to_fill].mean(), inplace=True)
                        else:
                            df[col_to_fill].fillna(df[col_to_fill].median(), inplace=True)
                        st.session_state.df = df
                        st.success(f"{col_to_fill} filled with {fill_method.lower()}")
                    except Exception as e:
                        st.error(str(e))
                else:
                    val = st.text_input("Fixed value")
                    if val:
                        df[col_to_fill].fillna(val, inplace=True)
                        st.session_state.df = df
                        st.success(f"{col_to_fill} filled with value: {val}")
            else:
                st.info("✅ No missing values detected")

        with col3:
            st.markdown("### ➕ Create New Column")
            new_col = st.text_input("New column name")
            formula = st.text_area("Formula (e.g. col1 + col2)")
            if st.button("Create column"):
                try:
                    df[new_col] = df.eval(formula)
                    st.session_state.df = df
                    st.success(f"✅ Column '{new_col}' created")
                except Exception as e:
                    st.error(f"Error: {e}")

    else:
        st.warning("Please upload a file first to use this section.")

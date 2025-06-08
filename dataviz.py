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
        if "df_updated" in st.session_state:
            del st.session_state.df_updated
            st.experimental_clear_cache()

        df = st.session_state.df.copy()

        # 🧪 Debug : aperçu des colonnes
        with st.expander("🧪 DEBUG – Columns and Types"):
            st.write("✅ Columns in memory:", df.columns.tolist())
            st.write("✅ Dtypes:", df.dtypes.astype(str).to_dict())

        # 🔄 Convert object columns to string (for Arrow compatibility)
        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    df[col] = df[col].astype(str)
                except:
                    pass

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

            x_label = st.text_input("X-axis label", x_label_default)
            y_label = st.text_input("Y-axis label", y_label_default)
            title = st.text_input("Chart title", "")
            color_label = st.text_input("Legend title", "")

        # Ajoute un graphique simple pour tester
        with st.expander("🎯 Try rendering (sanity check)"):
            st.write("🔍 Filtered columns used:", df.columns.tolist())

        fig = None
        try:
            if graph_type == "Pie Chart":
                fig = px.pie(df, names=category_column, values=value_column, title=title)
            elif graph_type == "Histogram":
                fig = px.histogram(df, x=selected_column, color=color_column, title=title)
            elif graph_type == "Box Plot":
                fig = px.box(df, y=selected_column, color=color_column, title=title)
            elif graph_type == "Scatter Plot":
                fig = px.scatter(df, x=x_column, y=y_column, color=color_column, title=title)
            elif graph_type == "Bar Chart":
                fig = px.bar(df, x=category_column, y=value_column, title=title)
            elif graph_type == "Stacked Bar Chart":
                stack_column = st.selectbox("Stack by", categorical_columns)
                fig = px.bar(df, x=category_column, y=value_column, color=stack_column, title=title)
            elif graph_type == "Treemap":
                fig = px.treemap(df, path=[category_column], values=value_column, title=title)
        except Exception as e:
            st.error(f"❌ Chart rendering error: {e}")

        if fig:
            fig.update_layout(xaxis_title=x_label, yaxis_title=y_label, legend_title=color_label)
            st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("Please upload a file in the first tab.")



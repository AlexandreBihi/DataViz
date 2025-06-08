import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Data Explorer", page_icon="📊", layout="wide")

st.markdown("""
    <div style="text-align: center; padding: 10px 0;">
        <h1 style="color: #4CAF50;">💎 Data Explorer</h1>
        <p style="font-size: 18px;">Import, explore, and transform your CSV files without writing code.</p>
    </div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["\ud83d\udcc2 Data Import", "\ud83d\udcca Visualization", "\ud83d\udee0 Data Transformation"])

if "df" not in st.session_state:
    st.session_state.df = None

# ---------------------------- TAB 1 ----------------------------
with tab1:
    st.markdown("## \ud83d\udcc2 Upload & Export")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("### \ud83d\udcc5 Upload CSV")
        uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
        separator = st.radio("Choose a separator:", [",", ";", "\t"])

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file, sep=separator)
            st.session_state.df = df.copy(deep=True)
            st.success("\u2705 File uploaded successfully!")
            st.dataframe(df.head(10), use_container_width=True)
        except Exception as e:
            st.error(f"Error reading file: {e}")

# ---------------------------- TAB 2 ----------------------------
with tab2:
    st.markdown("## \ud83d\udcca Interactive Visualization")

    if st.session_state.df is not None:
        if "df_updated" in st.session_state:
            del st.session_state.df_updated

        df = st.session_state.df.copy()

        with st.expander("\ud83e\uddea DEBUG – Columns and Types"):
            st.write("Columns:", df.columns.tolist())
            st.write("Types:", df.dtypes.astype(str).to_dict())

        for col in df.columns:
            if df[col].dtype == "object":
                try:
                    df[col] = df[col].astype(str)
                except:
                    pass

        numeric_columns = df.select_dtypes(include=["number"]).columns
        categorical_columns = df.select_dtypes(include=["object", "category", "string"]).columns

        with st.expander("\ud83d\udcc9 Select Chart Type"):
            graph_type = st.selectbox("Chart type", [
                "Histogram", "Box Plot", "Scatter Plot", "Bar Chart",
                "Stacked Bar Chart", "Bubble Chart", "Treemap", "Pie Chart"
            ])

        with st.expander("\ud83d\udd27 Parameters"):
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
            st.error(f"Chart rendering error: {e}")

        if fig:
            fig.update_layout(xaxis_title=x_label, yaxis_title=y_label, legend_title=color_label)
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("Please upload a file in the first tab.")

# ---------------------------- TAB 3 ----------------------------
with tab3:
    st.markdown("## \ud83d\udee0 Debug – Data Transformation")

    if st.session_state.df is not None:
        df = st.session_state.df.copy()

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown("### \ud83d\udd04 Convert Column Type")
            column_to_convert = st.selectbox("Select column", df.columns, key="convert_col")
            new_type = st.radio("Convert to:", ["int", "float", "string"], key="convert_type")
            if st.button("Convert", key="convert_button"):
                try:
                    df[column_to_convert] = df[column_to_convert].astype(new_type)
                    st.session_state.df = df.copy(deep=True)
                    st.session_state.df_updated = True
                    st.success(f"Column '{column_to_convert}' converted to {new_type}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Conversion error: {e}")

        with col2:
            st.markdown("### \u26a0\ufe0f Fill NA Values")
            na_cols = df.columns[df.isnull().any()].tolist()
            if na_cols:
                col_to_fill = st.selectbox("Select NA column", na_cols)
                method = st.radio("Method", ["Mean", "Median", "Fixed value"])
                if method == "Fixed value":
                    val = st.text_input("Value")
                    if st.button("Fill NA with fixed"):
                        df[col_to_fill] = df[col_to_fill].fillna(val)
                        st.session_state.df = df.copy(deep=True)
                        st.session_state.df_updated = True
                        st.success(f"Filled NA in '{col_to_fill}' with '{val}'")
                        st.rerun()
                else:
                    if st.button("Fill NA with stat"):
                        df[col_to_fill] = pd.to_numeric(df[col_to_fill], errors="coerce")
                        fill_val = df[col_to_fill].mean() if method == "Mean" else df[col_to_fill].median()
                        df[col_to_fill] = df[col_to_fill].fillna(fill_val)
                        st.session_state.df = df.copy(deep=True)
                        st.session_state.df_updated = True
                        st.success(f"Filled NA in '{col_to_fill}' with {method.lower()}")
                        st.rerun()
            else:
                st.info("No missing values found.")

        with col3:
            st.markdown("### \u2795 Create Column")
            new_col = st.text_input("New column name")
            formula = st.text_area("Formula (e.g. col1 + col2)")
            if st.button("Create column"):
                try:
                    df[new_col] = df.eval(formula)
                    st.session_state.df = df.copy(deep=True)
                    st.session_state.df_updated = True
                    if new_col in df.columns:
                        st.success(f"Column '{new_col}' created successfully.")
                    else:
                        st.error(f"Column '{new_col}' not found after creation!")
                    st.rerun()
                except Exception as e:
                    st.error(f"Formula error: {e}")

        with st.expander("\ud83d\udd0d Preview DataFrame"):
            st.dataframe(df.head(5))
            st.write("Columns:", df.columns.tolist())
            st.write("Types:", df.dtypes.astype(str).to_dict())

    else:
        st.warning("Please upload a file in the first tab.")

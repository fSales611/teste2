import streamlit as st
import pandas as pd
import numpy as np
import io
import base64
from data_processor import process_data, get_summary_stats, filter_data, detect_data_types
from visualizer import create_visualization, get_visualization_options
from data_assistant import query_data_with_rules
from utils import get_table_download_link, get_chart_download_link
from api_data_provider import (get_crypto_data, get_economic_indicators, 
                               get_covid_data, get_weather_data)

# Set page config
st.set_page_config(
    page_title="DataInsight Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state variables
if 'data' not in st.session_state:
    st.session_state.data = None
if 'processed_data' not in st.session_state:
    st.session_state.processed_data = None
if 'file_name' not in st.session_state:
    st.session_state.file_name = None
if 'chart' not in st.session_state:
    st.session_state.chart = None
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'data_source' not in st.session_state:
    st.session_state.data_source = None

# App header
st.title("DataInsight Pro")
st.markdown("### Análise e Visualização de Dados em Tempo Real")

# Sidebar for data upload and settings
with st.sidebar:
    st.header("Fonte de Dados")
    
    # Opções de fonte de dados
    data_source = st.radio(
        "Escolha a fonte de dados:",
        ["Fazer upload de arquivo", "APIs Públicas", "Conjuntos de dados de exemplo"]
    )
    st.session_state.data_source = data_source
    
    # Opção de upload de arquivo
    if data_source == "Fazer upload de arquivo":
        uploaded_file = st.file_uploader("Carregar arquivo de dados", type=['csv', 'xlsx', 'xls'])
        
        if uploaded_file is not None:
            try:
                # Process the uploaded file
                file_extension = uploaded_file.name.split('.')[-1]
                st.session_state.file_name = uploaded_file.name
                
                if file_extension.lower() == 'csv':
                    df = pd.read_csv(uploaded_file)
                elif file_extension.lower() in ['xlsx', 'xls']:
                    df = pd.read_excel(uploaded_file)
                else:
                    st.error("Formato de arquivo não suportado!")
                    df = None
                
                if df is not None:
                    st.session_state.data = df
                    st.session_state.processed_data = process_data(df)
                    st.success(f"Dados carregados com sucesso: {df.shape[0]} linhas e {df.shape[1]} colunas")
            except Exception as e:
                st.error(f"Erro ao carregar dados: {str(e)}")
    
    # Opção de APIs públicas
    elif data_source == "APIs Públicas":
        st.markdown("### Dados de APIs públicas em tempo real")
        api_source = st.selectbox(
            "Selecione a fonte de dados:",
            ["Selecione uma opção", "Criptomoedas (CoinGecko)", 
             "Indicadores Econômicos", "Dados de COVID-19", 
             "Dados Meteorológicos"]
        )
        
        if api_source != "Selecione uma opção":
            with st.spinner("Carregando dados da API..."):
                try:
                    if api_source == "Criptomoedas (CoinGecko)":
                        df = get_crypto_data()
                        st.session_state.file_name = "crypto_market_data.csv"
                    
                    elif api_source == "Indicadores Econômicos":
                        df = get_economic_indicators()
                        st.session_state.file_name = "economic_indicators.csv"
                    
                    elif api_source == "Dados de COVID-19":
                        df = get_covid_data()
                        st.session_state.file_name = "covid19_global_data.csv"
                    
                    elif api_source == "Dados Meteorológicos":
                        city = st.text_input("Digite o nome da cidade:", "São Paulo")
                        if st.button("Buscar dados meteorológicos"):
                            df = get_weather_data(city)
                            st.session_state.file_name = f"weather_data_{city}.csv"
                        else:
                            df = None
                    
                    if df is not None and not df.empty:
                        st.session_state.data = df
                        st.session_state.processed_data = process_data(df)
                        st.success(f"Dados da API carregados com sucesso: {df.shape[0]} linhas e {df.shape[1]} colunas")
                    elif df is not None and df.empty:
                        st.error("A API retornou um conjunto de dados vazio. Tente novamente mais tarde.")
                    
                except Exception as e:
                    st.error(f"Erro ao carregar dados da API: {str(e)}")
    
    # Opção de conjuntos de dados de exemplo
    elif data_source == "Conjuntos de dados de exemplo":
        example_dataset = st.selectbox(
            "Selecione um conjunto de dados:",
            ["Selecione uma opção", "Iris (Flores)", "Imóveis na Califórnia", 
             "Passageiros do Titanic"]
        )
        
        if example_dataset != "Selecione uma opção" and st.button("Carregar dados de exemplo"):
            try:
                if example_dataset == "Iris (Flores)":
                    from sklearn.datasets import load_iris
                    data = load_iris()
                    df = pd.DataFrame(data.data, columns=data.feature_names)
                    df['species'] = [data.target_names[i] for i in data.target]
                    st.session_state.file_name = "iris_dataset.csv"
                
                elif example_dataset == "Imóveis na Califórnia":
                    from sklearn.datasets import fetch_california_housing
                    data = fetch_california_housing()
                    df = pd.DataFrame(data.data, columns=data.feature_names)
                    df['PRICE'] = data.target
                    st.session_state.file_name = "california_housing.csv"
                    
                elif example_dataset == "Passageiros do Titanic":
                    url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
                    df = pd.read_csv(url)
                    st.session_state.file_name = "titanic.csv"
                
                st.session_state.data = df
                st.session_state.processed_data = process_data(df)
                st.success(f"Dados carregados com sucesso: {df.shape[0]} linhas e {df.shape[1]} colunas")
                
            except Exception as e:
                st.error(f"Erro ao carregar dados de exemplo: {str(e)}")
    
    # Configurações de dados (se dados foram carregados)
    if st.session_state.data is not None:
        st.header("Configurações de Análise")
        
        # Tamanho da amostra para análise
        sample_size = st.slider("Tamanho da amostra", 
                             min_value=100, 
                             max_value=min(10000, st.session_state.data.shape[0]), 
                             value=min(1000, st.session_state.data.shape[0]))
        
        # Aplicar tamanho da amostra
        if sample_size < st.session_state.data.shape[0]:
            st.session_state.processed_data = st.session_state.data.sample(sample_size).reset_index(drop=True)
        else:
            st.session_state.processed_data = st.session_state.data

# Main content area
if st.session_state.data is None:
    # Display welcome message when no data is loaded
    st.info("👋 Welcome to DataInsight Pro! Upload a CSV or Excel file to get started.")
    
    with st.expander("🔍 About DataInsight Pro"):
        st.markdown("""
        **DataInsight Pro** is a powerful data analysis tool that helps you:
        
        - 📊 Analyze your data with summary statistics
        - 🔍 Filter and explore your datasets
        - 📈 Create beautiful interactive visualizations
        - 💬 Chat with your data using our smart assistant
        - 📤 Share and export your findings
        
        Get started by uploading a CSV or Excel file using the sidebar, or try one of our example datasets.
        """)
        
else:
    # Create tabs for different functionalities
    tab1, tab2, tab3, tab4 = st.tabs(["Data Explorer", "Visualization Studio", "Data Assistant", "Share & Export"])
    
    with tab1:
        st.header("Data Explorer")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            # Show summary statistics
            st.subheader("Summary Statistics")
            summary_stats = get_summary_stats(st.session_state.processed_data)
            st.dataframe(summary_stats, use_container_width=True)
            
            # Data filtering options
            st.subheader("Filter Data")
            
            # Get columns for filtering
            numeric_cols = st.session_state.processed_data.select_dtypes(include=[np.number]).columns.tolist()
            categorical_cols = st.session_state.processed_data.select_dtypes(exclude=[np.number]).columns.tolist()
            
            # Filter by category
            if categorical_cols:
                selected_cat_col = st.selectbox("Select categorical column", ["None"] + categorical_cols)
                
                if selected_cat_col != "None":
                    unique_values = st.session_state.processed_data[selected_cat_col].dropna().unique().tolist()
                    selected_values = st.multiselect("Select values", unique_values, default=unique_values[:min(5, len(unique_values))])
                    
                    if selected_values:
                        st.session_state.processed_data = filter_data(
                            st.session_state.processed_data, 
                            selected_cat_col, 
                            selected_values
                        )
            
            # Filter by numeric range
            if numeric_cols:
                selected_num_col = st.selectbox("Select numeric column", ["None"] + numeric_cols)
                
                if selected_num_col != "None":
                    min_val = float(st.session_state.processed_data[selected_num_col].min())
                    max_val = float(st.session_state.processed_data[selected_num_col].max())
                    
                    range_values = st.slider(
                        f"Range for {selected_num_col}", 
                        min_value=min_val,
                        max_value=max_val,
                        value=(min_val, max_val)
                    )
                    
                    st.session_state.processed_data = st.session_state.processed_data[
                        (st.session_state.processed_data[selected_num_col] >= range_values[0]) & 
                        (st.session_state.processed_data[selected_num_col] <= range_values[1])
                    ]
        
        with col2:
            # Show data table
            st.subheader("Data Preview")
            st.dataframe(st.session_state.processed_data, use_container_width=True)
            
            # Data info
            st.subheader("Data Information")
            buffer = io.StringIO()
            st.session_state.processed_data.info(buf=buffer)
            info_str = buffer.getvalue()
            st.text(info_str)
    
    with tab2:
        st.header("Visualization Studio")
        
        col1, col2 = st.columns([1, 3])
        
        with col1:
            st.subheader("Chart Settings")
            
            # Get visualization options based on data
            viz_options = get_visualization_options(st.session_state.processed_data)
            
            # Select chart type
            chart_type = st.selectbox("Select Chart Type", list(viz_options.keys()))
            
            # Get required parameters for selected chart
            chart_params = {}
            
            if chart_type in viz_options:
                for param, options in viz_options[chart_type].items():
                    if isinstance(options, list):
                        chart_params[param] = st.selectbox(f"Select {param.replace('_', ' ').title()}", options)
                    elif isinstance(options, dict) and 'type' in options:
                        if options['type'] == 'multiselect':
                            chart_params[param] = st.multiselect(
                                f"Select {param.replace('_', ' ').title()}", 
                                options['options'],
                                default=options['options'][:min(3, len(options['options']))]
                            )
                        elif options['type'] == 'slider':
                            chart_params[param] = st.slider(
                                f"Select {param.replace('_', ' ').title()}",
                                min_value=options['min'],
                                max_value=options['max'],
                                value=options['default']
                            )
                        elif options['type'] == 'checkbox':
                            chart_params[param] = st.checkbox(
                                f"{param.replace('_', ' ').title()}",
                                value=options['default']
                            )
            
            # Additional chart settings
            st.subheader("Chart Customization")
            chart_title = st.text_input("Chart Title", f"{chart_type.title()} of {chart_params.get('x', '')} and {chart_params.get('y', '')}")
            chart_width = st.slider("Chart Width", 400, 1200, 800)
            chart_height = st.slider("Chart Height", 300, 800, 500)
            
            # Create button
            if st.button("Generate Visualization"):
                try:
                    fig = create_visualization(
                        st.session_state.processed_data,
                        chart_type,
                        chart_params,
                        title=chart_title,
                        width=chart_width,
                        height=chart_height
                    )
                    if fig:
                        st.session_state.chart = fig
                    else:
                        st.error("Unable to create visualization. Please check your parameters.")
                except Exception as e:
                    st.error(f"Error creating visualization: {str(e)}")
        
        with col2:
            st.subheader("Visualization Preview")
            
            if st.session_state.chart:
                st.plotly_chart(st.session_state.chart, use_container_width=True)
            else:
                st.info("Configure your chart settings and click 'Generate Visualization' to see the result.")
    
    with tab3:
        st.header("Data Assistant")
        st.markdown("Ask questions about your data and get intelligent answers.")
        
        # User input for queries
        user_query = st.text_input("Ask a question about your data:", key="data_query")
        
        # Example questions
        with st.expander("Example questions to try"):
            st.markdown("""
            - What is the overall summary of this dataset?
            - What is the average of [column name]?
            - Show me the distribution of [column name]
            - What is the correlation between [column1] and [column2]?
            - What are the minimum and maximum values of [column name]?
            - Compare [column1] and [column2]
            """)
        
        if st.button("Ask Assistant"):
            if user_query:
                with st.spinner("Analyzing your data..."):
                    try:
                        response, chart = query_data_with_rules(user_query, st.session_state.processed_data)
                        
                        # Add to chat history
                        st.session_state.chat_history.append({"user": user_query, "response": response, "chart": chart})
                        
                    except Exception as e:
                        st.error(f"Error analyzing data: {str(e)}")
                        if not st.session_state.chat_history:
                            st.session_state.chat_history.append({"user": user_query, "response": f"Error: {str(e)}", "chart": None})
            else:
                st.warning("Please enter a question.")
        
        # Display chat history
        if st.session_state.chat_history:
            st.subheader("Conversation History")
            
            for i, chat in enumerate(reversed(st.session_state.chat_history)):
                st.markdown(f"**You:** {chat['user']}")
                st.markdown(f"**Assistant:** {chat['response']}")
                
                if chat['chart'] is not None:
                    st.plotly_chart(chat['chart'], use_container_width=True)
                
                if i < len(st.session_state.chat_history) - 1:
                    st.markdown("---")
    
    with tab4:
        st.header("Share & Export")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Export Data")
            st.markdown("Download your processed data:")
            
            csv_link = get_table_download_link(st.session_state.processed_data, "csv", "Download CSV")
            excel_link = get_table_download_link(st.session_state.processed_data, "excel", "Download Excel")
            
            st.markdown(csv_link, unsafe_allow_html=True)
            st.markdown(excel_link, unsafe_allow_html=True)
        
        with col2:
            st.subheader("Export Visualization")
            
            if st.session_state.chart:
                st.markdown("Download your current visualization:")
                
                png_link = get_chart_download_link(st.session_state.chart, "png", "Download PNG")
                html_link = get_chart_download_link(st.session_state.chart, "html", "Download Interactive HTML")
                
                st.markdown(png_link, unsafe_allow_html=True)
                st.markdown(html_link, unsafe_allow_html=True)
                
            else:
                st.info("Create a visualization in the Visualization Studio tab first.")
        
        st.subheader("Share Link")
        st.info("This feature will allow you to share your analysis with others. Coming soon!")

# Footer
st.markdown("---")
st.markdown("DataInsight Pro - A powerful data analysis tool with advanced data assistant")
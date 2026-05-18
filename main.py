import streamlit as st
import pandas as pd
from brain import *

st.set_page_config(layout='wide')
st.title('Inventory Turnover Dashboard')

arquivo = st.file_uploader(
    'Upload Inventory file (CSV or Excel)',
    type=['csv', 'xlsx'],
    key='inventory_file'
)

arquivo2 = st.file_uploader(
    'Upload Receipts file (CSV or Excel)',
    type=['csv', 'xlsx'],
    key='receipts_file'
)

def load_file(file):
    if file.name.endswith('.csv'):
        return pd.read_csv(file)
    return pd.read_excel(file)

if arquivo is None or arquivo2 is None:
    st.info('Please upload both files to continue.')
    st.stop()

with st.spinner('Loading data...'):
    df = load_file(arquivo)
    df2 = load_file(arquivo2)

etl = create_etl(df)

st.subheader('Inventory Analysis (ETL)')
st.data_editor(etl, use_container_width=True)

prod = receipts(df2)

st.subheader('Receipts Analysis')
st.data_editor(prod, use_container_width=True)

st.write('Number of rows (Inventory):', len(df))
st.write('Number of rows (Receipts):', len(df2))


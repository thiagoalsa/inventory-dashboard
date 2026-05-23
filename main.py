import streamlit as st
import plotly.express as px
import pandas as pd
from brain import *

st.set_page_config(layout='wide')
st.title('Inventory Turnover Dashboard')

file = st.file_uploader(
    'Upload Inventory file (CSV or Excel)',
    type=['csv', 'xlsx'],
    key='inventory_file'
)

file2 = st.file_uploader(
    'Upload Receipts file (CSV or Excel)',
    type=['csv', 'xlsx'],
    key='receipts_file'
)

if file is None or file2 is None:
    st.info('Please upload both files to continue.')
    st.stop()

with st.spinner('Loading data...'):
    df = load_file(file)
    df2 = load_file(file2)

etl = create_etl(df)

fig = px.bar(
    etl,
    x='Year',
    y=["amount_sent", "surplus_amount", "used_in_production"],
    #color='amount_sent',
    barmode="group",
    title=f'Amount Per Year ({etl["Description"][0]})'
)

# formato de libra no eixo Y
fig.update_layout(
    yaxis_tickprefix="£",
    yaxis_tickformat=",.2f"
)

# formato de libra no hover
fig.update_traces(
    hovertemplate="Ano: %{x}<br>Valor: £%{y:,.2f}<extra></extra>"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader('Inventory Analysis (ETL)')

st.data_editor(etl,
               column_config={'amount_sent':st.column_config.NumberColumn(
                   'amount_sent', format='£%,.2f'
               ),
                   "surplus_amount": st.column_config.NumberColumn(
                       "surplus_amount",
                       format="£%,.2f"
                   ),
                   "used_in_production": st.column_config.NumberColumn(
                       "used_in_production",
                       format="£%,.2f"
                   ),
               },
               use_container_width=True)
st.write('Number of rows (Inventory):', len(df))

prod = receipts(df2)

st.subheader('Receipts Analysis')
st.data_editor(prod, use_container_width=True)
st.write('Number of rows (Receipts):', len(df2))


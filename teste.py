import pandas as pd
import streamlit as st
import datetime as dt
import seaborn as sns
import matplotlib.pyplot as plt


df = pd.read_csv('./data-source/Sample - Superstore.csv', sep=',', encoding='latin1', on_bad_lines='skip')
                 
csv = df.to_csv(index=False).encode('utf-8')

st.download_button(
    label="📥 Baixar dados como CSV",
    data=csv,
    file_name='Sample - Superstore.csv',
    mime='text/csv'
)

#formata coluna de data do pedido para datetime
df['Order Date'] = pd.to_datetime(df['Order Date'])

target_date_field = 'Order Date'
retention_target_field = 'Customer ID'
years = sorted(df['Order Date'].dt.year.unique())

def cohort_analyse(df, target_date_field, retention_target_field, year):

    #Filtro manual para não poluição    
    df = df[df['Order Date'].dt.year == year]   

    #formata coluna de data do pedido para datetime
    df[target_date_field] = pd.to_datetime(df[target_date_field])

    #Cria coluna Order Month que armazena o dado do mes da ordem, ja padronizado para o dia 1
    df['Order Month'] = df[target_date_field].apply(get_month)

    #Agrupa por customer e traz o order month
    grouping = df.groupby(retention_target_field)['Order Month']
    
    #Armazena o primeiro mes de compra do cliente em cada linha de ordem
    df['Cohort Month'] = grouping.transform('min')

    #Armazena os anos e meses de entrada dos clientes e de suas sequencias de compra
    order_date_year, order_date_month, _ = get_date_int(df, 'Order Month')
    cohort_date_year, cohort_date_month, _ = get_date_int(df, 'Cohort Month')

    #Armazena e cria coluna com a diferença do numero de meses que o cliente levou para voltar
    years_diff = order_date_year - cohort_date_year
    months_diff = order_date_month - cohort_date_month
    df['Cohort Index'] = years_diff * 12 + months_diff + 1

    grouping = df.groupby(['Cohort Month', 'Cohort Index'])

    retention_target_field = grouping['Customer ID'].apply(pd.Series.nunique)

    cohort_data = grouping['Customer ID'].apply(pd.Series.nunique)

    cohort_data = cohort_data.reset_index()
    cohort_counts = cohort_data.pivot(index='Cohort Month', columns = 'Cohort Index', values='Customer ID')

    cohort_sizes = cohort_counts.iloc[:,0]

    retention = cohort_counts.divide(cohort_sizes, axis = 0)

    retention.round(3)*100  

    st.title("Análise de Cohort — Retenção de Clientes em " + str(year))

    # Criando o heatmap com matplotlib
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.heatmap(
        data=retention,
        annot=True,
        fmt='.0%',
        cmap='Blues',

        ax=ax
    )

    ax.set_title("Taxa de Retenção")
    st.pyplot(fig)

#Função para padronizar data no dia 01
def get_month(x): return dt.datetime(x.year, x.month, 1)

#Função que retorna ano mes e dia de uma coluna de um df
def get_date_int(df, column):
    year = df[column].dt.year
    month = df[column].dt.month
    day = df[column].dt.day
    return year, month, day

for year in years:
    cohort_analyse(df, target_date_field, retention_target_field, year)


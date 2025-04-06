#formata coluna de data do pedido para datetime
df['Order Date'] = pd.to_datetime(df['Order Date'])

#Função para padronizar data no dia 01
def get_month(x): return dt.datetime(x.year, x.month, 1)

#Cria coluna Order Month que armazena o dado do mes da ordem, ja padronizado para o dia 1
df['Order Month'] = df['Order Date'].apply(get_month)

#Agrupa por customer e traz o order month
grouping = df.groupby('Customer ID')[['Order Month']]

#Armazena o primeiro mes de compra do cliente em cada linha de ordem
df['Cohort Month'] = grouping.transform('min')

#Função que retorna ano mes e dia de uma coluna de um df
def get_date_int(df, column):
    year = df[column].dt.year
    month = df[column].dt.month
    day = df[column].dt.day
    return year, month, day

#Armazena os anos e meses de entrada dos clientes e de suas sequencias de compra
order_date_year, order_date_month, _ = get_date_int(df, 'Order Month')
cohort_date_year, cohort_date_month, _ = get_date_int(df, 'Cohort Month')

#Armazena e cria coluna com a diferença do numero de meses que o cliente levou para voltar
years_diff = order_date_year - cohort_date_year
months_diff = order_date_month - cohort_date_month
df['Cohort Index'] = years_diff * 12 + months_diff + 1

#Filtro manual para não poluição
df = df[df['Order Date'].dt.year == 2014]

grouping = df.groupby(['Cohort Month', 'Cohort Index'])

cohort_data = grouping['Customer ID'].apply(pd.Series.nunique)

cohort_data = cohort_data.reset_index()
cohort_counts = cohort_data.pivot(index='Cohort Month', columns = 'Cohort Index', values='Customer ID')

cohort_sizes = cohort_counts.iloc[:,0]

retention = cohort_counts.divide(cohort_sizes, axis = 0)

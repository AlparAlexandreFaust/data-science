import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

# Função para ler arquivos de feriados sem cabeçalho e adicionar os cabeçalhos
def load_tables_with_headers(file_paths, delimiter, encoding, headers):
    tables = pd.DataFrame()
    for file_path in file_paths:
        df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding, header=None)
        df.columns = headers
        tables = pd.concat([tables, df], ignore_index=True)
    return tables

# Lista de arquivos de feriados
holiday_files = [
    # Adicione os caminhos dos arquivos de feriados aqui
]

# Lista de arquivos de acidentes
accident_files = [
    # Adicione os caminhos dos arquivos de acidentes aqui
]

# Definir os anos dos arquivos de feriados e acidentes
years = ['2010', '2011', '2012', '2013', '2014', '2015', '2016', '2017', '2018', '2019', '2020', '2021', '2022', '2023', '2024']

for year in years:
    holiday_files.append(f'src/feriados/municipal/csv/{year}.csv')
    holiday_files.append(f'src/feriados/estadual/csv/{year}.csv')
    holiday_files.append(f'src/feriados/nacional/csv/{year}.csv')
    accident_files.append(f'src/datatran{year}.csv')

# Cabeçalhos para os arquivos de feriados
holiday_headers = ['data', 'nome', 'tipo', 'descricao', 'uf', 'municipio']

# Carregar os feriados com cabeçalhos
holidays = load_tables_with_headers(holiday_files, ",", "latin1", holiday_headers)

# Filtrar feriados para incluir apenas aqueles onde uf é SP ou nulo
holidays = holidays[(holidays['uf'] == 'SP') | (holidays['uf'].isna())]

# Converter colunas de data para datetime
holidays['data'] = pd.to_datetime(holidays['data'], format='%d/%m/%Y')

# Função para ler arquivos de acidentes
def load_tables(file_paths, delimiter, encoding):
    tables = pd.DataFrame()
    for file_path in file_paths:
        df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
        tables = pd.concat([tables, df], ignore_index=True)
    return tables

# Carregar o arquivo CSV de acidentes (diferentes formatos)
def load_accidents(accident_files):
    tables = pd.DataFrame()
    for file_path in accident_files:
        if int(file_path[-8:-4]) <= 2011:
            df = pd.read_csv(file_path, delimiter=';', encoding='latin1')
        else:
            df = pd.read_csv(file_path, delimiter=';', encoding='latin1', quotechar='"')
        tables = pd.concat([tables, df], ignore_index=True)
    return tables

# Carregar os dados de acidentes
df = load_accidents(accident_files)

# Preencher valores ausentes
df['br'].fillna(0, inplace=True)
df['km'].fillna('0', inplace=True)
df.fillna('Não Informado', inplace=True)

# Filtrar os dados para apenas acidentes em São Paulo (SP)
df_sp = df[df['uf'] == 'SP']

# Adicionar coluna de feriado
df_sp['feriado'] = 'false'

# Converter colunas de data para datetime
df_sp['data_inversa'] = pd.to_datetime(df_sp['data_inversa'], errors='coerce')

# Verificar feriados e atualizar a coluna de feriado
for idx, row in df_sp.iterrows():
    accident_date = row['data_inversa']
    accident_city = row['municipio']
    
    # Verificar feriados nacionais e estaduais
    if not holidays[(holidays['data'] == accident_date) & 
                    (holidays['tipo'].isin(['NACIONAL', 'ESTADUAL']))].empty:
        df_sp.at[idx, 'feriado'] = 'true'
    
    # Verificar feriados municipais
    if not holidays[(holidays['data'] == accident_date) & 
                    (holidays['tipo'] == 'MUNICIPAL') & 
                    (holidays['municipio'] == accident_city)].empty:
        df_sp.at[idx, 'feriado'] = 'true'

# Garantir que o diretório de saída exista
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Caminho completo para o arquivo de saída
output_file_path = os.path.join(output_dir, 'datatran-sp.csv')

# Salvar a tabela de acidentes filtrada e com a coluna de feriado em um arquivo CSV local
df_sp.to_csv(output_file_path, index=False, sep=';', encoding='latin1')

# Configurações gerais para os gráficos
plt.style.use('ggplot')
plt.figure(figsize=(14, 10))

# Distribuição dos acidentes por dia da semana
plt.subplot(2, 2, 1)
df_sp['dia_semana'].value_counts().plot(kind='bar', color='blue')
plt.title('Distribuição dos Acidentes por Dia da Semana')
plt.xlabel('Dia da Semana')
plt.ylabel('Número de Acidentes')

# Distribuição dos tipos de acidente
plt.subplot(2, 2, 2)
df_sp['tipo_acidente'].value_counts().plot(kind='bar', color='green')
plt.title('Distribuição dos Tipos de Acidente')
plt.xlabel('Tipo de Acidente')
plt.ylabel('Número de Acidentes')

# Análise do número de acidentes com vítimas fatais
plt.subplot(2, 2, 3)
df_sp_fatal = df_sp[df_sp['mortos'] > 0]
df_sp_fatal['municipio'].value_counts().plot(kind='bar', color='red')
plt.title('Número de Acidentes com Vítimas Fatais por Município')
plt.xlabel('Município')
plt.ylabel('Número de Acidentes Fatais')

# Gráfico de barras para média de acidentes por dia
plt.subplot(2, 2, 4)
daily_accidents = df_sp.groupby(['data_inversa', 'feriado']).size().reset_index(name='num_acidentes')
daily_avg = daily_accidents.groupby('feriado')['num_acidentes'].mean().reset_index()

colors = ['red' if feriado == 'true' else 'blue' for feriado in daily_avg['feriado']]

plt.bar(daily_avg['feriado'], daily_avg['num_acidentes'], color=colors)
plt.title('Média de Acidentes por Dia')
plt.xlabel('Feriado')
plt.ylabel('Média de Acidentes')
plt.xticks(ticks=[0, 1], labels=['Não Feriado', 'Feriado'])

plt.tight_layout()
plt.show()

# Gráfico de barras dos últimos 365 dias
plt.figure(figsize=(18, 6))

# Filtrar os dados dos últimos 365 dias
end_date = df_sp['data_inversa'].max()
start_date = end_date - timedelta(days=365)
last_year_data = df_sp[(df_sp['data_inversa'] >= start_date) & (df_sp['data_inversa'] <= end_date)]

# Contar número de acidentes por dia
daily_accidents_last_year = last_year_data.groupby(['data_inversa', 'feriado']).size().reset_index(name='num_acidentes')

# Plotar o gráfico
colors = ['red' if feriado == 'true' else 'blue' for feriado in daily_accidents_last_year['feriado']]
plt.bar(daily_accidents_last_year['data_inversa'], daily_accidents_last_year['num_acidentes'], color=colors)
plt.title('Número de Acidentes nos Últimos 365 Dias')
plt.xlabel('Data')
plt.ylabel('Número de Acidentes')

plt.tight_layout()
plt.show()

# Exibir as primeiras linhas do dataframe atualizado para verificar a nova coluna
df_sp.head()

# Agrupar os dados de acidentes por data e contar o número de acidentes por dia
accidents_per_day = df_sp.groupby('data_inversa').size().reset_index(name='num_acidentes')

# Classificar os dias pelo número de acidentes em ordem decrescente
ranked_accidents = accidents_per_day.sort_values(by='num_acidentes', ascending=False)

# Exibir o ranking no console
print("Ranking dos dias com mais acidentes:")
print(ranked_accidents.head(10))  # Exibe os 10 dias com mais acidentes

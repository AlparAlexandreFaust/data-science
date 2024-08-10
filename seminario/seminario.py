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

classificar_feriados = False

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

# Converter colunas de data para datetime, lidando com diferentes formatos
holidays['data'] = pd.to_datetime(holidays['data'], format='%d/%m/%Y', errors='coerce')
holidays['data'].fillna(pd.to_datetime(holidays['data'], format='%Y-%m-%d', errors='coerce'), inplace=True)

# Função para ler arquivos de acidentes
def load_accidents(accident_files):
    tables = pd.DataFrame()
    for file_path in accident_files:
        year = int(file_path[-8:-4])
        if year <= 2011:
            df = pd.read_csv(file_path, delimiter=';', encoding='latin1')
            df['data_inversa'] = pd.to_datetime(df['data_inversa'], format='%d/%m/%Y', errors='coerce')
        elif year == 2016:
            df = pd.read_csv(file_path, delimiter=';', encoding='latin1')
            df['data_inversa'] = pd.to_datetime(df['data_inversa'], format='%d/%m/%y', errors='coerce')
        else:
            df = pd.read_csv(file_path, delimiter=';', encoding='latin1', quotechar='"')
            df['data_inversa'] = pd.to_datetime(df['data_inversa'], format='%Y-%m-%d', errors='coerce')
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

if classificar_feriados:
    # Adicionar coluna de feriado
    df_sp['feriado'] = 'false'

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

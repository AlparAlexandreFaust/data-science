import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt

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
    'src/feriados/municipal/csv/2023.csv',
    'src/feriados/estadual/csv/2023.csv',
    'src/feriados/nacional/csv/2023.csv',
    'src/feriados/municipal/csv/2024.csv',
    'src/feriados/estadual/csv/2024.csv',
    'src/feriados/nacional/csv/2024.csv'
]

# Lista de arquivos de acidentes
accident_files = [
    'src/datatran2023.csv',
    'src/datatran2024.csv'
]

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

# Carregar o arquivo CSV de acidentes
df = load_tables(accident_files, ";", "latin1")

# Preencher valores ausentes
df['br'] = df['br'].fillna(0)
df['km'] = df['km'].fillna('0')
df = df.fillna('Não Informado')

# Filtrar os dados para apenas acidentes em São Paulo (SP)
df_sp = df[df['uf'] == 'SP'].copy()

# Adicionar coluna de feriado
df_sp.loc[:, 'feriado'] = 'false'

# Converter colunas de data para datetime
df_sp.loc[:, 'data_inversa'] = pd.to_datetime(df_sp['data_inversa'], format='%Y-%m-%d')

# Verificar feriados e atualizar a coluna de feriado
for idx, row in df_sp.iterrows():
    accident_date = row['data_inversa']
    accident_city = row['municipio']
    
    # Verificar feriados nacionais e estaduais
    if not holidays[(holidays['data'] == accident_date) & 
                    (holidays['tipo'].isin(['NACIONAL', 'ESTADUAL']))].empty:
        df_sp.loc[idx, 'feriado'] = 'true'
    
    # Verificar feriados municipais
    if not holidays[(holidays['data'] == accident_date) & 
                    (holidays['tipo'] == 'MUNICIPAL') & 
                    (holidays['municipio'] == accident_city)].empty:
        df_sp.loc[idx, 'feriado'] = 'true'

# Normalizar os nomes dos municípios
df_sp['municipio'] = df_sp['municipio'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')
holidays['municipio'] = holidays['municipio'].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

# Garantir que o diretório de saída exista
output_dir = 'output'
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Caminho completo para o arquivo de saída
output_file_path = os.path.join(output_dir, 'datatran-sp.csv')

# Salvar a tabela de acidentes filtrada e com a coluna de feriado em um arquivo CSV local
df_sp.to_csv(output_file_path, index=False, sep=';', encoding='latin1')

# Verificar a presença de todos os arquivos do shapefile
shapefile_dir = 'src/shapefile'
shapefile_base = 'SP_Municipios_2022'
required_files = [f'{shapefile_base}.shp', f'{shapefile_base}.shx', f'{shapefile_base}.dbf']

for file in required_files:
    if not os.path.exists(os.path.join(shapefile_dir, file)):
        raise FileNotFoundError(f"Arquivo {file} não encontrado no diretório {shapefile_dir}")

# Carregar o shapefile dos municípios de São Paulo
shapefile_path = os.path.join(shapefile_dir, f'{shapefile_base}.shp')
gdf_municipios = gpd.read_file(shapefile_path)

# Verificar os nomes das colunas do GeoDataFrame
print(gdf_municipios.columns)

# Ajustar a coluna para fazer a união com a coluna correta
column_name = 'NM_MUN'  # Substitua pelo nome correto após inspecionar as colunas

# Normalizar os nomes dos municípios no GeoDataFrame
gdf_municipios[column_name] = gdf_municipios[column_name].str.upper().str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode('utf-8')

# Contar o número de acidentes por município
accidents_by_municipio = df_sp['municipio'].value_counts().reset_index()
accidents_by_municipio.columns = ['municipio', 'num_acidentes']

# Verificar exemplos de nomes de municípios de ambos os DataFrames
print("Exemplos de municípios no DataFrame de acidentes:")
print(df_sp['municipio'].unique()[:10])

print("Exemplos de municípios no GeoDataFrame:")
print(gdf_municipios[column_name].unique()[:10])

# Unir os dados de acidentes com os dados geoespaciais dos municípios
gdf_municipios = gdf_municipios.merge(accidents_by_municipio, how='left', left_on=column_name, right_on='municipio')

# Verificar as primeiras linhas após a junção
print(gdf_municipios.head())

# Plotar o mapa
fig, ax = plt.subplots(1, 1, figsize=(15, 15))
gdf_municipios.plot(column='num_acidentes', cmap='OrRd', linewidth=0.8, ax=ax, edgecolor='0.8', legend=True)
plt.title('Número de Acidentes por Município no Estado de São Paulo')
plt.show()

# Exibir as primeiras linhas do dataframe atualizado para verificar a nova coluna
df_sp.head()

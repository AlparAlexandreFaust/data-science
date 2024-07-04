import os
import pandas as pd
import matplotlib.pyplot as plt

# Função para ler arquivos de feriados
def load_tables(file_paths, delimiter, encoding):
    tables = pd.DataFrame()
    for file_path in file_paths:
        df = pd.read_csv(file_path, delimiter=delimiter, encoding=encoding)
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

accident_files = [
    'src/datatran2023.csv',
    'src/datatran2024.csv'
]

# Carregar os feriados
holidays = load_tables(holiday_files, ",", "latin1")

# Filtrar feriados para incluir apenas aqueles onde uf é SP ou nulo
holidays = holidays[(holidays['uf'] == 'SP') | (holidays['uf'].isna())]

# Converter colunas de data para datetime
holidays['data'] = pd.to_datetime(holidays['data'], format='%d/%m/%Y')

# Carregar o arquivo CSV de acidentes
df = load_tables(accident_files, ";", "latin1")

# Preencher valores ausentes
df['br'].fillna(0, inplace=True)
df['km'].fillna('0', inplace=True)
df.fillna('Não Informado', inplace=True)

# Filtrar os dados para apenas acidentes em São Paulo (SP)
df_sp = df[df['uf'] == 'SP']

# Adicionar coluna de feriado
df_sp['feriado'] = 'false'

# Converter colunas de data para datetime
df_sp['data_inversa'] = pd.to_datetime(df_sp['data_inversa'], format='%Y-%m-%d')

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
plt.figure(figsize=(14, 8))

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

plt.tight_layout()
plt.show()

# Exibir as primeiras linhas do dataframe atualizado para verificar a nova coluna
df_sp.head()
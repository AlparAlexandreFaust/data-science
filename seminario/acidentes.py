import pandas as pd
import matplotlib.pyplot as plt

# Recarregar o arquivo CSV com codificação ISO-8859-1
file_path = './src/acidentes2024.csv'  # Atualize com o caminho correto do arquivo
df = pd.read_csv(file_path, encoding='ISO-8859-1', on_bad_lines='skip', sep=None, engine='python')
df = df[df['uf'] == 'SP']

# Distribuição dos acidentes por dia da semana
accidents_per_day = df['dia_semana'].value_counts()

# Causas mais comuns dos acidentes
common_causes = df['causa_acidente'].value_counts().head(10)

# Gráfico de barras: Distribuição dos acidentes por dia da semana
plt.figure(figsize=(10, 6))
accidents_per_day.sort_index().plot(kind='bar', color='skyblue')
plt.title('Distribuição dos Acidentes por Dia da Semana')
plt.xlabel('Dia da Semana')
plt.ylabel('Número de Acidentes')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.show()

# Gráfico de barras: Causas mais comuns dos acidentes
plt.figure(figsize=(12, 6))
common_causes.plot(kind='bar', color='salmon')
plt.title('Causas Mais Comuns dos Acidentes')
plt.xlabel('Causa do Acidente')
plt.ylabel('Número de Ocorrências')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.show()

# Analisar a distribuição de acidentes ao longo do dia
accidents_per_hour = df['horario'].str[:2].value_counts().sort_index()

# Gráfico de linhas: Distribuição dos acidentes por hora do dia
plt.figure(figsize=(12, 6))
accidents_per_hour.plot(kind='line', marker='o', linestyle='-', color='green')
plt.title('Distribuição dos Acidentes por Hora do Dia')
plt.xlabel('Hora do Dia')
plt.ylabel('Número de Acidentes')
plt.grid(True)
plt.xticks(range(0, 24))
plt.show()

# Análise das condições meteorológicas durante os acidentes
weather_conditions = df['condicao_metereologica'].value_counts()

# Gráfico de barras: Condições meteorológicas mais comuns durante os acidentes
plt.figure(figsize=(10, 6))
weather_conditions.plot(kind='bar', color='purple')
plt.title('Condições Meteorológicas Mais Comuns Durante os Acidentes')
plt.xlabel('Condição Meteorológica')
plt.ylabel('Número de Acidentes')
plt.xticks(rotation=45)
plt.grid(axis='y')
plt.show()

import pandas as pd
import matplotlib.pyplot as plt

# Carregar o arquivo CSV filtrado de acidentes
df_sp = pd.read_csv('output/datatran-sp.csv', delimiter=';', encoding='latin1')

# Converter a coluna de data para datetime
df_sp['data_inversa'] = pd.to_datetime(df_sp['data_inversa'], errors='coerce')

# Agrupar os dados por mês e ano e contar o número de acidentes por mês
df_sp['ano_mes'] = df_sp['data_inversa'].dt.to_period('M')
accidents_per_month = df_sp.groupby('ano_mes').size().reset_index(name='num_acidentes')

# Converter 'ano_mes' de Period para datetime para plotagem
accidents_per_month['ano_mes'] = accidents_per_month['ano_mes'].dt.to_timestamp()


####################################################################################################

# Agrupar os dados por mês e ano e contar o número de acidentes por mês
df_sp['ano_mes'] = df_sp['data_inversa'].dt.to_period('M')
accidents_per_month = df_sp.groupby('ano_mes').size().reset_index(name='num_acidentes')

# Converter 'ano_mes' de Period para datetime para plotagem
accidents_per_month['ano_mes'] = accidents_per_month['ano_mes'].dt.to_timestamp()

# Configurações gerais para os gráficos
plt.figure(figsize=(14, 7))
plt.plot(accidents_per_month['ano_mes'], accidents_per_month['num_acidentes'], marker='o', linestyle='-')
plt.title('Quantidade de Acidentes por Mês')
plt.xlabel('Mês')
plt.ylabel('Número de Acidentes')
plt.grid(True)
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

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

# Gráfico de barras dos últimos 365 dias
plt.figure(figsize=(18, 6))

# Exibir as primeiras linhas do dataframe atualizado para verificar a nova coluna
df_sp.head()

# Agrupar os dados de acidentes por data e contar o número de acidentes por dia
accidents_per_day = df_sp.groupby('data_inversa').size().reset_index(name='num_acidentes')

# Classificar os dias pelo número de acidentes em ordem decrescente
ranked_accidents = accidents_per_day.sort_values(by='num_acidentes', ascending=False)

# Exibir o ranking no console
print("Ranking dos dias com mais acidentes:")
print(ranked_accidents.head(10))  # Exibe os 10 dias com mais acidentes

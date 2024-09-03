import pandas as pd
from sklearn.utils import resample

# Carregar o DataFrame
df = pd.read_csv('output/dados_acidentes_expandidos.csv', delimiter=';', encoding='utf-8', low_memory=False)

# Separar as classes
class_fatal = df[df['classificacao_acidente'] == 'Com Vítimas Fatais']
class_injured = df[df['classificacao_acidente'] == 'Com Vítimas Feridas']
class_non_fatal = df[df['classificacao_acidente'] == 'Sem Vítimas']


# Verificar os valores únicos na coluna 'classificacao_acidente'
print(df['classificacao_acidente'].unique())

# Separar as classes

# Verificar o número de registros em cada classe
print("Número de registros 'Com Vítimas Fatais':", len(class_fatal))
print("Número de registros 'Sem Vítimas Fatais':", len(class_non_fatal))
print("Número de registros 'Com Vítimas Feridas':", len(class_injured))

print("\n\nBalanceamento das classes:")

# Determinar o número de registros da classe minoritária (1.214 registros)
n_samples = min(len(class_fatal), len(class_injured), len(class_non_fatal))

# Balancear as classes para 1.214 registros cada
class_fatal_balanced = resample(class_fatal, 
                                replace=False, 
                                n_samples=n_samples, 
                                random_state=42)

class_injured_balanced = resample(class_injured, 
                                  replace=False, 
                                  n_samples=n_samples, 
                                  random_state=42)

class_non_fatal_balanced = resample(class_non_fatal, 
                                    replace=False, 
                                    n_samples=n_samples, 
                                    random_state=42)

# Combinar novamente as classes para criar o DataFrame balanceado
df_balanced = pd.concat([class_fatal_balanced, class_injured_balanced, class_non_fatal_balanced])

# Verificar a distribuição das classes após o balanceamento
print(df_balanced['classificacao_acidente'].value_counts())

df_balanced.to_csv('output/dados_acidentes_balanceados.csv', index=False, sep=';', encoding='utf-8')

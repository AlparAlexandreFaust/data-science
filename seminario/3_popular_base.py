import pandas as pd

# Carregar os dados originais
df = pd.read_csv('output/preprocessado.csv', delimiter=';', encoding='latin1')

df.head()

# Função para gerar novas linhas com km ajustado e target definido
def gerar_linhas(df, km_adjustments, target_value):
    dfs = []
    for adjust in km_adjustments:
        df_temp = df.copy()
        df_temp['km'] += adjust
        df_temp['target'] = target_value
        dfs.append(df_temp)
    return pd.concat(dfs, ignore_index=True)

# Linhas para acidentes (target = 1)
df_acidentes = gerar_linhas(df, km_adjustments=[0, 1, 2, -1, -2], target_value=1)

# Linhas para não acidentes (target = 0)
df_nao_acidentes = gerar_linhas(df, km_adjustments=[-3, -4, -5, -6, 3, 4], target_value=0)

# Concatenar os dataframes gerados
df_final = pd.concat([df_acidentes, df_nao_acidentes], ignore_index=True)

# Salvar o dataframe final
df_final.to_csv('output/dados_acidentes_expandidos.csv', index=False, sep=';', encoding='latin1')

print("Dados expandidos e salvos em 'dados_acidentes_expandidos.csv'.")

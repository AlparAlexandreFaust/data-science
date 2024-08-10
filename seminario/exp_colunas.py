import pandas as pd
import unicodedata

# Função para imprimir os itens únicos de uma coluna específica
def imprimir_itens_unicos(df, nome_arquivo, nome_coluna):
    try:
        # Verificar se a coluna existe
        if nome_coluna not in df.columns:
            print(f"A coluna '{nome_coluna}' não foi encontrada no arquivo.")
            return

        # Obter os itens únicos da coluna
        itens_unicos = df[nome_coluna].unique()

        # Imprimir os itens únicos em ordem alfabética
        for item in sorted(itens_unicos):
            print(f"'{item}'")
    except pd.errors.ParserError as e:
        print("Erro ao analisar o arquivo CSV:", e)
    except Exception as e:
        print("Ocorreu um erro:", e)


file_path = 'output/preprocessado.csv'
data = pd.read_csv(file_path, delimiter=';', encoding='ISO-8859-1', low_memory=False)

# Exemplo de uso:
imprimir_itens_unicos(data, 'output/preprocessado.csv', 'fase_dia')

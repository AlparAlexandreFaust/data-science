import pandas as pd
import unicodedata

# Função para imprimir os itens únicos de uma coluna específica
def imprimir_itens_unicos(df, nome_coluna):
    try:
        # Verificar se a coluna existe
        if nome_coluna not in df.columns:
            print(f"A coluna '{nome_coluna}' não foi encontrada no arquivo.")
            return

        # Obter os itens únicos da coluna
        itens_unicos = df[nome_coluna].unique()

        print(f"Coluna '{nome_coluna}':")

        # Imprimir os itens únicos em ordem alfabética
        for item in sorted(itens_unicos):
            print(f"'{item}'")
        
        print("\n")
    except pd.errors.ParserError as e:
        print("Erro ao analisar o arquivo CSV:", e)
    except Exception as e:
        print("Ocorreu um erro:", e)

# Função para remover acentuação
def remover_acentos(text):
    nfkd = unicodedata.normalize('NFKD', text)
    return "".join([c for c in nfkd if not unicodedata.combining(c)])

# Função para padronizar os dias da semana
def padronizar_dia_semana(dia):
    dia = remover_acentos(dia).lower().strip()
    dia = dia.replace("segunda-feira", "segunda")
    dia = dia.replace("terca-feira", "terca")
    dia = dia.replace("terça-feira", "terca")
    dia = dia.replace("quarta-feira", "quarta")
    dia = dia.replace("quinta-feira", "quinta")
    dia = dia.replace("sexta-feira", "sexta")
    dia = dia.replace("sábado", "sabado").replace("sabado", "sabado")
    dia = dia.replace("domingo", "domingo")
    
    # Corrigindo possíveis caracteres estranhos
    dia = dia.replace("si¿1⁄2bado", "sabado")
    dia = dia.replace("teri¿1⁄2a", "terca")
    dia = dia.replace("domingo", "domingo")

    return dia

# Função para padronizar as fases do dia
def padronizar_fase_dia(fase):
    fase = remover_acentos(fase).lower().strip()

    return fase

# Função para padronizar as condições meteorológicas
def padronizar_condicao_meteorologica(condicao):
    condicao = remover_acentos(condicao).lower().strip()
    condicao = condicao.replace("ignorada", "ignorado")
    condicao = condicao.replace("garoa/chuvisco", "chuvisco")
    condicao = condicao.replace("nevoeiro/neblina", "neblina")

    return condicao

# Função para verificar se é final de semana
def verificar_final_de_semana(dia):
    return dia in ['sabado', 'domingo']

# Carregar o arquivo CSV, sem definir 'dtype' inicialmente para evitar erros
file_path = 'output/datatran-sp.csv'
data = pd.read_csv(file_path, delimiter=';', encoding='ISO-8859-1', low_memory=False)

# 1. Coluna `km`: Substituir vírgulas por pontos e converter para número inteiro
data['km'] = data['km'].str.replace(',', '.').astype(float).fillna(0).astype(int)

# 2. Coluna `condicao_metereologica`: Padronizar strings
data['condicao_metereologica'] = data['condicao_metereologica'].str.strip().str.lower().apply(remover_acentos)

# 3. Padronizar colunas `dia_semana`, `fase_dia` e `condicao_metereologica`
# 3.1. Coluna `dia_semana`
data['dia_semana'] = data['dia_semana'].apply(padronizar_dia_semana)

# 3.2. Coluna `fase_dia`
data['fase_dia'] = data['fase_dia'].apply(padronizar_fase_dia)

# 3.3. Coluna `condicao_metereologica`
data['condicao_metereologica'] = data['condicao_metereologica'].apply(padronizar_condicao_meteorologica)

# 4. Coluna `br`: Filtrar apenas a rodovia BR-116
data = data[data['br'] == 116]

# 5. Adicionar a nova coluna 'final_de_semana' ao DataFrame
data['final_de_semana'] = data['dia_semana'].apply(verificar_final_de_semana)

# Salvar o arquivo processado com codificação UTF-8
output_file_path = 'output/preprocessado.csv'
data.to_csv(output_file_path, index=False, sep=';', encoding='utf-8')

# Exemplo de uso:
imprimir_itens_unicos(data, 'dia_semana')
imprimir_itens_unicos(data, 'fase_dia')
imprimir_itens_unicos(data, 'condicao_metereologica')
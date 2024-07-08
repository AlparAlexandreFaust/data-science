# Carregar pacotes necessários
library(readr)
library(dplyr)
library(ggplot2)
library(corrplot)

# Ler o arquivo CSV
dados <- read_csv("C:\mestrado\data-science\seminario\src\acidentes2023_todas_causas_tipos.csv")

# Selecionar apenas as colunas numéricas
dados_numericos <- dados %>% select_if(is.numeric)

# Calcular a matriz de correlação
matriz_correlacao <- cor(dados_numericos, use = "complete.obs")

# Exibir a matriz de correlação
print(matriz_correlacao)

# Visualizar a matriz de correlação usando corrplot
corrplot(matriz_correlacao, method = "color", tl.col = "black", tl.cex = 0.8, addCoef.col = "black", number.cex = 0.7)

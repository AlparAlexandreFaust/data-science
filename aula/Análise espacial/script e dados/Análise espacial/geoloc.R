pacotes <- c("tidyverse","sf","spdep","tmap","rgdal","rgeos","adehabitatHR","knitr",
             "kableExtra","gtools","grid")

if(sum(as.numeric(!pacotes %in% installed.packages())) != 0){
  instalador <- pacotes[!pacotes %in% installed.packages()]
  for(i in 1:length(instalador)) {
    install.packages(instalador, dependencies = T)
    break()}
  sapply(pacotes, require, character = T) 
} else {
  sapply(pacotes, require, character = T) 
}

data <- read.csv("datatran2023.csv",sep=";",dec = ",")
data_filter <- data[data$uf == "SC",]
# Se eu quisesse filtrar só os acidentes que tem mortos:
#data_filter <- data_filter[data_filter$mortos >= 1,]

# Criando um objeto do tipo sf a partir de um data frame:
acidentes <- st_as_sf(x = data_filter, 
                         coords = c("longitude", "latitude"), 
                         crs = 4326)
#o crs 4326 que utilizamos é o sistema de coordenadas geográficas não projetadas WGS84

# Plotando os pontos com ggplot:
acidentes %>%
  ggplot()+
  geom_sf()

# também é possível plotar com a projeção de Mercator, utilizando o st_transform:

acidentes %>% st_transform(3857) %>%
  ggplot() +
  geom_sf()

#outra forma de visualizar é com o tm_shape com o modo tmap, que vai utilizar um mapa interativo como base
# Adicionando uma camada de um mapa do Leafleet
tmap_mode("view")

tm_shape(shp = acidentes) + 
  tm_dots(col = "deepskyblue4", 
          border.col = "black", 
          size = 0.2, 
          alpha = 0.8)

#Outra forma de fazer é utilizar um arquivo ShapeFile com formas geométricas, polígonos
# Carregando um shapefile:
shp_sc <- readOGR(dsn = "shapefile_sc", 
                  layer = "sc_state",
                  encoding = "UTF-8", 
                  use_iconv = TRUE)

# Visualizando o shapefile carregado:
tm_shape(shp = shp_sc) +
  tm_borders()

# o modo abaixo permite gerar os gráficos para salvar, mas não para interagir
# tmap_mode("plot")

#unindo as duas observações com ggplot:
cidades <- st_read("shapefile_sc/sc_state.shp")
cidades %>% st_transform(4326) %>%
  ggplot() +
  geom_sf() +
  geom_sf(data=acidentes)

#Utilizando o mapa interativo:
tm_shape(shp = cidades) +
  tm_borders()+
  tm_shape(shp = acidentes)+
  tm_dots()

cidades <- cidades %>% st_transform(4326)
acidentes <- acidentes %>% st_transform(4326)
cidades <- cidades %>% rename("municipio"="NM_MUNICIP")
cidades_acidentes <- cidades  %>% 
  st_join(acidentes) 
cidades_num_acidentes <-  cidades_acidentes %>% group_by(municipio.x) %>% 
  tally() 


cidades_num_acidentes %>%
  ggplot() +
  geom_sf(aes(fill=n))

#outra forma:


tm_shape(shp=acidentes)+
  tm_dots(size = 0.01,alpha=0.3)+
  tm_shape(shp=cidades_num_acidentes)+
  tm_fill(col="n",alpha=0.4)+
  tm_borders()


#Análise espacial estatística
# Estabelecendo uma vizinhança:
vizinhos_queen <- poly2nb(pl = cidades_num_acidentes,
                          queen = TRUE,
                          row.names = cidades_num_acidentes$municipio.x)

summary(vizinhos_queen)
# 
# shp_sc <- readOGR(dsn = "shapefile_sc", 
#                   layer = "sc_state",
#                   encoding = "UTF-8", 
#                   use_iconv = TRUE)
# 
# # Observando a vizinhança estabelecida:
# plot.new()
# plot(shp_sc, border = "lightgray")
# plot(vizinhos_queen, 
#      coordinates(shp_sc), 
#      add = TRUE, 
#      col = "#FDE725FF")


# Definindo uma matriz de vizinhanças com padronização em linha:
matrizW_queen_linha <- nb2mat(vizinhos_queen,
                              style = "W")

# Observando a matriz de contiguidades, critério queen, padronizada em linha:
colnames(matrizW_queen_linha) <- rownames(matrizW_queen_linha)


# Antes de dar prosseguimento aos estudos das autocorrelações espaciais sobre
# a variável de número de acidentes, vamos observar alguns comportamentos:
tm_shape(shp = cidades_num_acidentes) +
  tm_fill(col = "n", 
          n=10,
          palette = "viridis",
          legend.hist = TRUE) +
  tm_borders() +
  tm_layout(legend.outside = TRUE)

# Salvando o gráfico da acidentes para uso subsequente:
acidentes_plot <- tm_shape(shp = cidades_num_acidentes) +
  tm_fill(col = "n", 
          n=10,
          palette = "viridis",
          legend.hist = TRUE) +
  tm_borders() +
  tm_layout(legend.outside = TRUE)


# Autocorrelação Global – a Estatística I de Moran ------------------------

# Para o cálculo da Estatística I de Moran, nosso algoritmo esperará como
# declaração um objeto de classe listw. Como exemplificação, voltaremos a 
# utilizar o objeto matrizW_queen:
listw_queen <- mat2listw(matrizW_queen_linha)

# Após isso, poderemos utilizar a função moran.test():
moran.test(x = cidades_num_acidentes$n, 
           listw = listw_queen)


###########################################################################

# A quais conclusões preliminares podemos chegar?


# O Diagrama da Estatística I de Moran ------------------------------------
moran.plot(x = cidades_num_acidentes$n, 
           listw = listw_queen, 
           #zero.policy = TRUE,
           xlab = "Óbitos", 
           ylab = "Óbitos epacialmente defasados"
           )


# Autocorrelação Local – a Estatística Moran Local ------------------------

# Considerando a variável poverty do objeto shp_co, podemos aferir sua 
# Estatística Moran Local, com o uso da função localmoran(), como se segue:
moran_local <- localmoran(x = cidades_num_acidentes$n, 
                          listw = listw_queen)



# Juntando os resultados da Estatística Moran Local no dataset do objeto shp_sp:
moran_local_mapa <- cbind(cidades_num_acidentes, moran_local)

# Plotando a Estatística Moran Local de forma espacial, sem problemas na escala
# de cores:
moran_local_mapa <- moran_local_mapa %>% 
  mutate(faixa_quantis = factor(quantcut(x = Ii, q = 5))) 

tm_shape(shp = moran_local_mapa) +
  tm_fill(col = "faixa_quantis", 
          palette = "plasma",
          n=10) +
  tm_borders() +
  tm_borders() +
  tm_layout(legend.outside = TRUE)

# Salvando o gráfico moran local para comparação subsequente:
moran_local_plot <- tm_shape(shp = moran_local_mapa) +
  tm_fill(col = "faixa_quantis", 
          palette = "plasma",
          n=10) +
  tm_borders() +
  tm_borders() +
  tm_layout(legend.outside = TRUE)

tmap_mode("plot")
# Criando um espaço no ambiente de visualização do R:
plot.new()
pushViewport(
  viewport(
    layout = grid.layout(1,2)
  )
)

# Comparando os dados da pobreza no Centro-Oeste brasileiro com os valores da
# Estatística Moran Local:
# Passo 4: Executar as plotagens
print(acidentes_plot, vp = viewport(layout.pos.col = 1, height = 5))
print(moran_local_plot, vp = viewport(layout.pos.col = 2, height = 5))
tmap_mode("view")
# Plotando as labels dadas pelas estatísticas de Moran (LL, LH, HL, HH):
moran_local_mapa <- cbind(moran_local_mapa, 
                          attr(x = moran_local, which = "quadr")[1])

tm_shape(shp = moran_local_mapa) +
  tm_fill(col = "mean", palette = "plasma", alpha=0.5) +
  tm_borders(col = "gray")+
  tm_shape(shp=acidentes)+
  tm_dots(size = 0.01,alpha=0.2)


# Estabelecendo uma Clusterização LISA ------------------------------------


# O primeiro passo é o estabelecimento de um objeto que reservará espaços para 
# conter, no futuro, os quadrantes AA, AB, BA e BB:
quadrantes <- vector(mode = "numeric", length = nrow(moran_local))

quadrantes

# Criando um vetor que contenha o centro das observações da variável poverty ao 
# redor de sua média:
variacao_acidentes_cidades <- cidades_num_acidentes$n - mean(cidades_num_acidentes$n)

variacao_acidentes_cidades

# Criando um vetor que contenha o centro dos valores da Estatística Moran Local 
# em torno de sua média:
centro_moran_local <- moran_local[,1] - mean(moran_local[,1])

centro_moran_local

# Criando um objeto que guarde a significância a ser adotada:
sig <- 0.05

# Enquadrando nossas observações em seus respectivos quadrantes:
quadrantes[variacao_acidentes_cidades > 0 & centro_moran_local > 0] <- "AA"
quadrantes[variacao_acidentes_cidades > 0 & centro_moran_local < 0] <- "AB"
quadrantes[variacao_acidentes_cidades < 0 & centro_moran_local > 0] <- "BA"
quadrantes[variacao_acidentes_cidades < 0 & centro_moran_local < 0] <- "BB"

quadrantes

# Ajustando a presença da observação em razão de sua significância estatística:
quadrantes[moran_local[,5] > sig] <- "Estatisticamente_não_significante"

quadrantes

# Juntando o objeto quadrantes ao objeto moran_local_mapa
moran_local_mapa["quadrantes"] <- factor(quadrantes)


# Versão do gráfico anterior para daltônicos:
tm_shape(shp = moran_local_mapa) +
  tm_polygons(col = "quadrantes", 
              pal = c(AA = "#FDE725FF",
                      AB = "#7AD151FF", 
                      BA = "#2A788EFF", 
                      BB = "#440154FF",
                      Estatisticamente_não_significante = "white")) +
  tm_borders() +
  tm_layout(legend.outside = TRUE)

# A que conclusões podemos chegar?

# Uma análise rápida sobre o Número de mortos

#avaliando mortos

cidades_num_mortos <- cidades_acidentes %>% group_by(municipio.x) %>% summarise(mortos = sum(mortos))  
cidades_num_mortos[is.na(cidades_num_mortos)] <-0

cidades_num_mortos %>%
  ggplot() +
  geom_sf(aes(fill=mortos))

tm_shape(shp=cidades_num_mortos)+
  tm_fill(col="mortos", alpha = 0.5)+
  tm_borders()+
  tm_shape(shp=acidentes[acidentes$mortos >= 1,])+
  tm_dots(size = 0.01,alpha=0.5)

setwd("I:/mestrado/data-science/seminario")

pacotes <- c("tidyverse","sf","spdep","tmap","adehabitatHR","knitr",
             "kableExtra","gtools","grid")

if(sum(as.numeric(!pacotes %in% installed.packages())) != 0){
  instalador <- pacotes[!pacotes %in% installed.packages()]
  for(i in 1:length(instalador)) {
    install.packages(instalador, dependencies = TRUE)
  }
  sapply(pacotes, require, character.only = TRUE) 
} else {
  sapply(pacotes, require, character.only = TRUE) 
}

data <- read.csv("output/datatran-sp.csv",sep=";",dec = ",",fileEncoding="ISO-8859-1")
#data_filter <- data[data$uf == "SP",]
data_filter <- data #Dados pré-processados

# Verificar se as colunas de latitude e longitude estão presentes e não são vazias
if (all(c("longitude", "latitude") %in% names(data_filter))) {
  data_filter <- data_filter[!is.na(data_filter$longitude) & !is.na(data_filter$latitude), ]
  
  # Criando um objeto do tipo sf a partir de um data frame:
  acidentes <- st_as_sf(x = data_filter, 
                        coords = c("longitude", "latitude"), 
                        crs = 4326)
  #o crs 4326 que utilizamos é o sistema de coordenadas geográficas não projetadas WGS84
  
  # Verificar se o objeto acidentes possui geometria válida
  if (nrow(acidentes) > 0) {
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
  } else {
    print("O objeto acidentes está vazio após a conversão para sf.")
  }
} else {
  print("As colunas de longitude e latitude não estão presentes no data_filter ou contêm valores NA.")
}

# Carregando um shapefile usando st_read:
shp_sc <- st_read("src/shapefile/SP_Municipios_2022.shp", 
                  options = "ENCODING=UTF-8")

# Visualizando o shapefile carregado:
tm_shape(shp = shp_sc) +
  tm_borders()

# Unindo as duas observações com ggplot:
cidades <- st_read("src/shapefile/SP_Municipios_2022.shp")
cidades %>% st_transform(4326) %>%
  ggplot() +
  geom_sf() +
  geom_sf(data=acidentes)

# Utilizando o mapa interativo:
tm_shape(shp = cidades) +
  tm_borders()+
  tm_shape(shp = acidentes)+
  tm_dots()

cidades <- cidades %>% st_transform(4326)
acidentes <- acidentes %>% st_transform(4326)
cidades <- cidades %>% rename("municipio"="NM_MUN")
cidades_acidentes <- cidades  %>% 
  st_join(acidentes) 
cidades_num_acidentes <-  cidades_acidentes %>% group_by(municipio.x) %>% 
  tally() 

cidades_num_acidentes %>%
  ggplot() +
  geom_sf(aes(fill=n))

# Outra forma:
tm_shape(shp=acidentes)+
  tm_dots(size = 0.01,alpha=0.3)+
  tm_shape(shp=cidades_num_acidentes)+
  tm_fill(col="n",alpha=0.4)+
  tm_borders()

# Análise espacial estatística
# Estabelecendo uma vizinhança:
vizinhos_queen <- poly2nb(pl = cidades_num_acidentes,
                          queen = TRUE,
                          row.names = cidades_num_acidentes$municipio.x)

summary(vizinhos_queen)

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

# Autocorrelação Global – a Estatística I de Moran
listw_queen <- mat2listw(matrizW_queen_linha)

moran.test(x = cidades_num_acidentes$n, 
           listw = listw_queen)

# O Diagrama da Estatística I de Moran
moran.plot(x = cidades_num_acidentes$n, 
           listw = listw_queen, 
           xlab = "Óbitos", 
           ylab = "Óbitos espacialmente defasados")

# Autocorrelação Local – a Estatística Moran Local
moran_local <- localmoran(x = cidades_num_acidentes$n, 
                          listw = listw_queen)

moran_local_mapa <- cbind(cidades_num_acidentes, moran_local)
moran_local_mapa <- moran_local_mapa %>% 
  mutate(faixa_quantis = factor(quantcut(x = Ii, q = 5))) 

tm_shape(shp = moran_local_mapa) +
  tm_fill(col = "faixa_quantis", 
          palette = "plasma",
          n=10) +
  tm_borders() +
  tm_borders() +
  tm_layout(legend.outside = TRUE)

moran_local_plot <- tm_shape(shp = moran_local_mapa) +
  tm_fill(col = "faixa_quantis", 
          palette = "plasma",
          n=10) +
  tm_borders() +
  tm_borders() +
  tm_layout(legend.outside = TRUE)

tmap_mode("plot")
plot.new()
pushViewport(
  viewport(
    layout = grid.layout(1,2)
  )
)

print(acidentes_plot, vp = viewport(layout.pos.col = 1, height = 5))
print(moran_local_plot, vp = viewport(layout.pos.col = 2, height = 5))
tmap_mode("view")

moran_local_mapa <- cbind(moran_local_mapa, 
                          attr(x = moran_local, which = "quadr")[1])

tm_shape(shp = moran_local_mapa) +
  tm_fill(col = "mean", palette = "plasma", alpha=0.5) +
  tm_borders(col = "gray")+
  tm_shape(shp=acidentes)+
  tm_dots(size = 0.01,alpha=0.2)

quadrantes <- vector(mode = "numeric", length = nrow(moran_local))

variacao_acidentes_cidades <- cidades_num_acidentes$n - mean(cidades_num_acidentes$n)
centro_moran_local <- moran_local[,1] - mean(moran_local[,1])
sig <- 0.05

quadrantes[variacao_acidentes_cidades > 0 & centro_moran_local > 0] <- "AA"
quadrantes[variacao_acidentes_cidades > 0 & centro_moran_local < 0] <- "AB"
quadrantes[variacao_acidentes_cidades < 0 & centro_moran_local > 0] <- "BA"
quadrantes[variacao_acidentes_cidades < 0 & centro_moran_local < 0] <- "BB"
quadrantes[moran_local[,5] > sig] <- "Estatisticamente_não_significante"

moran_local_mapa["quadrantes"] <- factor(quadrantes)

tm_shape(shp = moran_local_mapa) +
  tm_polygons(col = "quadr

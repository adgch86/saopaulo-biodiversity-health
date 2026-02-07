#####Abrindo dados de Saúde (Julia):
health<-read.csv(here("health_data//health_sp.csv"),sep="," )
head(health)
summary(health)
require(doBy)
summaryBy(malaria+leptospirose + diarrhea+dengue +chagas~ municipality, FUN=mean, data=health, rm.na=T )

#### Which municipalities have all the diseases? are they present in o
library(dplyr)
library(tidyr)
library(purrr)

# -------------------------------------------------------------------
# 1. Convert disease counts to presence/absence (1 = present, 0 = absent)
# -------------------------------------------------------------------

health_bin <- health %>%
  mutate(across(
    c(malaria, leptospirose, diarrhea, dengue, chagas),
    ~ ifelse(is.na(.), 0, ifelse(. > 0, 1, 0))
  ))


##### Lets calculate intensity, using populations
cus$COD<-as.integer(cus$Cod_ibge)


cus [cus$COD %in% health$COD,] ### erros with health municipality codes.
##I need to eliminate the last number in order to combine them:
library(stringr)
cus$COD<-as.integer(str_replace(cus$Cod_ibge, '[0-9]$', ''))

nrow(cus [cus$COD %in% health$COD,]) ### 187 are shared (because of health database)

###The dataframe generate includes population average between 2010 and 2022 for each yearw
names(cus)# quais variaveis correspondem a população e COD

kkk<-left_join(health,cus[,c(22,32)], keep=F) ##checar que use a varaivel população, e COD
nrow(kkk)
head(kkk)



library(dplyr)
library(tidyr)
library(purrr)

# -------------------------------------------------------------------
# 1. Convert disease counts to presence/absence (1 = present, 0 = absent)
# -------------------------------------------------------------------

health_bin <- kkk %>%
  mutate(across(
    c(malaria, leptospirose, diarrhea, dengue, chagas),
    ~ ifelse(is.na(.), 0, ifelse(. > 0, 1, 0))
  ))



# -------------------------
# 1. Definir variáveis
# -------------------------
disease_vars <- c("malaria", "leptospirose", "diarrhea", "dengue", "chagas")

# -------------------------
# 2. Persistência (anos com presença)
# -------------------------
persistence <- kkk %>%
  mutate(across(all_of(disease_vars), ~ ifelse(. > 0, 1, 0))) %>%
  group_by(COD, municipality) %>%
  summarise(across(all_of(disease_vars), sum, na.rm = TRUE), .groups = "drop") %>%
  rename_with(~ paste0("persist_", .), all_of(disease_vars))
head(persistence) #Esta em 0 ou todos os 10 anos? = persistence
# -------------------------
# 3. Intensidade (/100 mil hab)
# -------------------------
health_intensity <- kkk %>%
  mutate(across(
    all_of(disease_vars),
    ~ (. / population) * 100000,
    .names = "incidence_{col}"
  ))
head(health_intensity) ##em funcão da população, quao intensa é? para cada ano
# -------------------------
# 4. Intensidade média
# -------------------------
intensity_summary <- health_intensity %>%
  group_by(COD, municipality) %>%
  summarise(across(starts_with("incidence_"), mean, na.rm = TRUE), .groups = "drop")

# substituir NaN por 0
intensity_summary <- intensity_summary %>%
  mutate(across(starts_with("incidence_"), ~ ifelse(is.nan(.), 0, .)))

head(intensity_summary)

# -------------------------------------------------------------------
# 5. CO-PERSISTENCE — years with 2 or more diseases present
# -------------------------------------------------------------------
disease_vars <- c("malaria", "leptospirose", "diarrhea", "dengue", "chagas")

copersistence_table <- health_bin %>%
  rowwise() %>%
  mutate(n_present = sum(c_across(all_of(disease_vars)))) %>%
  ungroup() %>%
  group_by(COD, municipality) %>%
  summarise(
    copersistence = sum(n_present >= 2)
  )
head(copersistence_table) #Number of year with co-persistence
#Varies between 0-10 , 10 = all year this municipality had more than 1 disease

# -------------------------------------------------------------------
# 6. PAIRWISE CO-PERSISTENCE — all disease pairs
# -------------------------------------------------------------------

disease_pairs <- combn(disease_vars, 2, simplify = FALSE)
pairwise_table <- map_dfr(disease_pairs, function(pair) {
  a <- pair[1]
  b <- pair[2]
  
  health_bin %>%                     # ou kkk se estiver usando kkk no pipeline
    group_by(COD, municipality) %>%
    summarise(
      pair = paste(a, b, sep = "_"),
      copersistence = sum(.data[[a]] == 1 & .data[[b]] == 1, na.rm = TRUE),
      .groups = "drop"
    )
})

pairwise_wide <- pairwise_table %>%
  pivot_wider(names_from = pair, values_from = copersistence, values_fill = 0)
head(pairwise_wide)
nrow(pairwise_wide)
# -------------------------
# 7. Juntar tudo no dataset final
# -------------------------
health_final <- persistence %>%
  left_join(intensity_summary, by = c("COD", "municipality")) %>%
  left_join(copersistence_table, by = c("COD", "municipality")) %>%
  left_join(pairwise_wide, by = c("COD", "municipality"))

# visualizar
head(health_final)
names(health_final)
nrow(health_final)


names(cus)

subset_health<-left_join(health_final, cus, by="COD")
nrow(subset_health)
names(subset_health)
#subset_health$social_vulnerability<-subset_health$ge203

full_subset<-subset_health[,c(1:13,40:60)]
names(full_subset) #34


#Para arlex:
praArlex<-full_subset

arlex_tabela <- praArlex[ , c(1:32,34)] #eliminating geometry
names(arlex_tabela); head(arlex_tabela)

write.csv(as.data.frame(arlex_tabela), "para_arlex/praArlex_187tabela.csv", sep=";")
st_write(obj = praArlex, dsn = here("praArlexLate.shp"))


###Opening with sf package to be able to use ggplot with it
opa<-st_read(here("praArlexNew.shp"))

###############################################


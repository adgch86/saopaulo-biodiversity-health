# ==============================================================================
# Verificar codigo 351110 - posible DIADEMA segun datos Adrian
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("Verificando codigo 351110 vs datos de Adrian para DIADEMA\n")
cat("Adrian: 2014=841, 2015=3993, 2016=550\n")
cat("=======================================================================\n\n")

codigo <- "351110"

for (ano in c(2014, 2015, 2016)) {
  ano_2d <- substr(as.character(ano), 3, 4)
  filepath <- file.path(DATA_RAW, paste0("DENGBR", ano_2d, ".dbc"))

  df <- read.dbc(filepath)
  df_cod <- df[as.character(df$ID_MN_RESI) == codigo, ]

  cat(sprintf("Ano %d - Codigo %s: %d casos\n", ano, codigo, nrow(df_cod)))
}

cat("\n")

# Tambien verificar 351380 (codigo oficial DIADEMA)
cat("Comparando con 351380 (codigo IBGE oficial de DIADEMA):\n\n")
codigo2 <- "351380"

for (ano in c(2014, 2015, 2016)) {
  ano_2d <- substr(as.character(ano), 3, 4)
  filepath <- file.path(DATA_RAW, paste0("DENGBR", ano_2d, ".dbc"))

  df <- read.dbc(filepath)
  df_cod <- df[as.character(df$ID_MN_RESI) == codigo2, ]

  cat(sprintf("Ano %d - Codigo %s: %d casos\n", ano, codigo2, nrow(df_cod)))
}

cat("\n=======================================================================\n")
cat("COMPARACION:\n")
cat("Adrian DIADEMA:    841 | 3993 | 550\n")
cat("Codigo 351110:     843 |  ??? | ???\n")
cat("Codigo 351380:    1481 | 6953 | 2222\n")
cat("=======================================================================\n")

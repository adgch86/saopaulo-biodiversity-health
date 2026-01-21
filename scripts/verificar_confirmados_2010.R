# ==============================================================================
# Verificar datos CONFIRMADOS de ADAMANTINA, ADOLFO, AGUAI para 2010
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("Verificando ADAMANTINA, ADOLFO, AGUAI - Ano 2010\n")
cat("Comparando TOTAL vs CONFIRMADOS\n")
cat("=======================================================================\n\n")

# Codigos
codigos <- c("350010", "350020", "350030")
nombres <- c("ADAMANTINA", "ADOLFO", "AGUAI")
adrian <- c(246, 64, 325)

# Leer archivo 2010
filepath <- file.path(DATA_RAW, "DENGBR10.dbc")
df <- read.dbc(filepath)

# Filtrar SP
df_sp <- df[substr(as.character(df$ID_MN_RESI), 1, 2) == "35", ]

cat("RESULTADOS:\n")
cat(sprintf("%-12s %-12s %8s %8s %8s\n", "CODIGO", "MUNICIPIO", "ADRIAN", "TOTAL", "CONFIRM"))
cat(strrep("-", 55), "\n")

for (i in 1:3) {
  cod <- codigos[i]
  nome <- nombres[i]
  val_adrian <- adrian[i]

  # Total
  df_mun <- df_sp[as.character(df_sp$ID_MN_RESI) == cod, ]
  total <- nrow(df_mun)

  # Confirmados (CLASSI_FIN = 5, 10, 11, 12)
  classi <- as.numeric(as.character(df_mun$CLASSI_FIN))
  confirmados <- sum(classi %in% c(5, 10, 11, 12), na.rm = TRUE)

  cat(sprintf("%-12s %-12s %8d %8d %8d\n", cod, nome, val_adrian, total, confirmados))
}

cat("\n=======================================================================\n")
cat("Si Adrian = CONFIRMADOS, los valores deberian coincidir\n")
cat("=======================================================================\n")

# ==============================================================================
# Verificar CLASSI_FIN = 1 para ADAMANTINA, ADOLFO, AGUAI - 2010
# Criterio correcto segun sesion anterior
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("Verificando CLASSI_FIN = 1 - Ano 2010\n")
cat("Criterio: ID_MN_RESI + CLASSI_FIN == 1\n")
cat("=======================================================================\n\n")

# Codigos y valores de Adrian
codigos <- c("350010", "350020", "350030")
nombres <- c("ADAMANTINA", "ADOLFO", "AGUAI")
adrian <- c(246, 64, 325)

# Leer archivo
filepath <- file.path(DATA_RAW, "DENGBR10.dbc")
df <- read.dbc(filepath)

cat("RESULTADOS:\n")
cat(sprintf("%-12s %-12s %8s %8s %8s\n", "CODIGO", "MUNICIPIO", "ADRIAN", "CLASSI=1", "DIFF"))
cat(strrep("-", 55), "\n")

for (i in 1:3) {
  cod <- codigos[i]
  nome <- nombres[i]
  val_adrian <- adrian[i]

  # Filtrar municipio
  df_mun <- df[as.character(df$ID_MN_RESI) == cod, ]

  # Contar CLASSI_FIN = 1
  classi <- as.numeric(as.character(df_mun$CLASSI_FIN))
  n_classi1 <- sum(classi == 1, na.rm = TRUE)

  diff <- n_classi1 - val_adrian

  cat(sprintf("%-12s %-12s %8d %8d %8d\n", cod, nome, val_adrian, n_classi1, diff))
}

cat("\n=======================================================================\n")

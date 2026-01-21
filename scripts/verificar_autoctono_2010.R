# ==============================================================================
# Verificar AUTOCTONO (TPAUTOCTO = 1) para ADAMANTINA, ADOLFO, AGUAI - 2010
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("Verificando CASOS AUTOCTONOS (TPAUTOCTO = 1) - 2010\n")
cat("=======================================================================\n\n")

# Codigos y valores de Adrian
codigos <- c("350010", "350020", "350030")
nombres <- c("ADAMANTINA", "ADOLFO", "AGUAI")
adrian <- c(246, 64, 325)

# Leer archivo
filepath <- file.path(DATA_RAW, "DENGBR10.dbc")
df <- read.dbc(filepath)

cat("RESULTADOS:\n")
cat(sprintf("%-12s %-12s %8s %8s %8s\n", "CODIGO", "MUNICIPIO", "ADRIAN", "AUTOCTONO", "DIFF"))
cat(strrep("-", 55), "\n")

for (i in 1:3) {
  cod <- codigos[i]
  nome <- nombres[i]
  val_adrian <- adrian[i]

  # Filtrar municipio
  df_mun <- df[as.character(df$ID_MN_RESI) == cod, ]

  # Contar autoctonos (TPAUTOCTO = 1)
  auto <- as.numeric(as.character(df_mun$TPAUTOCTO))
  n_auto <- sum(auto == 1, na.rm = TRUE)

  diff <- n_auto - val_adrian

  cat(sprintf("%-12s %-12s %8d %8d %8d\n", cod, nome, val_adrian, n_auto, diff))
}

cat("\n=======================================================================\n")
cat("Si DIFF es pequeño (~0), el filtro AUTOCTONO es el correcto\n")
cat("=======================================================================\n")

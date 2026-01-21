# ==============================================================================
# Verificar datos de ADAMANTINA, ADOLFO, AGUAI para 2010
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("Verificando ADAMANTINA, ADOLFO, AGUAI - Ano 2010\n")
cat("Municipio de residencia + Ano de notificacao\n")
cat("=======================================================================\n\n")

# Codigos segun imagen de Adrian
codigos <- c(
  "350010" = "ADAMANTINA",
  "350020" = "ADOLFO",
  "350030" = "AGUAI"
)

# Valores de Adrian para 2010
adrian <- c(
  "350010" = 246,
  "350020" = 64,
  "350030" = 325
)

# Leer archivo 2010
filepath <- file.path(DATA_RAW, "DENGBR10.dbc")
cat("Leyendo", basename(filepath), "...\n\n")

df <- read.dbc(filepath)
cat(sprintf("Total registros Brasil: %d\n", nrow(df)))

# Filtrar SP
df_sp <- df[substr(as.character(df$ID_MN_RESI), 1, 2) == "35", ]
cat(sprintf("Total registros SP: %d\n\n", nrow(df_sp)))

# Contar para cada municipio
cat("COMPARACION:\n")
cat(sprintf("%-10s %-15s %10s %10s %10s\n", "CODIGO", "MUNICIPIO", "ADRIAN", "DATASUS", "DIFERENCIA"))
cat(strrep("-", 60), "\n")

for (cod in names(codigos)) {
  n_datasus <- sum(as.character(df_sp$ID_MN_RESI) == cod)
  n_adrian <- adrian[cod]
  diff <- n_datasus - n_adrian

  cat(sprintf("%-10s %-15s %10d %10d %10d\n",
              cod, codigos[cod], n_adrian, n_datasus, diff))
}

cat("\n=======================================================================\n")

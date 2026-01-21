# ==============================================================================
# Buscar el filtro correcto comparando con datos de Adrian 2010
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("Buscando filtro que coincida con Adrian - 2010\n")
cat("ADAMANTINA=246, ADOLFO=64, AGUAI=325\n")
cat("=======================================================================\n\n")

# Leer archivo
filepath <- file.path(DATA_RAW, "DENGBR10.dbc")
df <- read.dbc(filepath)

# Filtrar ADAMANTINA (350010) para analizar
df_adam <- df[as.character(df$ID_MN_RESI) == "350010", ]

cat(sprintf("ADAMANTINA (350010) - Total registros: %d\n", nrow(df_adam)))
cat(sprintf("Adrian tiene: 246\n\n"))

# Verificar valores de CLASSI_FIN
cat("Valores de CLASSI_FIN:\n")
print(table(df_adam$CLASSI_FIN, useNA = "ifany"))

# Probar diferentes filtros
classi <- as.numeric(as.character(df_adam$CLASSI_FIN))

cat("\nProbando filtros:\n")
cat(sprintf("  CLASSI_FIN = 5: %d\n", sum(classi == 5, na.rm = TRUE)))
cat(sprintf("  CLASSI_FIN = 10: %d\n", sum(classi == 10, na.rm = TRUE)))
cat(sprintf("  CLASSI_FIN = 11: %d\n", sum(classi == 11, na.rm = TRUE)))
cat(sprintf("  CLASSI_FIN = 12: %d\n", sum(classi == 12, na.rm = TRUE)))
cat(sprintf("  CLASSI_FIN in (5,10,11,12): %d\n", sum(classi %in% c(5,10,11,12), na.rm = TRUE)))
cat(sprintf("  CLASSI_FIN in (10,11,12): %d\n", sum(classi %in% c(10,11,12), na.rm = TRUE)))

# Verificar TPAUTOCTO
cat("\nValores de TPAUTOCTO:\n")
print(table(df_adam$TPAUTOCTO, useNA = "ifany"))

auto <- as.numeric(as.character(df_adam$TPAUTOCTO))
cat(sprintf("  TPAUTOCTO = 1 (autoctono): %d\n", sum(auto == 1, na.rm = TRUE)))

# Combinaciones
cat("\nCombinaciones:\n")
cat(sprintf("  Confirmado + Autoctono: %d\n",
            sum(classi %in% c(5,10,11,12) & auto == 1, na.rm = TRUE)))
cat(sprintf("  CLASSI_FIN = 5 + Autoctono: %d\n",
            sum(classi == 5 & auto == 1, na.rm = TRUE)))

# CRITERIO
cat("\nValores de CRITERIO:\n")
print(table(df_adam$CRITERIO, useNA = "ifany"))

criterio <- as.numeric(as.character(df_adam$CRITERIO))
cat(sprintf("  CRITERIO = 1 (lab): %d\n", sum(criterio == 1, na.rm = TRUE)))
cat(sprintf("  CRITERIO = 2 (clinico-epi): %d\n", sum(criterio == 2, na.rm = TRUE)))

# Buscar combinacion que de ~246
cat("\n\n*** Buscando valor cercano a 246 ***\n")

# Solo CLASSI_FIN = 5 parece ser el mas cercano
n_5 <- sum(classi == 5, na.rm = TRUE)
cat(sprintf("CLASSI_FIN = 5: %d (diff de 246: %d)\n", n_5, n_5 - 246))

# Confirmado + Criterio 2
n_conf_crit2 <- sum(classi %in% c(5,10,11,12) & criterio == 2, na.rm = TRUE)
cat(sprintf("Confirmado + CRITERIO=2: %d (diff de 246: %d)\n", n_conf_crit2, n_conf_crit2 - 246))

# Solo CLASSI_FIN = 5 + Criterio 2
n_5_crit2 <- sum(classi == 5 & criterio == 2, na.rm = TRUE)
cat(sprintf("CLASSI_FIN=5 + CRITERIO=2: %d (diff de 246: %d)\n", n_5_crit2, n_5_crit2 - 246))

cat("\n=======================================================================\n")

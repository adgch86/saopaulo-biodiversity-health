# ==============================================================================
# Probar diferentes filtros para encontrar match con datos de Adrian
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("Probando diferentes filtros para DIADEMA 2015 (Adrian = 3993)\n")
cat("=======================================================================\n\n")

filepath <- file.path(DATA_RAW, "DENGBR15.dbc")
df <- read.dbc(filepath)

# Filtrar DIADEMA
df_d <- df[as.character(df$ID_MN_RESI) == "351380", ]
cat(sprintf("Total DIADEMA 2015: %d\n\n", nrow(df_d)))

classi <- as.numeric(as.character(df_d$CLASSI_FIN))
auto <- as.numeric(as.character(df_d$TPAUTOCTO))
criterio <- as.numeric(as.character(df_d$CRITERIO))

# Probar cada valor de CLASSI_FIN
cat("Por CLASSI_FIN:\n")
for (v in c(1, 2, 3, 4, 5, 8, 10, 11, 12)) {
  n <- sum(classi == v, na.rm = TRUE)
  if (n > 0) {
    cat(sprintf("  CLASSI_FIN = %d: %d casos\n", v, n))
  }
}

# Probar combinaciones
cat("\nCombinaciones:\n")

# Solo CLASSI_FIN = 5 (confirmado antiguo)
cat(sprintf("  CLASSI_FIN = 5: %d\n", sum(classi == 5, na.rm = TRUE)))

# Solo CLASSI_FIN = 10 (dengue)
cat(sprintf("  CLASSI_FIN = 10: %d\n", sum(classi == 10, na.rm = TRUE)))

# Solo CLASSI_FIN in (10,11,12)
cat(sprintf("  CLASSI_FIN in (10,11,12): %d\n", sum(classi %in% c(10, 11, 12), na.rm = TRUE)))

# CLASSI_FIN = 5 + Autoctono
cat(sprintf("  CLASSI_FIN = 5 + AUTOCTONO: %d\n",
            sum(classi == 5 & auto == 1, na.rm = TRUE)))

# CLASSI_FIN = 10 + Autoctono
cat(sprintf("  CLASSI_FIN = 10 + AUTOCTONO: %d\n",
            sum(classi == 10 & auto == 1, na.rm = TRUE)))

# Por CRITERIO
cat("\nPor CRITERIO (1=lab, 2=clinico-epidemiologico):\n")
cat(sprintf("  CRITERIO = 1: %d\n", sum(criterio == 1, na.rm = TRUE)))
cat(sprintf("  CRITERIO = 2: %d\n", sum(criterio == 2, na.rm = TRUE)))

# Confirmado + Criterio lab
cat(sprintf("  Confirmado + CRITERIO = 1: %d\n",
            sum(classi %in% c(5, 10, 11, 12) & criterio == 1, na.rm = TRUE)))

# CLASSI_FIN = 5 + CRITERIO = 1
cat(sprintf("  CLASSI_FIN = 5 + CRITERIO = 1: %d\n",
            sum(classi == 5 & criterio == 1, na.rm = TRUE)))

# CLASSI_FIN = 5 + CRITERIO = 2
cat(sprintf("  CLASSI_FIN = 5 + CRITERIO = 2: %d\n",
            sum(classi == 5 & criterio == 2, na.rm = TRUE)))

# Solo confirmado laboratorial
cat("\n\nBuscando ~3993...\n")

# Probar CLASSI_FIN = 5 solo (que parece ser el criterio antiguo)
n_5 <- sum(classi == 5, na.rm = TRUE)
cat(sprintf("CLASSI_FIN = 5 total: %d (diferencia de 3993: %d)\n", n_5, n_5 - 3993))

# Probar diferentes combinaciones de autoctono
cat("\nAutoctonos por CLASSI_FIN:\n")
for (v in c(5, 10, 11, 12)) {
  n <- sum(classi == v & auto == 1, na.rm = TRUE)
  if (n > 0) {
    cat(sprintf("  CLASSI_FIN = %d + AUTOCTONO = 1: %d\n", v, n))
  }
}

# Quizas Adrian usa solo confirmados sin especificar tipo (CLASSI_FIN != 1,8)
n_no_desc <- sum(!classi %in% c(1, 8) & !is.na(classi), na.rm = TRUE)
cat(sprintf("\nNo descartados (CLASSI_FIN != 1, 8): %d\n", n_no_desc))

# Probar con la columna de evolucion
cat("\n\nValores de EVOLUCAO:\n")
print(table(df_d$EVOLUCAO, useNA = "ifany"))

cat("\n=======================================================================\n")
cat("OBJETIVO: Encontrar filtro que de 3993 para DIADEMA 2015\n")
cat("=======================================================================\n")

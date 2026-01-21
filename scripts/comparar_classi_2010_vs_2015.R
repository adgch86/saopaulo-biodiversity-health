# ==============================================================================
# Comparar valores de CLASSI_FIN entre 2010 y 2015
# ==============================================================================

.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

PROJECT_ROOT <- "C:/Users/arlex/Documents/Adrian David"
DATA_RAW <- file.path(PROJECT_ROOT, "data/raw/datasus")

cat("=======================================================================\n")
cat("Comparando CLASSI_FIN entre 2010 y 2015\n")
cat("=======================================================================\n\n")

# 2010
filepath_10 <- file.path(DATA_RAW, "DENGBR10.dbc")
df_10 <- read.dbc(filepath_10)
df_10_sp <- df_10[substr(as.character(df_10$ID_MN_RESI), 1, 2) == "35", ]

cat("CLASSI_FIN en 2010 (SP):\n")
print(table(df_10_sp$CLASSI_FIN, useNA = "ifany"))

# 2015
filepath_15 <- file.path(DATA_RAW, "DENGBR15.dbc")
df_15 <- read.dbc(filepath_15)
df_15_sp <- df_15[substr(as.character(df_15$ID_MN_RESI), 1, 2) == "35", ]

cat("\nCLASSI_FIN en 2015 (SP):\n")
print(table(df_15_sp$CLASSI_FIN, useNA = "ifany"))

cat("\n=======================================================================\n")
cat("INTERPRETACION:\n")
cat("2010: CLASSI_FIN=1 parece ser 'Confirmado'\n")
cat("2015: CLASSI_FIN=1 es 'Descartado', 5=Confirmado antiguo, 10/11/12=Confirmado nuevo\n")
cat("=======================================================================\n")

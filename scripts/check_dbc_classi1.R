# Verificar CLASSI_FIN = 1 como casos confirmados
.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))
library(read.dbc)

filepath <- "C:/Users/arlex/Documents/Adrian David/data/raw/datasus/DENGBR10.dbc"
df <- read.dbc(filepath)

# Filtrar solo SP por residencia Y CLASSI_FIN = 1
df_sp <- df[substr(as.character(df$ID_MN_RESI), 1, 2) == "35", ]
df_conf <- df_sp[df_sp$CLASSI_FIN == 1, ]

cat("=== DENGUE SP 2010 - SOLO CLASSI_FIN = 1 ===\n\n")
cat("Total SP residencia:", nrow(df_sp), "\n")
cat("Total CLASSI_FIN = 1:", nrow(df_conf), "\n")
cat("Esperado segun Adrian:", 190603, "\n")

# Verificar municipios especificos
cat("\n=== VERIFICACION POR MUNICIPIO ===\n")
municipios <- list(
  c("350010", "ADAMANTINA", 246),
  c("350020", "ADOLFO", 64),
  c("350030", "AGUAI", 325)
)

cat(sprintf("%-10s %-15s %10s %10s %10s\n", "COD", "MUNICIPIO", "ESPERADO", "OBTENIDO", "DIFF"))
cat(strrep("-", 60), "\n")

for (m in municipios) {
  cod <- m[1]
  nombre <- m[2]
  esperado <- as.numeric(m[3])

  casos <- nrow(df_conf[substr(as.character(df_conf$ID_MN_RESI), 1, 6) == cod, ])
  diff <- casos - esperado

  cat(sprintf("%-10s %-15s %10d %10d %10d\n", cod, nombre, esperado, casos, diff))
}

cat("\n=== TOTAL SP ===\n")
total <- nrow(df_conf)
cat("Total obtenido:", total, "\n")
cat("Total esperado:", 190603, "\n")
cat("Diferencia:", total - 190603, "\n")

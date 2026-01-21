# Script para verificar columnas en archivos DBC
.libPaths(c("C:/Users/arlex/R_libs", .libPaths()))

library(read.dbc)

filepath <- "C:/Users/arlex/Documents/Adrian David/data/raw/datasus/DENGBR10.dbc"
cat("Leyendo:", filepath, "\n")

df <- read.dbc(filepath)

cat("\n=== COLUMNAS DISPONIBLES ===\n")
print(names(df))

cat("\n=== COLUMNAS CON MUN/RESI/NOTIF ===\n")
mun_cols <- grep("MUN|RESI|NOTIF", names(df), value = TRUE, ignore.case = TRUE)
print(mun_cols)

cat("\n=== EJEMPLO DE VALORES ===\n")
for (col in mun_cols) {
  cat(col, ":", head(as.character(df[[col]]), 5), "\n")
}

cat("\n=== CONTEO PARA SP (codigo 35xxxx) ===\n")
if ("ID_MUNICIP" %in% names(df)) {
  sp_notif <- sum(substr(as.character(df$ID_MUNICIP), 1, 2) == "35", na.rm = TRUE)
  cat("Por ID_MUNICIP (notificacion):", sp_notif, "\n")
}
if ("ID_MN_RESI" %in% names(df)) {
  sp_resi <- sum(substr(as.character(df$ID_MN_RESI), 1, 2) == "35", na.rm = TRUE)
  cat("Por ID_MN_RESI (residencia):", sp_resi, "\n")
}

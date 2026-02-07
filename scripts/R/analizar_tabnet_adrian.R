# Análisis comparativo TABNET Adrian vs DATASUS DBC
# Objetivo: Identificar qué filtro usa TABNET para "Casos Prováveis"

library(read.dbc)

# Función segura para leer DBC
leer_dbc_seguro <- function(archivo) {
  tryCatch({
    df <- read.dbc(archivo)
    return(df)
  }, error = function(e) {
    cat("Error leyendo", archivo, ":", e$message, "\n")
    return(NULL)
  })
}

# Cargar datos 2015
cat("Cargando DENGSP15.dbc...\n")
df_2015 <- leer_dbc_seguro("data/raw/datasus/DENGSP15.dbc")

if (!is.null(df_2015)) {
  cat("Total registros 2015:", nrow(df_2015), "\n\n")

  # Distribución de CLASSI_FIN
  cat("Distribución de CLASSI_FIN en 2015:\n")
  print(table(df_2015$CLASSI_FIN, useNA = "ifany"))
  cat("\n")

  # =====================================================
  # ANÁLISIS DIADEMA (351380)
  # TABNET Adrian dice: 3996 casos en 2015
  # =====================================================

  diadema <- df_2015[df_2015$ID_MN_RESI == "351380", ]
  cat("\n========================================\n")
  cat("DIADEMA (351380) - 2015\n")
  cat("========================================\n")
  cat("Total registros:", nrow(diadema), "\n")
  cat("\nDistribución CLASSI_FIN:\n")
  print(table(diadema$CLASSI_FIN, useNA = "ifany"))

  cat("\n--- COMPARACIÓN CON TABNET ADRIAN (3996) ---\n")

  # Prueba 1: Excluir CLASSI_FIN = 5 (Descartado)
  n1 <- sum(diadema$CLASSI_FIN != 5 | is.na(diadema$CLASSI_FIN), na.rm = FALSE)
  cat("Excluir CLASSI_FIN=5:", n1, "\n")

  # Prueba 2: Excluir CLASSI_FIN = 5 y 8
  n2 <- sum((diadema$CLASSI_FIN != 5 & diadema$CLASSI_FIN != 8) | is.na(diadema$CLASSI_FIN), na.rm = FALSE)
  cat("Excluir CLASSI_FIN=5,8:", n2, "\n")

  # Prueba 3: Solo confirmados (10, 11, 12)
  n3 <- sum(diadema$CLASSI_FIN %in% c(10, 11, 12))
  cat("Solo confirmados (10,11,12):", n3, "\n")

  # Prueba 4: Incluir todo excepto descartados
  # Según TABNET: "casos prováveis foram incluídas todas notificações, exceto casos descartados"
  # En 2014+ descartados podrían ser CLASSI_FIN = 5
  n4 <- nrow(diadema) - sum(diadema$CLASSI_FIN == 5, na.rm = TRUE)
  cat("Total - CLASSI_FIN=5:", n4, "\n")

  cat("\n========================================\n")
  cat("VALOR ESPERADO (TABNET Adrian): 3996\n")
  cat("========================================\n")

  # =====================================================
  # ANÁLISIS CRAVINHOS (351310)
  # TABNET Adrian dice: 144 casos en 2015
  # =====================================================

  cravinhos <- df_2015[df_2015$ID_MN_RESI == "351310", ]
  cat("\n========================================\n")
  cat("CRAVINHOS (351310) - 2015\n")
  cat("========================================\n")
  cat("Total registros:", nrow(cravinhos), "\n")
  cat("\nDistribución CLASSI_FIN:\n")
  print(table(cravinhos$CLASSI_FIN, useNA = "ifany"))

  cat("\n--- COMPARACIÓN CON TABNET ADRIAN (144) ---\n")

  # Las mismas pruebas
  n1 <- sum(cravinhos$CLASSI_FIN != 5 | is.na(cravinhos$CLASSI_FIN), na.rm = FALSE)
  cat("Excluir CLASSI_FIN=5:", n1, "\n")

  n4 <- nrow(cravinhos) - sum(cravinhos$CLASSI_FIN == 5, na.rm = TRUE)
  cat("Total - CLASSI_FIN=5:", n4, "\n")

  cat("\n========================================\n")
  cat("VALOR ESPERADO (TABNET Adrian): 144\n")
  cat("========================================\n")

} else {
  cat("No se pudo cargar el archivo DBC\n")
}

cat("\nAnálisis completado.\n")

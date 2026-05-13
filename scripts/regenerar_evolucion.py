import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path.home() / "proyectos" / "gasolineras-mty"
DATA_PROCESSED = PROJECT_ROOT / "data" / "processed"
EXPORTS = DATA_PROCESSED / "looker_exports"

# Cargar datos ya procesados
estaciones_final = pd.read_csv(EXPORTS / "looker_estaciones_zm.csv")
magna = pd.read_parquet(DATA_PROCESSED / "magna_zm_diario.parquet")

# Recalcular evolución diaria por categoría
magna_cat = magna.merge(
    estaciones_final[["permiso", "categoria"]],
    left_on="numero_permiso", right_on="permiso", how="inner"
)

evolucion = (
    magna_cat.groupby(["fecha", "categoria"])["precio"]
    .agg(["mean", "median", "count"])
    .reset_index()
    .rename(columns={"mean": "precio_promedio", "median": "precio_mediano", "count": "estaciones"})
)

# Formato YYYYMMDD sin guiones (lo que Looker espera para tipo "Fecha (AAAAMMDD)")
evolucion["fecha"] = pd.to_datetime(evolucion["fecha"]).dt.strftime("%Y%m%d")

evolucion.to_csv(EXPORTS / "looker_evolucion_diaria.csv", index=False)
print(f"Re-exportado: {len(evolucion)} filas")
print(evolucion.head(8).to_string(index=False))
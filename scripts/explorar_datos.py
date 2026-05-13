"""
Exploración inicial — Pandas, NO awk.
Validar estructura de catálogo + precios + XML.
"""

import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET

DATA_DIR = Path.home() / "proyectos" / "gasolineras-mty" / "data" / "exploracion"

# ============================================================
# 1. CATÁLOGO DE PERMISOS
# ============================================================
print("=" * 70)
print("1. CATÁLOGO DE PERMISOS VIGENTES")
print("=" * 70)

permisos = pd.read_csv(DATA_DIR / "permisos_vigentes.csv")
print(f"\nFilas totales: {len(permisos):,}")
print(f"Columnas: {list(permisos.columns)}")
print(f"\nMuestra (5 filas):")
print(permisos.head().to_string())

print(f"\n--- Tipos de permiso ---")
print(permisos["tipo_permiso"].value_counts())

print(f"\n--- Estatus ---")
print(permisos["estatus"].value_counts())

print(f"\n--- Entidades (top 20) ---")
print(permisos["entidad"].value_counts().head(20))

print(f"\n--- Cobertura zona_geo ---")
print(permisos["zona_geo"].value_counts(dropna=False))
total = len(permisos)
sin_dato = (permisos["zona_geo"] == "sin dato").sum()
print(f"\n% con 'sin dato': {sin_dato / total * 100:.1f}%")

print(f"\n--- Permisos en Nuevo León ---")
nl = permisos[permisos["entidad"] == "Nuevo León"]
print(f"Total NL (todos los tipos): {len(nl)}")
nl_es = nl[
    (nl["tipo_permiso"] == "Expendio en estación de servicio")
    & (nl["estatus"] == "Vigente")
]
print(f"NL solo Expendio en estación de servicio + Vigente: {len(nl_es)}")

print(f"\n--- Formato de num_per (10 ejemplos NL Expendio Vigente) ---")
print(nl_es["num_per"].head(10).tolist())

# ============================================================
# 2. PRECIOS PROMEDIO DIARIOS
# ============================================================
print("\n" + "=" * 70)
print("2. PRECIOS PROMEDIO DIARIOS (feb 2026)")
print("=" * 70)

precios = pd.read_csv(DATA_DIR / "precios_promedio_diarios.csv")
print(f"\nFilas totales: {len(precios):,}")
print(f"Columnas: {list(precios.columns)}")
print(f"\nMuestra:")
print(precios.head().to_string())

precios["fecha"] = pd.to_datetime(precios["fecha"])
print(f"\n--- Rango de fechas ---")
print(f"Min: {precios['fecha'].min()}")
print(f"Max: {precios['fecha'].max()}")
print(f"Días únicos: {precios['fecha'].nunique()}")

print(f"\n--- Subproductos ---")
print(precios["subproducto"].value_counts())

print(f"\n--- Permisos únicos en precios ---")
print(f"Total permisos únicos: {precios['numero_permiso'].nunique():,}")
print(f"Muestra de num_permiso (5):")
print(precios["numero_permiso"].head().tolist())

# ============================================================
# 3. XML DE PLACES
# ============================================================
print("\n" + "=" * 70)
print("3. XML PLACES (coordenadas)")
print("=" * 70)

tree = ET.parse("/tmp/places_test.xml")
root = tree.getroot()

records = []
for place in root.findall("place"):
    pid = place.get("place_id")
    name = place.findtext("name", "")
    cre_id = place.findtext("cre_id", "")
    loc = place.find("location")
    x = float(loc.findtext("x")) if loc is not None and loc.findtext("x") else None
    y = float(loc.findtext("y")) if loc is not None and loc.findtext("y") else None
    records.append({"place_id": pid, "name": name, "cre_id": cre_id, "lng": x, "lat": y})

xml_df = pd.DataFrame(records)
print(f"\nFilas totales: {len(xml_df):,}")
print(f"Sin coordenadas (NaN): {xml_df['lat'].isna().sum()}")
print(f"\nMuestra cre_id:")
print(xml_df["cre_id"].head().tolist())

# ============================================================
# 4. JOIN CRÍTICO
# ============================================================
print("\n" + "=" * 70)
print("4. JOIN: catálogo NL Expendio Vigente ↔ XML")
print("=" * 70)

joined = nl_es.merge(
    xml_df, left_on="num_per", right_on="cre_id", how="left", indicator=True
)
match = (joined["_merge"] == "both").sum()
no_match = (joined["_merge"] == "left_only").sum()
print(f"\nTotal NL Expendio Vigente en catálogo: {len(nl_es)}")
print(f"Match en XML (con coords): {match}")
print(f"Sin match en XML: {no_match}")
print(f"% cobertura del join: {match / len(nl_es) * 100:.1f}%")

print(f"\n--- 5 ejemplos de num_per que NO matchean ---")
print(joined[joined["_merge"] == "left_only"]["num_per"].head(5).tolist())

# Bbox ZM Monterrey (Mty, San Pedro, San Nicolás, Guadalupe, Apodaca,
# Escobedo, García, Santa Catarina, Juárez)
zm_mty = joined[
    (joined["_merge"] == "both")
    & (joined["lng"].between(-100.65, -99.95))
    & (joined["lat"].between(25.55, 25.95))
]
print(f"\n--- Estaciones NL con coords dentro de bbox ZM Monterrey ---")
print(f"En bbox ZM Monterrey: {len(zm_mty)}")
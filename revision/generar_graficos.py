"""
Script para generar gráficos de análisis de reactancias.
Ayuda a visualizar la distribución de diferencias y validar umbrales.
"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Configuración
INPUT_FILE = Path(__file__).parent / "output" / "homologacion_clasificada.xlsx"
OUTPUT_DIR = Path(__file__).parent / "output" / "graficos"
OUTPUT_DIR.mkdir(exist_ok=True)

# Estilo
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.figsize'] = (12, 8)
plt.rcParams['font.size'] = 10


def cargar_datos():
    """Carga el archivo de homologación clasificada."""
    df = pd.read_excel(INPUT_FILE)
    print(f"Datos cargados: {len(df)} registros")
    return df


def grafico_histograma_diferencias(df):
    """
    Histograma de diferencias porcentuales con CNE e Infotécnica.
    Muestra dónde cae el umbral del 15%.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Diferencia con CNE
    diff_cne = df['diff_X_CNE_%'].dropna()
    diff_cne = diff_cne[diff_cne <= 200]  # Limitar outliers

    axes[0].hist(diff_cne, bins=50, edgecolor='black', alpha=0.7, color='steelblue')
    axes[0].axvline(x=15, color='red', linestyle='--', linewidth=2, label='Umbral 15%')
    axes[0].set_xlabel('Diferencia porcentual (%)')
    axes[0].set_ylabel('Frecuencia')
    axes[0].set_title(f'Distribución |X_ENT - X_CNE| / X_ENT\n(n={len(diff_cne)})')
    axes[0].legend()

    # Estadísticas CNE
    below_15_cne = (diff_cne < 15).sum()
    axes[0].text(0.95, 0.95, f'< 15%: {below_15_cne} ({below_15_cne/len(diff_cne)*100:.1f}%)\n≥ 15%: {len(diff_cne)-below_15_cne}',
                 transform=axes[0].transAxes, ha='right', va='top',
                 bbox=dict(boxstyle='round', facecolor='wheat'))

    # Diferencia con Infotécnica
    diff_inf = df['diff_X_Infotec_%'].dropna()
    diff_inf = diff_inf[diff_inf <= 200]

    axes[1].hist(diff_inf, bins=50, edgecolor='black', alpha=0.7, color='darkorange')
    axes[1].axvline(x=15, color='red', linestyle='--', linewidth=2, label='Umbral 15%')
    axes[1].set_xlabel('Diferencia porcentual (%)')
    axes[1].set_ylabel('Frecuencia')
    axes[1].set_title(f'Distribución |X_ENT - X_Infotec| / X_ENT\n(n={len(diff_inf)})')
    axes[1].legend()

    # Estadísticas Infotec
    below_15_inf = (diff_inf < 15).sum()
    axes[1].text(0.95, 0.95, f'< 15%: {below_15_inf} ({below_15_inf/len(diff_inf)*100:.1f}%)\n≥ 15%: {len(diff_inf)-below_15_inf}',
                 transform=axes[1].transAxes, ha='right', va='top',
                 bbox=dict(boxstyle='round', facecolor='wheat'))

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '1_histograma_diferencias_porcentuales.png', dpi=150)
    plt.close()
    print("✓ Gráfico 1: Histograma de diferencias porcentuales")


def grafico_scatter_comparacion(df):
    """
    Scatter plot comparando X_ENT vs X_CNE y X_Infotec.
    La línea diagonal representa coincidencia perfecta.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # X_ENT vs X_CNE
    mask_cne = df['X_CNE'].notna() & df['X_ENT'].notna()
    x_ent_cne = df.loc[mask_cne, 'X_ENT']
    x_cne = df.loc[mask_cne, 'X_CNE']

    axes[0].scatter(x_ent_cne, x_cne, alpha=0.4, s=20, c='steelblue')
    max_val = max(x_ent_cne.max(), x_cne.max())
    axes[0].plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='X_ENT = X_CNE')
    axes[0].set_xlabel('X_ENT (Ω)')
    axes[0].set_ylabel('X_CNE (Ω)')
    axes[0].set_title(f'X_ENT vs X_CNE\n(n={mask_cne.sum()})')
    axes[0].legend()
    axes[0].set_xlim(0, min(max_val, 500))
    axes[0].set_ylim(0, min(max_val, 500))

    # X_ENT vs X_Infotec
    mask_inf = df['X_Infotec'].notna() & df['X_ENT'].notna()
    x_ent_inf = df.loc[mask_inf, 'X_ENT']
    x_inf = df.loc[mask_inf, 'X_Infotec']

    axes[1].scatter(x_ent_inf, x_inf, alpha=0.4, s=20, c='darkorange')
    max_val = max(x_ent_inf.max(), x_inf.max())
    axes[1].plot([0, max_val], [0, max_val], 'r--', linewidth=2, label='X_ENT = X_Infotec')
    axes[1].set_xlabel('X_ENT (Ω)')
    axes[1].set_ylabel('X_Infotec (Ω)')
    axes[1].set_title(f'X_ENT vs X_Infotec\n(n={mask_inf.sum()})')
    axes[1].legend()
    axes[1].set_xlim(0, min(max_val, 500))
    axes[1].set_ylim(0, min(max_val, 500))

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '2_scatter_comparacion_fuentes.png', dpi=150)
    plt.close()
    print("✓ Gráfico 2: Scatter X_ENT vs fuentes")


def grafico_distribucion_delta(df):
    """
    Histograma de la magnitud del cambio (delta_X).
    Muestra dónde cae el umbral de 50 Ω.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    # Solo casos que discrepan
    df_discrepa = df[df['clasificacion_validacion'].str.startswith('DISCREPA', na=False)]
    delta = df_discrepa['delta_X'].dropna()

    # Histograma completo
    axes[0].hist(delta, bins=50, edgecolor='black', alpha=0.7, color='coral')
    axes[0].axvline(x=50, color='red', linestyle='--', linewidth=2, label='Umbral 50 Ω')
    axes[0].axvline(x=5, color='green', linestyle=':', linewidth=2, label='5 Ω (BAJO)')
    axes[0].set_xlabel('ΔX = |X_ENT - valor_sugerido| (Ω)')
    axes[0].set_ylabel('Frecuencia')
    axes[0].set_title(f'Distribución de Magnitud del Cambio (DISCREPA)\n(n={len(delta)})')
    axes[0].legend()

    # Estadísticas
    bajo = (delta < 5).sum()
    medio = ((delta >= 5) & (delta < 50)).sum()
    alto = (delta >= 50).sum()
    axes[0].text(0.95, 0.95, f'BAJO (<5Ω): {bajo}\nMEDIO (5-50Ω): {medio}\nALTO (≥50Ω): {alto}',
                 transform=axes[0].transAxes, ha='right', va='top',
                 bbox=dict(boxstyle='round', facecolor='wheat'))

    # Zoom en valores < 100 Ω
    delta_zoom = delta[delta < 100]
    axes[1].hist(delta_zoom, bins=40, edgecolor='black', alpha=0.7, color='coral')
    axes[1].axvline(x=50, color='red', linestyle='--', linewidth=2, label='Umbral 50 Ω')
    axes[1].axvline(x=5, color='green', linestyle=':', linewidth=2, label='5 Ω (BAJO)')
    axes[1].set_xlabel('ΔX (Ω)')
    axes[1].set_ylabel('Frecuencia')
    axes[1].set_title(f'Zoom: ΔX < 100 Ω\n(n={len(delta_zoom)})')
    axes[1].legend()

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '3_distribucion_magnitud_cambio.png', dpi=150)
    plt.close()
    print("✓ Gráfico 3: Distribución de magnitud del cambio")


def grafico_boxplot_categorias(df):
    """
    Boxplot de diferencias porcentuales por categoría.
    """
    # Preparar datos
    df_plot = df[df['diff_X_CNE_%'].notna() | df['diff_X_Infotec_%'].notna()].copy()

    # Usar la diferencia mínima disponible
    df_plot['diff_min'] = df_plot[['diff_X_CNE_%', 'diff_X_Infotec_%']].min(axis=1)
    df_plot = df_plot[df_plot['diff_min'] <= 200]  # Limitar outliers

    # Ordenar categorías
    orden = ['CORRECTO', 'CORRECTO_PARCIAL_CNE', 'CORRECTO_PARCIAL_INFOTEC',
             'DISCREPA_ENT_FUENTES_COINCIDEN', 'DISCREPA_FUENTES',
             'DISCREPA_PARCIAL_CNE', 'DISCREPA_PARCIAL_INFOTEC']

    fig, ax = plt.subplots(figsize=(14, 7))

    # Crear boxplot
    data_by_cat = [df_plot[df_plot['clasificacion_validacion'] == cat]['diff_min'].dropna()
                   for cat in orden if cat in df_plot['clasificacion_validacion'].values]
    labels = [cat.replace('_', '\n') for cat in orden if cat in df_plot['clasificacion_validacion'].values]

    bp = ax.boxplot(data_by_cat, labels=labels, patch_artist=True)

    # Colorear
    colors = ['lightgreen', 'lightgreen', 'lightgreen',
              'salmon', 'salmon', 'salmon', 'salmon']
    for patch, color in zip(bp['boxes'], colors[:len(bp['boxes'])]):
        patch.set_facecolor(color)

    ax.axhline(y=15, color='red', linestyle='--', linewidth=2, label='Umbral 15%')
    ax.set_ylabel('Diferencia porcentual mínima (%)')
    ax.set_title('Distribución de Diferencias por Categoría de Validación')
    ax.legend()

    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '4_boxplot_por_categoria.png', dpi=150)
    plt.close()
    print("✓ Gráfico 4: Boxplot por categoría")


def grafico_curva_sensibilidad(df):
    """
    Curva mostrando cómo cambia la clasificación según el umbral elegido.
    """
    # Calcular diferencia mínima disponible
    df_calc = df.copy()
    df_calc['diff_min'] = df_calc[['diff_X_CNE_%', 'diff_X_Infotec_%']].min(axis=1)
    df_valid = df_calc[df_calc['diff_min'].notna()]

    umbrales = range(1, 51)
    correctos = []
    discrepan = []

    for u in umbrales:
        corr = (df_valid['diff_min'] < u).sum()
        correctos.append(corr)
        discrepan.append(len(df_valid) - corr)

    fig, ax = plt.subplots(figsize=(12, 6))

    ax.plot(umbrales, correctos, 'g-', linewidth=2, label='CORRECTO (diff < umbral)')
    ax.plot(umbrales, discrepan, 'r-', linewidth=2, label='DISCREPA (diff ≥ umbral)')
    ax.axvline(x=15, color='blue', linestyle='--', linewidth=2, label='Umbral actual (15%)')

    # Marcar punto en 15%
    idx_15 = 14  # índice para umbral 15
    ax.plot(15, correctos[idx_15], 'bo', markersize=10)
    ax.annotate(f'({correctos[idx_15]} correctos)', xy=(15, correctos[idx_15]),
                xytext=(20, correctos[idx_15]+50), fontsize=10)

    ax.set_xlabel('Umbral de diferencia porcentual (%)')
    ax.set_ylabel('Cantidad de registros')
    ax.set_title('Sensibilidad del Umbral de Clasificación')
    ax.legend()
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '5_curva_sensibilidad_umbral.png', dpi=150)
    plt.close()
    print("✓ Gráfico 5: Curva de sensibilidad del umbral")


def grafico_distribucion_x_ent(df):
    """
    Histograma de valores de X_ENT para entender el rango de reactancias.
    """
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))

    x_ent = df['X_ENT'].dropna()

    # Histograma completo
    axes[0].hist(x_ent, bins=50, edgecolor='black', alpha=0.7, color='purple')
    axes[0].set_xlabel('X_ENT (Ω)')
    axes[0].set_ylabel('Frecuencia')
    axes[0].set_title(f'Distribución de X_ENT\n(n={len(x_ent)})')

    # Estadísticas
    axes[0].text(0.95, 0.95,
                 f'Media: {x_ent.mean():.1f} Ω\nMediana: {x_ent.median():.1f} Ω\nStd: {x_ent.std():.1f} Ω\nMax: {x_ent.max():.1f} Ω',
                 transform=axes[0].transAxes, ha='right', va='top',
                 bbox=dict(boxstyle='round', facecolor='wheat'))

    # Zoom en valores < 100 Ω
    x_zoom = x_ent[x_ent < 100]
    axes[1].hist(x_zoom, bins=40, edgecolor='black', alpha=0.7, color='purple')
    axes[1].set_xlabel('X_ENT (Ω)')
    axes[1].set_ylabel('Frecuencia')
    axes[1].set_title(f'Zoom: X_ENT < 100 Ω\n(n={len(x_zoom)}, {len(x_zoom)/len(x_ent)*100:.1f}% del total)')

    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / '6_distribucion_x_ent.png', dpi=150)
    plt.close()
    print("✓ Gráfico 6: Distribución de X_ENT")


def main():
    print("=" * 50)
    print("GENERACIÓN DE GRÁFICOS DE ANÁLISIS")
    print("=" * 50 + "\n")

    df = cargar_datos()

    print("\nGenerando gráficos...\n")

    grafico_histograma_diferencias(df)
    grafico_scatter_comparacion(df)
    grafico_distribucion_delta(df)
    grafico_boxplot_categorias(df)
    grafico_curva_sensibilidad(df)
    grafico_distribucion_x_ent(df)

    print(f"\n{'=' * 50}")
    print(f"Gráficos guardados en: {OUTPUT_DIR}")
    print(f"{'=' * 50}")


if __name__ == "__main__":
    main()

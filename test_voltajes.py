"""
Test para verificar extracción de voltajes de ambas barras
"""

from src.data_loader import extraer_barras_de_linnom, extraer_barras_infotecnica

print("=" * 60)
print("TEST: Extracción de voltajes de CNE (extraer_barras_de_linnom)")
print("=" * 60)

casos_cne = [
    "Los Changos 220->Kapatur 220 I",
    "Cardones 220->Cardones 110 I",
    "SUEZ_Los Changos 220->Kimal 500 II",
    "Paposo 220->Tap Tal Tal 220 C1",
]

for caso in casos_cne:
    barra_a, barra_b, voltaje_a, voltaje_b = extraer_barras_de_linnom(caso)
    print(f"\n'{caso}'")
    print(f"  → Barra A: '{barra_a}' @ {voltaje_a} kV")
    print(f"  → Barra B: '{barra_b}' @ {voltaje_b} kV")
    if voltaje_a != voltaje_b:
        print(f"  ⚠️  TRANSFORMADOR: {voltaje_a}kV ↔ {voltaje_b}kV")
    else:
        print(f"  ✓ Mismo voltaje: {voltaje_a} kV")

print("\n" + "=" * 60)
print("TEST: Extracción de voltajes de Infotécnica")
print("=" * 60)

casos_infotec = [
    "PAPOSO - TAP TAL TAL 220KV C1",
    "TAP NIRIVILO - TAP CENTRAL SAN JAVIER 66KV C1",
    "CARDONES - CENTRAL CARDONES 220KV C1",
]

for caso in casos_infotec:
    barra_a, barra_b, voltaje_a, voltaje_b = extraer_barras_infotecnica(caso)
    print(f"\n'{caso}'")
    print(f"  → Barra A: '{barra_a}' @ {voltaje_a} kV")
    print(f"  → Barra B: '{barra_b}' @ {voltaje_b} kV")
    if voltaje_a == voltaje_b:
        print(f"  ✓ Ambas barras al mismo voltaje: {voltaje_a} kV")
    else:
        print(f"  ⚠️  Voltajes diferentes: {voltaje_a}kV vs {voltaje_b}kV")

print("\n" + "=" * 60)
print("✓ Tests completados")
print("=" * 60)

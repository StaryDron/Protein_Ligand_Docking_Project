import pandas as pd

# Wczytaj i przygotuj dane
df = pd.read_csv("vina_affinity_matrix.csv", index_col=0)
df = df.replace(["brak", "błąd"], pd.NA)
df = df.apply(pd.to_numeric, errors='coerce')

# Zamień braki na -inf (czyli: bardzo złe wiązanie)
df_filled = df.fillna(float("inf"))

# Oblicz medianę dla każdej kieszeni (wiersz = jedna kieszeń)
pocket_medians = df_filled.median(axis=1, skipna=False)

# Posortuj kieszenie od najlepszej (najniższa mediana)
pocket_ranking = pocket_medians.sort_values()

# Zapisz do pliku
pocket_ranking.to_csv("best_pockets_by_median.csv", header=["Median affinity"])

# Podgląd
print("✅ Ranking kieszeni według mediany binding affinity (niższa = lepsza):")
print(pocket_ranking)

print(df.head(5))


# Wiersz odpowiadający kieszeni Pocket_69
pocket_69 = df.loc["Pocket_69"]

# Top 3 najniższe wartości (najlepsze wiązania)
top3_ligands = pocket_69.nsmallest(3)

# Wyświetl wynik
print("🔬 Top 3 ligandy dla Pocket_69:")
print(top3_ligands)
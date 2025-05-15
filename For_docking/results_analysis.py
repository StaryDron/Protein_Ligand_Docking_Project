import pandas as pd

# Wczytaj dane
df = pd.read_csv("vina_affinity_matrix.csv", index_col=0)

# Zamień błędne dane na NaN
df = df.replace(["brak", "błąd"], pd.NA)
df = df.apply(pd.to_numeric, errors='coerce')

# Oblicz metryki
min_affinity = df.min(skipna=True)
mean_top3_affinity = df.apply(lambda col: col.nsmallest(3).mean(skipna=True), axis=0)
mean_affinity = df.mean(skipna=True)

# Posortuj od najlepszego (najniższe affinity) do najgorszego
min_rank = min_affinity.sort_values()
top3_rank = mean_top3_affinity.sort_values()
mean_rank = mean_affinity.sort_values()

# Zbuduj tabelę rankingową
ranking_df = pd.DataFrame({
    "Min affinity": min_rank.index,
    "Avg of best 3": top3_rank.index,
    "Avg of all": mean_rank.index
})

# Zapisz ranking do pliku
ranking_df.to_csv("ligand_affinity_ranking.csv", index=False)

# Podgląd w konsoli
print("✅ Ranking ligandów według trzech metryk:")
print(ranking_df)
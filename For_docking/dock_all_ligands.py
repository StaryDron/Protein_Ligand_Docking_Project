import os
import subprocess
import re
import csv
import pandas as pd
from concurrent.futures import ProcessPoolExecutor, as_completed

# 🔧 Parametry globalne
ligand_folder = "For_docking_pdbqt"
output_folder = "results"
vina_exe = "vina.exe"
receptor = "nfkb.pdbqt"
gridbox_csv = "gridboxes.csv"

def dock_ligand_to_pocket(args):
    pocket, ligand_file, ligand_name = args
    ligand_path = os.path.join(ligand_folder, ligand_file)
    out_path = os.path.join(output_folder, f"{ligand_name}_p{pocket['pocket_id']}_out.pdbqt")
    log_path = os.path.join(output_folder, f"{ligand_name}_p{pocket['pocket_id']}.log")

    try:
        subprocess.run([
            vina_exe,
            "--receptor", receptor,
            "--ligand", ligand_path,
            "--center_x", str(pocket['center_x']),
            "--center_y", str(pocket['center_y']),
            "--center_z", str(pocket['center_z']),
            "--size_x", str(pocket['size_x']),
            "--size_y", str(pocket['size_y']),
            "--size_z", str(pocket['size_z']),
            "--out", out_path,
            "--log", log_path
        ], check=True)

        affinity = None
        with open(log_path, "r") as log_file:
            for line in log_file:
                match = re.match(r"\s+\d+\s+([-.\d]+)\s+", line)
                if match:
                    affinity = float(match.group(1))
                    break

        return (pocket['pocket_id'], ligand_name, affinity if affinity is not None else "brak")

    except Exception as e:
        print(f"❌ Błąd przy {ligand_name} w kieszeni {pocket['pocket_id']}: {e}")
        return (pocket['pocket_id'], ligand_name, "błąd")

# 🚀 Główna funkcja
if __name__ == "__main__":
    # 📥 Wczytaj kieszenie
    gridboxes = []
    with open(gridbox_csv, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            gridboxes.append({
                'pocket_id': int(row['pocket_id']),
                'center_x': float(row['center_x']),
                'center_y': float(row['center_y']),
                'center_z': float(row['center_z']),
                'size_x': float(row['size_x']),
                'size_y': float(row['size_y']),
                'size_z': float(row['size_z'])
            })

    # 🔍 Lista ligandów
    ligands = [f for f in os.listdir(ligand_folder) if f.endswith(".pdbqt")]
    ligand_names = [os.path.splitext(f)[0] for f in ligands]

    # 📁 Utwórz folder na wyniki
    os.makedirs(output_folder, exist_ok=True)

    # 📋 Lista zadań
    jobs = [(pocket, ligand_file, ligand_name)
            for pocket in gridboxes
            for ligand_file, ligand_name in zip(ligands, ligand_names)]

    print(f"🧠 Rozpoczynamy dokowanie {len(jobs)} kombinacji kieszeń–ligand...")

    # 🔁 Proces równoległy
    affinity_data = []
    with ProcessPoolExecutor(max_workers=6) as executor:  # Dopasuj do liczby rdzeni
        futures = [executor.submit(dock_ligand_to_pocket, job) for job in jobs]
        for future in as_completed(futures):
            result = future.result()
            affinity_data.append(result)

    # 📊 Tworzenie macierzy
    affinity_matrix = pd.DataFrame(index=[f"Pocket_{p['pocket_id']}" for p in gridboxes],
                                   columns=ligand_names)

    for pocket_id, ligand_name, affinity in affinity_data:
        affinity_matrix.at[f"Pocket_{pocket_id}", ligand_name] = affinity

    # 💾 Zapis do pliku
    affinity_matrix.to_csv("vina_affinity_matrix.csv")
    print("✅ Zakończono. Wyniki zapisane do vina_affinity_matrix.csv")

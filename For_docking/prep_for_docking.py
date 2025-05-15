import os
from openbabel import pybel

input_folder="."
output_folder="For_docking_pdbqt"
os.makedirs(output_folder,exist_ok=True)

for filename in os.listdir(input_folder):
    if filename.endswith(".pdb"):
        base = os.path.splitext(filename)[0]

        base_clean = base.replace(" ", "_").replace("(", "").replace(")", "")
        
        input_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, base_clean + ".pdbqt")

        print(f"przetwarzanie {filename}")
        try:
            mol=next(pybel.readfile("pdb",input_path))
            mol.addh()
            mol.write("pdbqt",output_path,overwrite=True)
        except Exception as e:
            print(f"blad przy {filename}:{e}")

print("gotowe")




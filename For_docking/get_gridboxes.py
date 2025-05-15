def parse_fpocket_output_by_pocket_number(filepath):
    pockets = []
    current_coords = []
    current_pocket_id = None

    with open(filepath, 'r') as f:
        for line in f:
            if line.startswith("HETATM") and "Ve" in line:
                pocket_id = int(line[23:26].strip())  # numer kieszeni
                x = float(line[30:38])
                y = float(line[38:46])
                z = float(line[46:54])

                # Jeśli zmienił się numer kieszeni
                if current_pocket_id is not None and pocket_id != current_pocket_id:
                    xs, ys, zs = zip(*current_coords)
                    center = (
                        round(sum(xs)/len(xs), 3),
                        round(sum(ys)/len(ys), 3),
                        round(sum(zs)/len(zs), 3),
                    )
                    size = (
                        round(max(xs) - min(xs) + 4, 3),
                        round(max(ys) - min(ys) + 4, 3),
                        round(max(zs) - min(zs) + 4, 3),
                    )
                    pockets.append({
                        'pocket_id': current_pocket_id,
                        'center_x': center[0],
                        'center_y': center[1],
                        'center_z': center[2],
                        'size_x': size[0],
                        'size_y': size[1],
                        'size_z': size[2],
                        'n_points': len(current_coords)
                    })
                    current_coords = []

                current_coords.append((x, y, z))
                current_pocket_id = pocket_id

    # Dodaj ostatnią kieszeń
    if current_coords:
        xs, ys, zs = zip(*current_coords)
        center = (
            round(sum(xs)/len(xs), 3),
            round(sum(ys)/len(ys), 3),
            round(sum(zs)/len(zs), 3),
        )
        size = (
            round(max(xs) - min(xs) + 4, 3),
            round(max(ys) - min(ys) + 4, 3),
            round(max(zs) - min(zs) + 4, 3),
        )
        pockets.append({
            'pocket_id': current_pocket_id,
            'center_x': center[0],
            'center_y': center[1],
            'center_z': center[2],
            'size_x': size[0],
            'size_y': size[1],
            'size_z': size[2],
            'n_points': len(current_coords)
        })

    return pockets


pockets = parse_fpocket_output_by_pocket_number("protein_out_1.txt")
for p in pockets[:3]:
    print(f"Pocket {p['pocket_id']}: Center=({p['center_x']}, {p['center_y']}, {p['center_z']}), "
          f"Size=({p['size_x']}, {p['size_y']}, {p['size_z']}), Points={p['n_points']}")

import csv

# Zapis do CSV
with open("gridboxes.csv", "w", newline="") as csvfile:
    fieldnames = ['pocket_id', 'center_x', 'center_y', 'center_z',
                  'size_x', 'size_y', 'size_z', 'n_points']
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

    writer.writeheader()
    for pocket in pockets:
        writer.writerow(pocket)

print("✅ Zapisano do gridboxes.csv")
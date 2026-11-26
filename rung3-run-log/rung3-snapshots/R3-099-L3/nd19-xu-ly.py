import csv

input_path = "/home/james/rung3/nd19-du-lieu.csv"
output_path = "/home/james/rung3/nd19-bao-cao.txt"

totals = {}
counts = {}

with open(input_path, newline="", encoding="utf-8") as csv_file:
    reader = csv.DictReader(csv_file)
    if not reader.fieldnames or not {"nhom", "diem"}.issubset(reader.fieldnames):
        raise ValueError("CSV must contain 'nhom' and 'diem' columns")
    for row in reader:
        group = row["nhom"]
        score = float(row["diem"])
        totals[group] = totals.get(group, 0.0) + score
        counts[group] = counts.get(group, 0) + 1

with open(output_path, "w", encoding="utf-8") as report:
    for group in sorted(counts):
        average = round(totals[group] / counts[group], 2)
        report.write(f"{group}, {counts[group]}, {average:.2f}\n")

import csv
import os
from datetime import datetime

# ======================= CONFIGURATION ========================
OUTPATH = "Desk"  # Set to "Desk" or "CWD"
FIXED_VAR = "BATTERYLOG"
HEADER = ["id", 
          "Nominal mAh", 
          "Real mAh", 
          "mR (IR)", 
          "Wh", 
          "Set", 
          "Chemestry", 
          "Vendor", 
          "From", 
          "Note", 
          "Health"]

# ======================= INFO =================================
print(f"""
BATTERY LOGGER — CSV ENTRY TOOL

This script helps you catalog and evaluate battery cells using basic parameters.

Battery Chemistries (enter in 'chemestry' field):
 - IMR       → Lithium Manganese Oxide (High drain, safer)
 - INR       → Lithium Nickel Manganese Cobalt (Balanced)
 - ICR       → Lithium Cobalt Oxide (High capacity, riskier)
 - LiFePO4   → Lithium Iron Phosphate (Very stable, long life)
 - LiPo      → Lithium Polymer (Flat, flexible form)

HEALTH EVALUATION:
 - If 'real mAh' < 1/3 of 'nominal mAh' → mark as: Exhausted
 - If 'mR (IR)' is given:
     • < 50     → New
     • 50–100   → Good
     • 100–150  → Just fine
     • 150–250  → Bad
     • > 250    → Critical
 - If both are present → example: "Good, Exhausted"
 - If neither → health = "Unknown"
""")

# =========================== RUN ==============================
timestamp = datetime.now().strftime("%Y%m%d-%H%M")
filename = f"{FIXED_VAR}-{timestamp}.csv"

if OUTPATH.upper() == "DESK":
    save_dir = os.path.join(os.path.expanduser("~"), "Desktop")
else:
    save_dir = os.getcwd()

file_path = os.path.join(save_dir, filename)

# === HEALTH EVALUATION FUNCTION ===
def get_health(nominal, real, ir):
    ir_status = None
    capacity_status = None

    # Internal Resistance
    try:
        ir = float(ir)
        if ir < 50:
            ir_status = "New"
        elif ir < 100:
            ir_status = "Good"
        elif ir < 150:
            ir_status = "Fine"
        elif ir < 250:
            ir_status = "Bad"
        else:
            ir_status = "Critical"
    except:
        pass

    # Capacity
    try:
        nominal = float(nominal)
        real = float(real)
        if real < (nominal / 3):
            capacity_status = "Exhausted"
    except:
        pass

    # Results
    if not ir_status and not capacity_status:
        return "Unknown"
    elif ir_status and capacity_status:
        return f"{ir_status}, {capacity_status}"
    elif ir_status:
        return ir_status
    elif capacity_status:
        return capacity_status

# === DATA COLLECTION ===
rows = []
counter = 1
print("Enter values. Leave empty (or spaces only) to set field as NULL.\n")

try:
    while True:
        row = []
        values = {}
        values["id"] = f"Cell-{counter}"
        print(f"\n→ Entering data for {values['id']} \n")
        counter += 1

        for field in HEADER[1:-1]:
            val = input(f"{field}: ").strip()
            values[field] = "NULL" if val.strip() == "" else val
            row.append(values[field])

        # Health
        health = get_health(values["Nominal mAh"], values["Real mAh"], values["mR (IR)"])
        full_row = [values["id"]] + row + [health]
        rows.append(full_row)

        while True:
            again = input("Add another entry? [Y/n]: ").strip().lower()
            if again in ("", "y"):
                break
            elif again == "n":
                raise KeyboardInterrupt
            else:
                print("Please enter Y or N (or just press ENTER to continue).")
except KeyboardInterrupt:
    print("\nExiting gracefully. Goodbye!")

# === WRITE TO CSV FILE ===
try:
    with open(file_path, mode='w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(HEADER)
        writer.writerows(rows)

    print(f"\n✅ File successfully saved to: {file_path}")
except Exception as e:
    print(f"\n❌ Failed to write file: {e}")

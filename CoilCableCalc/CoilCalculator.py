import math

nucleo = 15
cable = 4.75

def lunghezza_da_spire():
    N = int(input("\nNumero spire desiderate: "))
    extra_len = int(input("Lunghezza extra (mm):"))

    C = math.pi * (nucleo + cable)
    spire = N * C
    ground_total = total_len = spire + extra_len
    paracord = (ground_total+(ground_total*0.20))
    
    print(f"\nLunghezza (totale): {math.ceil(total_len/10)} cm")
    print(f"Lunghezza (per spire): {math.ceil(spire/10)} cm ")
    print(f"Lunghezza coil: {math.ceil((N*cable)/10)} cm ")
    print(f"Paracord: {math.ceil(paracord/10)} cm \n")

def spire_da_lunghezza():
    coil_len = int(input("\nLunghezza totale spirale (mm): "))
    extra_len = int(input("Lunghezza extra (mm):"))
    
    x_coil = math.ceil(coil_len/cable)
    C = math.pi * (nucleo + cable)
    spire = x_coil * C
    total_len = spire + extra_len
    ground_total = total_len + extra_len
    paracord = (ground_total+(ground_total*0.20))
    
    print(f"\nLunghezza (totale): {math.ceil(ground_total/10)} cm ")
    print(f"Lunghezza (per spire): {math.ceil(total_len/10)} cm")
    print(f"Spire necessarie: {x_coil}")
    print(f"Paracord: {math.ceil(paracord/10)} cm \n")

while True:
    scelta = input("\n Calcolare: \n 1. Spire da lunghezza \n 2. Lunghezza da spire \n 3. Exit \n\n >> ")
    if scelta == '1':
        spire_da_lunghezza()
    elif scelta == '2':
        lunghezza_da_spire()
    elif scelta == '3':
        break
    else:
        print("\n For real?!... ")
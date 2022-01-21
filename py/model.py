from msilib import datasizemask
import numpy as np
import prts

for row in prts.read_level("level_main_01-07.json"):
    for tile in row:
        print("[]" if tile & 128 else "--", end="")
    print()

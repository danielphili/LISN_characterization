# -*- coding: utf-8 -*-
"""
Concatenate s2p files cutting out headers
This is used for using multiple measurements in different frequency ranges
that together form the entire measurement.
In future, it would be easier to have this automated at time of measurement 
using the python code that is part of the nanovna project
(https://github.com/ttrftech/NanoVNA), but this was the quicker solution for
the moment.

Created on Sun Jun 23 15:08:05 2024

Author: Daniel Alexander Philipps

Email: dphilipps@freenet.de

"""

# filenames_in = [
#     "data/raw/INSERTION_LOSS_10k_100k.s2p",
#     "data/raw/INSERTION_LOSS_100k_1M.s2p",
#     "data/raw/INSERTION_LOSS_1M_10M.s2p",
#     "data/raw/INSERTION_LOSS_10M_100M.s2p",
#     "data/raw/INSERTION_LOSS_100M_1G.s2p",
#     ]

# filename_out = "data/processed/INSERTION_LOSS_10k_1G.s2p"


filenames_in = [
    "data/raw/THRU_10k_100k.s2p",
    "data/raw/THRU_100k_1M.s2p",
    "data/raw/THRU_1M_10M.s2p",
    "data/raw/THRU_10M_100M.s2p",
    "data/raw/THRU_100M_1G.s2p",
    ]

filename_out = "data/processed/THRU_10k_1G.s2p"



content = []

for fn in filenames_in:
    with open(fn, "r") as file:
        fc = file.read()
        fc = fc.split('\n')
        for fck in fc:
            if len(content) > 0:
                if not "#" in fck and fck != "":
                    content.append(fck)
            else:
                content.append(fck)
        file.close()

content = '\n'.join(content)

with open(filename_out, "w+") as file:
    file.write(content)
    file.close()


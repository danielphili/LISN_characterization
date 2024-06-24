# -*- coding: utf-8 -*-
"""
Using NanoVNA measurement recordings as Touchstone files, determine
    - Output Impedance (supply terminals open / shorted)
    - Insertion Loss (correction factor for spectrum analyzer measurements)

Created on Sat Jun 22 16:59:46 2024

Author: Daniel Alexander Philipps

Email: dphilipps@freenet.de

"""

import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


def import_DO160_LISN_output_impedance_limits() -> np.array:
    """
    import the upper and lower limit of the LISN output impedance according to
    DO-160 (source: https://documentation.com-power.com/pdf/LI-3100-2.pdf)

    Returns
    -------
    data_ul : np.array
        upper impedance limit (frequency and corresponding upper impedance
                               limit.)
    data_ll : np.array
        lower impedance limit (frequency and corresponding lower impedance
                               limit.).

    """
    ll = \
        pd.read_csv("data/DO-160 output impedance limits/DO-160_limits_ll.csv")
    
    ul = \
        pd.read_csv("data/DO-160 output impedance limits/DO-160_limits_ul.csv")
    
    data_ul = np.asfarray([ul['x'], ul['upper_limit']]).T
    data_ll = np.asfarray([ll['x'], ll['lower_limit']]).T

    return data_ul, data_ll

def read_complex_S11_S21(fn:str) -> np.array:
    """
    Extract the complex S11 and S21 scattering parameters from the touchstone
    file with name fn.

    Parameters
    ----------
    fn : str
        file name of touchstone file.

    Returns
    -------
    f : np.array
        Frequency.
    S11 : np.array
        S11 parameters as complex numbers.
    S21 : np.array
        S21 parameters as complex numbers.

    """
    with open(fn, "r") as file:
        data = file.read()
        file.close()

    data = data.split("\n")
    data = [dk.split(" ") for dk in data]
    data = data[1:-1] # discard first line (header), and bottom (empty line)
    data = np.asfarray(data)
    f = data[:,0]
    S11 = np.asarray([complex(dk[1], dk[2]) for dk in data])
    S21 = np.asarray([complex(dk[3], dk[4]) for dk in data])
    return f, S11, S21

def calculate_impedance(S11:np.array, Z0:float = 50.0, Z0_par:bool = False) \
    -> np.array:
    """
    Calculate the connected impedance from the reflection parameter S11.
    Consider parallel connection with Z0.

    Parameters
    ----------
    S11 : np.array
        S11 data.
    Z0 : float, optional
        System impedance (in Ohms). The default is 50.0.
    Z0_par : bool, optional
        True if a termination resistor with value Z0 is connected in parallel
        to the impedance to be measured. The default is False.

    Returns
    -------
    Z_outp : np.array
        impedance to be mesaured.

    """
    Z_meas = Z0 * (1+S11)/(1-S11) # measured impedance at port 1
    if Z0_par:
        Z_outp = 1/(1/Z_meas - 1/Z0) # actual system impedance if in parallel with Z0
    else:
        Z_outp = Z_meas
    return Z_outp


f_supply_open, S11_supply_open, _ = \
    read_complex_S11_S21(fn="data/raw/ZOUTP_ISO_SUPPLY_OPEN.s2p")
f_supply_short, S11_supply_short, _ = \
    read_complex_S11_S21(fn="data/raw/ZOUTP_ISO_SUPPLY_SHORT.s2p")
f_bias_1000mA, S11_bias_1000mA, _ = \
    read_complex_S11_S21(fn="data/processed/INSERTION_LOSS_10k_1G_1000mA.s2p")
f_bias_2000mA, S11_bias_2000mA, _ = \
    read_complex_S11_S21(fn="data/processed/INSERTION_LOSS_10k_1G_2000mA.s2p")

Z_outp_supply_open = calculate_impedance(S11_supply_open)
Z_outp_supply_short = calculate_impedance(S11_supply_short)
Z_outp_bias_1000mA = calculate_impedance(S11_bias_1000mA)
Z_outp_bias_2000mA = calculate_impedance(S11_bias_2000mA)
ref_ul, ref_ll = import_DO160_LISN_output_impedance_limits()


f_S21, _, S21 = \
    read_complex_S11_S21(fn="data/processed/INSERTION_LOSS_10k_1G.s2p")
f_S21_0mA, _, S21_0mA = \
    read_complex_S11_S21(fn="data/processed/INSERTION_LOSS_10k_1G_0mA.s2p")
f_S21_600mA, _, S21_600mA = \
    read_complex_S11_S21(fn="data/processed/INSERTION_LOSS_10k_1G_600mA.s2p")
f_S21_1000mA, _, S21_1000mA = \
    read_complex_S11_S21(fn="data/processed/INSERTION_LOSS_10k_1G_1000mA.s2p")
f_S21_1500mA, _, S21_1500mA = \
    read_complex_S11_S21(fn="data/processed/INSERTION_LOSS_10k_1G_1500mA.s2p")
f_S21_2000mA, _, S21_2000mA = \
    read_complex_S11_S21(fn="data/processed/INSERTION_LOSS_10k_1G_2000mA.s2p")



# plot LISN impedance
fig, ax = plt.subplots(1)
# ax = [ax, ax.twinx()]
ax = [ax]
ax[0].plot(f_supply_open/1E6, abs(Z_outp_supply_open), 
           label="$|Z_\mathrm{out,LISN,open}|$")
ax[0].plot(f_supply_short/1E6, abs(Z_outp_supply_short), 
           label="$|Z_\mathrm{out,LISN,short}|$")
ax[0].plot(f_bias_1000mA/1E6, abs(Z_outp_bias_1000mA), 
           label="$|Z_\mathrm{out,LISN}|$ @ 1000 mA bias$")
ax[0].plot(f_bias_2000mA/1E6, abs(Z_outp_bias_2000mA), 
           label="$|Z_\mathrm{out,LISN}|$ @ 2000 mA bias$")
ax[0].plot(ref_ul[:,0], ref_ul[:,1], color="red", linestyle="--",
           label="DO-160 limits")
ax[0].plot(ref_ll[:,0], ref_ll[:,1], color="red", linestyle="--")


for k, axk in enumerate(ax):
    axk.grid("both")
    axk.legend()
    axk.set_xscale("log")
    axk.set_xlim((0.01, 200))
    axk.set_yscale("log")
    # axk.set_ylim((0.1,100))
ax[0].set_ylabel("Impedance (Ohm)")
ax[-1].set_xlabel("Frequency (MHz)")

plt.tight_layout()
plt.savefig("data/out/Z_outp_LISN.png", format="png")



# plot insertion loss for different bias current scenarios
fig, ax = plt.subplots(1)
ax.plot(f_S21/1E6, 20*np.log10(abs(S21)),
        label="0 mA (open terminals)")
ax.plot(f_S21_0mA/1E6, 20*np.log10(abs(S21_0mA)),
        label="0 mA")
ax.plot(f_S21_600mA/1E6, 20*np.log10(abs(S21_600mA)),
        label="600 mA")
ax.plot(f_S21_1000mA/1E6, 20*np.log10(abs(S21_1000mA)),
        label="1000 mA")
ax.plot(f_S21_1500mA/1E6, 20*np.log10(abs(S21_1500mA)),
        label="1500 mA")
ax.plot(f_S21_2000mA/1E6, 20*np.log10(abs(S21_2000mA)),
        label="2000 mA")

ax.grid("both")
ax.legend(loc="lower right")
ax.set_xscale("log")
# ax.set_xlim((0.01, 200))
# ax.set_yscale("log")
# ax.set_ylim((0.1,100))
ax.set_ylabel("S21 Transmission Coefficient (dB)")
ax.set_xlabel("Frequency (MHz)")
plt.tight_layout()
plt.savefig("data/out/Insertion_loss.png", format="png")

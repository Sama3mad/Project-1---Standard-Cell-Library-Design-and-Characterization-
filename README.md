# Project 1 — SKY130 Standard Cell Library


## Team members

- Sama Emad Abu Zahra || 900233026
- Abdelrahman Mohamed Abdelbaky || 900232797

## Contribution

We did **not** split the work into separate “solo” tasks. **Both of us** took part in **SPICE modeling**, **logic verification**, **Python characterization** (including MAJ3), **NLDM data and plots**, and **the report**. We planned together, ran simulations and scripts together, and checked each other’s results as we went.

## What this is

This project is a **SKY130** standard cell library with **13 cells**. The work covers:

- Building the cells in **SPICE**
- Checking that they work as expected (**logic verification**)
- Using **Python** to measure **timing** (how fast signals change)
- Saving **NLDM** results — delay numbers that depend on input transition time and load (used in digital timing)

The **full write-up**, **complete delay tables**, and **extra figures** are in the **project report**. This README only lists the **main files** used for simulation and timing runs.

## Main files

| File | What it does |
|------|----------------|
| `cells.lib` | SPICE models (subcircuits) for all 13 cells. |
| `verify.sp` | Testbench to check cell logic. |
| `characterize.py` | Main script for inverters, NAND2, and NOR2. |
| `char maj3.py` | Script for MAJ3, with fixed **B = 1, C = 0** sensitization. |
| `nldm results.npy` | All NLDM timing data for the 13 cells (NumPy file). |
| `inverter delay vs load.png` | Plot of inverter delay vs. load. |

## GitHub

More course files and scripts are here:

[Project 1 — Standard Cell Library Design and Characterization](https://github.com/Sama3mad/Project-1---Standard-Cell-Library-Design-and-Characterization-.git)

---

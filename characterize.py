#!/usr/bin/env python3
"""
characterize.py - NLDM characterization for all 13 standard cells.
Cleans up temp files after each run to save storage.
"""

import os
import re
import subprocess
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

# ── Paths ──────────────────────────────────────────────────────────────────────
SKY130_LIB = (
    "/home/sama/work/pdks/volare/sky130/versions/"
    "dd7771c384ed36b91a25e9f8b314355fc26561be/"
    "sky130A/libs.tech/ngspice/sky130.lib.spice"
)
CELLS_LIB = os.path.abspath("cells.lib")
WORK_DIR  = os.path.abspath("char_work")
os.makedirs(WORK_DIR, exist_ok=True)

# ── Characterization vectors ────────────────────────────────────────────────────
TR_NS = [0.01, 0.0231, 0.0531, 0.1225, 0.2823, 0.6507, 1.5]
CL_PF = [5e-4, 1.3e-3, 3.5e-3, 9.4e-3, 0.0249, 0.0662, 0.1758]

VDD = 1.8
VTH = VDD / 2
V20 = 0.20 * VDD
V80 = 0.80 * VDD

# ── Cell definitions ────────────────────────────────────────────────────────────
CELLS = [
    ("invx1",   ["A"],         "Y", [("A", {},                True),
                                     ("A", {},                False)]),
    ("invx2",   ["A"],         "Y", [("A", {},                True),
                                     ("A", {},                False)]),
    ("invx4",   ["A"],         "Y", [("A", {},                True),
                                     ("A", {},                False)]),
    ("invx8",   ["A"],         "Y", [("A", {},                True),
                                     ("A", {},                False)]),
    ("nand2x1", ["A", "B"],    "Y", [("A", {"B": VDD},        True),
                                     ("A", {"B": VDD},        False)]),
    ("nand2x2", ["A", "B"],    "Y", [("A", {"B": VDD},        True),
                                     ("A", {"B": VDD},        False)]),
    ("nand2x4", ["A", "B"],    "Y", [("A", {"B": VDD},        True),
                                     ("A", {"B": VDD},        False)]),
    ("nor2x1",  ["A", "B"],    "Y", [("A", {"B": 0},          True),
                                     ("A", {"B": 0},          False)]),
    ("nor2x2",  ["A", "B"],    "Y", [("A", {"B": 0},          True),
                                     ("A", {"B": 0},          False)]),
    ("nor2x4",  ["A", "B"],    "Y", [("A", {"B": 0},          True),
                                     ("A", {"B": 0},          False)]),
    ("maj3x1",  ["A","B","C"], "Y", [("A", {"B": VDD,"C": VDD}, False),
                                     ("A", {"B": 0,  "C": 0  }, True)]),
    ("maj3x2",  ["A","B","C"], "Y", [("A", {"B": VDD,"C": VDD}, False),
                                     ("A", {"B": 0,  "C": 0  }, True)]),
    ("maj3x4",  ["A","B","C"], "Y", [("A", {"B": VDD,"C": VDD}, False),
                                     ("A", {"B": 0,  "C": 0  }, True)]),
]

# ── Netlist generator ───────────────────────────────────────────────────────────
def make_netlist(cell_name, all_pins, switch_pin,
                 held, rising_out, tr_ns, cl_pf):
    tr_ps  = tr_ns * 1e3
    pw_ns  = max(tr_ns * 10, 2)
    per_ns = pw_ns * 2 + tr_ns * 2
    v1, v2 = (VDD, 0.0) if rising_out else (0.0, VDD)

    lines = [
        f"* {cell_name} {switch_pin} rising={rising_out} tr={tr_ns} cl={cl_pf}",
        f".lib {SKY130_LIB} tt",
        f".temp 25",
        f".include {CELLS_LIB}",
        "",
        f"VDD vdd 0 {VDD}",
        f"VPULSE {switch_pin.lower()}sig 0 "
        f"PULSE({v1} {v2} 0 {tr_ps}p {tr_ps}p {pw_ns}n {per_ns}n)",
    ]
    for pin, val in held.items():
        lines.append(f"VDC_{pin} {pin.lower()}sig 0 {val}")

    inst_pins = " ".join(f"{p.lower()}sig" for p in all_pins)
    lines += [
        f"XDUT {inst_pins} y_out vdd 0 {cell_name}",
        f"CL y_out 0 {cl_pf}p",
        "",
        f".tran 1p {per_ns * 1.5}n",
        "",
        ".control",
        "run",
    ]
    if rising_out:
        lines += [
            f"meas tran cell_rise trig v({switch_pin.lower()}sig) val={VTH:.4f}"
            f" fall=1 targ v(y_out) val={VTH:.4f} rise=1",
            f"meas tran rise_tran trig v(y_out) val={V20:.4f}"
            f" rise=1 targ v(y_out) val={V80:.4f} rise=1",
        ]
    else:
        lines += [
            f"meas tran cell_fall trig v({switch_pin.lower()}sig) val={VTH:.4f}"
            f" rise=1 targ v(y_out) val={VTH:.4f} fall=1",
            f"meas tran fall_tran trig v(y_out) val={V80:.4f}"
            f" fall=1 targ v(y_out) val={V20:.4f} fall=1",
        ]
    lines += ["print all", ".endc", ".end", ""]
    return "\n".join(lines)

# ── Run ngspice and clean up immediately ────────────────────────────────────────
def run_and_parse(cell_name, all_pins, switch_pin,
                  held, rising_out, tr_ns, cl_pf, idx):
    sp_file  = os.path.join(WORK_DIR, "tmp.sp")
    log_file = os.path.join(WORK_DIR, "tmp.log")

    netlist = make_netlist(cell_name, all_pins, switch_pin,
                           held, rising_out, tr_ns, cl_pf)
    with open(sp_file, "w") as f:
        f.write(netlist)

    with open(log_file, "w") as f:
        subprocess.run(["ngspice", "-b", sp_file],
                       stdout=f, stderr=subprocess.STDOUT)

    with open(log_file) as f:
        log = f.read()

    # Delete temp files immediately to save storage
    os.remove(sp_file)
    os.remove(log_file)

    meas_key = "cell_rise"  if rising_out else "cell_fall"
    tran_key = "rise_tran"  if rising_out else "fall_tran"

    def grab(key):
        m = re.search(
            rf"{key}\s*=\s*([-+]?\d+\.?\d*[eE]?[-+]?\d*)",
            log, re.IGNORECASE)
        if m:
            v = float(m.group(1))
            return v if v > 0 else float("nan")
        return float("nan")

    return grab(meas_key) * 1e12, grab(tran_key) * 1e12

# ── Main loop ───────────────────────────────────────────────────────────────────
results = {}
total = len(CELLS) * 2 * len(TR_NS) * len(CL_PF)
done  = 0

for (cell_name, all_pins, out_pin, arcs) in CELLS:
    results[cell_name] = {}
    for (switch_pin, held, rising_out) in arcs:
        arc_label = "rise" if rising_out else "fall"
        delay_table = np.full((len(TR_NS), len(CL_PF)), float("nan"))
        tran_table  = np.full((len(TR_NS), len(CL_PF)), float("nan"))

        for i, tr in enumerate(TR_NS):
            for j, cl in enumerate(CL_PF):
                done += 1
                delay_ps, tran_ps = run_and_parse(
                    cell_name, all_pins, switch_pin,
                    held, rising_out, tr, cl, done)
                delay_table[i][j] = delay_ps
                tran_table[i][j]  = tran_ps
                print(f"[{done}/{total}] {cell_name:8s} {arc_label:4s}"
                      f"  tr={tr}ns  CL={cl}pF"
                      f"  delay={delay_ps:.1f}ps  tran={tran_ps:.1f}ps")

        results[cell_name][f"cell_{arc_label}"]       = delay_table
        results[cell_name][f"{arc_label}_transition"] = tran_table

# ── Save results ────────────────────────────────────────────────────────────────
out_npy = os.path.join(WORK_DIR, "nldm_results.npy")
np.save(out_npy, results)
print(f"\nAll done. Results saved to {out_npy}")

# ── Plot: inverter delay vs load ────────────────────────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
mid_tr_idx = 3  # tr = 0.1225 ns

for arc_label, ax in zip(["rise", "fall"], axes):
    for inv in ["invx1", "invx2", "invx4", "invx8"]:
        table = results[inv][f"cell_{arc_label}"]
        ax.plot(CL_PF, table[mid_tr_idx], marker='o', label=inv)
    ax.set_xlabel("CL (pF)")
    ax.set_ylabel("Propagation delay (ps)")
    ax.set_title(f"Inverter family — cell_{arc_label}  (tr = 0.1225 ns)")
    ax.legend()
    ax.grid(True)

plt.tight_layout()
plot_path = os.path.join(WORK_DIR, "inverter_delay_vs_load.png")
plt.savefig(plot_path, dpi=150)
print(f"Plot saved to {plot_path}")

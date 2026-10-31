"""
main.py
=======
Inflow Performance Relationship (IPR) Project — Petroleum Engineering
Runs all 5 sections, displays plots on screen, and saves figures and CSVs into outputs/.

Parts:
  Part 1: Simple IPR Curve for Undersaturated Reservoir (Constant J)
  Part 2: Vogel's Method (Saturated, Undersaturated & Depleted Future IPR)
  Part 3: Fetkovich Model (Multi-rate Log-Log Fitting, Saturated & Future IPR)
  Part 4: Real Field Case – Well B, Keokuk Pool (New Correlation, Vogel, Fetkovich)
  Part 5: Future IPR Prediction for Well B (8 Months Pressure Depletion)

Author: Petroleum Engineering Student
"""

import os
import sys
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import ipr_calculations as ipr

# Output sub-directories: plots go to outputs/plots/, tables go to outputs/tables/
_base_dir  = os.path.dirname(os.path.abspath(__file__))
plots_dir  = os.path.join(_base_dir, "outputs", "plots")
tables_dir = os.path.join(_base_dir, "outputs", "tables")
os.makedirs(plots_dir,  exist_ok=True)
os.makedirs(tables_dir, exist_ok=True)

# Helper function to save and display each plot
def show_and_save(filename):
    filepath = os.path.join(plots_dir, filename)
    plt.savefig(filepath, dpi=300)
    if "--no-block" in sys.argv:
        plt.show(block=False)
        plt.pause(0.2)
    else:
        plt.show()


# ==============================================================================
# PART 1: SIMPLE IPR CURVE (UNDERSATURATED RESERVOIR, CONSTANT J)
# ==============================================================================
print("\n" + "="*70)
print("PART 1: SIMPLE IPR (CONSTANT J APPROACH)")
print("="*70)

# Reservoir Inputs
Pr_1 = 1300.0         # Average reservoir pressure (psi)
Pwf_test_1 = 900.0    # Flowing bottom-hole pressure during test (psi)
Qo_test_1 = 110.0     # Stabilized oil rate (STB/day)

# Calculations
J_1, AOF_1 = ipr.calculate_constant_j(Qo_test_1, Pr_1, Pwf_test_1)
print(f"Productivity Index (J): {J_1:.4f} STB/day/psi")
print(f"Absolute Open Flow (AOF): {AOF_1:.2f} STB/day")

# Pressure range from Pr down to 0 psi
pwf_range_1 = np.linspace(Pr_1, 0, 11)
qo_range_1 = ipr.ipr_constant_j(J_1, Pr_1, pwf_range_1)

# Save Table to CSV
df_part1 = pd.DataFrame({"Pwf (psi)": pwf_range_1, "Qo (STB/day)": qo_range_1})
df_part1.to_csv(os.path.join(tables_dir, "part1_simple_ipr.csv"), index=False)

# Plot
plt.figure(figsize=(7, 5))
plt.plot(qo_range_1, pwf_range_1, color="blue", linewidth=2.5, label="Constant J Approach")
plt.scatter([Qo_test_1], [Pwf_test_1], color="red", s=70, zorder=5, label=f"Test Point ({Qo_test_1} STB/d, {Pwf_test_1} psi)")
plt.scatter([AOF_1], [0], color="green", s=70, marker="s", zorder=5, label=f"AOF ({AOF_1:.1f} STB/d)")
plt.title("Part 1: Simple IPR Curve for Undersaturated Reservoir\n(Constant J Approach)", fontweight="bold")
plt.xlabel("Oil Production Rate, Qo (STB/day)", fontweight="bold")
plt.ylabel("Flowing Bottom-Hole Pressure, Pwf (psi)", fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
show_and_save("part1_simple_ipr.png")


# ==============================================================================
# PART 2: VOGEL'S METHOD (SATURATED & UNDERSATURATED RESERVOIRS)
# ==============================================================================
print("\n" + "="*70)
print("PART 2: VOGEL'S METHOD")
print("="*70)

# 2A. Saturated Reservoir (Pr <= Pb)
Pr_2 = 2500.0         # Reservoir pressure (psi)
Pwf_test_2 = 2000.0   # Flowing pressure (psi)
Qo_test_2 = 350.0     # Oil rate (STB/day)

qmax_vogel_2 = ipr.calculate_vogel_qmax(Qo_test_2, Pwf_test_2, Pr_2)
J_const_2, _ = ipr.calculate_constant_j(Qo_test_2, Pr_2, Pwf_test_2)
print(f"Saturated Vogel Qmax: {qmax_vogel_2:.2f} STB/day")
print(f"Constant J: {J_const_2:.4f} STB/day/psi")

pwf_range_2 = np.linspace(Pr_2, 0, 11)
qo_vogel_2 = ipr.ipr_vogel(qmax_vogel_2, Pr_2, pwf_range_2)
qo_const_2 = ipr.ipr_constant_j(J_const_2, Pr_2, pwf_range_2)

# Save Table to CSV
df_part2 = pd.DataFrame({"Pwf (psi)": pwf_range_2, "Vogel Qo (STB/day)": qo_vogel_2, "Const J Qo (STB/day)": qo_const_2})
df_part2.to_csv(os.path.join(tables_dir, "part2_vogel_saturated.csv"), index=False)

# Plot Saturated: Vogel vs Constant J
plt.figure(figsize=(7, 5))
plt.plot(qo_vogel_2, pwf_range_2, color="crimson", linewidth=2.5, label="Vogel's Method")
plt.plot(qo_const_2, pwf_range_2, color="navy", linewidth=2.0, linestyle="--", label="Constant J Approach")
plt.scatter([Qo_test_2], [Pwf_test_2], color="black", s=70, zorder=5, label=f"Test Point ({Qo_test_2} STB/d, {Pwf_test_2} psi)")
plt.title(r"Part 2: Vogel's Method vs Constant J (Saturated Reservoir, $P_r \leq P_b$)", fontweight="bold")
plt.xlabel("Oil Production Rate, Qo (STB/day)", fontweight="bold")
plt.ylabel("Flowing Bottom-Hole Pressure, Pwf (psi)", fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
show_and_save("part2_vogel_vs_constant_j.png")

# 2B. Undersaturated Cases (Pr = 3000, Pb = 2130 psi)
Pr_under = 3000.0
Pb_under = 2130.0

# Case 1: Test Pwf >= Pb (Pwf = 2500, Qo = 250)
J_case1, _ = ipr.calculate_constant_j(250.0, Pr_under, 2500.0)
pwf_under = np.linspace(Pr_under, 0, 100)
qo_case1 = ipr.ipr_vogel_undersaturated(Pr_under, Pb_under, J_case1, pwf_under)

# Case 2: Test Pwf < Pb (Pwf = 1700, Qo = 630.7)
J_case2 = ipr.calculate_j_case2(630.7, 1700.0, Pr_under, Pb_under)
qo_case2 = ipr.ipr_vogel_undersaturated(Pr_under, Pb_under, J_case2, pwf_under)

plt.figure(figsize=(7, 5))
plt.plot(qo_case1, pwf_under, color="forestgreen", linewidth=2.5, label="Case 1: Test Pwf >= Pb (Pwf=2500 psi)")
plt.plot(qo_case2, pwf_under, color="darkorange", linewidth=2.0, linestyle="-.", label="Case 2: Test Pwf < Pb (Pwf=1700 psi)")
plt.axhline(y=Pb_under, color="red", linestyle=":", label=f"Bubble Point Pb = {Pb_under} psi")
plt.title("Part 2: Vogel Composite IPR for Undersaturated Reservoirs", fontweight="bold")
plt.xlabel("Oil Production Rate, Qo (STB/day)", fontweight="bold")
plt.ylabel("Flowing Bottom-Hole Pressure, Pwf (psi)", fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
show_and_save("part2_vogel_undersaturated_cases.png")

# 2C. Future Saturated IPR (Pr drops to 2200 psi)
Future_Pr_2 = 2200.0
fut_qmax_vogel = ipr.predict_future_vogel_saturated(qmax_vogel_2, Pr_2, Future_Pr_2)
fut_pwf_range_2 = np.linspace(Future_Pr_2, 0, 11)
fut_qo_vogel_2 = ipr.ipr_vogel(fut_qmax_vogel, Future_Pr_2, fut_pwf_range_2)

plt.figure(figsize=(7, 5))
plt.plot(qo_vogel_2, pwf_range_2, color="blue", linewidth=2.5, label=f"Present IPR (Pr = {Pr_2} psi)")
plt.plot(fut_qo_vogel_2, fut_pwf_range_2, color="red", linewidth=2.5, linestyle="--", label=f"Future IPR (Pr = {Future_Pr_2} psi)")
plt.title("Part 2: Vogel Present vs Future IPR Prediction (Saturated)", fontweight="bold")
plt.xlabel("Oil Production Rate, Qo (STB/day)", fontweight="bold")
plt.ylabel("Flowing Bottom-Hole Pressure, Pwf (psi)", fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
show_and_save("part2_vogel_future_ipr.png")

# 2D. Vogel Undersaturated Future IPR (Pr drops from 3000 to 2600 psi, Sheet 2 K57+)
Future_Pr_under = 2600.0
fut_J_case1 = ipr.predict_future_undersaturated_j(J_case1, Pr_under, Future_Pr_under)
fut_J_case2 = ipr.predict_future_undersaturated_j(J_case2, Pr_under, Future_Pr_under)
print(f"Vogel Undersaturated Future J Case 1: {fut_J_case1:.4f} STB/day/psi")
print(f"Vogel Undersaturated Future J Case 2: {fut_J_case2:.6f} STB/day/psi")

fut_pwf_under = np.linspace(Future_Pr_under, 0, 100)
fut_qo_case1 = ipr.ipr_vogel_undersaturated(Future_Pr_under, Pb_under, fut_J_case1, fut_pwf_under)
fut_qo_case2 = ipr.ipr_vogel_undersaturated(Future_Pr_under, Pb_under, fut_J_case2, fut_pwf_under)

# Save Table to CSV (11 evenly spaced Pwf points – keeps the table compact)
pwf_2d_table = np.linspace(Future_Pr_under, 0, 11)
qo_2d_case1  = ipr.ipr_vogel_undersaturated(Future_Pr_under, Pb_under, fut_J_case1, pwf_2d_table)
qo_2d_case2  = ipr.ipr_vogel_undersaturated(Future_Pr_under, Pb_under, fut_J_case2, pwf_2d_table)
df_part2d = pd.DataFrame({
    "Pwf (psi)":              np.round(pwf_2d_table, 2),
    "Case 1 Qo (STB/day)":   np.round(qo_2d_case1,  2),
    "Case 2 Qo (STB/day)":   np.round(qo_2d_case2,  2)
})
df_part2d.to_csv(os.path.join(tables_dir, "part2d_vogel_future_undersaturated.csv"), index=False)

plt.figure(figsize=(7, 5))
plt.plot(fut_qo_case1, fut_pwf_under, color="forestgreen", linewidth=2.5, label=f"Future Case 1 (Jf = {fut_J_case1:.4f})")
plt.plot(fut_qo_case2, fut_pwf_under, color="darkorange", linewidth=2.0, linestyle="-.", label=f"Future Case 2 (Jf = {fut_J_case2:.4f})")
plt.axhline(y=Pb_under, color="red", linestyle=":", label=f"Bubble Point Pb = {Pb_under} psi")
plt.title(r"Part 2: Vogel Future Undersaturated IPR ($P_r$ drops to 2600 psi)", fontweight="bold")
plt.xlabel("Oil Production Rate, Qo (STB/day)", fontweight="bold")
plt.ylabel("Flowing Bottom-Hole Pressure, Pwf (psi)", fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
show_and_save("part2_vogel_future_undersaturated.png")


# ==============================================================================
# PART 3: FETKOVICH MODEL (MULTI-RATE ANALYSIS & UNDERSATURATED IPR)
# ==============================================================================
print("\n" + "="*70)
print("PART 3: FETKOVICH MODEL")
print("="*70)

# Saturated Multi-Rate Test Data (Pr = 3600 psi)
Pr_3 = 3600.0
pwf_tests_3 = [3170.0, 2890.0, 2440.0, 2150.0]
qo_tests_3 = [263.0, 383.0, 497.0, 640.0]

slope_3, intercept_3, n_3, C_3, log_q_3, log_dp2_3 = ipr.fit_fetkovich_multirate(qo_tests_3, pwf_tests_3, Pr_3)
print(f"Log-Log Fit: slope = {slope_3:.4f}, intercept = {intercept_3:.4f}")
print(f"Fetkovich Parameters: n = {n_3:.4f}, C = {C_3:.7f} STB/day/(psi^2)^n")

# Log-Log Fit Plot
plt.figure(figsize=(7, 5))
plt.scatter(log_q_3, log_dp2_3, color="navy", s=80, label="Test Points")
x_line = np.linspace(min(log_q_3)-0.05, max(log_q_3)+0.05, 50)
plt.plot(x_line, slope_3 * x_line + intercept_3, color="red", label=f"Fit: y = {slope_3:.4f}x + {intercept_3:.4f}\nn={n_3:.4f}, C={C_3:.7f}")
plt.title("Part 3: Fetkovich Log-Log Multi-Rate Test Analysis", fontweight="bold")
plt.xlabel(r"$\log_{10}(Q_o)$ [STB/day]", fontweight="bold")
plt.ylabel(r"$\log_{10}(P_r^2 - P_{wf}^2)$ [$\mathrm{psi}^2$]", fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
show_and_save("part3_fetkovich_log_log_fit.png")

# Fetkovich Saturated IPR Curve
pwf_range_3 = np.linspace(Pr_3, 0, 11)
qo_fetkovich_3 = ipr.ipr_fetkovich(C_3, n_3, Pr_3, pwf_range_3)

# Save Table to CSV
df_part3 = pd.DataFrame({"Pwf (psi)": pwf_range_3, "Fetkovich Qo (STB/day)": qo_fetkovich_3})
df_part3.to_csv(os.path.join(tables_dir, "part3_fetkovich_saturated.csv"), index=False)

plt.figure(figsize=(7, 5))
plt.plot(qo_fetkovich_3, pwf_range_3, color="purple", linewidth=2.5, label=r"Fetkovich IPR: $Q_o = C(P_r^2 - P_{wf}^2)^n$")
plt.scatter(qo_tests_3, pwf_tests_3, color="red", s=70, label="Multi-Rate Test Data")
plt.title("Part 3: Fetkovich Saturated IPR Curve", fontweight="bold")
plt.xlabel("Oil Production Rate, Qo (STB/day)", fontweight="bold")
plt.ylabel("Flowing Bottom-Hole Pressure, Pwf (psi)", fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
show_and_save("part3_fetkovich_saturated_ipr.png")

# Darcy J Calculation for Undersaturated Reservoir (Sheet 3, Case 1)
J_darcy = ipr.calculate_darcy_j(k=65, h=20, uo=2.4, bo=1.4, re=660, rw=0.3, s=-0.5)
print(f"Calculated Darcy J: {J_darcy:.4f} STB/day/psi")

# 3B. Fetkovich Undersaturated IPR (Present) - Case 1 & Case 2
Pr_fet_c1 = 3000.0
Pb_fet_c1 = 1500.0
pwf_fet_c1 = np.linspace(Pr_fet_c1, 0, 100)
qo_fet_c1 = ipr.ipr_fetkovich_undersaturated(Pr_fet_c1, Pb_fet_c1, J_darcy, pwf_fet_c1)

Pr_fet_c2 = 4000.0
Pb_fet_c2 = 3200.0
J_fet_c2 = 700.0 / (4000.0 - 3000.0)  # J = Qo / (Pr - Pwf) = 700 / (4000 - 3000) = 0.7
pwf_fet_c2 = np.linspace(Pr_fet_c2, 0, 100)
qo_fet_c2 = ipr.ipr_fetkovich_undersaturated(Pr_fet_c2, Pb_fet_c2, J_fet_c2, pwf_fet_c2)

print(f"Fetkovich Undersaturated Case 1 J (Darcy): {J_darcy:.4f} STB/day/psi")
print(f"Fetkovich Undersaturated Case 2 J:        {J_fet_c2:.4f} STB/day/psi")

# Save Table to CSV (11 evenly spaced Pwf points each – compact, interview-ready)
pwf_3b_c1_table = np.linspace(Pr_fet_c1, 0, 11)
pwf_3b_c2_table = np.linspace(Pr_fet_c2, 0, 11)
df_part3b = pd.DataFrame({
    "Case1 Pwf (psi)": np.round(pwf_3b_c1_table, 2),
    "Case1 Qo (STB/day)": np.round(ipr.ipr_fetkovich_undersaturated(Pr_fet_c1, Pb_fet_c1, J_darcy,  pwf_3b_c1_table), 2),
    "Case2 Pwf (psi)": np.round(pwf_3b_c2_table, 2),
    "Case2 Qo (STB/day)": np.round(ipr.ipr_fetkovich_undersaturated(Pr_fet_c2, Pb_fet_c2, J_fet_c2, pwf_3b_c2_table), 2)
})
df_part3b.to_csv(os.path.join(tables_dir, "part3b_fetkovich_undersaturated_cases.csv"), index=False)

plt.figure(figsize=(7, 5))
plt.plot(qo_fet_c1, pwf_fet_c1, color="teal", linewidth=2.5, label=f"Case 1: Pr=3000, Pb=1500 (Darcy J={J_darcy:.4f})")
plt.plot(qo_fet_c2, pwf_fet_c2, color="chocolate", linewidth=2.0, linestyle="--", label=f"Case 2: Pr=4000, Pb=3200 (J={J_fet_c2:.4f})")
plt.title("Part 3: Fetkovich Undersaturated IPR (Case 1 & Case 2)", fontweight="bold")
plt.xlabel("Oil Production Rate, Qo (STB/day)", fontweight="bold")
plt.ylabel("Flowing Bottom-Hole Pressure, Pwf (psi)", fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
show_and_save("part3_fetkovich_undersaturated_cases.png")

# 3C. Future Saturated Fetkovich (Pr drops to 2000 psi)
Future_Pr_3 = 2000.0
C_future_3 = ipr.predict_future_fetkovich_c(C_3, Pr_3, Future_Pr_3)
fut_pwf_range_3 = np.linspace(Future_Pr_3, 0, 11)
fut_qo_fetkovich_3 = ipr.ipr_fetkovich(C_future_3, n_3, Future_Pr_3, fut_pwf_range_3)

plt.figure(figsize=(7, 5))
plt.plot(qo_fetkovich_3, pwf_range_3, color="navy", linewidth=2.5, label=f"Present IPR (Pr = {Pr_3} psi)")
plt.plot(fut_qo_fetkovich_3, fut_pwf_range_3, color="crimson", linewidth=2.5, linestyle="--", label=f"Future IPR (Pr = {Future_Pr_3} psi)")
plt.title("Part 3: Fetkovich Present vs Future IPR Curve (Saturated)", fontweight="bold")
plt.xlabel("Oil Production Rate, Qo (STB/day)", fontweight="bold")
plt.ylabel("Flowing Bottom-Hole Pressure, Pwf (psi)", fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
show_and_save("part3_fetkovich_future_ipr.png")

# 3D. Future Undersaturated IPR — Fetkovich vs Vogel Comparison (Sheet 3, L75+)
Pr_fut_under = 3000.0        # Present Pr
Pb_fut_under = 1500.0        # Bubble point
Pwf_test_fu = 2200.0         # Test Pwf
Qo_test_fu = 280.0           # Test Qo
Pr_depleted_fu = 2500.0      # Future Pr

J_p_fu = Qo_test_fu / (Pr_fut_under - Pwf_test_fu)  # Jp = 0.35 STB/d/psi

# Fetkovich Future Method:
Cp_fu = J_p_fu / (2.0 * Pb_fut_under)               # Cp = 0.0001167
Cf_fu = Cp_fu * (Pr_depleted_fu / Pr_fut_under)     # Cf = 0.0000972
Jf_fet_fu = 2.0 * Cf_fu * Pb_fut_under              # Jf = 0.2917 STB/d/psi

# Vogel Future Method:
Jf_vog_fu = J_p_fu * ((Pr_depleted_fu / Pr_fut_under) ** 2)  # Jf = 0.2431 STB/d/psi

print(f"Future Undersaturated (Pr: 3000 -> 2500 psi):")
print(f"  Fetkovich Future J: {Jf_fet_fu:.4f} STB/day/psi")
print(f"  Vogel Future J:     {Jf_vog_fu:.4f} STB/day/psi")

pwf_fu_range = np.linspace(Pr_depleted_fu, 0, 100)
qo_fut_fet = ipr.ipr_fetkovich_undersaturated(Pr_depleted_fu, Pb_fut_under, Jf_fet_fu, pwf_fu_range)
qo_fut_vog = ipr.ipr_vogel_undersaturated(Pr_depleted_fu, Pb_fut_under, Jf_vog_fu, pwf_fu_range)

plt.figure(figsize=(7, 5))
plt.plot(qo_fut_fet, pwf_fu_range, color="purple", linewidth=2.5, label=f"Fetkovich Future (Jf = {Jf_fet_fu:.4f})")
plt.plot(qo_fut_vog, pwf_fu_range, color="green", linewidth=2.0, linestyle="--", label=f"Vogel Future (Jf = {Jf_vog_fu:.4f})")
plt.axhline(y=Pb_fut_under, color="red", linestyle=":", label=f"Bubble Point Pb = {Pb_fut_under} psi")
plt.title("Part 3: Future Undersaturated IPR — Fetkovich vs Vogel", fontweight="bold")
plt.xlabel("Oil Production Rate, Qo (STB/day)", fontweight="bold")
plt.ylabel("Flowing Bottom-Hole Pressure, Pwf (psi)", fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
show_and_save("part3_fetkovich_future_undersaturated.png")


# ==============================================================================
# PART 4: REAL FIELD CASE — WELL B, KEOKUK POOL, OKLAHOMA (PRESENT IPR)
# ==============================================================================
print("\n" + "="*70)
print("PART 4: REAL FIELD CASE — WELL B (PRESENT IPR)")
print("="*70)

# Field Inputs
Pr_4 = 1714.0         # Reservoir pressure (psi)
Pb_4 = 3420.0         # Bubble-point pressure (psi)
C1_4 = 0.41           # Constant for New Correlation

# Actual Multi-Rate Test Data
actual_pwf_4 = [1714.0, 1583.0, 1443.0, 1272.0, 1196.0, 982.0]
actual_qo_4 = [0.0, 280.0, 508.0, 780.0, 1125.0, 1335.0]

# Model Calibrations:
# 1. Single test point (Pwf = 1196, Qo = 1125) for Vogel & New Correlation
qmax_vogel_4 = ipr.calculate_vogel_qmax(1125.0, 1196.0, Pr_4)
qmax_new_4 = ipr.calculate_new_correlation_qmax(1125.0, 1196.0, Pr_4, C1_4)

# 2. Two test points (Pwf1=1443, Qo1=508 and Pwf2=1196, Qo2=1125) for Fetkovich
_, _, n_fet_4, C_fet_4 = ipr.fit_fetkovich_two_points(1443.0, 508.0, 1196.0, 1125.0, Pr_4)

print(f"Vogel Qmax:           {qmax_vogel_4:.2f} STB/day")
print(f"New Correlation Qmax: {qmax_new_4:.2f} STB/day")
print(f"Fetkovich:            n = {n_fet_4:.4f}, C = {C_fet_4:.5e}")

# Predictions at actual test pressures
pred_new_4 = ipr.ipr_new_correlation(qmax_new_4, Pr_4, actual_pwf_4, C1_4)
pred_vog_4 = ipr.ipr_vogel(qmax_vogel_4, Pr_4, actual_pwf_4)
pred_fet_4 = ipr.ipr_fetkovich(C_fet_4, n_fet_4, Pr_4, actual_pwf_4)

# Error analysis (excluding zero production rate at Pwf = 1714 psi)
act_valid = actual_qo_4[1:]
err_new_4, aae_new_4 = ipr.calculate_errors(act_valid, pred_new_4[1:])
err_vog_4, aae_vog_4 = ipr.calculate_errors(act_valid, pred_vog_4[1:])
err_fet_4, aae_fet_4 = ipr.calculate_errors(act_valid, pred_fet_4[1:])

print(f"\nAverage Absolute Errors (AAE):")
print(f"  New Correlation: {aae_new_4:.2f}%  (Best match)")
print(f"  Fetkovich:       {aae_fet_4:.2f}%")
print(f"  Vogel:           {aae_vog_4:.2f}%")

# Save Comparison Table to CSV
df_well_b_present = pd.DataFrame({
    "Pwf (psi)": actual_pwf_4,
    "Actual Qo (bbl/day)": actual_qo_4,
    "New Correlation Qo": np.round(pred_new_4, 2),
    "Vogel Qo": np.round(pred_vog_4, 2),
    "Fetkovich Qo": np.round(pred_fet_4, 2)
})
df_well_b_present.to_csv(os.path.join(tables_dir, "part4_well_b_present_comparison.csv"), index=False)

# Plot Well B Present Comparison
pwf_smooth_4 = np.linspace(Pr_4, 0, 100)
plt.figure(figsize=(8, 5.5))
plt.scatter(actual_qo_4, actual_pwf_4, color="black", s=80, zorder=5, label="Actual Test Data (Well B)")
plt.plot(ipr.ipr_new_correlation(qmax_new_4, Pr_4, pwf_smooth_4, C1_4), pwf_smooth_4,
         color="blue", linewidth=2.5, label=f"New Correlation (AAE = {aae_new_4:.2f}%)")
plt.plot(ipr.ipr_vogel(qmax_vogel_4, Pr_4, pwf_smooth_4), pwf_smooth_4,
         color="green", linewidth=2.0, linestyle="--", label=f"Vogel's Method (AAE = {aae_vog_4:.2f}%)")
plt.plot(ipr.ipr_fetkovich(C_fet_4, n_fet_4, Pr_4, pwf_smooth_4), pwf_smooth_4,
         color="red", linewidth=2.0, linestyle="-.", label=f"Fetkovich (AAE = {aae_fet_4:.2f}%)")
plt.title("Part 4: Well B Present IPR Model Comparison against Field Data", fontweight="bold")
plt.xlabel("Oil Production Rate, Qo (bbl/day)", fontweight="bold")
plt.ylabel("Flowing Bottom-Hole Pressure, Pwf (psi)", fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
show_and_save("part4_well_b_present_ipr_comparison.png")


# ==============================================================================
# PART 5: FUTURE IPR PREDICTIONS FOR WELL B (AFTER 8 MONTHS DEPLETION)
# ==============================================================================
print("\n" + "="*70)
print("PART 5: FUTURE IPR PREDICTIONS FOR WELL B")
print("="*70)

# Future reservoir pressure drops to 1605 psi after 8 months
Future_Pr_5 = 1605.0
Future_C1_5 = 0.49

# Actual repeated multi-rate test points
actual_pwf_5 = [1605.0, 1381.0, 1231.0, 1120.0]
actual_qo_5 = [0.0, 420.0, 720.0, 850.0]

# Future deliverability calibrations (Eickmeier cubic equation)
fut_qmax_new_5 = ipr.predict_future_eickmeier(qmax_new_4, Pr_4, Future_Pr_5)
fut_qmax_vog_5 = ipr.predict_future_eickmeier(qmax_vogel_4, Pr_4, Future_Pr_5)
fut_C_fet_5 = ipr.predict_future_fetkovich_c(C_fet_4, Pr_4, Future_Pr_5)

print(f"Future New Qmax:   {fut_qmax_new_5:.2f} STB/day")
print(f"Future Vogel Qmax: {fut_qmax_vog_5:.2f} STB/day")
print(f"Future Fetkovich C:{fut_C_fet_5:.5e}")

# Predictions at repeated test pressures
pred_new_5 = ipr.ipr_new_correlation(fut_qmax_new_5, Future_Pr_5, actual_pwf_5, Future_C1_5)
pred_vog_5 = ipr.ipr_vogel(fut_qmax_vog_5, Future_Pr_5, actual_pwf_5)
pred_fet_5 = ipr.ipr_fetkovich(fut_C_fet_5, n_fet_4, Future_Pr_5, actual_pwf_5)

# Future Error analysis (excluding zero rate at Pwf = 1605 psi)
act_valid_5 = actual_qo_5[1:]
err_new_5, aae_new_5 = ipr.calculate_errors(act_valid_5, pred_new_5[1:])
err_vog_5, aae_vog_5 = ipr.calculate_errors(act_valid_5, pred_vog_5[1:])
err_fet_5, aae_fet_5 = ipr.calculate_errors(act_valid_5, pred_fet_5[1:])

print(f"\nFuture Average Absolute Errors (AAE):")
print(f"  Future New Correlation: {aae_new_5:.2f}%  (Best match)")
print(f"  Future Vogel:           {aae_vog_5:.2f}%")
print(f"  Future Fetkovich:       {aae_fet_5:.2f}%")

# Save Future Table to CSV
df_well_b_future = pd.DataFrame({
    "Pwf (psi)": actual_pwf_5,
    "Actual Qo (bbl/day)": actual_qo_5,
    "Future New Correlation Qo": np.round(pred_new_5, 2),
    "Future Vogel Qo": np.round(pred_vog_5, 2),
    "Future Fetkovich Qo": np.round(pred_fet_5, 2)
})
df_well_b_future.to_csv(os.path.join(tables_dir, "part5_well_b_future_comparison.csv"), index=False)

# Plot Well B Future Comparison
pwf_smooth_5 = np.linspace(Future_Pr_5, 0, 100)
plt.figure(figsize=(8, 5.5))
plt.scatter(actual_qo_5, actual_pwf_5, color="black", s=80, zorder=5, label="Actual Test Data (After 8 Months)")
plt.plot(ipr.ipr_new_correlation(fut_qmax_new_5, Future_Pr_5, pwf_smooth_5, Future_C1_5), pwf_smooth_5,
         color="blue", linewidth=2.5, label=f"Future New Correlation (AAE = {aae_new_5:.2f}%)")
plt.plot(ipr.ipr_vogel(fut_qmax_vog_5, Future_Pr_5, pwf_smooth_5), pwf_smooth_5,
         color="green", linewidth=2.0, linestyle="--", label=f"Future Vogel (AAE = {aae_vog_5:.2f}%)")
plt.plot(ipr.ipr_fetkovich(fut_C_fet_5, n_fet_4, Future_Pr_5, pwf_smooth_5), pwf_smooth_5,
         color="red", linewidth=2.0, linestyle="-.", label=f"Future Fetkovich (AAE = {aae_fet_5:.2f}%)")
plt.title("Part 5: Well B Future IPR Model Predictions after Pressure Depletion", fontweight="bold")
plt.xlabel("Oil Production Rate, Qo (bbl/day)", fontweight="bold")
plt.ylabel("Flowing Bottom-Hole Pressure, Pwf (psi)", fontweight="bold")
plt.grid(True, linestyle="--", alpha=0.6)
plt.legend()
plt.tight_layout()
show_and_save("part5_well_b_future_ipr_comparison.png")

print("\n" + "="*70)
print("PROJECT EXECUTION COMPLETED SUCCESSFULLY!")
print(f"  Plots  -> {plots_dir}")
print(f"  Tables -> {tables_dir}")
print("="*70 + "\n")

# Petroleum Engineering Inflow Performance Relationship (IPR) Project
## Streamlined 2-File Python Implementation & Technical Documentation

---

## 1. What This Python Integration Adds to Your Project

As a Petroleum Engineer, completing an Inflow Performance Relationship (IPR) project in Microsoft Excel demonstrates your solid understanding of reservoir drive mechanisms and deliverability curves. 

This **minimal, 2-file Python implementation** adds a computational edge to your portfolio without any software engineering bloat:
1. **Zero Excel Scraping Boilerplate**: You do not need hundreds of lines of complex cell-parsing code (`openpyxl`, cell coordinates, etc.). All reservoir inputs are defined directly as clean, readable engineering numbers and lists.
2. **True Petroleum Engineering Code**: Any petroleum engineer or interviewer can open `ipr_calculations.py` and immediately recognize Darcy's law, Vogel's equation, Fetkovich's backpressure equation, and Eickmeier's depletion relationship.
3. **Interactive Visualizations & Auto-Export**: Running `python main.py` pops up your plots on screen so you can inspect them visually and simultaneously saves publication-quality 300 DPI figures and clean CSV tables to `outputs/`.
4. **Original Files 100% Preserved**: Your original Excel workbook (`IPR_PROJECT_Gunathmini.xlsx`), PDF, and original `README.md` remain completely untouched.

---

## 2. Minimal 2-File Project Structure

The Python version contains only **two code files**:

```text
python_version/
│
├── ipr_calculations.py   <-- File 1: Pure petroleum engineering equations
├── main.py               <-- File 2: Clean input numbers/lists + plots + outputs
├── requirements.txt      <-- Package requirements (NumPy, Pandas, Matplotlib)
├── README_PYTHON.md      <-- This documentation & interview prep guide
└── outputs/              <-- Generated PNG plots and CSV tables
    ├── part1_simple_ipr.png
    ├── part1_simple_ipr.csv
    ├── part2_vogel_vs_constant_j.png
    ├── part2_vogel_undersaturated_cases.png
    ├── part2_vogel_future_ipr.png
    ├── part2_vogel_saturated.csv
    ├── part3_fetkovich_log_log_fit.png
    ├── part3_fetkovich_saturated_ipr.png
    ├── part3_fetkovich_future_ipr.png
    ├── part3_fetkovich_saturated.csv
    ├── part4_well_b_present_ipr_comparison.png
    ├── part4_well_b_present_comparison.csv
    ├── part5_well_b_future_ipr_comparison.png
    └── part5_well_b_future_comparison.csv
```

---

## 3. Technology Stack & Packages Used

Only 3 standard, industry-standard scientific libraries are used:

| Library | Role in This Project |
| :--- | :--- |
| **NumPy** (`numpy`) | Performs fast array calculations for pressure ranges and power laws $(P_r^2 - P_{wf}^2)^n$. |
| **Pandas** (`pandas`) | Organizes calculated results into clean tables and exports CSV files for Excel viewing. |
| **Matplotlib** (`matplotlib.pyplot`) | Displays graphs interactively on your screen and exports high-resolution PNG images. |

Install dependencies in one command:
```bash
pip install -r python_version/requirements.txt
```

---

## 4. How to Run the Project

Open PowerShell or Command Prompt:

```bash
# Navigate to the project
cd C:\Users\gunat\Downloads\IPR-Project-main

# Run the project
python python_version/main.py
```

- Each plot will **display directly on your screen**. Close the plot window to advance to the next part.
- All 8 plots and 5 CSV files are automatically saved in `python_version/outputs/`.

*(Tip: If you want to run the script in the background without waiting to close each window, run: `python python_version/main.py --no-block`)*

---

## 5. Petroleum Engineering Equations & Code Breakdown

### Part 1: Simple IPR Curve (Undersaturated Reservoir, $P_r > P_b$)

#### Physics:
When both reservoir pressure ($P_r$) and flowing bottom-hole pressure ($P_{wf}$) remain above bubble point ($P_b$), only single-phase liquid oil exists in the reservoir. Darcy's law governs flow, resulting in a **straight-line IPR**.

#### Equations:
1. **Productivity Index ($J$)**:
   $$J = \frac{Q_o}{P_r - P_{wf}} \quad \text{(STB/day/psi)}$$
2. **Absolute Open Flow Potential ($AOF$)**:
   $$AOF = J \times P_r \quad \text{(STB/day)}$$
3. **Oil Rate at Any Pressure**:
   $$Q_o(P_{wf}) = J \times (P_r - P_{wf})$$

#### In `main.py` (Inputs):
```python
Pr_1 = 1300.0         # Average reservoir pressure (psi)
Pwf_test_1 = 900.0    # Test flowing pressure (psi)
Qo_test_1 = 110.0     # Stabilized test rate (STB/day)
```

#### In `ipr_calculations.py`:
```python
def calculate_constant_j(oil_rate, reservoir_pressure, flowing_pressure):
    drawdown = reservoir_pressure - flowing_pressure
    j = oil_rate / drawdown
    aof = j * reservoir_pressure
    return j, aof
```

---

### Part 2: Vogel's Method (Saturated Reservoirs, $P_r \le P_b$)

#### Physics:
When reservoir pressure drops below the bubble point, gas bubbles liberate inside the pores. This evolution drastically reduces the relative permeability to oil ($k_{ro}$) and increases oil viscosity. Vogel (1968) introduced the universal non-dimensional parabolic curve.

#### Equations:
1. **Vogel Non-Dimensional Equation**:
   $$\frac{Q_o}{Q_{o,\max}} = 1 - 0.2\left(\frac{P_{wf}}{P_r}\right) - 0.8\left(\frac{P_{wf}}{P_r}\right)^2$$
2. **Maximum Deliverability ($Q_{o,\max}$)** from a stabilized test $(P_{wf}, Q_o)$:
   $$Q_{o,\max} = \frac{Q_o}{1 - 0.2(P_{wf}/P_r) - 0.8(P_{wf}/P_r)^2}$$
3. **Future Vogel IPR (Depletion to $(P_r)_f$)**:
   $$(Q_{o,\max})_f = (Q_{o,\max})_p \times \left(\frac{(P_r)_f}{(P_r)_p}\right) \times \left[0.2 + 0.8\left(\frac{(P_r)_f}{(P_r)_p}\right)\right]$$

#### In `main.py` (Inputs):
```python
Pr_2 = 2500.0
Pwf_test_2 = 2000.0
Qo_test_2 = 350.0
Future_Pr_2 = 2200.0
```

#### In `ipr_calculations.py`:
```python
def calculate_vogel_qmax(oil_rate, flowing_pressure, reservoir_pressure):
    ratio = flowing_pressure / reservoir_pressure
    vogel_term = 1.0 - 0.2 * ratio - 0.8 * (ratio ** 2)
    return oil_rate / vogel_term

def ipr_vogel(qmax, reservoir_pressure, flowing_pressures):
    pwf = np.array(flowing_pressures, dtype=float)
    ratio = pwf / reservoir_pressure
    vogel_term = 1.0 - 0.2 * ratio - 0.8 * (ratio ** 2)
    return qmax * np.maximum(0.0, vogel_term)
```

---

### Part 3: Fetkovich Empirical Deliverability Model

#### Physics:
Fetkovich (1973) applied the backpressure power law to oil wells to account for turbulence and multiphase flow near the wellbore.

#### Equations:
1. **Flow Equation**:
   $$Q_o = C (P_r^2 - P_{wf}^2)^n$$
   - $n$: Exponent indicating flow regime ($0.5 \le n \le 1.0$). $n=1.0$ is laminar; $n=0.5$ is fully turbulent.
   - $C$: Deliverability coefficient.
2. **Linear Log-Log Fit**:
   $$\log_{10}(P_r^2 - P_{wf}^2) = m \cdot \log_{10}(Q_o) + b$$
   $$n = \frac{1}{m}, \quad C = 10^{-b / m}$$
3. **Future Deliverability**:
   $$n_f = n_p, \quad C_f = C_p \times \left(\frac{(P_r)_f}{(P_r)_p}\right)$$

#### In `main.py` (Inputs):
```python
Pr_3 = 3600.0
pwf_tests_3 = [3170.0, 2890.0, 2440.0, 2150.0]
qo_tests_3 = [263.0, 383.0, 497.0, 640.0]
Future_Pr_3 = 2000.0
```

#### In `ipr_calculations.py`:
```python
def fit_fetkovich_multirate(oil_rates, flowing_pressures, reservoir_pressure):
    x = np.log10(oil_rates)
    y = np.log10((reservoir_pressure ** 2) - (np.array(flowing_pressures) ** 2))
    slope, intercept = np.polyfit(x, y, 1)
    n = 1.0 / slope
    c = 10.0 ** (-intercept / slope)
    return slope, intercept, n, c, x, y
```

---

### Part 4: Real Field Case – Well B, Keokuk Pool (Oklahoma)

#### Field Data:
Well B, Keokuk Pool, Seminole County, Oklahoma (August 1935).
- Saturated reservoir: $P_r = 1714\text{ psi}, P_b = 3420\text{ psi}$.
- Multi-rate test points:
  - $(P_{wf}, Q_o) = (1714, 0), (1583, 280), (1443, 508), (1272, 780), (1196, 1125), (982, 1335)$

#### Models Compared:
1. **New Correlation** ($C_1 = 0.41$, single test point $P_{wf}=1196, Q_o=1125$):
   $$\frac{Q_o}{Q_{o,\max}} = 1 - C_1\left(\frac{P_{wf}}{P_r}\right) - (1 - C_1)\left(\frac{P_{wf}}{P_r}\right)^2 \implies Q_{o,\max} = 2636.90\text{ STB/day}$$
2. **Vogel's Correlation** (same single test point):
   $$Q_{o,\max} = 2388.93\text{ STB/day}$$
3. **Fetkovich Correlation** (two test points: $(1443, 508)$ and $(1196, 1125)$):
   $$n = 1.4037, \quad C = 2.39097 \times 10^{-6}$$

#### Error Analysis:
$$\text{Percentage Error} = \frac{|Q_{\text{actual}} - Q_{\text{predicted}}|}{Q_{\text{actual}}} \times 100\%$$
$$\text{Average Absolute Error (AAE)} = \frac{1}{N} \sum_{i=1}^N \text{Percentage Error}_i$$

#### Present IPR Results:
- **New Correlation AAE**: **14.45%** (Best Match!)
- **Fetkovich Method AAE**: **14.64%**
- **Vogel's Method AAE**: **15.03%**

---

### Part 5: Future IPR Prediction for Well B (8 Months Depletion)

#### Depletion Context:
After 8 months of continuous production, reservoir pressure dropped from $1714\text{ psi}$ down to $1605\text{ psi}$.
- Future $C_1 = 0.49$.
- Repeated test data: $(1605, 0), (1381, 420), (1231, 720), (1120, 850)$.

#### Future Formulations:
1. **New Correlation & Vogel (Eickmeier Equation)**:
   $$(Q_{o,\max})_f = (Q_{o,\max})_p \times \left(\frac{(P_r)_f}{(P_r)_p}\right)^3$$
2. **Fetkovich Deliverability**:
   $$C_f = C_p \times \left(\frac{(P_r)_f}{(P_r)_p}\right) = 2.23892 \times 10^{-6}, \quad n = 1.4037$$

#### Future Performance Results:
- **Future New Correlation AAE**: **3.47%** (Outstanding Accuracy!)
- **Future Vogel AAE**: **7.05%**
- **Future Fetkovich AAE**: **11.18%**

---

## 6. Numerical Verification Table Against Excel

| Sheet & Section | Parameter | Excel Cell | Excel Value | Python Result | Match |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Sheet 1** | Productivity Index $J$ | `D7` | `0.2750 STB/d/psi` | `0.2750 STB/d/psi` | **Exact** |
| **Sheet 1** | AOF ($Q_{o,\max}$) | `D8` | `357.50 STB/day` | `357.50 STB/day` | **Exact** |
| **Sheet 2** | Saturated Vogel $Q_{\max}$ | `G19` | `1067.073 STB/day` | `1067.073 STB/day` | **Exact** |
| **Sheet 2** | Saturated Constant $J$ | `G18` | `0.7000 STB/d/psi` | `0.7000 STB/d/psi` | **Exact** |
| **Sheet 2** | Future Vogel $Q_{\max}$ | `C64` | `848.878 STB/day` | `848.878 STB/day` | **Exact** |
| **Sheet 3** | Fetkovich slope $m$ | `H26` | `1.226430` | `1.226430` | **Exact** |
| **Sheet 3** | Fetkovich $n$ | `H28` | `0.815374` | `0.815374` | **Exact** |
| **Sheet 3** | Fetkovich $C$ | `H29` | `0.0013939` | `0.0013939` | **Exact** |
| **Sheet 4** | Well B Vogel $Q_{\max}$ | `I22` | `2388.928 STB/day` | `2388.928 STB/day` | **Exact** |
| **Sheet 4** | Well B New $Q_{\max}$ | `C23` | `2636.900 STB/day` | `2636.900 STB/day` | **Exact** |
| **Sheet 4** | Well B Fetkovich $n$ | `Q37` | `1.403734` | `1.403734` | **Exact** |
| **Sheet 4** | Well B Fetkovich $C$ | `Q36` | `2.39097e-06` | `2.39097e-06` | **Exact** |
| **Sheet 4** | **Present New AAE** | `D58` | **14.45%** | **14.45%** | **Exact (Best)** |
| **Sheet 4** | Present Fetkovich AAE | `F58` | `14.64%` | `14.64%` | **Exact** |
| **Sheet 4** | Present Vogel AAE | `E58` | `15.03%` | `15.03%` | **Exact** |
| **Sheet 4** | **Future New AAE** | `D114` | **3.47%** | **3.47%** | **Exact (Best)** |
| **Sheet 4** | Future Vogel AAE | `E114` | `7.05%` | `7.05%` | **Exact** |
| **Sheet 4** | Future Fetkovich AAE | `F114` | `11.18%` | `11.18%` | **Exact** |

---

## 7. Petroleum Engineering Interview Questions & Answers

### Q1: Why does a saturated reservoir have a curved IPR while an undersaturated reservoir has a straight line?
> **Answer**: In an undersaturated reservoir ($P_{wf} \ge P_b$), the fluid is single-phase liquid oil. Permeability and viscosity remain virtually constant, obeying Darcy's linear law ($Q_o = J \Delta P$). In a saturated reservoir ($P_{wf} < P_b$), dissolved gas evolves into free gas bubbles. Free gas chokes oil flow channels (drastically decreasing $k_{ro}$) and strips light hydrocarbons, increasing oil viscosity. This two-phase interference causes the curve to bend toward the pressure axis as drawdown increases.

### Q2: What does the Fetkovich exponent $n$ represent?
> **Answer**: The exponent $n$ characterizes the flow regime near the wellbore. A value of $n = 1.0$ represents purely laminar (Darcy) flow. As drawdown and velocity increase, non-Darcy inertial/turbulent pressure losses occur near the perforations, causing $n$ to decrease toward $0.5$. In saturated reservoirs, values around $0.8$ are common.

### Q3: Why did the New Correlation outperform Vogel and Fetkovich on Well B?
> **Answer**: The New Correlation incorporates an adjustable parameter $C_1$ ($0.41$ for present, $0.49$ for future) that provides greater flexibility to model the specific gas-oil relative permeability curvature and skin behavior of the Keokuk Pool formation, resulting in the lowest Average Absolute Error (14.45% present and 3.47% future).

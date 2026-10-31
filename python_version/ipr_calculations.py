"""
ipr_calculations.py
===================
Pure petroleum engineering calculations for Inflow Performance Relationship (IPR):
  1. Constant Productivity Index (J) for Undersaturated Reservoirs
  2. Vogel's Equation for Saturated & Undersaturated Reservoirs
  3. Fetkovich's Empirical Backpressure Model (n and C Determination)
  4. Well B Field Case (New Correlation, Vogel, Fetkovich, % Error & AAE)
  5. Future IPR Deliverability Predictions (Eickmeier & Fetkovich Depletion)

Author: Petroleum Engineering Student
"""

import numpy as np


# ------------------------------------------------------------------------------
# PART 1: CONSTANT J APPROACH (UNDERSATURATED RESERVOIR, Pr > Pb)
# ------------------------------------------------------------------------------

def calculate_constant_j(oil_rate, reservoir_pressure, flowing_pressure):
    """Productivity index J = Qo / (Pr - Pwf) and AOF = J * Pr"""
    drawdown = reservoir_pressure - flowing_pressure
    j = oil_rate / drawdown
    aof = j * reservoir_pressure
    return j, aof


def ipr_constant_j(j, reservoir_pressure, flowing_pressures):
    """Qo = J * (Pr - Pwf)"""
    pwf = np.array(flowing_pressures, dtype=float)
    return j * (reservoir_pressure - pwf)


# ------------------------------------------------------------------------------
# PART 2: VOGEL'S CORRELATION (SATURATED & UNDERSATURATED RESERVOIRS)
# ------------------------------------------------------------------------------

def calculate_vogel_qmax(oil_rate, flowing_pressure, reservoir_pressure):
    """Qmax = Qo / [1 - 0.2*(Pwf/Pr) - 0.8*(Pwf/Pr)^2]"""
    ratio = flowing_pressure / reservoir_pressure
    vogel_term = 1.0 - 0.2 * ratio - 0.8 * (ratio ** 2)
    return oil_rate / vogel_term 


def ipr_vogel(qmax, reservoir_pressure, flowing_pressures):
    """Qo = Qmax * [1 - 0.2*(Pwf/Pr) - 0.8*(Pwf/Pr)^2]"""
    pwf = np.array(flowing_pressures, dtype=float)
    ratio = pwf / reservoir_pressure
    vogel_term = 1.0 - 0.2 * ratio - 0.8 * (ratio ** 2)
    return qmax * np.maximum(0.0, vogel_term)


def ipr_vogel_undersaturated(reservoir_pressure, bubble_point_pressure, j, flowing_pressures):
    """
    Vogel composite IPR for undersaturated reservoirs (Pr > Pb):
      - Straight line for Pwf >= Pb: Qo = J * (Pr - Pwf)
      - Vogel curve for Pwf < Pb:    Qo = Qob + Qmax_vogel * [1 - 0.2*(Pwf/Pb) - 0.8*(Pwf/Pb)^2]
    """
    pwf = np.array(flowing_pressures, dtype=float)
    qob = j * (reservoir_pressure - bubble_point_pressure)
    qmax_vogel = (j * bubble_point_pressure) / 1.8

    qo = []
    for p in pwf:
        if p >= bubble_point_pressure:
            rate = j * (reservoir_pressure - p)
        else:
            ratio = p / bubble_point_pressure
            rate = qob + qmax_vogel * (1.0 - 0.2 * ratio - 0.8 * (ratio ** 2))
        qo.append(max(0.0, rate))
    return np.array(qo)


def calculate_j_case2(oil_rate, flowing_pressure, reservoir_pressure, bubble_point_pressure):
    """J when test Pwf < Pb in an undersaturated reservoir"""
    ratio = flowing_pressure / bubble_point_pressure
    vogel_term = 1.0 - 0.2 * ratio - 0.8 * (ratio ** 2)
    denominator = (reservoir_pressure - bubble_point_pressure) + (bubble_point_pressure / 1.8) * vogel_term
    return oil_rate / denominator


# ------------------------------------------------------------------------------
# PART 3: FETKOVICH EMPIRICAL MODEL (Qo = C * (Pr^2 - Pwf^2)^n)
# ------------------------------------------------------------------------------

def fit_fetkovich_multirate(oil_rates, flowing_pressures, reservoir_pressure):
    """
    Linear regression on multi-rate test data:
      x = log10(Qo), y = log10(Pr^2 - Pwf^2)
      slope = m, intercept = b
      n = 1 / slope, C = 10^(-intercept / slope)
    """
    x = np.log10(oil_rates)
    y = np.log10((reservoir_pressure ** 2) - (np.array(flowing_pressures) ** 2))
    slope, intercept = np.polyfit(x, y, 1)
    n = 1.0 / slope
    c = 10.0 ** (-intercept / slope)
    return slope, intercept, n, c, x, y


def ipr_fetkovich(c, n, reservoir_pressure, flowing_pressures):
    """Qo = C * (Pr^2 - Pwf^2)^n"""
    pwf = np.array(flowing_pressures, dtype=float)
    delta_p2 = np.maximum(0.0, (reservoir_pressure ** 2) - (pwf ** 2))
    return c * (delta_p2 ** n)


def calculate_darcy_j(k, h, uo, bo, re, rw, s):
    """Darcy law: J = (0.00708 * k * h) / [uo * bo * (ln(re/rw) - 0.75 + s)]"""
    return (0.00708 * k * h) / (uo * bo * (np.log(re / rw) - 0.75 + s))


def ipr_fetkovich_undersaturated(reservoir_pressure, bubble_point_pressure, j, flowing_pressures):
    """
    Fetkovich composite equation for undersaturated reservoirs (Pr > Pb):
      - Straight line for Pwf >= Pb: Qo = J * (Pr - Pwf)
      - Curved below Pb (Pwf < Pb):  Qo = J * [(Pr - Pb) + (1 / (2*Pb)) * (Pb^2 - Pwf^2)]
    """
    pwf = np.array(flowing_pressures, dtype=float)
    qo = []
    for p in pwf:
        if p >= bubble_point_pressure:
            rate = j * (reservoir_pressure - p)
        else:
            term1 = reservoir_pressure - bubble_point_pressure
            term2 = (1.0 / (2.0 * bubble_point_pressure)) * (bubble_point_pressure**2 - p**2)
            rate = j * (term1 + term2)
        qo.append(max(0.0, rate))
    return np.array(qo)


def predict_future_undersaturated_j(j_present, pr_present, pr_future):
    """Future J for undersaturated reservoirs: (J)f = (J)p * (Pr_f / Pr_p)^2"""
    return j_present * ((pr_future / pr_present) ** 2)


# ------------------------------------------------------------------------------
# PART 4: REAL FIELD CASE - WELL B (KEOKUK POOL, OKLAHOMA)
# ------------------------------------------------------------------------------

def calculate_new_correlation_qmax(oil_rate, flowing_pressure, reservoir_pressure, c1):
    """New Correlation: Qo / Qmax = 1 - C1*(Pwf/Pr) - (1-C1)*(Pwf/Pr)^2"""
    ratio = flowing_pressure / reservoir_pressure
    factor = 1.0 - c1 * ratio - (1.0 - c1) * (ratio ** 2)
    return oil_rate / factor


def ipr_new_correlation(qmax, reservoir_pressure, flowing_pressures, c1):
    """Qo = Qmax * [1 - C1*(Pwf/Pr) - (1-C1)*(Pwf/Pr)^2]"""
    pwf = np.array(flowing_pressures, dtype=float)
    ratio = pwf / reservoir_pressure
    factor = 1.0 - c1 * ratio - (1.0 - c1) * (ratio ** 2)
    return qmax * np.maximum(0.0, factor)


def fit_fetkovich_two_points(pwf1, qo1, pwf2, qo2, reservoir_pressure):
    """Determines Fetkovich n and C from two test points"""
    x1, x2 = np.log10(qo1), np.log10(qo2)
    y1 = np.log10((reservoir_pressure ** 2) - (pwf1 ** 2))
    y2 = np.log10((reservoir_pressure ** 2) - (pwf2 ** 2))
    slope = (y2 - y1) / (x2 - x1)
    intercept = y1 - slope * x1
    n = 1.0 / slope
    c = 10.0 ** (-intercept / slope)
    return slope, intercept, n, c


def calculate_errors(actual_rates, predicted_rates):
    """
    Percentage Error = |Actual - Predicted| / Actual * 100%
    Average Absolute Error (AAE) = (1 / N) * sum(Percentage Error)
    """
    actual = np.array(actual_rates, dtype=float)
    pred = np.array(predicted_rates, dtype=float)
    percent_errors = np.abs((actual - pred) / actual) * 100.0
    aae = float(np.mean(percent_errors))
    return percent_errors, aae


# ------------------------------------------------------------------------------
# PART 5: FUTURE IPR PREDICTIONS
# ------------------------------------------------------------------------------

def predict_future_vogel_saturated(qmax_present, pr_present, pr_future):
    """Vogel Future: (Qmax)f = (Qmax)p * (Pr_f/Pr_p) * [0.2 + 0.8*(Pr_f/Pr_p)]"""
    ratio = pr_future / pr_present
    return qmax_present * ratio * (0.2 + 0.8 * ratio)


def predict_future_eickmeier(qmax_present, pr_present, pr_future):
    """Eickmeier Future: (Qmax)f = (Qmax)p * (Pr_f / Pr_p)^3"""
    return qmax_present * ((pr_future / pr_present) ** 3)


def predict_future_fetkovich_c(c_present, pr_present, pr_future):
    """Fetkovich Future: (C)f = (C)p * (Pr_f / Pr_p), n remains constant"""
    return c_present * (pr_future / pr_present)

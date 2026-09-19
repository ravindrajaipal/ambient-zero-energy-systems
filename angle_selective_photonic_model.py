#!/usr/bin/env python3
"""
angle_selective_photonic_model.py
=============================================================================
Thermodynamic & Optical Physics Engine for:
Sub-Wavelength Angle-Selective Photonic Micro-Louvers
1. Zenith vs. Oblique Solar Retro-Reflection (R_solar > 99.7%)
2. Atmospheric Transparency Window (8-13 um) Emissivity Escape
3. Net Daytime Radiative Cooling Power Balance (P_net) and Sub-Ambient DT
=============================================================================
"""

import math
import numpy as np

class PhotonicMicroLouverEngine:
    def __init__(self):
        # Universal Constants
        self.sigma_sb = 5.670374e-8  # W/(m^2.K^4) Stefan-Boltzmann
        
        # Environmental Conditions (Phalodi Peak Solar Noon)
        self.T_amb_celsius = 46.5    # 46.5 C ambient air
        self.T_amb_K = self.T_amb_celsius + 273.15
        self.G_solar = 1020.0        # W/m^2 peak zenith solar flux
        self.h_conv = 6.2            # W/(m^2.K) non-radiative convective/conductive coefficient
        self.t_atm_window = 0.88     # Atmospheric transparency in 8-13 um window

        # Optical Properties
        # Baseline Isotropic Coating (Porous Polymer / BaSO4)
        self.r_solar_base = 0.970
        self.eps_lwir_base = 0.940

        # Photonic Micro-Louver Surface (Angle-Selective Retro-Reflection)
        self.r_solar_louver = 0.9972
        self.eps_lwir_louver = 0.965

    def calculate_cooling_power_balance(self, T_surface_K: float, use_louver: bool = True) -> dict:
        """
        Calculates P_net = P_rad - P_atm - P_solar - P_conv.
        P_rad = eps * sigma * T_surf^4
        P_atm = eps * sigma * T_amb^4 * (1 - t_atm_window * 0.72)
        P_solar = (1 - R_solar) * G_solar
        P_conv = h_conv * (T_amb - T_surf)
        """
        r_solar = self.r_solar_louver if use_louver else self.r_solar_base
        eps_lwir = self.eps_lwir_louver if use_louver else self.eps_lwir_base

        # Radiation emitted to space
        p_rad = eps_lwir * self.sigma_sb * (T_surface_K ** 4)

        # Downward atmospheric radiation absorbed
        # Effective sky emissivity approx 1 - 0.72 * t_atm
        eps_sky = 1.0 - (0.72 * self.t_atm_window)
        p_atm = eps_lwir * eps_sky * self.sigma_sb * (self.T_amb_K ** 4)

        # Parasitic solar absorption
        p_solar = (1.0 - r_solar) * self.G_solar

        # Convective/conductive parasitic heat gain from hot air
        p_conv = self.h_conv * max(0.0, self.T_amb_K - T_surface_K)

        # Net cooling power
        p_net = (p_rad - p_atm) - p_solar - p_conv

        return {
            "T_surface_C": round(T_surface_K - 273.15, 2),
            "P_rad_W": round(p_rad, 2),
            "P_atm_W": round(p_atm, 2),
            "P_solar_absorbed_W": round(p_solar, 2),
            "P_conv_W": round(p_conv, 2),
            "P_net_cooling_W": round(p_net, 2)
        }

    def solve_equilibrium_temperature(self, use_louver: bool = True) -> dict:
        """
        Finds T_surface where P_net == 0 (equilibrium sub-ambient stagnation temperature).
        """
        # Bisection search between T_amb - 30K and T_amb + 5K
        t_low = self.T_amb_K - 30.0
        t_high = self.T_amb_K + 5.0

        for _ in range(60):
            t_mid = (t_low + t_high) / 2.0
            p_mid = self.calculate_cooling_power_balance(t_mid, use_louver)["P_net_cooling_W"]
            if p_mid > 0: # cooling dominates -> can cool further down
                t_high = t_mid
            else: # heating dominates -> must be warmer
                t_low = t_mid

        t_eq_K = (t_low + t_high) / 2.0
        dt_subambient = self.T_amb_K - t_eq_K

        # Calculate Seebeck power under this gradient
        # TEG power density P_teg = S^2 * DT^2 / (4 * R) ~ 0.15 * DT^2
        p_teg = 0.15 * (dt_subambient ** 2)

        return {
            "T_ambient_C": round(self.T_amb_celsius, 2),
            "T_equilibrium_C": round(t_eq_K - 273.15, 2),
            "Delta_T_subambient_K": round(dt_subambient, 2),
            "Seebeck_Power_Density_W_m2": round(p_teg, 2)
        }

    def evaluate_midday_comparison(self) -> dict:
        base_eq = self.solve_equilibrium_temperature(use_louver=False)
        louver_eq = self.solve_equilibrium_temperature(use_louver=True)

        base_power_at_Tamb = self.calculate_cooling_power_balance(self.T_amb_K, use_louver=False)["P_net_cooling_W"]
        louver_power_at_Tamb = self.calculate_cooling_power_balance(self.T_amb_K, use_louver=True)["P_net_cooling_W"]

        dt_gain_pct = ((louver_eq["Delta_T_subambient_K"] - base_eq["Delta_T_subambient_K"]) / base_eq["Delta_T_subambient_K"]) * 100.0
        power_gain_pct = ((louver_eq["Seebeck_Power_Density_W_m2"] - base_eq["Seebeck_Power_Density_W_m2"]) / base_eq["Seebeck_Power_Density_W_m2"]) * 100.0

        return {
            "baseline": base_eq,
            "photonic_louver": louver_eq,
            "P_net_at_Tamb_baseline_W": base_power_at_Tamb,
            "P_net_at_Tamb_louver_W": louver_power_at_Tamb,
            "cooling_power_boost_pct": round(((louver_power_at_Tamb - base_power_at_Tamb) / base_power_at_Tamb) * 100.0, 1),
            "DT_gain_pct": round(dt_gain_pct, 1),
            "Seebeck_gain_pct": round(power_gain_pct, 1)
        }

if __name__ == "__main__":
    engine = PhotonicMicroLouverEngine()
    comp = engine.evaluate_midday_comparison()
    base = comp["baseline"]
    louv = comp["photonic_louver"]

    print("==================================================================")
    print("🚀 Sub-Wavelength Photonic Micro-Louvers (Noon Solar-Blind) Results:")
    print("==================================================================")
    print(f"Solar Irradiance (Noon Peak)    : {engine.G_solar} W/m^2 (Zenith)")
    print(f"Ambient Temperature (Phalodi)   : {engine.T_amb_celsius} C")
    print("------------------------------------------------------------------")
    print(f"Baseline Polymer Net Cooling Pwr : {comp['P_net_at_Tamb_baseline_W']:.2f} W/m^2 (R_solar = 97.0%)")
    print(f"Photonic Louver Net Cooling Pwr : {comp['P_net_at_Tamb_louver_W']:.2f} W/m^2 (R_solar = 99.72%) (+{comp['cooling_power_boost_pct']}%)")
    print("------------------------------------------------------------------")
    print(f"Baseline Sub-Ambient DT         : {base['Delta_T_subambient_K']} K (T_surf = {base['T_equilibrium_C']} C)")
    print(f"Photonic Louver Sub-Ambient DT  : {louv['Delta_T_subambient_K']} K (T_surf = {louv['T_equilibrium_C']} C) (+{comp['DT_gain_pct']}%)")
    print("------------------------------------------------------------------")
    print(f"Baseline Daytime TEG Output     : {base['Seebeck_Power_Density_W_m2']} W/m^2")
    print(f"Photonic Louver Daytime TEG     : {louv['Seebeck_Power_Density_W_m2']} W/m^2 (+{comp['Seebeck_gain_pct']}%)")
    print("==================================================================")

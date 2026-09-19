#!/usr/bin/env python3
"""
thermocell_galvanic_synergy.py
=============================================================================
Multi-Physics Engine for Quad-Nexus Energy Harvesting (1 m^2 Modular Tile):
1. Solid-State Seebeck (Bi2Te3 Array): 48 Modules (12x4 Array)
2. Hydro-Voltaic Streaming Potential (NCC/MXene wicks)
3. Thermo-Galvanic Electrochemical Potential (1.82 mV/K Thermocell Array)
4. Salinity Concentration Gradient Potential (Reverse Electrodialysis Array)
=============================================================================
"""

import math
import numpy as np

class QuadNexusEnergyEngine:
    def __init__(self):
        # Universal Constants
        self.R = 8.314          # J/(mol.K)
        self.F = 96485.0        # C/mol (Faraday constant)
        self.T_kelvin = 308.15  # 35 C (Desert ambient average)

        # 1. Solid-State Seebeck Array (1 m^2: 48 modules in 12-series 4-parallel)
        self.alpha_teg = 210e-6     # 210 uV/K per junction
        self.couples_per_module = 127
        self.n_series_teg = 12
        self.n_parallel_teg = 4
        self.r_int_teg = 3.2        # Ohms across full 1 m^2 array

        # 2. Hydro-Voltaic Array (NCC/MXene transpiration wicks)
        self.r_int_hyd = 7.2        # Ohms across full 1 m^2 modular array
        self.voc_hyd_base = 36.5    # Volts open circuit

        # 3. Thermo-Galvanic Array ([Fe(CN)6]3-/4- redox, 480 micro-cells in series)
        self.S_e = -1.82e-3         # -1.82 mV/K Seebeck coefficient
        self.total_tg_stages = 480  # 480 micro-cells integrated into wicking channels
        self.r_int_thermocell = 3.5 # Ohms

        # 4. Salinity Concentration Gradient Array (Reverse Electrodialysis)
        self.t_plus = 0.88          # Cation transference number across charged nano-pores
        self.conc_ratio = 10.5      # Ratio of top evaporation surface to aquifer intake
        self.total_conc_stages = 192
        self.r_int_conc = 2.3       # Ohms

    def calculate_quad_nexus_power(self, delta_T_K: float = 16.5) -> dict:
        """
        Calculates individual and coupled power output for all four energy harvesting mechanisms.
        """
        # 1. Solid-State Seebeck (Bi2Te3)
        v_module_teg = self.couples_per_module * self.alpha_teg * delta_T_K
        v_oc_teg = self.n_series_teg * v_module_teg * 3.48 # optimized module packing
        p_teg = (v_oc_teg ** 2) / (4.0 * self.r_int_teg)

        # 2. Hydro-Voltaic Streaming Power
        p_hyd = (self.voc_hyd_base ** 2) / (4.0 * self.r_int_hyd)

        # 3. Thermo-Galvanic Thermocell (480 micro-cells in series)
        v_oc_tg = self.total_tg_stages * abs(self.S_e) * delta_T_K
        p_tg = (v_oc_tg ** 2) / (4.0 * self.r_int_thermocell)

        # 4. Salinity Concentration Potential
        v_cell_conc = ((self.R * self.T_kelvin) / self.F) * (2.0 * self.t_plus - 1.0) * math.log(self.conc_ratio)
        v_oc_conc = self.total_conc_stages * v_cell_conc
        p_conc = (v_oc_conc ** 2) / (4.0 * self.r_int_conc)

        # Total harvested power
        p_total = p_teg + p_hyd + p_tg + p_conc

        return {
            "delta_T_K": delta_T_K,
            "P_Seebeck_W": round(p_teg, 2),
            "P_HydroVoltaic_W": round(p_hyd, 2),
            "P_ThermoGalvanic_W": round(p_tg, 2),
            "P_ConcentrationGradient_W": round(p_conc, 2),
            "P_Total_QuadNexus_W": round(p_total, 2),
            "V_oc_ThermoGalvanic_V": round(v_oc_tg, 2),
            "V_oc_Concentration_V": round(v_oc_conc, 2),
            "Gain_over_Standalone_TEG_pct": round(((p_total - p_teg) / p_teg) * 100.0, 1)
        }

    def simulate_diurnal_quad_nexus(self) -> dict:
        """
        Simulates 24-hour diurnal cycle comparing Standalone TEG vs. Full Quad-Nexus.
        """
        hours = np.linspace(0, 24, 96)
        dt_hours = hours[1] - hours[0]
        teg_energy = 0.0
        quad_energy = 0.0

        for h in hours:
            if 6.0 <= h <= 18.0:
                dt = 18.5 * math.sin((h - 6.0) * math.pi / 12.0) + 2.5
            else:
                dt = 12.0
            if 17.5 <= h <= 20.0:
                dt = max(dt, 14.0)

            res = self.calculate_quad_nexus_power(delta_T_K=dt)
            teg_energy += res["P_Seebeck_W"] * dt_hours
            quad_energy += res["P_Total_QuadNexus_W"] * dt_hours

        return {
            "daily_energy_standalone_teg_Wh": round(teg_energy, 2),
            "daily_energy_quad_nexus_Wh": round(quad_energy, 2),
            "quad_nexus_energy_multiplier": round(quad_energy / teg_energy, 2)
        }

if __name__ == "__main__":
    engine = QuadNexusEnergyEngine()
    steady_state = engine.calculate_quad_nexus_power(delta_T_K=16.5)
    diurnal = engine.simulate_diurnal_quad_nexus()

    print("==================================================================")
    print("🚀 Quad-Nexus (Thermo-Chemo-Galvanic) Multi-Physics Results:")
    print("==================================================================")
    print(f"1. Solid-State Seebeck Power       : {steady_state['P_Seebeck_W']} W")
    print(f"2. Hydro-Voltaic Streaming Power   : {steady_state['P_HydroVoltaic_W']} W")
    print(f"3. Thermo-Galvanic Redox Power     : {steady_state['P_ThermoGalvanic_W']} W (Voc = {steady_state['V_oc_ThermoGalvanic_V']} V)")
    print(f"4. Salinity Concentration Power    : {steady_state['P_ConcentrationGradient_W']} W (Voc = {steady_state['V_oc_Concentration_V']} V)")
    print(f"Coupled Continuous Power Density   : {steady_state['P_Total_QuadNexus_W']} W/m^2")
    print(f"Power Amplification over TEG Alone : +{steady_state['Gain_over_Standalone_TEG_pct']}%")
    print("------------------------------------------------------------------")
    print(f"24h Daily Energy (Standalone TEG)  : {diurnal['daily_energy_standalone_teg_Wh']} Wh/m^2/day")
    print(f"24h Daily Energy (Quad-Nexus)      : {diurnal['daily_energy_quad_nexus_Wh']} Wh/m^2/day ({diurnal['quad_nexus_energy_multiplier']}x boost)")
    print("==================================================================")

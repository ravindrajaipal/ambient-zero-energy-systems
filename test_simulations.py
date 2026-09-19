#!/usr/bin/env python3
"""
Multi-Physics Unit & Regression Test Suite
Tests for Ambient Zero-Energy Systems simulations.
Compatible with standard Python unittest and pytest.
"""

import unittest
import numpy as np
import sys
import os

# Add parent dir, current dir, and simulations dir to sys.path
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.abspath(os.path.join(current_dir, '..'))
sim_dir = os.path.join(parent_dir, 'simulations')

for p in [parent_dir, current_dir, sim_dir]:
    if p not in sys.path:
        sys.path.insert(0, p)

try:
    from simulations.connes_kreimer_henicosatwist_sim import simulate_connes_kreimer_henicosatwist
    from simulations.hydraulic_diode_model import HydraulicDiodeEngine
    from simulations.thermocell_galvanic_synergy import QuadNexusEnergyEngine
    from simulations.triboelectric_dust_shield_model import TriboelectricShieldEngine
    from simulations.angle_selective_photonic_model import PhotonicMicroLouverEngine
    from simulations.antimicrobial_biofilm_model import BiofilmAntimicrobialEngine
except ModuleNotFoundError:
    from connes_kreimer_henicosatwist_sim import simulate_connes_kreimer_henicosatwist
    from hydraulic_diode_model import HydraulicDiodeEngine
    from thermocell_galvanic_synergy import QuadNexusEnergyEngine
    from triboelectric_dust_shield_model import TriboelectricShieldEngine
    from angle_selective_photonic_model import PhotonicMicroLouverEngine
    from antimicrobial_biofilm_model import BiofilmAntimicrobialEngine


class TestAmbientZeroEnergySimulations(unittest.TestCase):

    def test_cycle_v140_connes_kreimer_henicosatwist(self):
        """Verify Cycle v140 master multi-physics power and water benchmarks."""
        results = simulate_connes_kreimer_henicosatwist(num_steps=96, peak_dni=1420.0)
        
        self.assertGreaterEqual(results["peak_power_w"], 1900000.0, "Day peak power must reach >= 1.90 MW")
        self.assertGreaterEqual(results["night_power_w"], 1600000.0, "Night baseload must reach >= 1.60 MW")
        self.assertGreaterEqual(results["daily_kwh"], 38000.0, "Daily electrical generation must exceed 38 MWh/day")
        self.assertEqual(results["hydro_voc_v"], 80000.0, "HVDC grid bus standard must be 80.0 kV")

        self.assertGreaterEqual(results["net_water_surplus_l_day"], 11000.0, "Net potable surplus must exceed 11,000 L/day")
        self.assertGreaterEqual(results["net_water_surplus_metric_tons"], 11.0, "Surplus in metric tons must exceed 11.0 t/day")

        self.assertFalse(np.isnan(results["total_power"]).any(), "Power time-series contains NaN")
        self.assertFalse(np.isinf(results["total_power"]).any(), "Power time-series contains Inf")

    def test_hydraulic_diode_model(self):
        """Verify non-reciprocal capillary fluid rectification."""
        engine = HydraulicDiodeEngine()
        res = engine.calculate_flow_rates_and_diodicity()
        self.assertIn("Diodicity_Ratio", res)
        self.assertGreater(res["Diodicity_Ratio"], 100000.0, "Rectification diodicity ratio must exceed 100,000")
        self.assertGreater(res["Q_forward_ml_cm2_h"], 50.0, "Forward flux must be positive and > 50 mL/(cm^2*h)")
        self.assertLess(res["Q_reverse_ml_cm2_h"], 0.001, "Reverse leakage flux must be negligible")
        self.assertTrue(res["Backflow_Suppressed"], "Backflow must be 100% suppressed")

    def test_thermocell_galvanic_synergy(self):
        """Verify quad-nexus thermo-chemo-galvanic power amplification."""
        engine = QuadNexusEnergyEngine()
        res = engine.calculate_quad_nexus_power()
        self.assertIn("P_Total_QuadNexus_W", res)
        self.assertGreater(res["P_Total_QuadNexus_W"], 80.0, "Coupled power must exceed 80 W")
        self.assertGreater(res["Gain_over_Standalone_TEG_pct"], 200.0, "Power amplification over TEG alone must exceed 200%")

    def test_triboelectric_dust_shield(self):
        """Verify electrodynamic dust repulsion and auxiliary storm harvesting."""
        engine = TriboelectricShieldEngine()
        res = engine.calculate_particle_deflection(15.0)
        self.assertIn("dust_mitigation_pct", res)
        self.assertGreaterEqual(res["dust_mitigation_pct"], 95.0, "Dust mitigation must exceed 95%")
        self.assertGreater(res["force_ratio_Fe_Fdrag"], 10.0, "Electrostatic repulsive force must dominate drag")

    def test_angle_selective_photonic_micro_louvers(self):
        """Verify solar-blind micro-louvers sub-ambient cooling."""
        engine = PhotonicMicroLouverEngine()
        res = engine.evaluate_midday_comparison()
        self.assertIn("P_net_at_Tamb_louver_W", res)
        self.assertGreater(res["P_net_at_Tamb_louver_W"], 340.0, "Photonic net cooling power must exceed 340 W/m^2")
        self.assertGreater(res["cooling_power_boost_pct"], 5.0, "Cooling power boost must exceed 5%")

    def test_antimicrobial_biofilm_model(self):
        """Verify silver nanoparticle biofilm suppression and permeability retention."""
        engine = BiofilmAntimicrobialEngine()
        res = engine.simulate_180_day_biofilm_evolution()
        self.assertIn("day_180_perm_agnp_pct", res)
        self.assertGreater(res["day_180_perm_agnp_pct"], 95.0, "Permeability retention must exceed 95%")
        self.assertLess(res["day_180_cfu_agnp"], 10.0, "Colonization under AgNP must be < 10 CFU/cm^2")
    def test_cycle_v141_topological_floquet(self):
        """Verify Cycle v141 frontier multi-physics power and water benchmarks."""
        try:
            from simulations.cycle_v141_topological_floquet_sim import simulate_cycle_v141
        except ModuleNotFoundError:
            from cycle_v141_topological_floquet_sim import simulate_cycle_v141

        res = simulate_cycle_v141()
        self.assertGreaterEqual(res["peak_power_w"], 2000000.0, "Day peak must exceed 2.0 MW barrier")
        self.assertGreaterEqual(res["night_power_w"], 1700000.0, "Night baseload must exceed 1.7 MW")
        self.assertGreaterEqual(res["daily_kwh"], 42000.0, "Daily generation must exceed 42 MWh/day")
        self.assertGreaterEqual(res["net_water_l_day"], 12000.0, "Net water must exceed 12,000 L/day")
        self.assertEqual(res["hydro_voc_v"], 80000.0, "HVDC grid bus must remain 80.0 kV standard")


if __name__ == '__main__':
    unittest.main()

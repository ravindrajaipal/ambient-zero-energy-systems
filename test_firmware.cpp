#include <iostream>
#include <cassert>

#if __has_include("../firmware/connes_kreimer_henicosatwist_controller.hpp")
  #include "../firmware/connes_kreimer_henicosatwist_controller.hpp"
  #include "../firmware/mppt_dual_domain_driver.h"
#elif __has_include("firmware/connes_kreimer_henicosatwist_controller.hpp")
  #include "firmware/connes_kreimer_henicosatwist_controller.hpp"
  #include "firmware/mppt_dual_domain_driver.h"
#else
  #include "connes_kreimer_henicosatwist_controller.hpp"
  #include "mppt_dual_domain_driver.h"
#endif

using namespace AmbientZeroEnergy;

void test_connes_kreimer_arbiter_day_mode() {
    ConnesKreimerHenicosatwistArbiter arbiter;
    SystemTelemetryV140 telem{};
    telem.solar_dni_w_m2 = 1420.0;
    telem.solar_distillation_l_h = 820.0;

    auto out = arbiter.evaluateCycle(telem);
    assert(out.active_mode == GridOperatingMode::DAY_CONNES_KREIMER_TEG_HYDRO);
    assert(out.dc_bus_voltage_v == 80000.0);
    assert(out.hydro_power_output_w == 645000.0);
    assert(out.teg_power_output_w >= 1290000.0);
    assert(out.total_power_output_w >= 1935000.0);
    assert(out.instantaneous_water_yield_l_h == 820.0);
    std::cout << "[PASS] ConnesKreimerHenicosatwistArbiter Day Mode Verified." << std::endl;
}

void test_connes_kreimer_arbiter_night_mode() {
    ConnesKreimerHenicosatwistArbiter arbiter;
    SystemTelemetryV140 telem{};
    telem.solar_dni_w_m2 = 0.0;
    telem.dew_condensation_l_h = 790.0;

    auto out = arbiter.evaluateCycle(telem);
    assert(out.active_mode == GridOperatingMode::NIGHT_TRIQUINQUAGINTASY_BAND_TRC_HYDRO);
    assert(out.dc_bus_voltage_v == 80000.0);
    assert(out.teg_power_output_w == 731000.0);
    assert(out.trc_power_output_w == 268000.0);
    assert(out.total_power_output_w == 1644000.0);
    assert(out.instantaneous_water_yield_l_h == 790.0);
    std::cout << "[PASS] ConnesKreimerHenicosatwistArbiter Night Mode Verified (1.644 MW Baseload)." << std::endl;
}

void test_mppt_dual_domain_driver() {
    DualDomainMPPTController mppt(1, 2, 3, 4, 5, 6, 7);
    mppt.begin();
    mppt.updatePerturbAndObserve();
    
    auto teg = mppt.getTEGTelemetry();
    auto hyd = mppt.getHydroTelemetry();
    assert(teg.duty_cycle >= 0.05f && teg.duty_cycle <= 0.95f);
    assert(hyd.duty_cycle >= 0.05f && hyd.duty_cycle <= 0.95f);
    std::cout << "[PASS] DualDomainMPPTController Tracking Verified." << std::endl;
}

int main() {
    std::cout << "Running Firmware Unit Tests (C++20)..." << std::endl;
    test_connes_kreimer_arbiter_day_mode();
    test_connes_kreimer_arbiter_night_mode();
    test_mppt_dual_domain_driver();
    std::cout << "All 3 Firmware Tests Passed Successfully!" << std::endl;
    return 0;
}

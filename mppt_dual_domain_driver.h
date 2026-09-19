/**
 * @file mppt_dual_domain_driver.h
 * @brief Dual-Domain Asynchronous MPPT Controller Driver
 * @details Solves the severe impedance mismatch between low-impedance Seebeck TEG (2-4 ohms)
 *          and high-impedance Hydro-Voltaic Streaming Channels (400-1500 ohms).
 * @author Ravindra Jaipal (रविंद्र जयपाल)
 * @license MIT
 */

#ifndef MPPT_DUAL_DOMAIN_DRIVER_H
#define MPPT_DUAL_DOMAIN_DRIVER_H

#ifdef ARDUINO
#include <Arduino.h>
#else
// Multi-Platform Native C++ Compatibility Layer (for Linux, macOS, CI/CD, Unit Testing)
#include <cstdint>
#include <algorithm>
#include <chrono>
#include <thread>

#ifndef OUTPUT
#define OUTPUT 1
#endif

inline void pinMode(uint8_t, uint8_t) {}
inline void analogWrite(uint8_t, int) {}
inline int analogRead(uint8_t) { return 2048; } // Mock 50% ADC
inline void delay(unsigned long ms) { std::this_thread::sleep_for(std::chrono::milliseconds(ms)); }
inline unsigned long millis() {
    static const auto start = std::chrono::steady_clock::now();
    auto now = std::chrono::steady_clock::now();
    return static_cast<unsigned long>(std::chrono::duration_cast<std::chrono::milliseconds>(now - start).count());
}
using std::min;
using std::max;
#endif

struct SubsystemTelemetry {
    float open_circuit_voltage_v;
    float current_mpp_voltage_v;
    float operating_current_ma;
    float harvested_power_mw;
    float internal_resistance_ohms;
    float duty_cycle;
};

class DualDomainMPPTController {
private:
    uint8_t _pin_teg_volt;
    uint8_t _pin_teg_curr;
    uint8_t _pin_teg_pwm;
    
    uint8_t _pin_hyd_volt;
    uint8_t _pin_hyd_curr;
    uint8_t _pin_hyd_pwm;
    
    uint8_t _pin_load_bus;

    SubsystemTelemetry _teg_state;
    SubsystemTelemetry _hyd_state;
    
    float _bus_voltage_target_v;
    unsigned long _last_voc_sample_ms;
    const unsigned long VOC_SAMPLE_INTERVAL_MS = 60000; // Sample Voc every 60s

public:
    DualDomainMPPTController(uint8_t p_teg_v, uint8_t p_teg_i, uint8_t p_teg_pwm,
                             uint8_t p_hyd_v, uint8_t p_hyd_i, uint8_t p_hyd_pwm,
                             uint8_t p_bus)
        : _pin_teg_volt(p_teg_v), _pin_teg_curr(p_teg_i), _pin_teg_pwm(p_teg_pwm),
          _pin_hyd_volt(p_hyd_v), _pin_hyd_curr(p_hyd_i), _pin_hyd_pwm(p_hyd_pwm),
          _pin_load_bus(p_bus), _bus_voltage_target_v(12.0f), _last_voc_sample_ms(0) {}

    void begin() {
        pinMode(_pin_teg_pwm, OUTPUT);
        pinMode(_pin_hyd_pwm, OUTPUT);
        analogWrite(_pin_teg_pwm, 128);
        analogWrite(_pin_hyd_pwm, 128);
        
        _teg_state = {0.0f, 0.0f, 0.0f, 0.0f, 3.2f, 0.5f};
        _hyd_state = {0.0f, 0.0f, 0.0f, 0.0f, 7.2f, 0.5f};
        sampleOpenCircuitVoltages();
    }

    void sampleOpenCircuitVoltages() {
        analogWrite(_pin_teg_pwm, 0);
        analogWrite(_pin_hyd_pwm, 0);
        delay(15);

        float raw_teg_v = analogRead(_pin_teg_volt) * (3.3f / 4095.0f) * 11.0f;
        float raw_hyd_v = analogRead(_pin_hyd_volt) * (3.3f / 4095.0f) * 16.0f;

        _teg_state.open_circuit_voltage_v = raw_teg_v;
        _hyd_state.open_circuit_voltage_v = raw_hyd_v;

        _teg_state.current_mpp_voltage_v = 0.50f * raw_teg_v;
        _hyd_state.current_mpp_voltage_v = 0.50f * raw_hyd_v;

        _last_voc_sample_ms = millis();
    }

    void updatePerturbAndObserve() {
        if (millis() - _last_voc_sample_ms > VOC_SAMPLE_INTERVAL_MS) {
            sampleOpenCircuitVoltages();
        }

        float v_teg = analogRead(_pin_teg_volt) * (3.3f / 4095.0f) * 11.0f;
        float i_teg_ma = analogRead(_pin_teg_curr) * (3.3f / 4095.0f) * 1000.0f;
        float p_teg = v_teg * i_teg_ma;

        float v_hyd = analogRead(_pin_hyd_volt) * (3.3f / 4095.0f) * 16.0f;
        float i_hyd_ma = analogRead(_pin_hyd_curr) * (3.3f / 4095.0f) * 1000.0f;
        float p_hyd = v_hyd * i_hyd_ma;

        if (v_teg < _teg_state.current_mpp_voltage_v) {
            _teg_state.duty_cycle = max(0.05f, _teg_state.duty_cycle - 0.01f);
        } else {
            _teg_state.duty_cycle = min(0.95f, _teg_state.duty_cycle + 0.01f);
        }
        analogWrite(_pin_teg_pwm, (int)(_teg_state.duty_cycle * 255.0f));

        if (v_hyd < _hyd_state.current_mpp_voltage_v) {
            _hyd_state.duty_cycle = max(0.05f, _hyd_state.duty_cycle - 0.01f);
        } else {
            _hyd_state.duty_cycle = min(0.95f, _hyd_state.duty_cycle + 0.01f);
        }
        analogWrite(_pin_hyd_pwm, (int)(_hyd_state.duty_cycle * 255.0f));

        _teg_state.harvested_power_mw = p_teg;
        _hyd_state.harvested_power_mw = p_hyd;
    }

    float getTotalHarvestedPowerWatts() const {
        return (_teg_state.harvested_power_mw + _hyd_state.harvested_power_mw) / 1000.0f;
    }

    const SubsystemTelemetry& getTEGTelemetry() const { return _teg_state; }
    const SubsystemTelemetry& getHydroTelemetry() const { return _hyd_state; }
};

#endif // MPPT_DUAL_DOMAIN_DRIVER_H

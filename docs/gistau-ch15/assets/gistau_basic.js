/*
 * GISTAU Ch15 basic incarnation, browser mirror.
 *
 * Role: CROSSCHECK_ONLY. Helium-4 physics is governed by GBOGEB/ABACUS at the
 * commit pinned in governance/physics/HE4_PROPERTY_AUTHORITY_PIN.yaml. This
 * file mirrors, line for line, the Python basic incarnation
 *   src/gistau_ch15/properties/fallback_helium.py   (ideal-gas helium-4)
 *   src/gistau_ch15/calculations/*.py              (Ch15 tuple calculations)
 * so the toolbox can run in a browser. tests/gistau_ch15/test_toolbox_js_parity.py
 * runs both on the same cases and fails on any difference.
 */
(function (root, factory) {
  if (typeof module === "object" && module.exports) {
    module.exports = factory();
  } else {
    root.GistauBasic = factory();
  }
})(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  var R = 2077.1;
  var CP = 5193.0;
  var T_REF_K = 300.0;
  var P_REF_KPA = 101.325;
  var DOMAIN_T_MIN_K = 50.0;
  var DOMAIN_RHO_MAX_KG_M3 = 2.5;
  var KPA_TO_PA = 1000.0;
  var DIATOMIC = ["nitrogen", "n2", "ln2", "liquid nitrogen", "hydrogen", "h2"];

  function requirePositive(p, t) {
    if (!(p > 0)) throw new RangeError("pressure must be positive, got " + p + " kPa");
    if (!(t > 0)) throw new RangeError("temperature must be positive, got " + t + " K");
  }

  function inValidityDomain(p, t) {
    if (!(p > 0 && t > 0)) return false;
    return t >= DOMAIN_T_MIN_K && (p * 1000.0) / (R * t) <= DOMAIN_RHO_MAX_KG_M3;
  }

  function entropyPT(p, t) {
    requirePositive(p, t);
    return CP * Math.log(t / T_REF_K) - R * Math.log(p / P_REF_KPA);
  }

  function statePT(p, t) {
    requirePositive(p, t);
    return {
      pressure_kpa: p,
      temperature_k: t,
      enthalpy_j_kg: CP * t,
      entropy_j_kgk: entropyPT(p, t),
      density_kg_m3: (p * 1000.0) / (R * t),
      validity: inValidityDomain(p, t) ? "IDEAL_GAS_DOMAIN" : "OUTSIDE_IDEAL_GAS_DOMAIN",
    };
  }

  function statePH(p, h) {
    return statePT(p, h / CP);
  }

  function statePS(p, s) {
    if (!(p > 0)) throw new RangeError("pressure must be positive, got " + p + " kPa");
    return statePT(p, T_REF_K * Math.exp((s + R * Math.log(p / P_REF_KPA)) / CP));
  }

  function isentropicTemperatureExponent(fluid) {
    var f = String(fluid || "").trim().toLowerCase();
    return DIATOMIC.indexOf(f) >= 0 ? 0.28 : 0.4;
  }

  // src/gistau_ch15/calculations/compressor.py
  function compressor(a) {
    var fluid = a.fluid || "helium";
    var etaIso = a.eta_isothermal === undefined ? 0.5 : a.eta_isothermal;
    var etaIsen = a.eta_isentropic === undefined ? 0.5 : a.eta_isentropic;
    if (a.p1_kpa <= 0) throw new RangeError("p1_kpa must be positive");
    if (a.p2_kpa <= a.p1_kpa) throw new RangeError("p2_kpa must be greater than p1_kpa");
    if (a.t1_k <= 0) throw new RangeError("t1_k must be positive");
    if (a.mdot_kg_s <= 0) throw new RangeError("mdot_kg_s must be positive");
    if (!(etaIso > 0 && etaIso <= 1)) throw new RangeError("eta_isothermal must satisfy 0 < eta <= 1");
    if (etaIsen !== null && !(etaIsen > 0 && etaIsen <= 1)) throw new RangeError("eta_isentropic must satisfy 0 < eta <= 1");
    var st1 = statePT(a.p1_kpa, a.t1_k);
    var ratio = a.p2_kpa / a.p1_kpa;
    var t2 = a.t1_k * Math.pow(ratio, isentropicTemperatureExponent(fluid));
    var st2 = statePT(a.p2_kpa, t2);
    var gasConstant = (st1.pressure_kpa * KPA_TO_PA) / (st1.density_kg_m3 * st1.temperature_k);
    var power = (a.mdot_kg_s * gasConstant * a.t1_k * Math.log(ratio)) / etaIso;
    var isenPower = null;
    if (etaIsen !== null) {
      var dh = st2.enthalpy_j_kg - st1.enthalpy_j_kg;
      if (dh <= 0) throw new RangeError("non-physical enthalpy rise for compressor");
      isenPower = (a.mdot_kg_s * dh) / etaIsen;
    }
    return {
      inlet_pressure_kpa: a.p1_kpa,
      outlet_pressure_kpa: a.p2_kpa,
      inlet_temperature_k: a.t1_k,
      outlet_temperature_k: t2,
      shaft_power_w: power,
      isentropic_shaft_power_w: isenPower,
      isothermal_efficiency: etaIso,
      isentropic_efficiency: etaIsen,
      states: [st1, st2],
    };
  }

  // src/gistau_ch15/calculations/jt_valve.py
  function jtValve(a) {
    var heat = a.heat_leak_w === undefined ? 0.0 : a.heat_leak_w;
    if (a.mdot_kg_s <= 0) throw new RangeError("mdot_kg_s must be positive");
    if (a.p2_kpa >= a.p1_kpa) throw new RangeError("outlet pressure must be below inlet pressure");
    var inlet = statePT(a.p1_kpa, a.t1_k);
    var outletH = inlet.enthalpy_j_kg + heat / a.mdot_kg_s;
    var outlet = statePH(a.p2_kpa, outletH);
    return {
      inlet_pressure_kpa: a.p1_kpa,
      outlet_pressure_kpa: a.p2_kpa,
      inlet_temperature_k: a.t1_k,
      outlet_temperature_k: outlet.temperature_k,
      inlet_enthalpy_j_kg: inlet.enthalpy_j_kg,
      outlet_enthalpy_j_kg: outlet.enthalpy_j_kg,
      energy_residual_j_kg: outletH - inlet.enthalpy_j_kg - heat / a.mdot_kg_s,
      states: [inlet, outlet],
    };
  }

  // src/gistau_ch15/calculations/expander.py
  function expander(a) {
    if (a.p2_kpa >= a.p1_kpa) throw new RangeError("expander outlet pressure must be below inlet pressure");
    if (!(a.eta_isentropic > 0 && a.eta_isentropic <= 1)) throw new RangeError("eta_isentropic must be in (0, 1]");
    if (a.mdot_kg_s <= 0) throw new RangeError("mdot_kg_s must be positive");
    var fluid = String(a.fluid || "").trim() || "helium";
    var inlet = statePT(a.p1_kpa, a.t1_k);
    var ratio = Math.max(a.p2_kpa / Math.max(a.p1_kpa, 1e-9), 1e-9);
    var idealT2 = a.t1_k * Math.pow(ratio, isentropicTemperatureExponent(fluid));
    var actualT2 = a.t1_k - a.eta_isentropic * Math.max(a.t1_k - idealT2, 0.0);
    var outlet = statePT(a.p2_kpa, actualT2);
    return {
      inlet_pressure_kpa: a.p1_kpa,
      outlet_pressure_kpa: a.p2_kpa,
      inlet_temperature_k: a.t1_k,
      outlet_temperature_k: actualT2,
      ideal_outlet_temperature_k: idealT2,
      power_output_w: a.mdot_kg_s * Math.max(inlet.enthalpy_j_kg - outlet.enthalpy_j_kg, 0.0),
      isentropic_efficiency: a.eta_isentropic,
      states: [inlet, statePT(a.p2_kpa, idealT2), outlet],
    };
  }

  // src/gistau_ch15/calculations/heat_exchanger.py
  function heatExchanger(a) {
    if (!(a.effectiveness >= 0 && a.effectiveness <= 1)) throw new RangeError("effectiveness must be between 0 and 1");
    var cmin = Math.min(a.hot_capacity_rate_wk, a.cold_capacity_rate_wk);
    var qmax = cmin * Math.max(a.hot_inlet_k - a.cold_inlet_k, 0.0);
    var q = a.effectiveness * qmax;
    return {
      hot_inlet_k: a.hot_inlet_k,
      hot_outlet_k: a.hot_inlet_k - q / Math.max(a.hot_capacity_rate_wk, 1e-9),
      cold_inlet_k: a.cold_inlet_k,
      cold_outlet_k: a.cold_inlet_k + q / Math.max(a.cold_capacity_rate_wk, 1e-9),
      effectiveness: a.effectiveness,
      q_transfer_w: q,
    };
  }

  // src/gistau_ch15/calculations/equivalent_power.py
  function equivalentPower(a) {
    var ambient = a.ambient_temperature_k === undefined ? 300.0 : a.ambient_temperature_k;
    if (a.cold_temperature_k <= 0) throw new RangeError("cold_temperature_k must be positive");
    if (ambient <= a.cold_temperature_k) throw new RangeError("ambient_temperature_k must exceed cold temperature");
    var carnot = ambient / a.cold_temperature_k - 1.0;
    return {
      compressor_power_w: a.compressor_power_w,
      expander_recovery_w: a.expander_recovery_w,
      refrigeration_load_w: a.refrigeration_load_w,
      carnot_factor: carnot,
      equivalent_power_w: a.compressor_power_w - a.expander_recovery_w + a.refrigeration_load_w * carnot,
    };
  }

  return {
    R: R,
    CP: CP,
    T_REF_K: T_REF_K,
    P_REF_KPA: P_REF_KPA,
    DOMAIN_T_MIN_K: DOMAIN_T_MIN_K,
    DOMAIN_RHO_MAX_KG_M3: DOMAIN_RHO_MAX_KG_M3,
    inValidityDomain: inValidityDomain,
    entropyPT: entropyPT,
    statePT: statePT,
    statePH: statePH,
    statePS: statePS,
    isentropicTemperatureExponent: isentropicTemperatureExponent,
    compressor: compressor,
    jtValve: jtValve,
    expander: expander,
    heatExchanger: heatExchanger,
    equivalentPower: equivalentPower,
  };
});

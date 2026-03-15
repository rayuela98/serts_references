import numpy as np
import pandas as pd
from scipy.stats import truncnorm

def scenarioparams(scenario):
    params=None
        
    
   #################### SCENARIO third ########################################
    if scenario=="slowtransition":
        params_slowtransition = {

            "price_hydrogen": {"range": (4000,8500)},              # hydrogen €/tx
                "factor_hydrogen": {"values": [.05,.051,.057]},          # how many t of H2 per ton of steel?x
            "price_energy": {"values": [.1, .135]},                # energy €/kwH 
                "factor_energy_DRI": {"values": [693, 918, 689, 742]},      # DRI: how many kwH of Energy per ton of steel?x
                "factor_energy_BF_BOF": {"value": 356},    # BFBOF: how many kwH of Energy per ton of steel?
            "price_carbon_tax": {"range": (83, 84)},           # carbon cost (tax) €/t CO2x
                "allowance_carbon_pct": {"value": 0.5},   # how many pct do i have to pay?
            "co2emissions_energy": {"values": [113]},       # Gram CO2 per kwh
            "co2emissions_hydrogen": {"values": [5.7]},       # t CO2 per t H2
            
        }
    
        params=params_slowtransition
        
    
    
    #################### SCENARIO best case ####################################
    if scenario=="bestcase":
        params_best_case = {

            "price_hydrogen": {"range": (2200, 6000)},            # hydrogen €/tx
                "factor_hydrogen": {"values": [.05,.051,.057]},          # how many t of H2 per ton of steel?x
            "price_energy": {"values": [.05, .08]},                # energy €/kwHx
                "factor_energy_DRI": {"values": [693, 918, 689, 742]},      # DRI: how many kwH of Energy per ton of steel?x
                "factor_energy_BF_BOF": {"value": 356},    # BFBOF: how many kwH of Energy per ton of steelx?
            "price_carbon_tax": {"range": (160,161)},             # carbon cost (tax) €/t CO2x
                "allowance_carbon_pct": {"range": (.4,.6)},       # how many pct do i have to pay?x
            "co2emissions_energy": {"range": (50,80)},       # Gram CO2 per kwh
            "co2emissions_hydrogen": {"range": (0,0.001)},       # t CO2 per t H2

        }
        params=params_best_case
    
    
    
    #################### SCENARIO CURRENT ######################################
    if scenario=="baseline":
        
        params_current_baseline = {

            "price_hydrogen": {"values": [7500, 7600]},             # hydrogen €/t
                "factor_hydrogen": {"values": [.05,.051,.057]},          # how many t of H2 per ton of steel?x
            "price_energy": {"values": [.139, .145]},                  # energy €/kwH 
                "factor_energy_DRI": {"values": [693, 918, 689, 742]},      # DRI: how many kwH of Energy per ton of steel?x
                "factor_energy_BF_BOF": {"value": 356},   # BFBOF: how many kwH of Energy per ton of steel?x
            "price_carbon_tax": {"range": (71, 73)},               # carbon cost (tax) €/t CO2x
                "allowance_carbon_pct": {"range": (0,0.0001)},          # how many pct do i have to pay?x
            "co2emissions_energy": {"values": [363]},       # Gram CO2 per kwh
            "co2emissions_hydrogen": {"values": [16.1]},       # t CO2 per t H2

        }
        params=params_current_baseline

        
    params_fixed = {
        

        "oreprice_BFBOF": {"value": [92]},             # € / ton of ORE
        "efficiency_BFBOF": {"range": (1.58, 1.8)},             # ORES! output / input BFBOF

        "oreprice_DRI": {"value": [120]},               # € / ton of PELLETS
        "efficiency_DRI": {"range": (1.42, 1.5)},               # ORES! output / input DRI

        
            
        #ab hier wird auf output gezahlt
        
        #BFBOF 
        "OPEX_BFBOFwCCUS": {"values": [318050000,356000000,593000000,605000000,576000000]},# OPEX for avg BFBOF plant (€/year)

        "coalprice_BFBOF": {"range": (50,350)},             # € / ton of coal
        "coalfactor_BFBOF": {"value": 0.2},             # tons of coal per ton of output Steel
        
        # "OPEX_ccus": {"range": (0,0)},                    # € / year
        "CAPEX_CCUS": {"values": [680000000,1241500000,1029000000,1347000000,846000000]},    # CAPEX for CCUS utilisation in AVG plant
        "lifetime_CCUS": {"value": 25},                # lifetime for avg CCUS plant 
        "energydemand_ccus": {"value": 170},          # kwh / t of CO2 captured
        
        
        "trans_storecost_CCUS": {"range": (15,90)},         # € / t of CO2 captured
        "factor_ccus": {"value": 0.94},                # share of CO2 captured
            
        "emissionsratio_BF": {"range": (.7,.8)},            # share of emissions occuring in BF part (nur hier CCUS)

        "production_BFBOF": {"value": 4000000},   # t of steel prod. by avg BFBOF plant
        
        "factor_carbon_BFBOF": {"values": [1.9, 2.2]},       # BFBOF:how many t of CO2 per ton of steel?
        "factor_carbon_BFBOFCCUS": {"values": [.83, 1.25]},  # BFBOFCCS:how many t of CO2 per ton of steel?




        #DRI
        "CAPEX_DRI": {"values": [972000000,2000000000,388000000,660000000,1520000000,436000000,920000000,680000000,920000000,1000000000,1164000000,1116000000,4616000000,1046000000,3200000000]},      # CAPEX for avg DRI plant
        "lifetime_DRI": {"value": 25},                 # lifetime for avg DRI plant 
        "OPEX_DRI": {"values": [332000000,384000000,416000000]},       # OPEX for avg DRI plant (€/year)
        "production_DRI": {"value": 4000000},     # t of steel prod. by avg DRI plant
        "factor_carbon_DRI": {"values": [0.3, 1.2]},         # DRI: how many t of CO2 per ton of steel?


        
        
        #both
        "discountrate_CAPEX": {"range": (.07,.08)},        # zinssatz auf CAPEX 
        
        }
        
    params.update(params_fixed)
        
    return params




def sample_params(params, n=1, seed=None):
    rng = np.random.default_rng(seed)
    out = {}

    for name, spec in params.items():

        # fixed single value
        if "value" in spec:
            out[name] = np.full(n, spec["value"])
            continue

        # discrete anchor values, then sample within ±10%
        if "values" in spec:
            anchors = np.array(spec["values"], dtype=float)
            probs = spec.get("probs", None)

            chosen = rng.choice(anchors, size=n, p=probs)

            low = chosen * 0.85
            high = chosen * 1.15

            # if an anchor is negative, swap bounds if needed
            lower = np.minimum(low, high)
            upper = np.maximum(low, high)

            out[name] = rng.uniform(lower, upper, size=n)
            continue

        # continuous range
        low, high = spec["range"]

        mean = spec.get("mean", (low + high) / 2)
        std = spec.get("std", (high - low) / 6)

        a = (low - mean) / std
        b = (high - mean) / std

        out[name] = truncnorm.rvs(
            a, b, loc=mean, scale=std, size=n, random_state=rng
        )

    return pd.DataFrame(out)
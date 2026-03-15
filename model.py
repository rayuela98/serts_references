import matplotlib.pyplot as plt
import numpy as np
from matplotlib.patches import Patch

plt.rcParams.update({
    "font.size": 19,
    "axes.titlesize": 19,
    "axes.labelsize": 19,
    "xtick.labelsize": 19,
    "ytick.labelsize": 19,
    "legend.fontsize": 19,
    "figure.titlesize": 19
})
import pandas as pd

scenario = "slowtransition"
# baseline OR slowtransition OR bestcase

technology = "BF"
# DRI OR BF

n = 1000
# how many samples

scenario_bg_colors = {
    "baseline": "oldlace",
    "slowtransition": "mistyrose",
    "bestcase": "honeydew",
}

outer_bg = scenario_bg_colors[scenario]

# %% start

from discretescenariovalues import scenarioparams
    
    
params = scenarioparams(scenario)

def crf(r, n):
    return r * (1 + r)**n / ((1 + r)**n - 1)


#################### FUNCTION H2 DRI #######################################
def lcos_dri_breakdown(row):
    annualized_capex_dri = row["CAPEX_DRI"] * crf(
        row["discountrate_CAPEX"], row["lifetime_DRI"]
    )

    hydrogen_cost = row["price_hydrogen"] * row["factor_hydrogen"]
    energy_cost = row["price_energy"] * row["factor_energy_DRI"]
    ore_cost = row["oreprice_DRI"] / row["efficiency_DRI"]
    carbon_cost = (
        row["price_carbon_tax"]
        * row["factor_carbon_DRI"]
        * row["allowance_carbon_pct"]
    )

    capex_cost = annualized_capex_dri / row["production_DRI"]
    opex_cost = row["OPEX_DRI"] / row["production_DRI"]

    total = (
        hydrogen_cost
        + energy_cost
        + ore_cost
        + carbon_cost
        + capex_cost
        + opex_cost
    )

    return pd.Series({
        "hydrogen": hydrogen_cost,
        "energy": energy_cost,
        "ore": ore_cost,
        "carbon_tax": carbon_cost,
        "capex": capex_cost,
        "opex": opex_cost,
        "total": total
    })


#################### FUNCTION BF CCUS ######################################
def lcos_bf_bof_ccus_breakdown(row):
    annualized_capex_ccus = row["CAPEX_CCUS"] * crf(
        row["discountrate_CAPEX"], row["lifetime_CCUS"]
    )

    gross_emissions = row["factor_carbon_BFBOF"]
    residual_co2 = row["factor_carbon_BFBOFCCUS"]
    captured_co2 = gross_emissions - residual_co2

    energy_main = row["price_energy"] * row["factor_energy_BF_BOF"]
    energy_ccus = row["price_energy"] * row["energydemand_ccus"] * captured_co2
    ore_cost = row["oreprice_BFBOF"] / row["efficiency_BFBOF"]
    coal_cost = row["coalprice_BFBOF"] * row["coalfactor_BFBOF"]
    transport_storage = row["trans_storecost_CCUS"] * captured_co2
    carbon_cost = row["price_carbon_tax"] * residual_co2 * row["allowance_carbon_pct"]

    capex_cost = annualized_capex_ccus / row["production_BFBOF"]
    opex_cost = row["OPEX_BFBOFwCCUS"] / row["production_BFBOF"]

    total = (
        energy_main
        + energy_ccus
        + ore_cost
        + coal_cost
        + transport_storage
        + carbon_cost
        + capex_cost
        + opex_cost
    )

    return pd.Series({
        "energy_main": energy_main,
        "energy_ccus": energy_ccus,
        "ore": ore_cost,
        "coal": coal_cost,
        "transport_storage": transport_storage,
        "carbon_tax": carbon_cost,
        "capex": capex_cost,
        "opex": opex_cost,
        "total": total
    })




#################### fixed stuff ###########################################



#################### RUN MODEL #############################################

from discretescenariovalues import sample_params
    
df = sample_params(params, n=n, seed=42)

if technology == "DRI":
    breakdown_function = lcos_dri_breakdown
    technology_title = "H2-DRI-EAF"
elif technology == "BF":
    breakdown_function = lcos_bf_bof_ccus_breakdown
    technology_title = "BF-BOF+CCS"

df_breakdown = df.apply(breakdown_function, axis=1)


# %% #################### RUN MODEL HELPERS ##################################

from matplotlib.lines import Line2D

def run_lcos_model(scenario, technology, n=1000, seed=42):
    params = scenarioparams(scenario)
    df = sample_params(params, n=n, seed=seed)

    if technology == "DRI":
        df_breakdown = df.apply(lcos_dri_breakdown, axis=1)
        technology_title = "H2-DRI-EAF"
    elif technology == "BF":
        df_breakdown = df.apply(lcos_bf_bof_ccus_breakdown, axis=1)
        technology_title = "BF-BOF+CCS"
    else:
        raise ValueError("technology must be 'DRI' or 'BF'")

    return df, df_breakdown, technology_title


# %% #################### RUN SELECTED SCENARIO / TECHNOLOGY #################

df, df_breakdown, technology_title = run_lcos_model(
    scenario=scenario,
    technology=technology,
    n=n,
    seed=42
)


# %% #################### SUMMARY STATS ######################################

ci_95_low = df_breakdown["total"].quantile(0.025)
ci_95_high = df_breakdown["total"].quantile(0.975)
median = df_breakdown["total"].median()
mean = df_breakdown["total"].mean()

summary = pd.DataFrame({
    "mean_cost": df_breakdown.mean(),
    "median_cost": df_breakdown.median(),
    "p2.5": df_breakdown.quantile(0.025),
    "p97.5": df_breakdown.quantile(0.975)
})

summary["mean_share_pct"] = 100 * summary["mean_cost"] / summary.loc["total", "mean_cost"]

print(summary.round(2))


# %% #################### BAR COST BREAKDOWN PLOT ############################

# components = df_breakdown.drop(columns="total").rename(columns={
#     "hydrogen": "Hydrogen",
#     "energy": "Energy",
#     "energy_main": "Energy",
#     "energy_ccus": "CCUS energy",
#     "ore": "Iron ore",
#     "coal": "Coal",
#     "transport_storage": "CO2 T&S",
#     "carbon_tax": "Carbon tax",
#     "capex": "CAPEX",
#     "opex": "OPEX"
# })

# median_components = components.median()
# ci_low = components.quantile(0.025)
# ci_high = components.quantile(0.975)

# lower_err = median_components - ci_low
# upper_err = ci_high - median_components

# order = median_components.sort_values(ascending=False).index
# median_components = median_components[order]
# lower_err = lower_err[order]
# upper_err = upper_err[order]

# colors = [
#     "tab:blue",
#     "tab:orange",
#     "tab:green",
#     "tab:red",
#     "tab:purple",
#     "tab:brown",
#     "tab:pink",
#     "tab:gray",
#     "tab:olive",
#     "tab:cyan",
# ]

# fig, ax = plt.subplots(figsize=(10, 6), facecolor=outer_bg)

# x = np.arange(len(median_components))

# bars = ax.bar(
#     x,
#     median_components.values,
#     yerr=[lower_err.values, upper_err.values],
#     capsize=6,
#     color=colors[:len(median_components)]
# )

# if scenario == "baseline":
#     ax.set_title(f"{technology_title} Current Baseline - Cost Component Medians with 95% CI")
# elif scenario == "slowtransition":
#     ax.set_title(f"{technology_title} Slow Transition Scenario - Cost Component Medians with 95% CI")
# elif scenario == "bestcase":
#     ax.set_title(f"{technology_title} Best Case Scenario - Cost Component Medians with 95% CI")

# for i, v in enumerate(median_components.values):
#     ax.text(i + 0.34, v, f"{v:.1f}", ha="center", va="bottom")

# ax.set_ylabel("Cost per ton (€)")
# ax.set_xticks([])

# ax.legend(
#     bars,
#     median_components.index,
#     loc="upper right",
#     frameon=True
# )

# plt.tight_layout()
# plt.show()


# %% #################### COMBINED LCOS INTERVAL PLOT ########################

scenario_list = ["baseline", "slowtransition", "bestcase"]
technology_list = ["DRI", "BF"]

scenario_labels = {
    "baseline": "Current baseline",
    "slowtransition": "Slow transition",
    "bestcase": "Best case",
}

technology_labels = {
    "DRI": "H2-DRI-EAF",
    "BF": "BF-BOF+CCS",
}

technology_colors = {
    "DRI": "dodgerblue",
    "BF": "crimson",
}

positions = []
box_colors = []
group_centers = []
median_values = []
ci_low_values = []
ci_high_values = []
scenario_names_out = []
technology_names_out = []

group_starts = [1.0, 2.6, 4.2]
within_group_gap = 0.55
box_width = 0.42

for start, scenario_name in zip(group_starts, scenario_list):
    scenario_positions = [start, start + within_group_gap]
    group_centers.append(np.mean(scenario_positions))

    for pos, technology_name in zip(scenario_positions, technology_list):
        _, breakdown_tmp, _ = run_lcos_model(
            scenario=scenario_name,
            technology=technology_name,
            n=n,
            seed=42
        )

        totals = breakdown_tmp["total"]

        positions.append(pos)
        box_colors.append(technology_colors[technology_name])

        median_values.append(totals.median())
        ci_low_values.append(totals.quantile(0.025))
        ci_high_values.append(totals.quantile(0.975))

        scenario_names_out.append(scenario_labels[scenario_name])
        technology_names_out.append(technology_labels[technology_name])

positions = np.array(positions)
median_values = np.array(median_values)
ci_low_values = np.array(ci_low_values)
ci_high_values = np.array(ci_high_values)

# print lo, hi, and range
interval_summary = pd.DataFrame({
    "scenario": scenario_names_out,
    "technology": technology_names_out,
    "median": median_values,
    "lo_95": ci_low_values,
    "hi_95": ci_high_values,
    "range_95": ci_high_values - ci_low_values
})

print(interval_summary.round(2))




















# %% #################### COST BREAKDOWN PLOTS: ALL SCENARIOS / TECHNOLOGIES ####################

scenario_list = ["baseline", "slowtransition", "bestcase"]
technology_list = ["DRI", "BF"]

scenario_labels = {
    "baseline": "Current Baseline",
    "slowtransition": "Slow Transition",
    "bestcase": "Best Case",
}

technology_labels = {
    "DRI": "H2-DRI-EAF",
    "BF": "BF-BOF+CCS",
}

component_colors = {
    "Hydrogen": "cornflowerblue",
    "Electricity": "silver",
    "CCS electricity": "darkgray",
    "Iron ore": "peru",
    "Coal": "dimgray",
    "CO2 T&S": "mediumseagreen",
    "Carbon tax": "lightcoral",
    "CAPEX": "firebrick",
    "OPEX": "mediumblue",
}

for scenario_name in scenario_list:
    for technology_name in technology_list:

        _, breakdown_tmp, _ = run_lcos_model(
            scenario=scenario_name,
            technology=technology_name,
            n=n,
            seed=42
        )

        components_tmp = breakdown_tmp.drop(columns="total").rename(columns={
            "hydrogen": "Hydrogen",
            "energy": "Electricity",
            "energy_main": "Electricity",
            "energy_ccus": "CCS electricity",
            "ore": "Iron ore",
            "coal": "Coal",
            "transport_storage": "CO2 T&S",
            "carbon_tax": "Carbon tax",
            "capex": "CAPEX",
            "opex": "OPEX"
        })

        median_components = components_tmp.median()

        order = median_components.sort_values(ascending=False).index
        median_components = median_components[order]

        colors = [component_colors[c] for c in median_components.index]

        fig, ax = plt.subplots(
            figsize=(10, 6),
            facecolor=scenario_bg_colors[scenario_name]
        )

        x = np.arange(len(median_components))

        bars = ax.bar(
            x,
            median_components.values,
            capsize=6,
            color=colors
        )

        ax.set_title(
            f"{technology_labels[technology_name]} {scenario_labels[scenario_name]} - Cost Component Medians"
        )

        for i, v in enumerate(median_components.values):
            ax.text(i + 0, v, f"{v:.1f}", ha="center", va="bottom")

        ax.set_ylabel("Cost per ton (€)")
        ax.set_xticks([])

        ax.legend(
            bars,
            median_components.index,
            loc="upper right",
            frameon=True
        )
        plt.ylim(0, 430)
        plt.tight_layout()
        plt.show()

# %% #################### CO2 EMISSIONS BREAKDOWN ############################

def co2_breakdown(row):
    # H2-DRI
    energy_dri = (
        row["co2emissions_energy"] * row["factor_energy_DRI"] / 1_000_000
    )
    hydrogen_dri = (
        row["co2emissions_hydrogen"] * row["factor_hydrogen"]
    )
    process_dri = row["factor_carbon_DRI"]

    # BF-BOF without CCUS
    energy_bf_noccus = (
        row["co2emissions_energy"] * row["factor_energy_BF_BOF"] / 1_000_000
    )
    process_bf_noccus = row["factor_carbon_BFBOF"]

    # BF-BOF + CCUS
    gross_bf = row["factor_carbon_BFBOF"]
    process_bf_ccus = row["factor_carbon_BFBOFCCUS"]
    captured_bf = gross_bf - process_bf_ccus

    electricity_bf_main = row["factor_energy_BF_BOF"]
    electricity_bf_ccus = row["energydemand_ccus"] * captured_bf

    energy_bf_ccus = (
        row["co2emissions_energy"] * (electricity_bf_main + electricity_bf_ccus) / 1_000_000
    )

    return pd.Series({
        "DRI_energy_emissions": energy_dri,
        "DRI_hydrogen_emissions": hydrogen_dri,
        "DRI_process_emissions": process_dri,
        "BFCCUS_energy_emissions": energy_bf_ccus,
        "BFCCUS_process_emissions": process_bf_ccus,
        "BF_energy_emissions": energy_bf_noccus,
        "BF_process_emissions": process_bf_noccus,
    })

df_co2 = df.apply(co2_breakdown, axis=1)
means = df_co2.mean()

energy = [
    means["DRI_energy_emissions"],
    means["BFCCUS_energy_emissions"],
    means["BF_energy_emissions"],
]

hydrogen = [
    means["DRI_hydrogen_emissions"],
    0,
    0,
]

non_energy = [
    means["DRI_process_emissions"],
    means["BFCCUS_process_emissions"],
    means["BF_process_emissions"],
]

totals = [energy[i] + hydrogen[i] + non_energy[i] for i in range(3)]

x = [0, 1, 2]
labels = ["H2-DRI-EAF", "BF-BOF+CCS", "BF-BOF"]

fig, ax = plt.subplots(figsize=(10, 6), facecolor=outer_bg)

energy_color = "silver"
hydrogen_color = "cornflowerblue"
process_color = "lightcoral"

ax.bar(x, energy, label="Electricity-related CO2", color=energy_color)
ax.bar(x, hydrogen, bottom=energy, label="Hydrogen-related CO2", color=hydrogen_color)
ax.bar(
    x,
    non_energy,
    bottom=[energy[i] + hydrogen[i] for i in range(3)],
    label="Process / residual CO2",
    color=process_color
)

ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel("tCO2 per ton steel")

if scenario == "baseline":
    ax.set_title("Current Baseline - Mean CO2 emissions breakdown by production route")
elif scenario == "slowtransition":
    ax.set_title("Slow Transition Scenario - Mean CO2 emissions breakdown by production route")
elif scenario == "bestcase":
    ax.set_title("Best Case Scenario - Mean CO2 emissions breakdown by production route")

for i, total in enumerate(totals):
    ax.text(x[i], total + 0.03, f"Total: {total:.2f}", ha="center", va="bottom")

for i in range(3):
    if energy[i] > 0.03:
        ax.text(x[i], energy[i] / 2, f"{energy[i]:.2f}", ha="center", va="center")

    if hydrogen[i] > 0.03:
        ax.text(
            x[i],
            energy[i] + hydrogen[i] / 2,
            f"{hydrogen[i]:.2f}",
            ha="center",
            va="center"
        )

    if non_energy[i] > 0.03:
        ax.text(
            x[i],
            energy[i] + hydrogen[i] + non_energy[i] / 2,
            f"{non_energy[i]:.2f}",
            ha="center",
            va="center"
        )

ax.legend(ncol=2)
plt.ylim(0, 3.1)
plt.tight_layout()
plt.show()


# %% #################### SIMPLE CAPEX / OPEX COMPARISON PLOT ###############

def annualized_capex_per_ton(row, capex_col, lifetime_col, production_col):
    annualized = row[capex_col] * crf(row["discountrate_CAPEX"], row[lifetime_col])
    return annualized / row[production_col]


#################### DRI COST COMPONENTS ####################################

capex_dri = df.apply(
    lambda row: annualized_capex_per_ton(row, "CAPEX_DRI", "lifetime_DRI", "production_DRI"),
    axis=1
)

hydrogen_dri = df["price_hydrogen"] * df["factor_hydrogen"]
electricity_dri = df["price_energy"] * df["factor_energy_DRI"]
material_dri = df["oreprice_DRI"] / df["efficiency_DRI"]
carbon_dri = (
    df["price_carbon_tax"]
    * df["factor_carbon_DRI"]
    * df["allowance_carbon_pct"]
)
labour_maintenance_dri = df["OPEX_DRI"] / df["production_DRI"]


#################### BF-BOF+CCS COST COMPONENTS #############################

capex_bf = df.apply(
    lambda row: annualized_capex_per_ton(row, "CAPEX_CCUS", "lifetime_CCUS", "production_BFBOF"),
    axis=1
)

electricity_bf = (
    df["price_energy"] * df["factor_energy_BF_BOF"]
    + df["price_energy"] * df["energydemand_ccus"] * (df["factor_carbon_BFBOF"] - df["factor_carbon_BFBOFCCUS"])
)

material_bf = (
    df["oreprice_BFBOF"] / df["efficiency_BFBOF"]
    + df["coalprice_BFBOF"] * df["coalfactor_BFBOF"]
    + df["trans_storecost_CCUS"] * (df["factor_carbon_BFBOF"] - df["factor_carbon_BFBOFCCUS"])
)

carbon_bf = (
    df["price_carbon_tax"]
    * df["factor_carbon_BFBOFCCUS"]
    * df["allowance_carbon_pct"]
)

labour_maintenance_bf = df["OPEX_BFBOFwCCUS"] / df["production_BFBOF"]


#################### MEDIAN VALUES ##########################################

capex_vals = pd.Series({
    "CAPEX\nH2-DRI-EAF": capex_dri.median(),
    "CAPEX\nBF-BOF+CCS": capex_bf.median(),
})

opex_stack = pd.DataFrame({
    "Hydrogen": [hydrogen_dri.median(), 0],
    "Electricity": [electricity_dri.median(), electricity_bf.median()],
    "Material": [material_dri.median(), material_bf.median()],
    "Carbon emissions": [carbon_dri.median(), carbon_bf.median()],
    "Labour and maintenance": [labour_maintenance_dri.median(), labour_maintenance_bf.median()],
}, index=["OPEX\nH2-DRI-EAF", "OPEX\nBF-BOF+CCS"])


#################### PLOT ###################################################

x = np.arange(4)
labels = ["CAPEX\nH2-DRI-EAF", "OPEX\nH2-DRI-EAF", "CAPEX\nBF-BOF+CCS", "OPEX\nBF-BOF+CCS"]

fig, ax = plt.subplots(figsize=(10, 6), facecolor="white")

# CAPEX bars
capex_colors = {
    "CAPEX\nH2-DRI-EAF": "indianred",
    "CAPEX\nBF-BOF+CCS": "firebrick",
}

bar_capex_dri = ax.bar(
    x[0],
    capex_vals["CAPEX\nH2-DRI-EAF"],
    color=capex_colors["CAPEX\nH2-DRI-EAF"]
)

bar_capex_bf = ax.bar(
    x[2],
    capex_vals["CAPEX\nBF-BOF+CCS"],
    color=capex_colors["CAPEX\nBF-BOF+CCS"]
)

# OPEX stacked bars
stack_colors = {
    "Hydrogen": "cornflowerblue",
    "Electricity": "silver",
    "Material": "peru",
    "Carbon emissions": "lightcoral",
    "Labour and maintenance": "mediumblue",
}

bottom_dri = 0
bottom_bf = 0
opex_handles = []

for component in opex_stack.columns:
    vals = opex_stack[component].values

    bars = ax.bar(
        [x[1], x[3]],
        vals,
        bottom=[bottom_dri, bottom_bf],
        color=stack_colors[component],
        label=component
    )

    opex_handles.append(bars[0])

    bottom_dri += vals[0]
    bottom_bf += vals[1]

# total labels on top of all bars
total_vals = [
    capex_vals["CAPEX\nH2-DRI-EAF"],
    opex_stack.loc["OPEX\nH2-DRI-EAF"].sum(),
    capex_vals["CAPEX\nBF-BOF+CCS"],
    opex_stack.loc["OPEX\nBF-BOF+CCS"].sum(),
]

for i, total in enumerate(total_vals):
    ax.text(
        x[i],
        total + 1,
        f"{total:.1f}",
        ha="center",
        va="bottom"
    )

ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.set_ylabel("Cost per ton (€)")
ax.set_title("Median CAPEX and OPEX Comparison")

legend_handles = [
    Patch(facecolor="indianred", edgecolor="black", label="CAPEX H2-DRI-EAF"),
    Patch(facecolor="firebrick", edgecolor="black", label="CAPEX BF-BOF+CCS"),
    Patch(facecolor=stack_colors["Hydrogen"], edgecolor="black", label="Hydrogen"),
    Patch(facecolor=stack_colors["Electricity"], edgecolor="black", label="Electricity"),
    Patch(facecolor=stack_colors["Material"], edgecolor="black", label="Material"),
    Patch(facecolor=stack_colors["Carbon emissions"], edgecolor="black", label="Carbon emissions"),
    Patch(facecolor=stack_colors["Labour and maintenance"], edgecolor="black", label="Labour and maintenance"),
]

ax.legend(handles=legend_handles, loc="upper right", ncol=2)

plt.ylim(0, 750)
plt.tight_layout()
plt.show()
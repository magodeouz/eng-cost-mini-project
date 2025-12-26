import base64
import io
from typing import Dict, List

import matplotlib
import matplotlib.pyplot as plt
from flask import Flask, render_template, request
from matplotlib.ticker import StrMethodFormatter

# Use non-GUI backend for server-side rendering
matplotlib.use("Agg")
plt.style.use("seaborn-v0_8-whitegrid")
matplotlib.rcParams.update(
    {
        "axes.edgecolor": "#cbd5e1",
        "axes.labelcolor": "#0f172a",
        "axes.titlecolor": "#0f172a",
        "figure.facecolor": "#ffffff",
        "axes.facecolor": "#f8fafc",
        "grid.color": "#e2e8f0",
        "text.color": "#0f172a",
        "xtick.color": "#475569",
        "ytick.color": "#475569",
        "legend.frameon": False,
    }
)

def apply_formatters(ax, fmt_x: bool = True, fmt_y: bool = True):
    """Avoid scientific notation; show thousand separators."""
    if fmt_x:
        ax.xaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    if fmt_y:
        ax.yaxis.set_major_formatter(StrMethodFormatter("{x:,.0f}"))
    return ax


def strip_label(data: Dict[str, float]) -> Dict[str, float]:
    """Remove optional 'label' key when passing params into calculations."""
    return {k: v for k, v in data.items() if k != "label"}

app = Flask(__name__)


def currencyformat(value: float) -> str:
    try:
        return f"${value:,.0f}"
    except Exception:
        return "$0"


app.jinja_env.filters["currencyformat"] = currencyformat

DEFAULTS = {
    "selling_price": 3000.0,
    "variable_cost": 500.0,
    "fixed_costs": 3_000_000.0,
    "target_net_income": 1_500_000.0,
    "tax_rate": 25.0,
    "units_sold": 2000.0,
    # scenario defaults
    "scA_price_drop": 20.0,
    "scA_sales_lift": 11.0,
    "scB_vc_drop": 50.0,
    "scB_sp_drop": 250.0,
    "scC_fc_drop": 20.0,
    "scC_sp_drop": 10.0,
    "scC_units": 1700.0,
}


def parse_float(name: str, default: float) -> float:
    val = request.args.get(name, None)
    if val is None or val == "":
        return default
    try:
        return float(val)
    except ValueError:
        return default


def calculate_metrics(
    *, selling_price: float, variable_cost: float, fixed_costs: float, units_sold: float, tax_rate: float
) -> Dict[str, float]:
    cm_per_unit = selling_price - variable_cost
    total_cm = cm_per_unit * units_sold
    operating_income = total_cm - fixed_costs
    net_income = operating_income * (1 - tax_rate / 100.0)
    breakeven_units = fixed_costs / cm_per_unit if cm_per_unit > 0 else 0
    breakeven_revenue = breakeven_units * selling_price
    cm_pct = cm_per_unit / selling_price if selling_price > 0 else 0
    return {
        "cm_per_unit": cm_per_unit,
        "total_cm": total_cm,
        "cm_pct": cm_pct,
        "operating_income": operating_income,
        "net_income": net_income,
        "breakeven_units": breakeven_units,
        "breakeven_revenue": breakeven_revenue,
    }


def units_range(max_units: float, steps: int = 30) -> List[float]:
    max_units = max(max_units, 1_000.0)
    step = max_units / steps
    return [i * step for i in range(steps + 1)]


def plot_costs(params: Dict[str, float]) -> str:
    sp, vc, fc = params["selling_price"], params["variable_cost"], params["fixed_costs"]
    units = units_range(max(params["units_sold"] * 1.6, fc / max(sp - vc, 1) * 1.3))
    fixed_line = [fc for _ in units]
    variable_line = [vc * u for u in units]
    total_cost = [fc + vc * u for u in units]
    revenue = [sp * u for u in units]

    fig, ax = plt.subplots(figsize=(7, 4.2))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")
    ax.plot(units, fixed_line, label="Fixed cost", color="#2563eb", linewidth=2.5)
    ax.plot(units, variable_line, label="Variable cost", color="#f97316", linewidth=2.5)
    ax.plot(units, total_cost, label="Total cost", color="#a855f7", linewidth=2.5)
    ax.plot(units, revenue, label="Revenue", color="#22c55e", linewidth=2.5, linestyle="--")
    ax.set_xlabel("Units sold")
    ax.set_ylabel("USD")
    ax.grid(True, alpha=0.2)
    ax.legend()
    apply_formatters(ax, fmt_x=True, fmt_y=True)
    fig.tight_layout()
    return fig_to_base64(fig)


def plot_contribution_margin(params: Dict[str, float]) -> str:
    sp, vc = params["selling_price"], params["variable_cost"]
    units = units_range(params["units_sold"] * 1.6)
    cm_line = [(sp - vc) * u for u in units]
    fig, ax = plt.subplots(figsize=(7, 4.2))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")
    ax.plot(units, cm_line, label="Total contribution margin", color="#fb7185", linewidth=2.5)
    ax.set_xlabel("Units sold")
    ax.set_ylabel("USD")
    ax.grid(True, alpha=0.2)
    ax.legend()
    apply_formatters(ax, fmt_x=True, fmt_y=True)
    fig.tight_layout()
    return fig_to_base64(fig)


def plot_scenario_compare(scenarios: Dict[str, Dict[str, float]]) -> str:
    colors = {"A": "#2563eb", "B": "#f97316", "C": "#22c55e"}
    max_units = 0
    metrics_map: Dict[str, Dict[str, float]] = {}
    for key, p in scenarios.items():
        m = calculate_metrics(**strip_label(p))
        metrics_map[key] = m
        max_units = max(max_units, p["units_sold"] * 1.4, m["breakeven_units"] * 1.6)

    units = units_range(max_units)
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")

    for key, p in scenarios.items():
        m = metrics_map[key]
        oi_line = [(p["selling_price"] - p["variable_cost"]) * u - p["fixed_costs"] for u in units]
        ax.plot(units, oi_line, label=f'{p["label"]}', color=colors[key], linewidth=2.6)
        ax.scatter(
            [m["breakeven_units"]],
            [0],
            color=colors[key],
            edgecolors="#0f172a",
            zorder=5,
            s=55,
            label=f"B/E {key} ({m['breakeven_units']:.0f} units, {m['breakeven_revenue']:.0f} USD)",
        )

    ax.axhline(0, color="#94a3b8", linestyle="--", linewidth=1.4)
    ax.set_xlabel("Units sold")
    ax.set_ylabel("Operating income (USD)")
    ax.grid(True, alpha=0.2)
    ax.legend(fontsize=8)
    apply_formatters(ax, fmt_x=True, fmt_y=True)
    fig.tight_layout()
    return fig_to_base64(fig)


def plot_scenario_cost_revenue(scenarios: Dict[str, Dict[str, float]]) -> str:
    colors = {"A": "#2563eb", "B": "#f97316", "C": "#22c55e"}
    max_units = 0
    metrics_map: Dict[str, Dict[str, float]] = {}
    for key, p in scenarios.items():
        m = calculate_metrics(**strip_label(p))
        metrics_map[key] = m
        max_units = max(max_units, p["units_sold"] * 1.4, m["breakeven_units"] * 1.6)

    units = units_range(max_units)
    fig, ax = plt.subplots(figsize=(7.5, 4.5))
    fig.patch.set_facecolor("#ffffff")
    ax.set_facecolor("#f8fafc")
    for key, p in scenarios.items():
        m = metrics_map[key]
        revenue = [p["selling_price"] * u for u in units]
        total_cost = [p["fixed_costs"] + p["variable_cost"] * u for u in units]
        ax.plot(units, revenue, label=f'{p["label"]} revenue', color=colors[key], linewidth=2.6)
        ax.plot(
            units,
            total_cost,
            label=f'{p["label"]} total cost',
            color=colors[key],
            linewidth=2.6,
            linestyle="--",
        )
        ax.scatter(
            [m["breakeven_units"]],
            [m["breakeven_revenue"]],
            color=colors[key],
            edgecolors="#0f172a",
            zorder=5,
            s=55,
            label=f'B/E {key} ({m["breakeven_units"]:.0f} units, {m["breakeven_revenue"]:.0f} USD)',
        )

    ax.set_xlabel("Units sold")
    ax.set_ylabel("USD")
    ax.grid(True, alpha=0.2)
    ax.legend(fontsize=8)
    apply_formatters(ax, fmt_x=True, fmt_y=True)
    fig.tight_layout()
    return fig_to_base64(fig)


def fig_to_base64(fig: matplotlib.figure.Figure) -> str:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=140, bbox_inches="tight")
    plt.close(fig)
    buf.seek(0)
    return base64.b64encode(buf.read()).decode("ascii")


@app.route("/")
def analysis():
    # Baseline inputs
    params = {
        "selling_price": parse_float("selling_price", DEFAULTS["selling_price"]),
        "variable_cost": parse_float("variable_cost", DEFAULTS["variable_cost"]),
        "fixed_costs": parse_float("fixed_costs", DEFAULTS["fixed_costs"]),
        "units_sold": parse_float("units_sold", DEFAULTS["units_sold"]),
        "tax_rate": parse_float("tax_rate", DEFAULTS["tax_rate"]),
    }

    baseline_metrics = calculate_metrics(**params)

    # Scenarios
    scA = {
        **params,
        "selling_price": params["selling_price"] * (1 - parse_float("scA_price_drop", DEFAULTS["scA_price_drop"]) / 100),
        "units_sold": params["units_sold"] * (1 + parse_float("scA_sales_lift", DEFAULTS["scA_sales_lift"]) / 100),
        "label": "Scenario A (price ↓, volume ↑)",
    }
    scB = {
        **params,
        "selling_price": max(0, params["selling_price"] - parse_float("scB_sp_drop", DEFAULTS["scB_sp_drop"])),
        "variable_cost": max(0, params["variable_cost"] - parse_float("scB_vc_drop", DEFAULTS["scB_vc_drop"])),
        "label": "Scenario B (lower price & VC)",
    }
    scC = {
        **params,
        "selling_price": params["selling_price"] * (1 - parse_float("scC_sp_drop", DEFAULTS["scC_sp_drop"]) / 100),
        "fixed_costs": params["fixed_costs"] * (1 - parse_float("scC_fc_drop", DEFAULTS["scC_fc_drop"]) / 100),
        "units_sold": parse_float("scC_units", DEFAULTS["scC_units"]),
        "label": "Scenario C (fixed ↓, price ↓)",
    }
    scenarios = {"A": scA, "B": scB, "C": scC}
    scenario_metrics = {k: calculate_metrics(**strip_label(v)) for k, v in scenarios.items()}

    # Plots (base64)
    cost_img = plot_costs(params)
    cm_img = plot_contribution_margin(params)
    scenario_img = plot_scenario_compare(scenarios)
    scenario_cost_img = plot_scenario_cost_revenue(scenarios)

    return render_template(
        "analysis.html",
        defaults=DEFAULTS,
        params=params,
        baseline=baseline_metrics,
        scenarios=scenarios,
        scenario_metrics=scenario_metrics,
        cost_img=cost_img,
        cm_img=cm_img,
        scenario_img=scenario_img,
        scenario_cost_img=scenario_cost_img,
    )


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001)


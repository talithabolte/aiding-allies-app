"""Calculations for parts (b) and (c). Kept separate from the app so they can be tested."""
import numpy as np
import pandas as pd
from scipy.optimize import linprog

from data import ORIGINS, MIDS, CITIES, PORTS, AIRFIELDS


def arc_times(arcs, vehicles, km_per_mile=1.609):
    """Add miles and travel hours to each arc."""
    a = arcs.copy()
    speed = vehicles.set_index("Vehicle")["Speed (mph)"]
    a["Speed (mph)"] = a["Vehicle"].map(speed)
    a["Distance (miles)"] = pd.to_numeric(a["Distance (km)"], errors="coerce") / km_per_mile
    a["Hours"] = a["Distance (miles)"] / a["Speed (mph)"]
    return a


def all_routes(arcs_t):
    """Every two-leg route (US -> NATO stop -> Russian city) with its total time."""
    h = arcs_t.set_index(["From", "To"])["Hours"]
    rows = []
    for o in ORIGINS:
        for c in CITIES:
            for m in MIDS:
                l1, l2 = h.get((o, m), np.nan), h.get((m, c), np.nan)
                rows.append(
                    {
                        "Origin": o,
                        "Via": m,
                        "Stop type": "Port (ship + truck)" if m in PORTS else "Airfield (plane + plane)",
                        "Destination": c,
                        "Leg 1 (h)": l1,
                        "Leg 2 (h)": l2,
                        "Total (h)": l1 + l2,
                    }
                )
    r = pd.DataFrame(rows)
    best = r.groupby(["Origin", "Destination"])["Total (h)"].transform("min")
    r["Fastest"] = np.isclose(r["Total (h)"], best) & r["Total (h)"].notna()
    return r


def fastest(routes):
    """Fastest route for each origin-destination pair."""
    b = routes[routes["Fastest"]].copy()
    b["Route"] = b["Origin"] + " → " + b["Via"] + " → " + b["Destination"]
    b["Hours + minutes"] = b["Total (h)"].apply(lambda x: f"{int(x)} h {round((x % 1) * 60):02d} min")
    return b[["Origin", "Destination", "Route", "Total (h)", "Hours + minutes"]].reset_index(drop=True)


def min_cost(arcs, vehicles, nodes):
    """Part (c): minimum-cost flow. Flows are in thousand tons; costs in $ thousand.

    Returns (status_message, plan DataFrame or None, total cost in $ thousand or None).
    """
    a = arcs.copy()
    cap = vehicles.set_index("Vehicle")["Capacity (tons)"]
    a["Vehicle capacity (t)"] = a["Vehicle"].map(cap).astype(float)
    a["Unit cost ($/ton)"] = pd.to_numeric(a["Cost per vehicle ($k)"], errors="coerce") * 1000 / a["Vehicle capacity (t)"]
    mv = pd.to_numeric(a["Max vehicles"], errors="coerce")
    a["Capacity (kt)"] = mv * a["Vehicle capacity (t)"] / 1000

    if a["Unit cost ($/ton)"].isna().any():
        return "Every route needs a cost per vehicle.", None, None

    supply = {r["City"]: float(r["Thousand tons"]) for _, r in nodes.iterrows() if r["Role"].startswith("Supply")}
    demand = {r["City"]: float(r["Thousand tons"]) for _, r in nodes.iterrows() if r["Role"].startswith("Requirement")}
    all_nodes = ORIGINS + MIDS + CITIES

    A_eq, b_eq, A_ub, b_ub = [], [], [], []
    for n in all_nodes:
        row = [(1 if f == n else 0) - (1 if t == n else 0) for f, t in zip(a["From"], a["To"])]
        if n in ORIGINS:  # can't send more than is available
            A_ub.append(row); b_ub.append(supply.get(n, 0))
        elif n in CITIES:  # must receive at least the requirement
            A_ub.append(row); b_ub.append(-demand.get(n, 0))
        else:  # transhipment: what comes in goes out
            A_eq.append(row); b_eq.append(0)

    bounds = [(0, None if np.isnan(c) else c) for c in a["Capacity (kt)"]]
    res = linprog(a["Unit cost ($/ton)"].values, A_ub=A_ub, b_ub=b_ub, A_eq=A_eq, b_eq=b_eq,
                  bounds=bounds, method="highs")
    if res.status != 0:
        need, have = sum(demand.values()), sum(supply.values())
        msg = "No feasible plan with these limits."
        if need > have:
            msg += f" Requirements ({need:,.0f}) exceed supply ({have:,.0f})."
        return msg, None, None

    a["Ship (kt)"] = np.round(res.x, 6)
    a["Vehicles needed"] = a["Ship (kt)"] * 1000 / a["Vehicle capacity (t)"]
    a["Cost ($k)"] = a["Ship (kt)"] * a["Unit cost ($/ton)"]
    return "Optimal", a, float(res.fun)

"""Default case data for the Aiding Allies case (Hillier & Hillier).

Every value here is only a starting point — the app lets you edit all of it.
"""
import pandas as pd

ORIGINS = ["Boston", "Jacksonville"]
PORTS = ["Hamburg", "Rotterdam", "Napoli"]
AIRFIELDS = ["Berlin", "London", "Istanbul"]
CITIES = ["St Petersburg", "Moscow", "Rostov"]
MIDS = AIRFIELDS + PORTS


def vehicle_for(frm, to):
    if to in PORTS:
        return "Transport"
    if frm in PORTS:
        return "Truck"
    return "Globemaster"


def default_vehicles():
    return pd.DataFrame(
        [
            {"Vehicle": "Globemaster", "Type": "Aircraft", "Speed (mph)": 400, "Capacity (tons)": 150},
            {"Vehicle": "Transport", "Type": "Ship", "Speed (mph)": 35, "Capacity (tons)": 240},
            {"Vehicle": "Truck", "Type": "Palletised load system truck", "Speed (mph)": 60, "Capacity (tons)": 16},
        ]
    )


# Distances (km). Rotterdam -> St Petersburg is not given in the case (left blank).
_DIST = {
    ("Boston", "Berlin"): 7250, ("Boston", "Hamburg"): 8250, ("Boston", "Istanbul"): 8300,
    ("Boston", "London"): 6200, ("Boston", "Rotterdam"): 6900, ("Boston", "Napoli"): 7950,
    ("Jacksonville", "Berlin"): 9200, ("Jacksonville", "Hamburg"): 9800, ("Jacksonville", "Istanbul"): 10100,
    ("Jacksonville", "London"): 7900, ("Jacksonville", "Rotterdam"): 8900, ("Jacksonville", "Napoli"): 9400,
    ("Berlin", "St Petersburg"): 1280, ("Berlin", "Moscow"): 1600, ("Berlin", "Rostov"): 1730,
    ("Hamburg", "St Petersburg"): 1880, ("Hamburg", "Moscow"): 2120, ("Hamburg", "Rostov"): 2470,
    ("Istanbul", "St Petersburg"): 2040, ("Istanbul", "Moscow"): 1700, ("Istanbul", "Rostov"): 990,
    ("London", "St Petersburg"): 1980, ("London", "Moscow"): 2300, ("London", "Rostov"): 2860,
    ("Rotterdam", "St Petersburg"): None, ("Rotterdam", "Moscow"): 2450, ("Rotterdam", "Rostov"): 2760,
    ("Napoli", "St Petersburg"): 2970, ("Napoli", "Moscow"): 2890, ("Napoli", "Rostov"): 2800,
}

# Cost per vehicle ($ thousand) from the case's costs tab.
_COST = {
    ("Boston", "Berlin"): 50, ("Boston", "Hamburg"): 30, ("Boston", "Istanbul"): 55,
    ("Boston", "London"): 45, ("Boston", "Rotterdam"): 30, ("Boston", "Napoli"): 32,
    ("Jacksonville", "Berlin"): 57, ("Jacksonville", "Hamburg"): 48, ("Jacksonville", "Istanbul"): 61,
    ("Jacksonville", "London"): 49, ("Jacksonville", "Rotterdam"): 44, ("Jacksonville", "Napoli"): 56,
    ("Berlin", "St Petersburg"): 24, ("Hamburg", "St Petersburg"): 3, ("Istanbul", "St Petersburg"): 28,
    ("London", "St Petersburg"): 22, ("Rotterdam", "St Petersburg"): 3, ("Napoli", "St Petersburg"): 5,
    ("Berlin", "Moscow"): 22, ("Hamburg", "Moscow"): 4, ("Istanbul", "Moscow"): 25,
    ("London", "Moscow"): 19, ("Rotterdam", "Moscow"): 5, ("Napoli", "Moscow"): 5,
    ("Berlin", "Rostov"): 23, ("Hamburg", "Rostov"): 7, ("Istanbul", "Rostov"): 2,
    ("London", "Rostov"): 4, ("Rotterdam", "Rostov"): 8, ("Napoli", "Rostov"): 9,
}

# Maximum vehicles allowed on an arc (blank = no limit).
#  - Snow: no trucks into St Petersburg (0)
#  - Rostov truck routes: at most 2,500 trucks from each port
#  - Ukraine: at most 200 flights Berlin->Rostov and London->Rostov
_MAXVEH = {
    ("Hamburg", "St Petersburg"): 0, ("Rotterdam", "St Petersburg"): 0, ("Napoli", "St Petersburg"): 0,
    ("Berlin", "Rostov"): 200, ("London", "Rostov"): 200,
    ("Hamburg", "Rostov"): 2500, ("Rotterdam", "Rostov"): 2500, ("Napoli", "Rostov"): 2500,
}


def default_arcs():
    rows = []
    pairs = [(o, m) for o in ORIGINS for m in MIDS] + [(m, c) for m in MIDS for c in CITIES]
    for frm, to in pairs:
        rows.append(
            {
                "From": frm,
                "To": to,
                "Vehicle": vehicle_for(frm, to),
                "Distance (km)": _DIST[(frm, to)],
                "Cost per vehicle ($k)": _COST[(frm, to)],
                "Max vehicles": _MAXVEH.get((frm, to)),
            }
        )
    return pd.DataFrame(rows)


def default_nodes():
    req = {"St Petersburg": 320, "Moscow": 440, "Rostov": 240}
    rows = [{"City": o, "Role": "Supply (US)", "Thousand tons": 500} for o in ORIGINS]
    rows += [{"City": c, "Role": "Requirement (Russia)", "Thousand tons": req[c]} for c in CITIES]
    return pd.DataFrame(rows)

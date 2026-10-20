"""Aiding Allies — network model, fastest routes and minimum-cost plan.

Run locally:   streamlit run app.py
"""
import io

import pandas as pd
import streamlit as st

from data import default_arcs, default_nodes, default_vehicles, PORTS
from network import draw
from solver import all_routes, arc_times, fastest, min_cost

st.set_page_config(page_title="Aiding Allies", page_icon="✈️", layout="wide")

# ---------- state ----------
def reset():
    st.session_state.vehicles = default_vehicles()
    st.session_state.arcs = default_arcs()
    st.session_state.nodes = default_nodes()
    st.session_state.km_per_mile = 1.609
    for k in ("ed_veh", "ed_arcs", "ed_nodes"):
        st.session_state.pop(k, None)


if "arcs" not in st.session_state:
    reset()

st.title("✈️ Aiding Allies: US → NATO → Russia")
st.caption("Edit any number on the **Inputs** tab; every answer, table and network diagram recalculates instantly.")

tab_in, tab_a, tab_b, tab_c = st.tabs(["⚙️ Inputs", "(a) Network", "(b) Fastest routes", "(c) Minimum cost"])

# ---------- inputs ----------
with tab_in:
    c1, c2 = st.columns([3, 2])
    with c1:
        st.subheader("Vehicles")
        vehicles = st.data_editor(st.session_state.vehicles, key="ed_veh", hide_index=True,
                                  disabled=["Vehicle", "Type"], width="stretch")
    with c2:
        st.subheader("Supply and requirements")
        nodes = st.data_editor(st.session_state.nodes, key="ed_nodes", hide_index=True,
                               disabled=["City", "Role"], width="stretch",
                               column_config={"Thousand tons": st.column_config.NumberColumn(min_value=0, format="%.0f")})
        km_per_mile = st.number_input("Kilometres per mile", value=st.session_state.km_per_mile, step=0.001, format="%.3f")
        st.button("↺ Reset everything to the case data", on_click=reset)

    st.subheader("Routes (arcs)")
    st.markdown(
        "**Distance** is used in part (b); **cost per vehicle** and **max vehicles** in part (c). "
        "Leave *Max vehicles* blank for no limit, or set **0** to close a route."
    )
    arcs = st.data_editor(
        st.session_state.arcs, key="ed_arcs", hide_index=True, disabled=["From", "To", "Vehicle"],
        width="stretch", height=560,
        column_config={
            "Distance (km)": st.column_config.NumberColumn(min_value=0, format="%d"),
            "Cost per vehicle ($k)": st.column_config.NumberColumn(min_value=0, format="%.1f"),
            "Max vehicles": st.column_config.NumberColumn(min_value=0, format="%d"),
        },
    )
    with st.expander("Where the defaults come from"):
        st.markdown(
            "- Speeds and capacities: the case's vehicle table (Globemaster 400 mph / 150 t, "
            "transport 35 mph / 240 t, truck 60 mph / 16 t).\n"
            "- Airfield distances and costs: the case spreadsheet (distances tab and costs tab).\n"
            "- Port distances: the published case. **Rotterdam → St Petersburg isn't given**, so it's blank; "
            "it can't affect part (b) because ship routes take 120+ hours.\n"
            "- Limits: no trucks into St Petersburg (snow), ≤ 2,500 trucks per port into Rostov, "
            "≤ 200 flights Berlin → Rostov and London → Rostov (Ukraine)."
        )

# ---------- calculations ----------
arcs_t = arc_times(arcs, vehicles, km_per_mile)
routes = all_routes(arcs_t)
best = fastest(routes)
status, plan, total = min_cost(arcs, vehicles, nodes)

# ---------- (a) ----------
with tab_a:
    st.subheader("Part (a): network of possible routes")
    st.markdown(
        "**Nodes:** 2 US origins, 3 NATO ports, 3 NATO airfields, 3 Russian cities.  \n"
        "**Arcs:** ships US → ports, trucks ports → Russia, Globemasters US → airfields → Russia "
        f"({len(arcs)} arcs, {len(routes)} possible routes)."
    )
    st.pyplot(draw(arcs, title="Aiding Allies: network of possible routes"))

# ---------- (b) ----------
with tab_b:
    st.subheader("Part (b): how quickly can troops reach each city?")
    for o in ["Boston", "Jacksonville"]:
        cols = st.columns(3)
        for col, (_, r) in zip(cols, best[best["Origin"] == o].iterrows()):
            col.metric(f"{o} → {r['Destination']}", f"{r['Total (h)']:.2f} h",
                       f"via {r['Route'].split(' → ')[1]} · {r['Hours + minutes']}", delta_color="off")
    overall = best.loc[best.groupby("Destination")["Total (h)"].idxmin()]
    st.markdown("**Fastest to each city (either origin):** " + " · ".join(
        f"{r['Destination']} {r['Total (h)']:.2f} h ({r['Route']})" for _, r in overall.iterrows()))

    hl = set()
    for rt in best["Route"]:
        o, m, d = rt.split(" → ")
        hl |= {(o, m), (m, d)}
    st.pyplot(draw(arcs, highlight=hl, title="Fastest paths highlighted"))

    st.markdown("**All routes** (fastest per origin and city ticked)")
    st.dataframe(routes.style.format({"Leg 1 (h)": "{:.2f}", "Leg 2 (h)": "{:.2f}", "Total (h)": "{:.2f}"},
                                     na_rep="no distance"),
                 hide_index=True, width="stretch", height=400)
    with st.expander("Travel time for each arc"):
        st.dataframe(arcs_t[["From", "To", "Vehicle", "Distance (km)", "Distance (miles)", "Speed (mph)", "Hours"]]
                     .style.format({"Distance (miles)": "{:,.0f}", "Hours": "{:.2f}"}, na_rep="—"),
                     hide_index=True, width="stretch")

# ---------- (c) ----------
with tab_c:
    st.subheader("Part (c): meet every requirement at minimum cost")
    if plan is None:
        st.error(status)
    else:
        used = plan[plan["Ship (kt)"] > 1e-6]
        m1, m2, m3 = st.columns(3)
        m1.metric("Minimum total cost", f"${total * 1000:,.0f}")
        m2.metric("In $ millions", f"${total / 1000:,.1f} m")
        m3.metric("Routes used", f"{len(used)} of {len(plan)}")

        node_lab = {r["City"]: f"{r['City']}\n{'supply' if r['Role'].startswith('Supply') else 'needs'} "
                               f"{r['Thousand tons']:,.0f}" for _, r in nodes.iterrows()}
        st.pyplot(draw(arcs, highlight=set(zip(used["From"], used["To"])),
                       labels={(r["From"], r["To"]): f"{r['Ship (kt)']:,.0f}" for _, r in used.iterrows()},
                       node_labels=node_lab,
                       title=f"Minimum-cost plan (thousand tons per route) · total ≈ ${total / 1000:,.1f} million"))

        show = used[["From", "To", "Vehicle", "Ship (kt)", "Vehicles needed", "Unit cost ($/ton)", "Cost ($k)"]]
        st.dataframe(show.style.format({"Ship (kt)": "{:,.1f}", "Vehicles needed": "{:,.0f}",
                                        "Unit cost ($/ton)": "${:,.2f}", "Cost ($k)": "${:,.1f}"}),
                     hide_index=True, width="stretch")

        binding = plan[plan["Capacity (kt)"].notna() & (plan["Capacity (kt)"] > 0)
                       & (plan["Ship (kt)"] >= plan["Capacity (kt)"] - 1e-6)]
        if len(binding):
            st.info("Routes at their limit: " + ", ".join(f"{r['From']} → {r['To']}" for _, r in binding.iterrows()))

        with st.expander("Full model (all routes, like the Excel Solver sheet)"):
            st.dataframe(plan[["From", "To", "Ship (kt)", "Capacity (kt)", "Cost per vehicle ($k)", "Vehicle",
                               "Max vehicles", "Vehicle capacity (t)", "Unit cost ($/ton)"]]
                         .style.format({"Ship (kt)": "{:,.1f}", "Capacity (kt)": "{:,.1f}",
                                        "Unit cost ($/ton)": "${:,.2f}"}, na_rep=""),
                         hide_index=True, width="stretch", height=500)
            st.markdown("Unit cost ($/ton) = cost per vehicle × 1,000 ÷ vehicle capacity · "
                        "Capacity (kt) = max vehicles × vehicle capacity ÷ 1,000 · "
                        "Total cost ($k) = Σ ship (kt) × unit cost ($/ton).")

# ---------- download ----------
buf = io.BytesIO()
with pd.ExcelWriter(buf, engine="openpyxl") as xw:
    arcs.to_excel(xw, sheet_name="Inputs - routes", index=False)
    vehicles.to_excel(xw, sheet_name="Inputs - vehicles", index=False)
    nodes.to_excel(xw, sheet_name="Inputs - supply & demand", index=False)
    best.to_excel(xw, sheet_name="(b) Fastest", index=False)
    routes.to_excel(xw, sheet_name="(b) All routes", index=False)
    if plan is not None:
        plan.to_excel(xw, sheet_name="(c) Min-cost plan", index=False)
st.sidebar.header("Export")
st.sidebar.download_button("⬇️ Download results (.xlsx)", buf.getvalue(), "aiding_allies_results.xlsx")
st.sidebar.markdown("Changes you make stay until you refresh the page. Use **Reset** on the Inputs tab to go back to the case data.")

# Aiding Allies: network optimisation app

An interactive Streamlit app for the *Aiding Allies* case (Hillier & Hillier, *Introduction to Management Science*). It covers three parts:

- **(a) Network.** A diagram of every route from Boston and Jacksonville through the NATO ports and airfields to St Petersburg, Moscow and Rostov.
- **(b) Fastest routes.** The shortest travel time for each origin–city pair, with the paths highlighted.
- **(c) Minimum cost.** The cheapest way to meet each city's requirement within the snow, truck and Ukrainian flight limits. It uses the same model as the Excel Solver sheet.

Every speed, distance, cost, capacity, limit and requirement can be edited on the **Inputs** tab. All the answers and diagrams recalculate instantly. A sidebar button exports the results to Excel.

## Run it on your computer

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Put it online (free)

1. Create a new **public** repository on [github.com](https://github.com/new), for example `aiding-allies-app`.
2. Click **Add file → Upload files** and drag in every file from this folder. Then click **Commit changes**.
3. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
4. Click **Create app**, pick your repository, set the main file to `app.py`, and click **Deploy**.

To update the app later, edit `data.py` on GitHub (for example to change a default cost). Streamlit Cloud redeploys automatically.

## Files

| File | What it does |
|---|---|
| `app.py` | The Streamlit interface (tabs, tables, charts) |
| `data.py` | Default case data. Change default values here |
| `solver.py` | Part (b) route times and the part (c) linear programme (SciPy / HiGHS) |
| `network.py` | Draws the network diagrams |

## Model notes

- **Times.** Hours = (km ÷ 1.609) ÷ speed in mph.
- **Unit cost.** $ per ton = cost per vehicle ($ thousand) × 1,000 ÷ vehicle capacity (tons).
- **Capacity.** Thousand tons = maximum vehicles × vehicle capacity ÷ 1,000.
- **Part (c).** This is a minimum-cost flow problem in thousand tons:
  - Origins ship no more than their supply.
  - Russian cities receive at least their requirement.
  - Ports and airfields pass on everything they receive.
- **Missing distance.** Rotterdam → St Petersburg isn't given in the case. It can't affect part (b), because ship routes take more than 120 hours.

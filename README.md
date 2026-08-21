Interactive dashboard for a vehicle routing optimization project, built with Streamlit and Python.

It lets you explore three delivery-routing scenarios (base case, mixed fleet, and a relaxed-constraint case), compare daily and annual mileage, visualize individual routes on a map, inspect stop-level details, and read auto-generated insights.

Highlights
Scenario selector across the Q1, Q2, and Q3 solution files
Daily and annual mileage comparison (Plotly charts)
Route map and full route-stop details table
Insights such as average daily miles and most efficient day
Tech stack

Python, Streamlit, Pandas, NumPy, Plotly

Run locally
bash
pip install -r requirements.txt
streamlit run Dashboard.py

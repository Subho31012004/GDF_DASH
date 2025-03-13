import dash
import dash_bootstrap_components as dbc
import plotly.express as px
import pandas as pd
import numpy as np
import time
from dash import dcc, html, Input, Output, State, dash_table
from dash.exceptions import PreventUpdate
import threading

# Sample Data (Global Economic Data)
df = px.data.gapminder()

# Initialize Dash app with a modern Bootstrap theme
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY])

# Dummy function to simulate real-time data updates
live_data = pd.DataFrame({"Time": [], "Value": []})

def generate_live_data():
    global live_data
    while True:
        time.sleep(2)
        new_row = {"Time": pd.Timestamp.now(), "Value": np.random.randint(50, 200)}
        live_data = pd.concat([live_data, pd.DataFrame([new_row])]).tail(15)  # Keep latest 15 points

# Start real-time data thread
thread = threading.Thread(target=generate_live_data, daemon=True)
thread.start()

# Layout
app.layout = dbc.Container([
    
    # Title
    dbc.Row([
        dbc.Col(html.H1("📊 Advanced Data Dashboard", className="text-center mt-4"), width=12)
    ]),

    # Theme Toggle
    dbc.Row([
        dbc.Col(
            dbc.Button("Toggle Theme", id="theme-toggle", n_clicks=0, className="btn btn-info"),
            width=3
        ),
    ], className="mb-3"),

    # Row with Controls & Dropdowns
    dbc.Row([
        dbc.Col(dcc.Dropdown(
            id="country-dropdown",
            options=[{"label": c, "value": c} for c in df["country"].unique()],
            value="India",
            clearable=False,
            className="mb-3"
        ), width=4),

        dbc.Col(dcc.Dropdown(
            id="chart-type",
            options=[
                {"label": "Line Chart", "value": "line"},
                {"label": "Bar Chart", "value": "bar"},
                {"label": "Pie Chart", "value": "pie"}
            ],
            value="line",
            clearable=False,
            className="mb-3"
        ), width=4)
    ]),

    # Graph Display
    dbc.Row([
        dbc.Col(dcc.Graph(id="main-chart"), width=8),
        dbc.Col(dcc.Graph(id="pie-chart"), width=4),
    ]),

    # Real-time Data Section
    dbc.Row([
        dbc.Col(html.H4("📡 Live Data Stream", className="mt-4"), width=12),
        dbc.Col(dcc.Graph(id="live-graph"), width=12),
    ]),

    # User Input Form
    dbc.Row([
        dbc.Col(html.H4("✍️ User Data Entry", className="mt-4"), width=12),
        dbc.Col(dbc.Input(id="user-input", type="text", placeholder="Enter something...", className="mb-3"), width=4),
        dbc.Col(dbc.Button("Submit", id="submit-btn", n_clicks=0, color="success"), width=2),
    ]),

    # Data Table
    dbc.Row([
        dbc.Col(html.H4("📋 Data Table", className="mt-4"), width=12),
        dbc.Col(dash_table.DataTable(
            id="data-table",
            columns=[{"name": i, "id": i} for i in df.columns],
            page_size=10,
            filter_action="native",
            sort_action="native",
            style_table={"overflowX": "auto"},
        ), width=12)
    ])
], fluid=True)

# Callbacks for Dynamic Updates

# Theme Toggle Callback
@app.callback(
    Output("theme-toggle", "children"),
    Input("theme-toggle", "n_clicks"),
)
def toggle_theme(n_clicks):
    return "Dark Mode" if n_clicks % 2 == 0 else "Light Mode"

# Chart Update Callback
@app.callback(
    Output("main-chart", "figure"),
    [Input("country-dropdown", "value"), Input("chart-type", "value")]
)
def update_chart(selected_country, chart_type):
    filtered_df = df[df["country"] == selected_country]

    if chart_type == "line":
        fig = px.line(filtered_df, x="year", y="gdpPercap", title=f"GDP Per Capita of {selected_country}")
    elif chart_type == "bar":
        fig = px.bar(filtered_df, x="year", y="gdpPercap", title=f"GDP Per Capita of {selected_country}")
    elif chart_type == "pie":
        fig = px.pie(filtered_df, names="year", values="gdpPercap", title=f"GDP Share Over Years")
    
    return fig

# Pie Chart Update
@app.callback(
    Output("pie-chart", "figure"),
    Input("country-dropdown", "value")
)
def update_pie_chart(selected_country):
    filtered_df = df[df["country"] == selected_country]
    fig = px.pie(filtered_df, names="year", values="pop", title=f"Population Distribution in {selected_country}")
    return fig

# Live Data Update
@app.callback(
    Output("live-graph", "figure"),
    Input("theme-toggle", "n_clicks")  # Dummy trigger to update every few seconds
)
def update_live_graph(_):
    global live_data
    fig = px.line(live_data, x="Time", y="Value", title="Live Sensor Data")
    return fig

# User Input Handling
@app.callback(
    Output("submit-btn", "children"),
    Input("submit-btn", "n_clicks"),
    State("user-input", "value")
)
def handle_user_input(n_clicks, user_input):
    if n_clicks > 0:
        return f"Submitted: {user_input}"
    return "Submit"

# Run app
if __name__ == "__main__":
    app.run_server(debug=True)

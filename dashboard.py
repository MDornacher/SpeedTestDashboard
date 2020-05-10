import pandas as pd
import plotly.express as px

import dash
import dash_core_components as dcc
import dash_html_components as html


df = pd.read_csv('speedtests.csv')
fig = px.line(df, x='Timestamp', y='Download')

app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])
app.run_server(host='0.0.0.0')

import os

import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


import dash
import dash_core_components as dcc
import dash_html_components as html


def fig_from_df_cols(df, x_col, y_cols):
    fig = make_subplots(rows=len(y_cols),
                        cols=1,
                        shared_xaxes=True
                        )

    for i, col_name in enumerate(y_cols, 1):
        fig.add_trace(
            go.Scatter(x=df[x_col],
                       y=df[col_name],
                       name=col_name,
                       mode='lines+markers',
                       ),
            row=i, col=1)
    return fig


df_speedtest = pd.read_csv(os.path.join('example', 'speedtests.csv'))

fig = fig_from_df_cols(df_speedtest, 'Timestamp', ['Download', 'Upload', 'Ping'])
fig.update_layout(title_text='Timeseries of Speedtests',
                  template='plotly_dark',
                  )


app = dash.Dash()
app.layout = html.Div([
    dcc.Graph(figure=fig)
])
app.run_server(host='0.0.0.0')

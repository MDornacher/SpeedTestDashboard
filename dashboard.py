from datetime import datetime
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


import dash
import dash_core_components as dcc
import dash_html_components as html


def fig_from_df_cols(df, x_col, y_cols):
    fig = make_subplots(rows=len(y_cols),
                        cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
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


def fig_from_df_cols_grouped(df, x_group, y_cols):
    fig = make_subplots(rows=len(y_cols),
                        cols=1,
                        shared_xaxes=True,
                        vertical_spacing=0.05,
                        )

    for i, col_name in enumerate(y_cols, 1):
        data_mean = df.groupby(x_group)[col_name].aggregate(np.mean)
        fig.add_trace(
            go.Scatter(x=data_mean.index.tolist(),
                       y=data_mean.values,
                       name=col_name,
                       mode='lines+markers',
                       ),
            row=i, col=1)
    return fig


def timedelta_from_utc():
    dt_now = datetime.now()
    dt_utc = datetime.utcnow()
    return dt_now - dt_utc


if __name__ == "__main__":
    # import data
    df_speedtest = pd.read_csv(os.path.join('example', 'speedtests.csv'))

    # convert timestamp
    df_speedtest['Timestamp'] = pd.to_datetime(df_speedtest['Timestamp'])
    df_speedtest['Timestamp'] = df_speedtest['Timestamp'] + timedelta_from_utc()

    # add groupable timestamp variations
    df_speedtest['Hour'] = [ts.hour for ts in df_speedtest['Timestamp']]
    df_speedtest['Weekday'] = [ts.weekday() for ts in df_speedtest['Timestamp']]
    df_speedtest['Week'] = [ts.week for ts in df_speedtest['Timestamp']]
    df_speedtest['Month'] = [ts.month for ts in df_speedtest['Timestamp']]
    df_speedtest['Year'] = [ts.year for ts in df_speedtest['Timestamp']]

    # prepare plots
    default_layout = {'template': 'plotly_dark',
                      'height': 600,
                      'width': 800,
                      }

    fig_timeseries = fig_from_df_cols(df_speedtest, 'Timestamp', ['Download', 'Upload', 'Ping'])
    fig_timeseries.update_layout(title_text='Timeseries of Speedtests',
                                 **default_layout
                                 )

    fig_mean = fig_from_df_cols_grouped(df_speedtest, 'Hour', ['Download', 'Upload', 'Ping'])
    fig_mean.update_layout(title_text='Hourly Average',
                           **default_layout
                           )
    # create dashboard
    app = dash.Dash()
    app.layout = html.Div([
        dcc.Graph(figure=fig_timeseries),
        dcc.Graph(figure=fig_mean),
    ])
    app.run_server(host='0.0.0.0')

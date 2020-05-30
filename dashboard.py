#!/bin/env python3

import os
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash
import dash_core_components as dcc
import dash_html_components as html
import sqlite3


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
        data_var = df.groupby(x_group)[col_name].aggregate(np.std)
        fig.add_trace(
            go.Scatter(x=data_mean.index.tolist(),
                       y=data_mean.values,
                       error_y=dict(type='data',
                                    array=data_var.values,
                                    visible=True,
                                    ),
                       name=col_name,
                       mode='lines+markers',
                       ),
            row=i, col=1)
    return fig


def con_db(db):
    return sqlite3.connect(db)


if __name__ == "__main__":
    db_con = con_db(os.path.join('example', 'mydb.db'))

    # import data
    df_speedtest = pd.read_sql('''select *
                                  from speedtest;''', db_con)
    # convert timestamp
    df_speedtest['timestamp'] = pd.to_datetime(df_speedtest['timestamp'])

    # add groupable timestamp variations
    df_speedtest['hour'] = [ts.hour for ts in df_speedtest['timestamp']]
    df_speedtest['weekday'] = [ts.weekday() for ts in df_speedtest['timestamp']]
    df_speedtest['week'] = [ts.week for ts in df_speedtest['timestamp']]
    df_speedtest['month'] = [ts.month for ts in df_speedtest['timestamp']]
    df_speedtest['year'] = [ts.year for ts in df_speedtest['timestamp']]

    # prepare plots
    default_layout = {'template': 'plotly_dark',
                      'height': 600,
                      'width': 800,
                      }

    fig_timeseries = fig_from_df_cols(df_speedtest, 'timestamp', ['download', 'upload', 'latency'])
    fig_timeseries.update_layout(title_text='Timeseries of Speedtests',
                                 **default_layout
                                 )

    fig_mean = fig_from_df_cols_grouped(df_speedtest, 'hour', ['download', 'upload', 'latency'])
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

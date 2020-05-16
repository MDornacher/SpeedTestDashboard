from datetime import datetime
import os

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import dash
import dash_core_components as dcc
import dash_html_components as html

import sqlite3
import csv
from tkinter import *
from tkinter.filedialog import askopenfilename


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


def timedelta_from_utc():
    dt_now = datetime.now()
    dt_utc = datetime.utcnow()
    return dt_now - dt_utc


def con_db(db):
    return sqlite3.connect(db)


def crt_table(con, table):
    con.execute(f'''create table if not exists {table}
                    (server_id char,
                     sponsor char,
                     server_name char,
                     timestamp char primary key,
                     distance char,
                     ping dec,
                     download dec,
                     upload dec,
                     share char,
                     ip_address char
                     );''')
    con.execute(f'''create temp table §{table} as 
                    select * from {table};''')


def fill_table(con, table, csv_file):
    cur = con.cursor()
    with open(csv_file) as fin:
        dr = csv.DictReader(fin)
        for line in dr:
            to_db = (line['Server ID'],
                     line['Sponsor'],
                     line['Server Name'],
                     line['Timestamp'],
                     line['Distance'],
                     line['Ping'],
                     line['Download'],
                     line['Upload'],
                     line['Share'],
                     line['IP Address'])
            cur.execute(f'''insert into §{table}
                            values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ;''', to_db)
            con.commit()
    cur.execute(f'''insert into {table}
                    select *
                    from §{table} a
                    where not exists(select 1
                                     from {table} b 
                                     where b.timestamp = a.timestamp);
                    ''')
    con.commit()
    con.close()


if __name__ == "__main__":
    # choose file
    root = Tk()
    root.withdraw()
    root.update()
    file = askopenfilename()
    root.destroy()
    while not file.endswith('.csv'):
        print('please pick a CSV file')
        file = askopenfilename()

    # import data
    df_speedtest = pd.read_csv(file)

    db_con = con_db(os.path.join('example', 'mydb.db'))
    crt_table(db_con, 'speedtest')
    fill_table(db_con, 'speedtest', file)

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

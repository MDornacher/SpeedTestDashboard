import os
import argparse
from tkinter import *
from tkinter.filedialog import askopenfilename

import pandas as pd
import sqlite3


def con_db(db):
    return sqlite3.connect(db)


def drop_table(con, table):
    con.execute(f'drop table {table};')


def crt_table(con, table):
    con.execute(f'''create table if not exists {table}
                    (timestamp char primary key,
                     server_name char,
                     server_id char,
                     latency int,
                     jitter int,
                     packet_loss int,
                     download int,
                     upload int,
                     downloaded_bytes int,
                     uploaded_bytes int,
                     share_url char
                     );''')
    con.execute(f'''create temp table §{table} as 
                    select * from {table};''')


def fill_table(con, table, q_df):
    cur = con.cursor()
    for index, row in q_df.iterrows():
        ts = str(row['Timestamp'])
        to_db = (ts,
                 row['server id'],
                 row['server name'],
                 row['latency'],
                 row['jitter'],
                 row['packet loss'],
                 row['download'],
                 row['upload'],
                 row['downloaded bytes'],
                 row['uploaded bytes'],
                 row['share url']
                 )
        cur.execute(f'''insert into §{table}
                        values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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


def split_file(f):
    x_path, x_name = os.path.split(f)
    x_name, x_ext = os.path.splitext(x_name)
    return x_path, x_name, x_ext


if __name__ == "__main__":
    # import data with parser
    parser = argparse.ArgumentParser(description='Visualize speed test results with plotly and dash')
    parser.add_argument('input_path', help='Path to CSV from speedtest')
    parser.add_argument('-d', '--drop', action='store_true', help='Drop Table if exists')
    args = parser.parse_args()

    # choose file
    if os.path.exists(args.input_path):
        file = args.input_path
    else:
        root = Tk()
        root.withdraw()
        root.update()
        file = askopenfilename()
        root.destroy()
        if not os.path.exists(file):
            raise ValueError(f'{file} does not exist')

    file_path, file_name, file_ext = split_file(file)

    # import data
    df_speedtest = pd.read_csv(file)

    # convert timestamp
    df_speedtest['Timestamp'] = pd.to_datetime(df_speedtest['Timestamp'])
    df_speedtest['Timestamp'] = df_speedtest['Timestamp'].dt.tz_localize('Europe/Vienna')


    # import into Database
    db_con = con_db(os.path.join('example', 'mydb.db'))
    crt_table(db_con, 'speedtest')
    fill_table(db_con, 'speedtest', df_speedtest)

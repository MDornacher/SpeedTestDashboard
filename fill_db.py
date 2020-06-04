#!/bin/env python3

import os
import pandas as pd
import mysql.connector
import re
import math


def mysql_con():
    mydb = mysql.connector.connect(host='192.168.0.2',
                                   user='adornacher',
                                   passwd='YellowAndDangerous=Bananen',
                                   auth_plugin='caching_sha2_password')

    cur = mydb.cursor()

    cur.execute("show databases;")
    exists = False
    for x in cur:
        if 'mydb' in x:
            exists = True
    if not exists:
        cur.execute("create database mydb")
    cur.close()
    mydb.close()

    return mysql.connector.connect(host='192.168.0.2',
                                   user='adornacher',
                                   passwd='YellowAndDangerous=Bananen',
                                   database='mydb',
                                   auth_plugin='caching_sha2_password')


def drop_table(cur, table):
    cur.execute(f'drop table {table};')


def crt_table(cur, table):
    cur.execute('show tables;')
    exists = False
    for x in cur:
        if table in x:
            exists = True
    if not exists:
        cur.execute(f'''create table {table}
                        (timestamp timestamp primary key,
                         server_name char(50),
                         server_id decimal(10,0),
                         latency decimal(20,10),
                         jitter decimal(20,10),
                         packet_loss decimal(20,10),
                         download decimal(20,0),
                         upload decimal(20,0),
                         downloaded_bytes decimal(20,0),
                         uploaded_bytes decimal(20,0),
                         share_url char(200)
                         );''')
    cur.execute(f'create temporary table if not exists §{table} (select * from {table});')


def fill_table(con, cur, table, q_df):
    for index, row in q_df.iterrows():
        ts = str(row['Timestamp'])[:19]
        name = re.search('\"(.+?)\"', row['server name']).group(1)
        if math.isnan(row['packet loss']):
            pack_loss = 0
        else:
            pack_loss = row['packet loss']
        sql = f'''insert into §{table}
                  values("{ts}",
                         "{name}",
                         {row['server id']},
                         {row['latency']},
                         {row['jitter']},
                         {pack_loss},
                         {row['download']},
                         {row['upload']},
                         {row['downloaded bytes']},
                         {row['uploaded bytes']},
                         "{row['share url']}");'''
        cur.execute(sql)
    cur.execute(f'''insert into {table}
                    select *
                    from §{table} a
                    where not exists(select 1
                                     from {table} b 
                                     where b.timestamp = a.timestamp);
                    ''')
    con.commit()


if __name__ == "__main__":
    file = os.path.join('example', 'speedtest.csv')

    # import data
    df_speedtest = pd.read_csv(file)

    # convert timestamp
    df_speedtest['Timestamp'] = pd.to_datetime(df_speedtest['Timestamp'])
    df_speedtest['Timestamp'] = df_speedtest['Timestamp'].dt.tz_localize('Europe/Vienna')

    # import into Database
    db_con = mysql_con()
    db_cur = db_con.cursor()
    crt_table(db_cur, 'speedtest')
    fill_table(db_con, db_cur, 'speedtest', df_speedtest)
    db_cur.close()
    db_con.close()

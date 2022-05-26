#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import sqlite3

con = sqlite3.connect('mydatabase.db')


def sql_fetch(con):
    cursor_obj = con.cursor()
    cursor_obj.execute(
        "SELECT name from sqlite_master where type='table'"
    )
    print(cursor_obj.fetchall())


if __name__ == "__main__":
    sql_fetch(con)

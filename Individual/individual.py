#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import argparse
import sqlite3
import typing as t
from pathlib import Path


def display_flights(flights: t.List[t.Dict[str, t.Any]]) -> None:
    """
    Отобразить список рейсов.
    """
    if flights:
        # Заголовок таблицы.
        line = '+-{}-+-{}-+-{}-+-{}-+'.format(
            '-' * 4,
            '-' * 30,
            '-' * 20,
            '-' * 15
        )
        print(line)
        print(
            '| {:^4} | {:^30} | {:^20} | {:^15} |'.format(
                "No",
                "Пункт назначения",
                "Номер рейса",
                "Тип самолёта"
            )
        )
        print(line)
        for idx, flight in enumerate(flights, 1):
            print(
                '| {:>4} | {:<30} | {:<20} | {:<15} |'.format(
                    idx,
                    flight.get('flight_destination', ''),
                    flight.get('flight_number', ''),
                    flight.get('airplane_type', 0)
                )
            )
            print(line)
    else:
        print("Список рейсов пуст.")


def create_db(database_path: Path) -> None:
    """
    Создать базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS flight_numbers (
        num_id INTEGER PRIMARY KEY AUTOINCREMENT,
        num_title TEXT NOT NULL
        )
        """
    )
    cursor.execute(
        """
    CREATE TABLE IF NOT EXISTS flights (
        flight_id INTEGER PRIMARY KEY AUTOINCREMENT,
        flight_destination TEXT NOT NULL,
        num_id INTEGER NOT NULL,
        airplane_type TEXT NOT NULL,
        FOREIGN KEY(num_id) REFERENCES flight_numbers(num_id)
        )
        """
    )
    conn.close()


def add_flight(
        database_path: Path,
        flight_destination: str,
        flight_number: str,
        airplane_type: int
) -> None:
    """
    Добавить рейс в базу данных.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT num_id FROM flight_numbers WHERE num_title = ?
        """,
        (flight_number,)
    )
    row = cursor.fetchone()
    if row is None:
        cursor.execute(
            """
            INSERT INTO flight_numbers (num_title) VALUES (?)
            """,
            (flight_number,)
        )
        num_id = cursor.lastrowid
    else:
        num_id = row[0]
    cursor.execute(
        """
        INSERT INTO flights (flight_destination, num_id, airplane_type)
        VALUES (?, ?, ?)
        """,
        (flight_destination, num_id, airplane_type)
    )
    conn.commit()
    conn.close()


def select_all(database_path: Path) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать все рейсы.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """SELECT flights.flight_destination, flight_numbers.num_title, 
        flights.airplane_type FROM flights INNER JOIN flight_numbers ON 
        flight_numbers.num_id = flights.num_id """
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "flight_destination": row[0],
            "flight_number": row[1],
            "airplane_type": row[2],
        }
        for row in rows
    ]


def select_flights(
        database_path: Path, air_type: str
) -> t.List[t.Dict[str, t.Any]]:
    """
    Выбрать все рейсы заданного типа.
    """
    conn = sqlite3.connect(database_path)
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT flights.flight_destination, flight_numbers.num_title, 
        flights.airplane_type
        FROM flights
        INNER JOIN flight_numbers ON flight_numbers.num_id = flights.num_id
        WHERE flights.airplane_type == ?
        """,
        (air_type,)
    )
    rows = cursor.fetchall()
    conn.close()
    return [
        {
            "flight_destination": row[0],
            "flight_number": row[1],
            "airplane_type": row[2],
        }
        for row in rows
    ]


def main(command_line=None):
    # Создать родительский парсер для определения имени файла.
    file_parser = argparse.ArgumentParser(add_help=False)
    file_parser.add_argument(
        "--db",
        action="store",
        required=False,
        default=str(Path.home() / "workers.db"),
        help="The database file name"
    )
    # Создать основной парсер командной строки.
    parser = argparse.ArgumentParser("workers")
    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0"
    )
    subparsers = parser.add_subparsers(dest="command")
    add = subparsers.add_parser(
        "add",
        parents=[file_parser],
        help="Add a new flight"
    )
    add.add_argument(
        "-d",
        "--dest",
        action="store",
        required=True,
        help="Flight destination"
    )
    add.add_argument(
        "-n",
        "--flight_num",
        action="store",
        help="The flight number"
    )
    add.add_argument(
        "-t",
        "--type",
        action="store",
        type=str,
        required=True,
        help="The airplane type"
    )
    _ = subparsers.add_parser(
        "display",
        parents=[file_parser],
        help="Display all flights"
    )
    select = subparsers.add_parser(
        "select",
        parents=[file_parser],
        help="Select the flights"
    )
    select.add_argument(
        "-T",
        "--type",
        action="store",
        type=str,
        required=True,
        help="The required type"
    )
    # Выполнить разбор аргументов командной строки.
    args = parser.parse_args(command_line)
    # Получить путь к файлу базы данных.
    db_path = Path(args.db)
    create_db(db_path)
    if args.command == "add":
        add_flight(db_path, args.dest, args.flight_num, args.type)
    elif args.command == "display":
        display_flights(select_all(db_path))
    elif args.command == "select":
        display_flights(select_flights(db_path, args.type))
        pass


if __name__ == "__main__":
    main()

import mysql.connector

db_connector = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="",
    database="pycrawl"
)

db = db_connector.cursor()


def get_results(sql, params):
    db.execute(sql, params)
    field_names = [i[0] for i in db.description]

    rows = []

    for row in db.fetchall():
        row_object = {}

        for index, f in enumerate(field_names):
            row_object[f] = row[index]

        rows.append(row_object)

    return rows


def query(sql, params):
    db.execute(sql, params)
    db_connector.commit()
    return db.rowcount
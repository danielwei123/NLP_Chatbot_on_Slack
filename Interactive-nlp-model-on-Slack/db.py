import pymysql.cursors
# import click
# from flask import current_app, g
# from flask.cli import with_appcontext
import json


def get_db():
    # if 'db' not in g:
    # mysql = MySQL()
    database = pymysql.connect(
        host='127.0.0.1',
        user='root',
        # password='BeyondLimits@400',
        # password='Beyond@L1m1ts',
        password='pass', # change to the password of your own mysql database for use
        db='test', # change to the database you wanna use
        charset='utf8mb4',
        # cursorclass=pymysql.cursors.DictCursor
    )
    return database


def close_db(e=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    with current_app.open_resource('schema.sql') as f:
        db.executescript(f.read().decode('utf8'))

# @click.command('init-db')
# @with_appcontext
def init_db_command():
    """ Clear the existing data and create new tables """
    init_db()
    click.echo('Initialized the database')


def init_app(app):
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


def print_polygons():
    connection = get_db()

    try:
        with connection.cursor() as cursor:
            sql = "SELECT POLY_ID, POLY_NAME, TYPE FROM POLYGON "
            cursor.execute(sql)
            print("POLYGONS:")
            for row in cursor:
                print(row)

    finally:
        connection.close()


def print_points(poly_id):
    connection = get_db()

    try:
        with connection.cursor() as cursor:
            sql = "SELECT COORD_X, COORD_Y FROM POINTS WHERE POLY_ID = %s" % (poly_id)
            cursor.execute(sql)
            print("POINTS:")
            for row in cursor:
                print(row)

    finally:
        connection.close()


def insert_polygon(poly_id, poly_name, poly_type):
    connection = get_db()

    try:
        cursor = connection.cursor()
        sql = """INSERT INTO POLYGON(POLY_ID, POLY_NAME, TYPE) VALUES (%s, %s, %s)"""
        cursor.execute(sql, (poly_id, poly_name, poly_type))
        connection.commit()

    finally:
        connection.close()


def insert_point(poly_id, point_id, coord_x, coord_y):
    connection = get_db()

    try:
        cursor = connection.cursor()
        # sql = "Insert into POINTS (point_id, coord_x, coord_y) VALUES (point_id, coord_x, coord_y)"
        # where POLY_ID = poly_id"

        # insert POINTS into SQL
        sql = """INSERT INTO POINTS(POLY_ID, POINT_ID, COORD_X, COORD_Y)
             VALUES (%s, %s, %s, %s)"""
        cursor.execute(sql, (poly_id, point_id, coord_x, coord_y))
        connection.commit()

    finally:
        connection.close()


def insert_coordinates(poly_id, polygon_string):
    coordinates = polygon_string["geometry"]["coordinates"]

    # point_id starting from 1000 * poly_id + 1 for each polygon
    point_id = 1000 * poly_id + 1

    coords = coordinates[0]
    coord_x = 0
    coord_y = 0
    for i in range(len(coords)):
        for j in range(len(coords[i])):
            if j == 0:
                coord_x = coords[i][j]
            else:
                coord_y = coords[i][j]
        insert_point(poly_id, point_id, coord_x, coord_y)
        point_id += 1

        coord_x = 0
        coord_y = 0


def get_polygon(poly_id):
    connection = get_db()

    try:
        cursor = connection.cursor()
        sql = """SELECT POLY_ID, POLY_NAME, TYPE FROM POLYGON WHERE (POLY_ID = %s)"""
        cursor.execute(sql, poly_id)
        result1 = cursor.fetchone()

        sql = """SELECT COORD_X, COORD_Y FROM POINTS WHERE (POLY_ID = %s)"""
        cursor.execute(sql, poly_id)
        result2 = cursor.fetchall()

    finally:
        connection.close()

    result = {'polygon': result1, 'points': result2}
    return result


def get_all_polygon():
    connection = get_db()

    polygons = []

    try:
        cursor = connection.cursor()
        sql = """SELECT COUNT(POLY_NAME) FROM POLYGON"""
        cursor.execute(sql)
        poly_num = cursor.fetchone()

        for i in range(1, poly_num[0] + 1):
            # polygon_string += str(get_polygon(i)) + "\n"
            polygons.append(get_polygon(i))

    finally:
        connection.close()

    # return polygon_string
    return polygons


def move_polygon(poly_name, dist_x, dist_y):
    connection = get_db()

    try:
        cursor = connection.cursor()
        
        sql = """SELECT POLY_ID FROM POLYGON WHERE (POLY_NAME = %s)"""
        cursor.execute(sql, poly_name)
        poly_id = cursor.fetchone()[0]

        sql = """SELECT POINT_ID, COORD_X, COORD_Y FROM POINTS WHERE (POLY_ID = %s)"""
        cursor.execute(sql, poly_id)
        result = cursor.fetchall()

        for point in result:
            point_id = point[0]
            x = point[1] + dist_x
            y = point[2] + dist_y

            sql = """UPDATE POINTS SET COORD_X = %s, COORD_Y = %s WHERE (POLY_ID = %s) AND (POINT_ID = %s)"""
            cursor.execute(sql, (x,y,poly_id,point_id))
            connection.commit()

    finally:
        connection.close()

# move point bases on new origin
def move_point(poly_name, point_id, new_x, new_y, origin_x, origin_y):
    connection = get_db()

    try:
        cursor = connection.cursor()
        
        sql = """SELECT POLY_ID FROM POLYGON WHERE (POLY_NAME = %s)"""
        cursor.execute(sql, poly_name)
        poly_id = cursor.fetchone()[0]

        sql = """SELECT POINT_ID, COORD_X, COORD_Y FROM POINTS WHERE (POLY_ID = %s) AND (POINT_ID = %s)"""
        cursor.execute(sql, (poly_id, point_id))
        point = cursor.fetchone()

        x = new_x + origin_x
        y = new_y + origin_y

        sql = """UPDATE POINTS SET COORD_X = %s, COORD_Y = %s WHERE (POLY_ID = %s) AND (POINT_ID = %s)"""
        cursor.execute(sql, (x,y,poly_id,point_id))
        connection.commit()

    finally:
        connection.close()

# given the name of a polygon, return its centroid coordinate
def center_cord(poly_name):
    connection = get_db()

    polygons = []

    try:
        cursor = connection.cursor()

        sql = """SELECT COUNT(POLY_NAME) FROM POLYGON WHERE (POLY_NAME = %s)"""
        cursor.execute(sql, poly_name)
        poly_num = cursor.fetchone()[0]
        
        # check if the polygon exists
        if poly_num == 0:
            return 'Sorry, the poly_name you entered does not exist.'

        sql = """SELECT POLY_ID FROM POLYGON WHERE (POLY_NAME = %s)"""
        cursor.execute(sql, poly_name)
        poly_id = cursor.fetchone()[0]

        sql = """SELECT COORD_X, COORD_Y FROM POINTS WHERE (POLY_ID = %s)"""
        cursor.execute(sql, poly_id)
        result = cursor.fetchall()

        sides = len(result)

        # check if it is a circle or polygon
        if sides > 1:
            result = result[:-1]
            sides -= 1

        avg_x = 0
        avg_y = 0

        for i in range(sides):
            avg_x += result[i][0]
            avg_y += result[i][1]

        avg_x /= sides
        avg_y /= sides

    finally:
        connection.close()

    return (avg_x, avg_y)
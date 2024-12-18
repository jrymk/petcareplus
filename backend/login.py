from flask import Blueprint, jsonify, request, session, render_template, url_for, current_app
from db import get_psql_conn


login = Blueprint("login", __name__)


@login.get('/login')
def serve_login_page():
    return render_template("login.html")


@login.post('/submit_login')
def submit_login():
    print(request.json)
    # Get data from frontend
    username = request.json['username']
    password = request.json['password']
    
    # Search for user
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT *
            FROM "USER"
            WHERE username = '{username}' AND password = '{password}'
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        if len(results) == 0:
            return jsonify({'success': 0, 'error': 'Wrong username or password.'})
        
        # Login success!
        session["login"] = True
        session["user_id"] = results[0][0]
        session["username"] = results[0][1]
        
        # Login as a doctor or as a client
        cur.execute(f"""
            SELECT *
            FROM DOCTOR
            WHERE doctor_id = '{session.get("user_id")}'
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        if len(results):
            session["role"] = "doctor"
        else:
            session["role"] = "client"
        
        # Return success json
        return jsonify({'success': 1})


@login.post('/submit_register')
def submit_register():
    # Get data from frontend
    username = "'" + request.json['username'] + "'"
    password = "'" + request.json['password'] + "'"
    contact = "'" + request.json['contact'] + "'"
    if contact == "''": contact = "NULL"  # the user left this blank
    email = "'" + request.json['email'] + "'"
    if email == "''": email = "NULL"
    
    # Search for user
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT *
            FROM "USER"
            WHERE username = {username}
        """)  # not commit: protect from unrepeatable read
        results = cur.fetchall()
        if len(results):  # duplicate username
            get_psql_conn().rollback()
            return jsonify({'success': 0, 'error': 'Duplicate username.'})
        
        # start registering
        try:
            cur.execute(f"""
                INSERT INTO "USER"(username, email, password, contact)
                VALUES({username}, {email}, {password}, {contact})
            """)
            get_psql_conn().commit()
        except:
            get_psql_conn().rollback()
            return jsonify({'success': 0, 'error': 'Failed to insert record.'})
        return jsonify({'success': 1})


@login.post('/logout')
def logout():
    session["login"] = False
    session["user_id"] = None
    session["username"] = None
    session["role"] = None
    return jsonify({'success': 1})


@login.post('/random_user_login')
def random_user_login():
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT user_id, username
            FROM "USER"
            WHERE user_id NOT IN (SELECT doctor_id FROM DOCTOR)
            ORDER BY random()
            LIMIT 1
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        if len(results) == 0:
            return jsonify({'success': 0, 'error': 'No user found.'})
        
        session["login"] = True
        session["user_id"] = results[0][0]
        session["username"] = results[0][1]
        session["role"] = "client"
        return jsonify({'success': 1})
    
    return jsonify({'success': 0, 'error': 'Failed to login.'})

@login.post('/random_doctor_login')
def random_doctor_login():
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT user_id, username
            FROM "USER" as u
            WHERE user_id IN (SELECT doctor_id FROM DOCTOR)
            ORDER BY random()
            LIMIT 1
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        if len(results) == 0:
            return jsonify({'success': 0, 'error': 'No doctor found.'})
        
        session["login"] = True
        session["user_id"] = results[0][0]
        session["username"] = results[0][1]
        session["role"] = "doctor"
        return jsonify({'success': 1})
    
    return jsonify({'success': 0, 'error': 'Failed to login.'})
from flask import (Blueprint, jsonify, request, session,
                    render_template, url_for, redirect)
from db import get_psql_conn
import pandas as pd
from datetime import datetime, timedelta


client_appointments = Blueprint("client_appointments", __name__)

###### serving pages ######
@client_appointments.get('/client-appointments')
def serve_client_appointment_page():
    if not session.get("login"):
        return redirect("/login")
    return render_template("client-appointments.html")

@client_appointments.get('/client-appointments/make')
def serve_client_appointment_make_page():
    if not session.get("login"):
        return redirect("/login")
    return render_template("client-appointments-make.html")


###### api calls ######
@client_appointments.post('/get_user_appointments_table')
def get_user_appointments():
    status = "'" + request.json['status'] + "'"
    
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT appointment_id, datetime, created_at,
                S.service_name, B.branch_name, D.name
            FROM APPOINTMENT AS AP
                JOIN SERVICE AS S ON AP.for_service = S.service_id
                JOIN BRANCH AS B ON AP.at_branch = B.branch_id
                JOIN DOCTOR AS D ON AP.chosen_doctor = D.doctor_id
            WHERE made_by_user = {session.get("user_id")}
                AND status = {status}
            ORDER BY datetime DESC, created_at DESC
            LIMIT 10
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        if len(results) == 0:  # user has no pets
            return jsonify({'tableHTML': "<p>No appointments found.</p>"})
        
        # convert query result into dataframe and return
        apps_df = pd.DataFrame(results, columns=[
            "appointment_id", "appointment time", "creation time", "service",
            "branch", "doctor"
        ])
        return jsonify({
            'tableHTML': apps_df.to_html(index=False)
        })


@client_appointments.post('/append_appointment')
def append_appointment():
    # Get data from frontend
    app_datetime = "'" + str(request.json['appDatetime']) + "'"
    app_service = "'" + request.json['appService'] + "'"
    app_branch = "'" + request.json['appBranch'] + "'"
    app_doctor = "'" + request.json['appDoctor'] + "'"
    app_pets = request.json['appPets']
    
    with get_psql_conn().cursor() as cur:
        # Get expected time for the service
        cur.execute(f"""
            SELECT duration FROM SERVICE WHERE service_id = {app_service}
        """)
        get_psql_conn().commit()
        service_time = cur.fetchone()[0]
        
        # compute expected end time and weekday of the service
        app_begin_dttime = datetime.strptime(app_datetime, "'%Y-%m-%dT%H:%M'")
        app_end_dttime = app_begin_dttime + timedelta(minutes=service_time)
        wkday = app_begin_dttime.strftime('%w')
        if wkday == '0': wkday = '7'  # Sunday
        
        # Check for operating hours
        cur.execute(f"""
            SELECT *
            FROM OPERATING_HOURS
            WHERE day = {wkday}
                AND branch_id = {app_branch}
                AND open_time <= '{app_begin_dttime}'
                AND '{app_end_dttime}' <= close_time
        """)
        get_psql_conn().commit()
        oh_results = cur.fetchall()
        if not len(oh_results):  # appointment is not within operating hours
            return jsonify({'success': 0, 'error': 'Appointment not within operating hours.'})
        
        # Check for doctor schedule
        cur.execute(f"""
            SELECT *
            FROM DOCTOR_AVAILABLE_SCHEDULE
            WHERE doctor_id = {app_doctor}
                AND available_from <= '{app_begin_dttime}'
                AND '{app_end_dttime}' <= available_to
        """)
        get_psql_conn().commit()
        das_results = cur.fetchall()
        if not len(das_results):  # appointment is not within doctor avail schedule
            return jsonify({'success': 0, 'error': "Appointment not within the doctor's available schedule."})
        
        # check for colliding appointments
        cur.execute(f"""
            SELECT A.datetime, S.duration
            FROM APPOINTMENT AS A
                JOIN SERVICE AS S ON A.for_service = S.service_id
            WHERE chosen_doctor = {app_doctor}
                AND DATE(datetime) = {app_datetime}
                AND status = 'P'
            FOR SHARE
        """)  # no commit: concurrency control
        flag = True
        for other_dttime, other_duration in cur.fetchall():
            other_begin_dttime = other_dttime
            other_end_dttime = other_begin_dttime + timedelta(minutes=other_duration)
            if (other_begin_dttime <= app_begin_dttime and 
                app_begin_dttime < other_end_dttime):
                flag = False
                break
            if (app_begin_dttime <= other_begin_dttime and 
                other_begin_dttime < app_end_dttime):
                flag = False
                break
        if not flag:  # appointment collides with other appointments
            get_psql_conn().commit()  # unlock APPOINTMENT
            return jsonify({'success': 0, 'error': "Appointment collides with other appointments."})
            
        
        # Insert the appointment
        try:
            cur.execute(f"""
                INSERT INTO APPOINTMENT(status, datetime, created_at,
                    made_by_user, for_service, at_branch, chosen_doctor)
                VALUES('P', {app_datetime}, '{datetime.now()}',
                    {session.get("user_id")}, {app_service}, {app_branch},
                    {app_doctor})
            """)
            
            cur.execute("""SELECT max(appointment_id) FROM APPOINTMENT""")
            app_id = f"'{cur.fetchone()[0]}'"
            for pet_id in app_pets:
                cur.execute(f"""
                    INSERT INTO PET_PARTICIPATION
                    VALUES('{pet_id}', {app_id})
                """)
            get_psql_conn().commit()
        except:
            get_psql_conn().rollback()
            return jsonify({'success': 0, 'error': 'Failed to insert record.'})
        return jsonify({'success': 1})
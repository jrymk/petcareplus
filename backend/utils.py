from flask import (Blueprint, jsonify, request, session,
                    render_template, url_for, redirect)
from db import get_psql_conn
import pandas as pd


utils = Blueprint("utils", __name__)


@utils.post('/get_user_pets')
def get_user_pets():
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT *
            FROM PET
            WHERE owned_by = {session.get("user_id")}
            ORDER BY pet_id ASC
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        
        return jsonify({
            'pets': results
        })


@utils.post('/get_branches')
def get_branches():
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT *
            FROM BRANCH
            WHERE branch_id <> 0
            ORDER BY branch_id ASC
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        
        return jsonify({
            'branches': results
        })


@utils.post('/get_branch_doctors')
def get_branch_doctors():
    branch = request.json['branch_id']
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT *
            FROM DOCTOR
            WHERE branch_id = {branch}
            ORDER BY doctor_id ASC
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        
        return jsonify({
            'doctors': results
        })


@utils.post('/get_branch_services')
def get_branch_services():
    branch = request.json['branch_id']
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT S.*, SO.service_cost
            FROM SERVICE_OFFERS AS SO
                JOIN SERVICE AS S ON SO.service_id = S.service_id
            WHERE branch_id = {branch}
            ORDER BY S.service_id ASC
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        
        return jsonify({
            'services': results
        })


@utils.post('/get_user_pending_appointments')
def get_user_pending_appointments():
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT appointment_id, datetime, created_at,
                S.service_name, B.branch_name, D.name
            FROM APPOINTMENT AS AP
                JOIN SERVICE AS S ON AP.for_service = S.service_id
                JOIN BRANCH AS B ON AP.at_branch = B.branch_id
                JOIN DOCTOR AS D ON AP.chosen_doctor = D.doctor_id
            WHERE made_by_user = {session.get("user_id")}
                AND status = 'P'
            ORDER BY appointment_id ASC
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        
        return jsonify({
            'apps': results
        })


@utils.post('/get_branch_opening_hours_table')
def get_branch_opening_hours_table():
    branch_id = request.json['branchId']
    
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT day, open_time, close_time
            FROM OPERATING_HOURS
            WHERE branch_id = {branch_id}
            ORDER BY day ASC, open_time ASC
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        if len(results) == 0:  # cannot find branch opening hours
            return jsonify({'tableHTML': "<p>No branch information found.</p>"})
        
        # convert query result into dataframe and return
        boh_df = pd.DataFrame(results, columns=[
            "day of the week", "open time", "close time"
        ])
        return jsonify({
            'tableHTML': boh_df.to_html(index=False)
        })


@utils.post('/get_doctor_available_hours_table')
def get_doctor_available_hours_table():
    doctor_id = request.json['doctorId']
    
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT available_from, available_to
            FROM DOCTOR_AVAILABLE_SCHEDULE
            WHERE doctor_id = {doctor_id}
            ORDER BY available_from ASC
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        if len(results) == 0:  # cannot find doctor available schedule
            return jsonify({'tableHTML': "<p>No doctor information found.</p>"})
        
        # convert query result into dataframe and return
        dah_df = pd.DataFrame(results, columns=[
            "available from", "available to"
        ])
        return jsonify({
            'tableHTML': dah_df.to_html(index=False)
        })


@utils.post('/user_get_existing_appointments_table')
def user_get_existing_appointments_table():
    app_datetime = "'" + str(request.json['appDatetime']) + "'"
    branch_id = "'" + request.json['branchId'] + "'"
    doctor_id = "'" + request.json['doctorId'] + "'"
    
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT A.datetime,
                (A.datetime + MAKE_INTERVAL(mins => CAST(S.duration AS INT)))
            FROM APPOINTMENT AS A
                JOIN SERVICE AS S ON A.for_service = S.service_id
            WHERE chosen_doctor = {doctor_id}
                AND at_branch = {branch_id}
                AND DATE(datetime) = {app_datetime}
                AND status = 'P'
            ORDER BY A.datetime ASC
        """)
        get_psql_conn().commit()  # not preventing unrepeatable read
        results = cur.fetchall()
        if len(results) == 0:  # cannot find any existing appointments
            return jsonify({'tableHTML': "<p>No existing appointments found.</p>"})
        
        
        # convert query result into dataframe and return
        eapp_df = pd.DataFrame(results, columns=[
            "from", "to"
        ])
        return jsonify({
            'tableHTML': eapp_df.to_html(index=False)
        })
    
@utils.get('/get_vaccine_names')
def get_vaccine_names():
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT vaccine_name
            FROM VACCINE
        """)
        get_psql_conn().commit()
        results = cur.fetchall()

        vaccines = [v[0] for v in results]
        
        return jsonify({
            'success': 1,
            'vaccines': vaccines
        })
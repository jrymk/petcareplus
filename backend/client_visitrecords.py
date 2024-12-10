from flask import (Blueprint, jsonify, request, session,
                    render_template, url_for, redirect)
from db import get_psql_conn
import pandas as pd
from datetime import datetime, timedelta


client_visitrecords = Blueprint("client_visitrecords", __name__)

###### serving pages ######
@client_visitrecords.get('/client-records')
def serve_client_appointment_page():
    if not session.get("login"):
        return redirect("/login")
    return render_template("client-visitrecords.html")


###### api calls ######
@client_visitrecords.post('/user_get_visit_records_table')
def user_get_visit_records_table():
    service_type = int(request.json['serviceType'])
    pet_id = request.json['petId']
    
    sel_items = [  # corresponds to service type
        None,
        'datetime, name, branch_name, general_observation, body_temp, pulse_rate, notes',
        'datetime, name, branch_name, symptoms, diagnosis, treatment_plan, follow_up',
        'datetime, name, branch_name, vaccine_name, vaccine_due'
    ]
    with get_psql_conn().cursor() as cur:
        cols = []
        if service_type == 1:
            cols = ['datetime', 'doctor name', 'branch name', 'general observation',
                'body temp', 'pulse rate', 'notes']
            cur.execute(f"""
                SELECT datetime, name, branch_name, general_observation,
                    body_temp, pulse_rate, notes
                FROM HEALTH_CHECK AS R
                    JOIN APPOINTMENT AS AP ON R.appointment_id = AP.appointment_id
                    JOIN BRANCH AS B ON AP.at_branch = B.branch_id
                    JOIN DOCTOR AS D ON AP.chosen_doctor = D.doctor_id
                WHERE R.pet_id = {pet_id}
                ORDER BY datetime DESC
                LIMIT 10
            """)
        elif service_type == 2:
            cols = ['datetime', 'doctor name', 'branch name', 'symptoms', 'diagnosis',
                'treatment plan', 'follow up info', "medicine name", "dosage",
                "frequency", "duration", "notes"]
            cur.execute(f"""
                SELECT datetime, name, branch_name, symptoms, diagnosis,
                    treatment_plan, follow_up, medicine_name, dosage, frequency,
                    duration, notes
                FROM DIAGNOSIS AS R
                    JOIN APPOINTMENT AS AP ON R.appointment_id = AP.appointment_id
                    JOIN BRANCH AS B ON AP.at_branch = B.branch_id
                    JOIN DOCTOR AS D ON AP.chosen_doctor = D.doctor_id
                    LEFT JOIN PRESCRIPTIONS AS P ON R.pet_id = P.pet_id
                        AND R.appointment_id = P.appointment_id
                WHERE R.pet_id = {pet_id}
                ORDER BY datetime DESC
                LIMIT 10
            """)
        else:
            cols = ['datetime', 'doctor name', 'branch name', 'vaccine name',
                'vaccine due']
            cur.execute(f"""
                SELECT datetime, name, branch_name, R.vaccine_name,
                    datetime + MAKE_INTERVAL(months => next_due_span) AS vaccine_due
                FROM VACCINATION AS R
                    JOIN VACCINE AS V ON R.vaccine_name = V.vaccine_name
                    JOIN APPOINTMENT AS AP ON R.appointment_id = AP.appointment_id
                    JOIN BRANCH AS B ON AP.at_branch = B.branch_id
                    JOIN DOCTOR AS D ON AP.chosen_doctor = D.doctor_id
                WHERE R.pet_id = {pet_id}
                ORDER BY datetime DESC, vaccine_due ASC
                LIMIT 10
            """)
        get_psql_conn().commit()
        results = cur.fetchall()
        if len(results) == 0:
            return jsonify({'tableHTML': "<p>No visit records found.</p>"})
        
        # convert query result into dataframe and return
        records_df = pd.DataFrame(results, columns=cols)
        return jsonify({
            'tableHTML': records_df.to_html(index=False)
        })
        
        
        

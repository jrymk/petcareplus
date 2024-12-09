import datetime
from flask import (Blueprint, jsonify, request, session,
                    render_template, url_for, redirect)
from db import get_psql_conn
import pandas as pd


doctor_schedule = Blueprint("doctor_schedule", __name__)

@doctor_schedule.get('/doctor-home')
def serve_doctor_home():
    if not session.get("login"):
        return redirect("/login")
    
    return render_template("doctor-home.html")


@doctor_schedule.post('/get_doctor_schedule')
def get_doctor_schedule():
    if not session.get("login") or session.get("role") != "doctor":
        return jsonify({'success': 0, 'error': 'Unauthorized access.'})

    data = request.get_json()
    week_offset = data.get('weekOffset', 0)

    try:
        with get_psql_conn().cursor() as cur:
            cur.execute(f"""
                SELECT a.datetime, u.username, u.contact, p.name, a.status, s.service_name, s.description, s.duration, b.branch_name
                FROM APPOINTMENT as a
                JOIN "USER" as u ON a.made_by_user = u.user_id
                JOIN PET_PARTICIPATION as pp ON pp.appointment_id = a.appointment_id
                JOIN PET as p ON pp.pet_id = p.pet_id
                JOIN SERVICE as s ON a.for_service = s.service_id
                JOIN BRANCH as b ON a.at_branch = b.branch_id
                WHERE a.chosen_doctor = {session.get("user_id")}
                AND a.datetime >= date_trunc('week', now()) + ({week_offset} * interval '1 week')
                AND a.datetime < date_trunc('week', now()) + ({week_offset + 1} * interval '1 week')
                ORDER BY a.datetime ASC
            """)
            results = cur.fetchall()

            # Process results into a dictionary with days of the week as keys
            schedule = {day: [] for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']}
            for row in results:
                day_of_week = row[0].strftime('%a')
                schedule[day_of_week].append(row)

            # Determine the maximum number of appointments in a single day
            max_appointments = max(len(appointments) for appointments in schedule.values())

            # Generate HTML table
            tableHTML = "<table table-layout='fixed'><thead><tr>"
            for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
                date = (datetime.datetime.now() + datetime.timedelta(days=(week_offset * 7) + (['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'].index(day) - datetime.datetime.now().weekday()))).strftime('%Y-%m-%d')
                if date == datetime.datetime.now().strftime('%Y-%m-%d'):
                    color = '#FF8888' if day[0] == 'S' else '#88FFFF'
                else:
                    color = '#FFDDDD' if day[0] == 'S' else '#DDFFFF'
                tableHTML += f"<th width='120pt' style='border-width: 1px; background-color: {color}'>{day}<br>{date}</th>"
            tableHTML += "</tr></thead><tbody>"

            for i in range(max_appointments):
                tableHTML += "<tr>"
                for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']:
                    if i < len(schedule[day]):
                        appointment = schedule[day][i]
                        tableHTML += f"<td style='border-width: 1px; background-color: {'#DDDDDD' if appointment[4] == 'O' else '#FFDDDD' if appointment[4] == 'C' else '#DDFFDD'}'>"
                        tableHTML += f"{appointment[1]}<br>{appointment[2]}<br>{appointment[3]}<br>"
                        tableHTML += f"<span title={appointment[6]}>{appointment[5]}</span> <span style='color: #888888'>{
                            (str(appointment[7] // 60) + "小時") if (appointment[7] // 60) != 0 else ""
                            + (str(appointment[7] % 60) + "分鐘") if (appointment[7] % 60) != 0 else ""}</span>"
                        tableHTML += f"<br>{appointment[8]}"
                        tableHTML += f"<br><a href='todo'>Enter</a></td>"
                    else:
                        tableHTML += "<td style='border-width: 1px'></td>"
                tableHTML += "</tr>"

            tableHTML += "</tbody></table>"
            return jsonify({'tableHTML': tableHTML})
    except Exception as e:
        get_psql_conn().rollback()
        return jsonify({'tableHTML': f"<p>Failed to retrieve schedule. Error: {str(e)}</p>"})
    finally:
        get_psql_conn().commit()

    

# @client_mypets.post('/get_user_pets')
# def get_user_pets():
#     with get_psql_conn().cursor() as cur:
#         cur.execute(f"""
#             SELECT *
#             FROM PET
#             WHERE owned_by = {session.get("user_id")}
#             ORDER BY pet_id ASC
#         """)
#         get_psql_conn().commit()
#         results = cur.fetchall()
#         if len(results) == 0:  # user has no pets
#             return jsonify({'tableHTML': "<p>You don't have any pets yet.</p>"})
        
#         # convert query result into dataframe and return
#         pets_df = pd.DataFrame(results, columns=[
#             "pet_id", "name", "species", "breed", "bdate", "gender", "owned_by"
#         ])
#         pets_df = pets_df.drop(columns=["pet_id", "owned_by"])
        
#         return jsonify({
#             'tableHTML': pets_df.to_html(index=False)
#         })


# @client_mypets.post('/append_pet')
# def append_pet():
#     # Get data from frontend
#     pet_name = request.json['petName']
#     pet_species = request.json['petSpecies']
#     pet_breed = request.json['petBreed']
#     pet_bdate = request.json['petBdate']
#     pet_gender = request.json['petGender']
    
#     with get_psql_conn().cursor() as cur:
#         cur.execute(f"""
#             SELECT *
#             FROM PET
#             WHERE owned_by = {session.get("user_id")}
#         """)
#         get_psql_conn().commit()
#         results = cur.fetchall()
#         if len(results) >= 5:  # check num. of pets
#             return jsonify({'success': 0, 'error': 'A user can only register 5 pets.'})
        
#         # Insert the pet data
#         print(pet_name, pet_species, pet_breed, str(pet_bdate), pet_gender)
#         cur.execute(f"""
#             INSERT INTO PET(name, species, breed, bdate, gender, owned_by)
#             VALUES('{pet_name}', '{pet_species}', '{pet_breed}',
#                    '{str(pet_bdate)}', '{pet_gender}', {session.get("user_id")})
#         """)
#         get_psql_conn().commit()
#         return jsonify({'success': 1})
import datetime
from flask import (Blueprint, jsonify, request, session,
                    render_template, url_for, redirect)
from db import get_psql_conn
import pandas as pd


doctor_appointment = Blueprint("doctor_appointment", __name__)

@doctor_appointment.get('/doctor-appointment')
def serve_doctor_appointment():
    if not session.get("login"):
        return redirect("/login")
    
    appointment_id = request.args.get('appointment_id')
    pet_id = request.args.get('pet_id', None)
    return render_template("doctor-appointment.html", 
                           appointment_id=appointment_id,
                           pet_id=pet_id,
                           username=session.get("username"))


@doctor_appointment.get('/get_appointment_details')
def get_appointment_details():
    if not session.get("login") or session.get("role") != "doctor":
        return jsonify({'success': 0, 'error': 'Unauthorized access.'})

    appointment_id = request.args.get('appointment_id')
    appointment_details = dict()

    try:
        with get_psql_conn().cursor() as cur:
            cur.execute(f"""
                SELECT * FROM APPOINTMENT
                WHERE appointment_id = {appointment_id}
            """)
            get_psql_conn().commit()
            results = cur.fetchall()
            if len(results) == 0:
                return jsonify({'success': 0, 'error': 'Appointment not found.'})
            # elif results[0][7] != session.get("user_id"):
            #     return jsonify({'success': 0, 'error': 'Unauthorized access. You are not the chosen doctor for this appointment.'})

            cur.execute(f"""
                SELECT a.status, a.chosen_doctor, u.username, u.contact, s.service_name, s.description, s.duration, p.pet_id, p.name, p.species, p.breed, p.bdate, p.gender
                FROM APPOINTMENT as a
                JOIN "USER" as u ON a.made_by_user = u.user_id
                JOIN SERVICE as s ON a.for_service = s.service_id
                JOIN PET_PARTICIPATION as pp ON a.appointment_id = pp.appointment_id
                JOIN PET as p ON pp.pet_id = p.pet_id
                WHERE a.appointment_id = {appointment_id}
                ORDER BY p.pet_id ASC
            """)
            results = cur.fetchall()
            if len(results) == 0:
                return jsonify({'success': 0, 'error': 'No pets registered for this appointment.'})
            
            is_chosen_doctor = False
            if session.get("login"):
                if session.get("user_id") == results[0][1]:
                    is_chosen_doctor = True

            # convert query result into {username, contact, ..., pet: {pet_id, name, species, ...}}
            appointment_details = {
                'status': results[0][0] + ('!' if is_chosen_doctor else ''),
                'chosen_doctor': results[0][1],
                'username': results[0][2],
                'contact': results[0][3],
                'service_name': results[0][4],
                'service_description': results[0][5],
                'service_duration': results[0][6],
                'pets': []
            }
            for row in results:
                appointment_details['pets'].append({
                    'pet_id': row[7],
                    'name': row[8],
                    'species': row[9],
                    'breed': row[10],
                    'bdate': row[11],
                    'age': (datetime.datetime.now().date() - row[11]).days,
                    'gender': row[12]
                })
    except Exception as e:
        get_psql_conn().rollback()
        print(str(e))
        return jsonify({'success': 0, 'error': str(e)})
    finally:
        get_psql_conn().commit()
        return jsonify({'success': 1, 'appointment': appointment_details})


@doctor_appointment.get('/get_pet_appointments')
def get_pet_appointments():
    if not session.get("login") or session.get("role") != "doctor":
        return jsonify({'success': 0, 'error': 'Unauthorized access.'})

    pet_id = request.args.get('pet_id')
    # count = request.args.get('count', 100)
    if pet_id is None:
        return jsonify({'success': 0, 'error': 'Pet ID not provided.'})

    try:
        with get_psql_conn().cursor() as cur:
            cur.execute(f"""
                SELECT a.appointment_id, a.status, a.datetime, s.service_name, dt.name, hc.general_observation, hc.body_temp, hc.pulse_rate, d.symptoms, d.diagnosis, v.vaccine_name
                FROM APPOINTMENT as a
                LEFT JOIN DOCTOR as dt ON a.chosen_doctor = dt.doctor_id
                LEFT JOIN SERVICE as s ON a.for_service = s.service_id
                JOIN PET_PARTICIPATION as pp ON a.appointment_id = pp.appointment_id AND pp.pet_id = {pet_id}
                LEFT JOIN HEALTH_CHECK as hc ON a.appointment_id = hc.appointment_id AND hc.pet_id = {pet_id}
                LEFT JOIN DIAGNOSIS as d ON a.appointment_id = d.appointment_id AND d.pet_id = {pet_id}
                LEFT JOIN VACCINATION as v ON a.appointment_id = v.appointment_id AND v.pet_id = {pet_id}
                WHERE a.status <> 'C'
                ORDER BY a.datetime DESC
            """)
            results = cur.fetchall()
            
            new_results = dict()
            for row in results:
                if new_results.get(row[0]) is None:
                    new_results[row[0]] = dict()
                    new_results[row[0]]['appointment_id'] = row[0]
                    new_results[row[0]]['status'] = row[1]
                    new_results[row[0]]['datetime'] = row[2]
                    new_results[row[0]]['service'] = row[3]
                    new_results[row[0]]['doctor'] = row[4]
                    new_results[row[0]]['general_observation'] = row[5]
                    new_results[row[0]]['body_temp'] = row[6]
                    new_results[row[0]]['pulse_rate'] = row[7]
                    new_results[row[0]]['symptoms'] = row[8]
                    new_results[row[0]]['diagnosis'] = row[9]
                    new_results[row[0]]['vaccine_name'] = [row[10]]
                else:
                    new_results[row[0]]['vaccine_name'].append(row[10])
            results = sorted(new_results.values(), key=lambda x: x['datetime'], reverse=True)
    
    except Exception as e:
        get_psql_conn().rollback()
        print(str(e))
        return jsonify({'success': 0, 'error': str(e)})
    finally:
        get_psql_conn().commit()
        return jsonify({'success': 1, 'appointments': results})
    
@doctor_appointment.post('/archive')
def archive_appointment():
    if not session.get("login") or session.get("role") != "doctor":
        return jsonify({'success': 0, 'error': 'Unauthorized access.'})

    appointment_id = request.json['appointment_id']
    try:
        with get_psql_conn().cursor() as cur:
            cur.execute(f"""
                SELECT chosen_doctor FROM APPOINTMENT
                WHERE appointment_id = {appointment_id}
            """)
            results = cur.fetchall()
            if len(results) == 0:
                return jsonify({'success': 0, 'error': 'Appointment not found.'})
            elif results[0][0] != session.get("user_id"):
                return jsonify({'success': 0, 'error': 'Unauthorized access. You are not the chosen doctor for this appointment.'})

            cur.execute(f"""
                UPDATE APPOINTMENT
                SET status = 'O'
                WHERE appointment_id = {appointment_id}
            """)
    except Exception as e:
        get_psql_conn().rollback()
        print(str(e))
        return jsonify({'success': 0, 'error': str(e)})
    finally:
        get_psql_conn().commit()
        return jsonify({'success': 1})
    
@doctor_appointment.post('/cancel')
def cancel_appointment():
    if not session.get("login") or session.get("role") != "doctor":
        return jsonify({'success': 0, 'error': 'Unauthorized access.'})

    appointment_id = request.json['appointment_id']
    try:
        with get_psql_conn().cursor() as cur:
            cur.execute(f"""
                SELECT chosen_doctor FROM APPOINTMENT
                WHERE appointment_id = {appointment_id}
            """)
            results = cur.fetchall()
            if len(results) == 0:
                return jsonify({'success': 0, 'error': 'Appointment not found.'})
            elif results[0][0] != session.get("user_id"):
                return jsonify({'success': 0, 'error': 'Unauthorized access. You are not the chosen doctor for this appointment.'})

            cur.execute(f"""
                UPDATE APPOINTMENT
                SET status = 'C'
                WHERE appointment_id = {appointment_id}
            """)
    except Exception as e:
        get_psql_conn().rollback()
        print(str(e))
        return jsonify({'success': 0, 'error': str(e)})
    finally:
        get_psql_conn().commit()
        return jsonify({'success': 1})
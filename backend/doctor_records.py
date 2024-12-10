import datetime
from flask import (Blueprint, jsonify, request, session,
                    render_template, url_for, redirect)
from db import get_psql_conn
import pandas as pd


doctor_records = Blueprint("doctor_records", __name__)


@doctor_records.get('/get_pet_record')
def get_pet_record():
    if not session.get("login") or session.get("role") != "doctor":
        return jsonify({'success': 0, 'error': 'Unauthorized access.'})

    pet_id = request.args.get('pet_id')
    appointment_id = request.args.get('appointment_id')
    if pet_id is None or appointment_id is None:
        return jsonify({'success': 0, 'error': 'Pet ID or appointment ID not provided.'})

    health_check, diagnosis, prescriptions, vaccination = None, None, None, None

    try:
        with get_psql_conn().cursor() as cur:
            cur.execute(f"""
                SELECT hc.general_observation, hc.body_temp, hc.pulse_rate, hc.notes
                FROM HEALTH_CHECK as hc
                WHERE hc.pet_id = {pet_id} AND hc.appointment_id = {appointment_id}
            """)
            health_check = cur.fetchall()
            print(health_check)
            
            cur.execute(f"""
                SELECT d.symptoms, d.diagnosis, d.treatment_plan, d.follow_up
                FROM DIAGNOSIS as d
                WHERE pet_id = {pet_id} AND appointment_id = {appointment_id}
            """)
            diagnosis = cur.fetchall()

            cur.execute(f"""
                SELECT ps.medicine_name, ps.dosage, ps.frequency, ps.duration, ps.notes
                FROM PRESCRIPTIONS as ps
                WHERE pet_id = {pet_id} AND appointment_id = {appointment_id}
            """)
            prescriptions = cur.fetchall()

            cur.execute(f"""
                SELECT v.vaccine_name, vc.next_due_span
                FROM VACCINATION as v
                JOIN VACCINE as vc ON v.vaccine_name = vc.vaccine_name
                WHERE pet_id = {pet_id} AND appointment_id = {appointment_id}
            """)
            vaccination = cur.fetchall()

        if len(health_check) == 0:
            health_check = None
        else:
            new_health_check = dict()
            new_health_check['general_observation'] = health_check[0][0]
            new_health_check['body_temp'] = health_check[0][1]
            new_health_check['pulse_rate'] = health_check[0][2]
            new_health_check['notes'] = health_check[0][3]
            health_check = new_health_check
        
        if len(diagnosis) == 0:
            diagnosis = None
        else:
            new_diagnosis = dict()
            new_diagnosis['symptoms'] = diagnosis[0][0]
            new_diagnosis['diagnosis'] = diagnosis[0][1]
            new_diagnosis['treatment_plan'] = diagnosis[0][2]
            new_diagnosis['follow_up'] = diagnosis[0][3]
            diagnosis = new_diagnosis

        new_prescriptions = []
        for i in range(len(prescriptions)):
            new_prescription = dict()
            new_prescription['medicine_name'] = prescriptions[i][0]
            new_prescription['dosage'] = prescriptions[i][1]
            new_prescription['frequency'] = prescriptions[i][2]
            new_prescription['duration'] = prescriptions[i][3]
            new_prescription['notes'] = prescriptions[i][4]
            new_prescriptions.append(new_prescription)
        prescriptions = new_prescriptions

        new_vaccination = []
        for i in range(len(vaccination)):
            new_vaccine = dict()
            new_vaccine['vaccine_name'] = vaccination[i][0]
            new_vaccine['due_span'] = vaccination[i][1]
            current_date = datetime.datetime.now()
            new_month = (current_date.month + vaccination[i][1] - 1) % 12 + 1
            new_year = current_date.year + ((current_date.month + vaccination[i][1] - 1) // 12)
            print(new_year, new_month)
            new_vaccine['due_date'] = current_date.replace(year=new_year, month=new_month)
            new_vaccination.append(new_vaccine)
        vaccination = new_vaccination

    except Exception as e:
        get_psql_conn().rollback()
        print(str(e))
        return jsonify({'success': 0, 'error': str(e)})
    finally:
        get_psql_conn().commit()
        return jsonify({'success': 1, 'health_check': health_check, 'diagnosis': diagnosis, 'prescriptions': prescriptions, 'vaccination': vaccination})


@doctor_records.post('/update-health-check')
def update_health_check():
    print(request.json)
    # Get data from frontend
    pet_id = request.json['pet_id']
    appointment_id = request.json['appointment_id']
    general_observation = "'" + request.json['general_observation'] + "'"
    body_temp = request.json['body_temp']
    try:
        body_temp = float(body_temp)
    except ValueError:
        body_temp = 'NULL'
    pulse_rate = request.json['pulse_rate']
    try:
        pulse_rate = int(pulse_rate)
    except ValueError:
        pulse_rate = 'NULL'
    notes = "'" + request.json['notes'] + "'"

    print("inserting", pet_id, appointment_id, general_observation, body_temp, pulse_rate, notes)

    with get_psql_conn().cursor() as cur:
        try:
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
                UPDATE HEALTH_CHECK
                SET general_observation = {general_observation}, body_temp = {body_temp}, pulse_rate = {pulse_rate}, notes = {notes}
                WHERE pet_id = {pet_id} AND appointment_id = {appointment_id}
            """)
            if cur.rowcount == 0:
                cur.execute(f"""
                    INSERT INTO HEALTH_CHECK (pet_id, appointment_id, general_observation, body_temp, pulse_rate, notes)
                    VALUES ({pet_id}, {appointment_id}, {general_observation}, {body_temp}, {pulse_rate}, {notes})
                """)
        
        except Exception as e:
            get_psql_conn().rollback()
            print(str(e))
            return jsonify({'success': 0, 'error': str(e)})
        finally:
            get_psql_conn().commit()
            return jsonify({'success': 1})


@doctor_records.post('/update-diagnosis')
def update_diagnosis():
    # Get data from frontend
    pet_id = request.json['pet_id']
    appointment_id = request.json['appointment_id']
    symptoms = "'" + request.json['symptoms'] + "'"
    diagnosis = "'" + request.json['diagnosis'] + "'"
    treatment_plan = "'" + request.json['treatment_plan'] + "'"
    follow_up = "'" + request.json['follow_up'] + "'"

    with get_psql_conn().cursor() as cur:
        try:
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
                UPDATE DIAGNOSIS
                SET symptoms = {symptoms}, diagnosis = {diagnosis}, treatment_plan = {treatment_plan}, follow_up = {follow_up}
                WHERE pet_id = {pet_id} AND appointment_id = {appointment_id}
            """)
            if cur.rowcount == 0:
                cur.execute(f"""
                    INSERT INTO DIAGNOSIS (pet_id, appointment_id, symptoms, diagnosis, treatment_plan, follow_up)
                    VALUES ({pet_id}, {appointment_id}, {symptoms}, {diagnosis}, {treatment_plan}, {follow_up})
                """)
        
        except Exception as e:
            get_psql_conn().rollback()
            print(str(e))
            return jsonify({'success': 0, 'error': str(e)})
        finally:
            get_psql_conn().commit()
            return jsonify({'success': 1})
        
@doctor_records.post('/insert-prescription')
def insert_prescription():
    # Get data from frontend
    pet_id = request.json['pet_id']
    appointment_id = request.json['appointment_id']
    medicine_name = "'" + request.json['medicine_name'] + "'"
    dosage = "'" + request.json['dosage'] + "'"
    frequency = "'" + request.json['frequency'] + "'"
    duration = "'" + request.json['duration'] + "'"
    notes = "'" + request.json['notes'] + "'"

    with get_psql_conn().cursor() as cur:
        try:
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
                INSERT INTO PRESCRIPTIONS (pet_id, appointment_id, medicine_name, dosage, frequency, duration, notes)
                VALUES ({pet_id}, {appointment_id}, {medicine_name}, {dosage}, {frequency}, {duration}, {notes})
            """)
        
        except Exception as e:
            get_psql_conn().rollback()
            print(str(e))
            return jsonify({'success': 0, 'error': str(e)})
        finally:
            get_psql_conn().commit()
            return jsonify({'success': 1})
        
@doctor_records.post('/delete-prescription')
def delete_prescription():
    # Get data from frontend
    pet_id = request.json['pet_id']
    appointment_id = request.json['appointment_id']
    medicine_name = "'" + request.json['medicine_name'] + "'"

    with get_psql_conn().cursor() as cur:
        try:
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
                DELETE FROM PRESCRIPTIONS
                WHERE pet_id = {pet_id} AND appointment_id = {appointment_id} AND medicine_name = {medicine_name}
            """)
        
        except Exception as e:
            get_psql_conn().rollback()
            print(str(e))
            return jsonify({'success': 0, 'error': str(e)})
        finally:
            get_psql_conn().commit()
            return jsonify({'success': 1})
        
@doctor_records.post('/insert-vaccination')
def insert_vaccination():
    # Get data from frontend
    pet_id = request.json['pet_id']
    appointment_id = request.json['appointment_id']
    vaccine_name = "'" + request.json['vaccine_name'] + "'"

    with get_psql_conn().cursor() as cur:
        try:
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
                INSERT INTO VACCINATION (pet_id, appointment_id, vaccine_name)
                VALUES ({pet_id}, {appointment_id}, {vaccine_name})
            """)
        
        except Exception as e:
            get_psql_conn().rollback()
            print(str(e))
            return jsonify({'success': 0, 'error': str(e)})
        finally:
            get_psql_conn().commit()
            return jsonify({'success': 1})
        
@doctor_records.post('/delete-vaccination')
def delete_vaccination():
    # Get data from frontend
    pet_id = request.json['pet_id']
    appointment_id = request.json['appointment_id']
    vaccine_name = "'" + request.json['vaccine_name'] + "'"

    with get_psql_conn().cursor() as cur:
        try:
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
                DELETE FROM VACCINATION
                WHERE pet_id = {pet_id} AND appointment_id = {appointment_id} AND vaccine_name = {vaccine_name}
            """)
        
        except Exception as e:
            get_psql_conn().rollback()
            print(str(e))
            return jsonify({'success': 0, 'error': str(e)})
        finally:
            get_psql_conn().commit()
            return jsonify({'success': 1})
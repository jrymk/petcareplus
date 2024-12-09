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
    branch = "'" + request.json['branch_id'] + "'"
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
    branch = "'" + request.json['branch_id'] + "'"
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
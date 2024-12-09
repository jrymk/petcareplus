from flask import (Blueprint, jsonify, request, session,
                    render_template, url_for, redirect)
from db import get_psql_conn
import pandas as pd


client_mypets = Blueprint("client_mypets", __name__)


@client_mypets.get('/client-mypets')
def serve_mypet_page():
    if not session.get("login"):
        return redirect("/login")
    
    return render_template("client-mypets.html")


@client_mypets.post('/get_user_pets')
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
        if len(results) == 0:  # user has no pets
            return jsonify({'tableHTML': "<p>You don't have any pets yet.</p>"})
        
        # convert query result into dataframe and return
        pets_df = pd.DataFrame(results, columns=[
            "pet_id", "name", "species", "breed", "bdate", "gender", "owned_by"
        ])
        pets_df = pets_df.drop(columns=["pet_id", "owned_by"])
        
        return jsonify({
            'tableHTML': pets_df.to_html(index=False)
        })


@client_mypets.post('/append_pet')
def append_pet():
    # Get data from frontend
    pet_name = "'" + request.json['petName'] + "'"
    pet_species = "'" + request.json['petSpecies'] + "'"
    pet_breed = "'" + request.json['petBreed'] + "'"
    if pet_breed == "''": pet_breed = "NULL"  # pet_breed is left blank
    pet_bdate = "'" + str(request.json['petBdate']) + "'"
    if pet_bdate == "''": pet_bdate = "NULL"  # pet_breed is left blank
    pet_gender = "'" + request.json['petGender'] + "'"
    
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT *
            FROM PET
            WHERE owned_by = {session.get("user_id")}
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        if len(results) >= 5:  # check num. of pets
            return jsonify({'success': 0, 'error': 'A user can only register 5 pets.'})
        
        # Insert the pet data
        cur.execute(f"""
            INSERT INTO PET(name, species, breed, bdate, gender, owned_by)
            VALUES({pet_name}, {pet_species}, {pet_breed},
                   {pet_bdate}, {pet_gender}, {session.get("user_id")})
        """)
        get_psql_conn().commit()
        return jsonify({'success': 1})
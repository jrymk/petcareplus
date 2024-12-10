from flask import (Blueprint, jsonify, request, session,
                    render_template, url_for, redirect)
from db import get_psql_conn
import pandas as pd
from datetime import datetime, timedelta


client_bills = Blueprint("client_bills", __name__)

###### serving pages ######
@client_bills.get('/client-bills')
def serve_client_appointment_page():
    if not session.get("login"):
        return redirect("/login")
    return render_template("client-bills.html")


###### api calls ######
@client_bills.post('/get_bill_with_status')
def get_bill_with_status():
    bill_pmt_status = "'" + request.json['pStatus'] + "'"
    
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT bill_id
            FROM BILL AS B
                JOIN APPOINTMENT AS A ON B.created_by_appointment = A.appointment_id
                JOIN "USER" AS U ON A.made_by_user = U.user_id
            WHERE payment_status = {bill_pmt_status}
                AND user_id = {session.get("user_id")}
            ORDER BY bill_id DESC
        """)
        get_psql_conn().commit()
        results = cur.fetchall()
        return jsonify({
            'bill_ids': results
        })


@client_bills.post('/get_bill_details')
def get_bill_details():
    bill_id = request.json['billId'] 
    
    with get_psql_conn().cursor() as cur:
        cur.execute(f"""
            SELECT B.created_by_appointment, B.created_at, SUM(BD.amount),
                B.paid_at, B.payment_method
            FROM BILL AS B
                JOIN BILL_DETAILS AS BD ON B.bill_id = BD.bill_id
            WHERE B.bill_id = {bill_id}
            GROUP BY B.created_by_appointment, B.created_at, B.paid_at, B.payment_method
        """)
        get_psql_conn().commit()
        bill_results = cur.fetchall()
        bill_df = pd.DataFrame(bill_results, columns=[
            "appointment id", "created at", "total amount", "paid at", "payment method"  
        ])
        bill_df["payment method"] = bill_df["payment method"].map({
            'C': "Cash", 'W': "Wire Transfer", "E": "Electronic Payment", 'O': "Other"
        })
        
        cur.execute(f"""
            SELECT item, amount
            FROM BILL_DETAILS
            WHERE bill_id = {bill_id}
        """)
        get_psql_conn().commit()
        bill_item_results = cur.fetchall()
        bill_item_df = pd.DataFrame(bill_item_results, columns=[
            "item", "amount"
        ])
        
        return jsonify({
            'billHTML': bill_df.to_html(index=False),
            'billDetailsHTML': bill_item_df.to_html(index=False)
        })
        
        

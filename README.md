# PetCare+
Try the demo out at [https://petcareplus.jerrymk.uk](https://petcareplus.jerrymk.uk)!

PetCare+ is a management platform for animal hospitals. It allows users to make an appointment online, check medical records, etc., and the doctor can check the schedule and fill in check in results, diagnoses, etc.

This is a demonstration program and is not production-ready.

For deployment guide, go to [Deploying](#deploying)

---

### Doctor Schedule Page
![image](https://github.com/user-attachments/assets/59d41850-b588-4045-a051-79af288459c0)

---

### Fill in check in results, diagnosis, prescriptions, and vaccines
![image](https://github.com/user-attachments/assets/8a857193-9f4c-41aa-8a30-276551e10970)

---

### Check past medical records
![image](https://github.com/user-attachments/assets/81e4ef80-403b-4c5f-8b3c-f0adb07eab8f)

---

### Log in page
![image](https://github.com/user-attachments/assets/27639a7d-4a0f-44b7-9817-b8572d1d8390)

---

### User pet management
![image](https://github.com/user-attachments/assets/e23ebfe4-bfbc-4e63-a556-44b618bbaf01)

---

### Check appointments
![image](https://github.com/user-attachments/assets/54f3eae0-af68-457a-a9b8-a9a9ec86c039)

---

### Making an appointment
![image](https://github.com/user-attachments/assets/2e0a2234-9287-42d2-886a-4c871e5d4dfe)

---

### Check medical records
![image](https://github.com/user-attachments/assets/34dc3820-666b-4483-af35-c65cc8512c56)

---

## Deploying

Deploying yourself require an environment variable file located at the `backend` folder. 

It should look something like this:
```
POSTGRES_HOST=jerrymk.uk
POSTGRES_PORT=5558
POSTGRES_DB=petcareplus
POSTGRES_USER="obfuscated"
POSTGRES_PASSWORD="obfuscated"
```

You may use the `.sql` and backup files located in the `database` folder to set up your own database server.

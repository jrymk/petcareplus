CREATE TABLE IF NOT EXISTS SERVICE (
	Service_Id BIGINT NOT NULL,
	Service_Name VARCHAR(20) NOT NULL,
	Description VARCHAR(100),
	Duration BIGINT NOT NULL,
	Primary Key(Service_Id),
	Unique(Service_Name)
);

CREATE TABLE IF NOT EXISTS BRANCH (
	Branch_Id BIGINT NOT NULL,
	Branch_Name VARCHAR(20) NOT NULL,
	Address VARCHAR(50),
	Contact VARCHAR(20),
	Primary Key(Branch_Id),
	Unique(Branch_Name)
);

CREATE TABLE IF NOT EXISTS OPERATING_HOURS(
	Branch_Id BIGINT NOT NULL,
	Day INT NOT NULL,
	Open_Time TIME NOT NULL,
	Close_Time TIME NOT NULL,
	Primary Key(Branch_Id, Day, Open_Time, Close_Time),
	Foreign Key(Branch_Id) REFERENCES BRANCH(Branch_Id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS SERVICE_OFFERS(
	Branch_Id BIGINT NOT NULL,
	Service_Id BIGINT NOT NULL,
	Service_Cost INT NOT NULL,
	Primary Key(Branch_Id, Service_Id),
	Foreign Key(Branch_Id) REFERENCES BRANCH(Branch_Id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	Foreign Key(Service_Id) REFERENCES SERVICE(Service_Id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS "USER" (
	User_Id BIGSERIAL NOT NULL,
	Username VARCHAR(20) NOT NULL,
	Email VARCHAR(50),
	Password VARCHAR(50) NOT NULL,
	Contact VARCHAR(20),
	Primary Key(User_Id),
	Unique(Username)
);

CREATE TABLE IF NOT EXISTS DOCTOR (
	Doctor_Id BIGINT NOT NULL,
	Name VARCHAR(10) NOT NULL,
	Specialty VARCHAR(50),
	Contact VARCHAR(20),
	Branch_Id BIGINT NOT NULL DEFAULT 0,
	Primary Key(Doctor_Id),
	Foreign Key(Doctor_Id) REFERENCES "USER"(User_Id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	Foreign Key(Branch_Id) REFERENCES BRANCH(Branch_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS DOCTOR_AVAILABLE_SCHEDULE (
	Doctor_Id BIGINT NOT NULL,
	Available_From TIME NOT NULL,
	Available_To TIME NOT NULL,
	Primary Key(Doctor_Id, Available_From, Available_To),
	Foreign Key(Doctor_Id) REFERENCES DOCTOR(Doctor_Id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS PET (
	Pet_Id BIGSERIAL NOT NULL,
	Name VARCHAR(20) NOT NULL,
	Species VARCHAR(20) NOT NULL,
	Breed VARCHAR(20),
	Bdate DATE,
	Gender CHAR NOT NULL,
	Owned_By BIGINT NOT NULL DEFAULT 0,
	Primary Key(Pet_Id),
	Foreign Key(Owned_By) REFERENCES "USER"(User_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS APPOINTMENT (
	Appointment_Id BIGSERIAL NOT NULL,
	Status CHAR NOT NULL,
	Datetime TIMESTAMP NOT NULL,
	Created_At TIMESTAMP NOT NULL,
	Made_By_User BIGINT NOT NULL DEFAULT 0,
	For_Service BIGINT NOT NULL DEFAULT 0,
	At_Branch BIGINT NOT NULL DEFAULT 0,
	Chosen_Doctor BIGINT NOT NULL DEFAULT 0,
	Primary Key(Appointment_Id),
	Foreign Key(Made_By_User) REFERENCES "USER"(User_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE,
	Foreign Key(For_Service) REFERENCES SERVICE(Service_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE,
	Foreign Key(At_Branch) REFERENCES BRANCH(Branch_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE,
	Foreign Key(Chosen_Doctor) REFERENCES DOCTOR(Doctor_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS PET_PARTICIPATION (
	Pet_Id BIGINT NOT NULL,
	Appointment_Id BIGINT NOT NULL,
	Foreign Key(Pet_Id) REFERENCES PET(Pet_Id)
		ON DELETE CASCADE
		ON UPDATE CASCADE,
	Foreign Key(Appointment_Id) REFERENCES APPOINTMENT(Appointment_Id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS BILL (
	Bill_Id BIGSERIAL NOT NULL,
	Created_At TIMESTAMP NOT NULL,
	Payment_Status CHAR NOT NULL,
	Payment_Method CHAR,
	Paid_At TIMESTAMP,
	Created_By_Appointment BIGINT NOT NULL DEFAULT 0,
	Primary Key(Bill_Id),
	Foreign Key(Created_By_Appointment) REFERENCES APPOINTMENT(Appointment_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS BILL_DETAILS (
	Bill_Id BIGINT NOT NULL,
	Item VARCHAR(50) NOT NULL,
	Amount INT NOT NULL,
	Primary Key(Bill_Id, Item, Amount),
	Foreign Key(Bill_Id) REFERENCES BILL(Bill_Id)
		ON DELETE CASCADE
		ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS HEALTH_CHECK (
	General_Observation VARCHAR(500),
	Body_Temp FLOAT,
	Pulse_Rate INT,
	Notes VARCHAR(100),
	Pet_Id BIGINT NOT NULL DEFAULT 0,
	Appointment_Id BIGINT NOT NULL DEFAULT 0,
	Primary Key(Pet_Id, Appointment_Id),
	Foreign Key(Pet_Id) REFERENCES PET(Pet_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE,
	Foreign Key(Appointment_Id) REFERENCES APPOINTMENT(Appointment_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS DIAGNOSIS (
	Symptoms VARCHAR(50) NOT NULL,
	Diagnosis VARCHAR(50) NOT NULL,
	Treatment_Plan VARCHAR(50) NOT NULL,
	Follow_Up VARCHAR(50),
	Pet_Id BIGINT NOT NULL DEFAULT 0,
	Appointment_Id BIGINT NOT NULL DEFAULT 0,
	Primary Key(Pet_Id, Appointment_Id),
	Foreign Key(Pet_Id) REFERENCES PET(Pet_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE,
	Foreign Key(Appointment_Id) REFERENCES APPOINTMENT(Appointment_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS PRESCRIPTIONS (
	Medicine_Name VARCHAR(20) NOT NULL,
	Dosage VARCHAR(20) NOT NULL,
	Frequency VARCHAR(20) NOT NULL,
	Duration VARCHAR(20) NOT NULL,
	Notes VARCHAR(100),
	Pet_Id BIGINT NOT NULL DEFAULT 0,
	Appointment_Id BIGINT NOT NULL DEFAULT 0,
	Primary Key(Medicine_Name, Pet_Id, Appointment_Id),
	Foreign Key(Pet_Id) REFERENCES PET(Pet_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE,
	Foreign Key(Appointment_Id) REFERENCES APPOINTMENT(Appointment_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE
);

CREATE TABLE IF NOT EXISTS VACCINE (
	Vaccine_Name VARCHAR(20) NOT NULL,
	Next_Due_Span INT NOT NULL,
	Primary Key(Vaccine_Name)
);

CREATE TABLE IF NOT EXISTS VACCINATION (
	Pet_Id BIGINT NOT NULL DEFAULT 0,
	Appointment_Id BIGINT NOT NULL DEFAULT 0,
	Vaccine_Name VARCHAR(20) NOT NULL DEFAULT 'default',
	Primary Key(Pet_Id, Appointment_Id, Vaccine_Name),
	Foreign Key(Pet_Id) REFERENCES PET(Pet_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE,
	Foreign Key(Appointment_Id) REFERENCES APPOINTMENT(Appointment_Id)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE,
	Foreign Key(Vaccine_Name) REFERENCES VACCINE(Vaccine_Name)
		ON DELETE SET DEFAULT
		ON UPDATE CASCADE
);
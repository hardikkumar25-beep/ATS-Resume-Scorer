import json
import mysql.connector

conn = mysql.connector.connect(
    host="localhost",
    user="root",
    password="12345",
    database="resume_data"
)

cursor = conn.cursor()

def insert_resume_from_json(data):
    query = """
    INSERT INTO resumes (name, email, skills, experience, raw_json)
    VALUES (%s, %s, %s, %s, %s)
    """

    skills_str = json.dumps(data["skills"])  
    exp_str = json.dumps(data["experience"]) 

    values = (
        data["name"],
        data["email"],
        skills_str,
        exp_str,
        json.dumps(data)  
    )

    cursor.execute(query, values)
    conn.commit()
    return cursor.lastrowid 

def insert_job(jd):
    query = """
    INSERT INTO job_descriptions (title, required_skills, preferred_skills, required_experience, jd_json)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        json.dumps(jd["job_title"]),
        json.dumps(jd["required_skills"]),
        json.dumps(jd["preferred_skills"]),
        json.dumps(jd["experience_years"]),
        json.dumps(jd)
    )

    cursor.execute(query, values)
    conn.commit()
    return cursor.lastrowid 

def insert_score(score_json, resume_id, job_id, improvements):
    query = """
    INSERT INTO scores (resume_id, jd_id, overall_score, breakdown, improvements)
    VALUES (%s, %s, %s, %s, %s)
    """

    values = (
        resume_id,
        job_id,
        score_json["overall_score"],
        json.dumps(score_json),
        improvements
    )

    cursor.execute(query, values)
    conn.commit()
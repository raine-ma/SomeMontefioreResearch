import csv
import sqlite3
from datetime import datetime
from dateutil.relativedelta import relativedelta
import os

CHUNK_SIZE = 999  

def calculate_age(visit_date_str, year_of_birth, month_of_birth):
    """
    Compute age (in full years) at visit_date_str, given year and month of birth.
    We assume day of birth is the 1st if only year/month is known.
    """
    if not visit_date_str or not year_of_birth or not month_of_birth:
        return None

    try:
        visit_date = datetime.strptime(visit_date_str, "%Y-%m-%d")
    except ValueError:

        return None

    try:
        birth_date = datetime(int(year_of_birth), int(month_of_birth), 1)
    except ValueError:
        return None

    age_delta = relativedelta(visit_date, birth_date)
    return age_delta.years

def fetch_person_data(conn, person_ids_batch):
    """
    Fetch rows from PERSON for a list of person_ids in one query.
    Returns a dict keyed by PERSON_ID, e.g.:
    {
        1234: {'GENDER_CONCEPT_ID': 8507, 'RACE_CONCEPT_ID': ..., ...},
        5678: {...},
        ...
    }
    """

    if not person_ids_batch:
        return {}

    placeholders = ",".join("?" for _ in person_ids_batch)
    query = f"""
        SELECT
            PERSON_ID,
            GENDER_CONCEPT_ID,
            RACE_CONCEPT_ID,
            ETHNICITY_CONCEPT_ID,
            YEAR_OF_BIRTH,
            MONTH_OF_BIRTH
        FROM PERSON
        WHERE PERSON_ID IN ({placeholders})
    """

    cursor = conn.execute(query, person_ids_batch)
    rows = cursor.fetchall()

    result_dict = {}
    for row in rows:
        person_id = row[0]
        result_dict[person_id] = {
            'GENDER_CONCEPT_ID': row[1],
            'RACE_CONCEPT_ID': row[2],
            'ETHNICITY_CONCEPT_ID': row[3],
            'YEAR_OF_BIRTH': row[4],
            'MONTH_OF_BIRTH': row[5]
        }

    return result_dict

def process_chunk(chunk, conn, writer, base_fieldnames):
    """
    - Extract unique PERSON_IDs from the chunk.
    - Fetch the corresponding records from PERSON in a single query.
    - For each row in the chunk, compute AGE, and write out to CSV.
    """

    person_ids = []
    for row in chunk:
        pid_str = row.get("PERSON_ID", "")
        try:
            pid = int(pid_str)
            person_ids.append(pid)
        except ValueError:

            continue

    person_data_dict = fetch_person_data(conn, person_ids)

    for row in chunk:
        pid_str = row.get("PERSON_ID", "")
        try:
            pid = int(pid_str)
        except ValueError:

            pid = None

        if pid and pid in person_data_dict:
            pinfo = person_data_dict[pid]
            row["GENDER_CONCEPT_ID"] = pinfo['GENDER_CONCEPT_ID']
            row["RACE_CONCEPT_ID"] = pinfo['RACE_CONCEPT_ID']
            row["ETHNICITY_CONCEPT_ID"] = pinfo['ETHNICITY_CONCEPT_ID']

            year_of_birth = pinfo['YEAR_OF_BIRTH']
            month_of_birth = pinfo['MONTH_OF_BIRTH']
            visit_date_str = row.get("VISIT_START_DATE", "")
            row["AGE"] = calculate_age(visit_date_str, year_of_birth, month_of_birth)
        else:

            row["GENDER_CONCEPT_ID"] = None
            row["RACE_CONCEPT_ID"] = None
            row["ETHNICITY_CONCEPT_ID"] = None
            row["AGE"] = None

        writer.writerow({fn: row.get(fn, None) for fn in base_fieldnames})

def main():
    input_csv_path = r"F:\Raine\all_visits.csv"
    output_csv_path = r"F:\Raine\all_visits_updated1.csv"
    sqlite_path = r"F:\AllMontefiore2024August.sqlite"

    conn = sqlite3.connect(sqlite_path)

    with open(input_csv_path, 'r', newline='', encoding='utf-8') as infile, \
         open(output_csv_path, 'w', newline='', encoding='utf-8') as outfile:

        reader = csv.DictReader(infile)

        base_fieldnames = reader.fieldnames + [
            'GENDER_CONCEPT_ID',
            'RACE_CONCEPT_ID',
            'ETHNICITY_CONCEPT_ID',
            'AGE'
        ]
        writer = csv.DictWriter(outfile, fieldnames=base_fieldnames)
        writer.writeheader()

        chunk = []
        for row in reader:
            chunk.append(row)

            if len(chunk) >= CHUNK_SIZE:
                process_chunk(chunk, conn, writer, base_fieldnames)
                chunk = []

        if chunk:
            process_chunk(chunk, conn, writer, base_fieldnames)

    c

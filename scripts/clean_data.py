import duckdb
con = duckdb.connect()

con.execute("""
COPY (
  SELECT DISTINCT name, type, lon, lat FROM (
    SELECT
      CASE
        WHEN regexp_matches(eng, '[A-Za-z]') THEN eng
        ELSE full_name
      END AS name,
      type, lon, lat
    FROM (
      SELECT
        trim(name) AS full_name,
        trim(regexp_extract(trim(name), '.* - (.*)$', 1)) AS eng,
        CASE
          WHEN category = 'hospital' THEN 'Hospital'
          WHEN category = 'dental_clinic' THEN 'Dental'
          WHEN category = 'diagnostics_imaging_or_lab_service' THEN 'Lab / Diagnostics'
          WHEN category = 'specialized_health_care' THEN 'Specialist'
          WHEN category LIKE '%pharmac%' THEN 'Pharmacy'
          ELSE 'Clinic / Doctor'
        END AS type,
        round(lon, 5) AS lon,
        round(lat, 5) AS lat
      FROM 'pune_health.csv'
      WHERE name IS NOT NULL
        AND trim(name) <> ''
        AND confidence >= 0.5
        AND lon BETWEEN 73.70 AND 74.05
        AND lat BETWEEN 18.40 AND 18.65
    )
  )
) TO 'pune_health_clean.csv' (HEADER, DELIMITER ',')
""")

print("before:", con.execute("SELECT count(*) FROM 'pune_health.csv'").fetchone()[0])
print("after: ", con.execute("SELECT count(*) FROM 'pune_health_clean.csv'").fetchone()[0])
print(con.execute("SELECT type, count(*) FROM 'pune_health_clean.csv' GROUP BY 1 ORDER BY 2 DESC").fetchall())
print("still Marathi-only:", con.execute("SELECT count(*) FROM 'pune_health_clean.csv' WHERE NOT regexp_matches(name, '[A-Za-z]')").fetchone()[0])
print(con.execute("SELECT name FROM 'pune_health_clean.csv' LIMIT 8").fetchall())

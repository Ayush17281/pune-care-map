import duckdb
con = duckdb.connect()
con.execute("INSTALL spatial; LOAD spatial; INSTALL httpfs; LOAD httpfs; SET s3_region='us-west-2';")

RELEASE = "2026-10-21.0"
SRC = f"s3://overturemaps-us-west-2/release/{RELEASE}/theme=places/type=place/*"

con.execute(f"""
COPY (
  SELECT names.primary AS name,
         basic_category AS category,
         bbox.xmin AS lon,
         bbox.ymin AS lat,
         confidence
  FROM read_parquet('{SRC}')
  WHERE bbox.xmin BETWEEN 73.70 AND 74.05
    AND bbox.ymin BETWEEN 18.40 AND 18.65
    AND (basic_category IN ('hospital','dental_clinic','specialized_health_care','diagnostics_imaging_or_lab_service')
         OR basic_category LIKE '%pharmac%'
         OR basic_category LIKE '%clinic%'
         OR basic_category LIKE '%doctor%')
) TO 'pune_health.csv' (HEADER, DELIMITER ',')
""")

print(con.execute("SELECT category, count(*) FROM 'pune_health.csv' GROUP BY 1 ORDER BY 2 DESC").fetchall())

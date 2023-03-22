import os
import requests
import psycopg2
import hashlib



# Get the values of the environment variables
db_host = os.getenv('DB_HOST')
db_name = os.getenv('DB_NAME')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
api_key = os.getenv('API_KEY')
api_email = os.getenv('API_EMAIL')



# Set up a connection to the Postgres database
conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)

# Set up a cursor to execute SQL commands
cur = conn.cursor()

# Define the search criteria
headers = {
    'Host': 'data.usajobs.gov',
    'Authorization-Key': api_key,
    'User-Agent': api_email
}
email = 'recruiting@tasman.ai'
response = requests.get('https://data.usajobs.gov/api/search?Keyword=data engineering', headers=headers)


results = response.json()



# Define the SQL statement to create the table
create_table_sql = """
CREATE TABLE IF NOT EXISTS usajobs (
    key TEXT PRIMARY KEY, 
    position_title VARCHAR(255) NOT NULL,
    position_uri VARCHAR(255) NOT NULL,
    posting_date_str VARCHAR(255) NOT NULL,
    position_city VARCHAR(255) NOT NULL,
    position_country VARCHAR(255) NOT NULL,
    position_remuneration_min VARCHAR(50) NOT NULL,
    position_remuneration_max VARCHAR(50) NOT NULL,
    position_description VARCHAR(255) NOT NULL
);
"""

cur.execute(create_table_sql)





# Iterate over the results and insert them into the Postgres database
for result in results['SearchResult']['SearchResultItems']:
    position_title = result['MatchedObjectDescriptor']['PositionTitle']
    position_uri = result['MatchedObjectDescriptor']['PositionURI']
    posting_date_str = result['MatchedObjectDescriptor']['PublicationStartDate']

    for location in result['MatchedObjectDescriptor']['PositionLocation']:
        position_city = location['CityName']
        position_country = location['CountryCode']

    for remuneration in result['MatchedObjectDescriptor']['PositionRemuneration']:
        position_remuneration_min = remuneration['MinimumRange']
        position_remuneration_max = remuneration['MaximumRange']
        position_description = remuneration['Description']

    # Create a hash object
    hash_object = hashlib.sha256()

    # Hash the values
    hash_object.update(str(position_title).encode('utf-8'))
    hash_object.update(str(position_uri).encode('utf-8'))
    hash_object.update(str(posting_date_str).encode('utf-8'))
    hash_object.update(str(position_city).encode('utf-8'))
    hash_object.update(str(position_country).encode('utf-8'))
    hash_object.update(str(position_remuneration_min).encode('utf-8'))
    hash_object.update(str(position_remuneration_max).encode('utf-8'))
    hash_object.update(str(position_description).encode('utf-8'))

    # Get the hashed value
    hashed_key = hash_object.hexdigest()
    

    # Insert the data into the Postgres database
    cur.execute(f"""INSERT INTO usajobs (key, position_title, position_uri, position_city, 
    position_country, position_remuneration_min, position_remuneration_max, position_description,posting_date_str) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""" , 
    (hashed_key, position_title,position_uri,position_city,position_country,position_remuneration_min,position_remuneration_max,position_description,posting_date_str))


# Commit the changes to the database
conn.commit()

# Close the database connection
cur.close()
conn.close()

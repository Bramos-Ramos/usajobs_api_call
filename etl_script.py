import os
import requests
import psycopg2
import hashlib

def get_database_connection(db_host,db_name,db_user,db_password):
    """
    Returns a connection object to the Postgres database
    """
    
    try:
        conn = psycopg2.connect(
            host=db_host, 
            database=db_name, 
            user=db_user, 
            password=db_password
        )
        return conn
    except psycopg2.Error as e:
        print("Error connecting to database: ", e)

def create_usajobs_table(conn):

    # Creates the 'usajobs' table in the Postgres database

    create_table_sql = """
    CREATE TABLE IF NOT EXISTS usajobs (
        key TEXT PRIMARY KEY, 
        position_title VARCHAR(255) NOT NULL,
        position_uri VARCHAR(255) NOT NULL,
        position_city VARCHAR(255) NOT NULL,
        position_country VARCHAR(255) NOT NULL,
        position_remuneration_min VARCHAR(50) NOT NULL,
        position_remuneration_max VARCHAR(50) NOT NULL,
        position_description VARCHAR(255) NOT NULL,
        posting_date_str VARCHAR(255) NOT NULL
    );
    """

    cur = conn.cursor()
    cur.execute(create_table_sql)
    conn.commit()
    cur.close()


def api_call(api_key,api_email,keyword):
    # Define the search criteria
    try:
        # Define the search criteria
        headers = {
            'Host': 'data.usajobs.gov',
            'Authorization-Key': api_key,
            'User-Agent': api_email
        }
        response = requests.get(f'https://data.usajobs.gov/api/search?Keyword={keyword}', headers=headers)


        results = response.json()
        return results
    except requests.exceptions.RequestException as e:
        print("Error in API call: ", e)


def insert_result(conn, columns):
     # Insert the data into the Postgres database
    try:
        # Insert the data into the Postgres database
        cur = conn.cursor()
        for row in columns:
            cur.execute(f"""INSERT INTO usajobs (key, position_title, position_uri, position_city, 
            position_country, position_remuneration_min, position_remuneration_max, position_description,posting_date_str) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""" , 
            (row[0], row[1],row[2],row[3],row[4],row[5],row[6],row[7],row[8]))

        conn.commit()
        cur.close()
    except psycopg2.Error as e:
        print("Error inserting data: ", e)
        

def iterate_result(results):
    columns = []
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

        column = [hashed_key, position_title, position_uri, posting_date_str, position_city, position_country, 
        position_remuneration_min, position_remuneration_max, position_description]

        columns.append(column)
    return columns

# Define the main function
def main():
    # Get the values of the environment variables
    db_host = os.getenv('DB_HOST')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    api_key = os.getenv('API_KEY')
    api_email = os.getenv('API_EMAIL')
    keyword = 'data engineering'


    # Set up a connection to the Postgres database
    conn = psycopg2.connect(host=db_host, database=db_name, user=db_user, password=db_password)

    # Create the table if it does not exist
    create_usajobs_table(conn)

    results = api_call(api_key, api_email, keyword)

    # interate_res

    columns = iterate_result(results)

    insert_result(conn,columns)


main()

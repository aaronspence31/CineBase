import ast
import mysql.connector  # pip install mysql-connector-python to get this package


config = {
    "user": "db_user",
    "password": "your_password",
    "host": "localhost",
    "database": "cinebase_db",
    "raise_on_warnings": True,
}

# Connect to the database
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()


# Handling data from TempJsonStringDataTableCredits
# Batch processing is used here to prevent server timeout
batch_size = 20
offset = 0
continue_processing = True

while continue_processing:
    # Prepare bulk insert data for new tables
    bulk_data_participants = []
    bulk_data_cast = []
    bulk_data_crew = []

    credits_query = f"SELECT tmdbId, rawCast, rawCrew FROM TempJsonStringDataTableCredits LIMIT {batch_size} OFFSET {offset}"
    cursor.execute(credits_query)
    rows = cursor.fetchall()

    if not rows:
        continue_processing = False  # Exit loop if no more data
        break
    else:
        for tmdbId, rawCast, rawCrew in rows:
            # Process cast members
            try:
                cast_members = ast.literal_eval(rawCast)
            except Exception as e:
                print(e)
                print(f"error occured cast LITERALEVAL for tmdbId {tmdbId}")
                print(rawCast)
            try:
                for member in cast_members:
                    creditId = member.get("credit_id")
                    name = member.get("name")
                    gender = member.get("gender", None)  # Assuming gender can be null

                    # Append to MovieParticipants
                    bulk_data_participants.append((creditId, tmdbId, name, gender))

                    # Specific data for CastMember
                    character_name = (member.get("character") or None)[:255]
                    order = member.get("order", None)
                    if not (character_name is None and order is None):
                        bulk_data_cast.append((creditId, character_name, order))
            except Exception as e:
                print(e)
                print(f"error occured cast FORLOOP for tmdbId {tmdbId}")
                print(rawCast)

            # Process crew members
            try:
                crew_members = ast.literal_eval(rawCrew)
            except Exception as e:
                print(e)
                print(f"error occured crew LITERALEVAL for tmdbId {tmdbId}")
                print(rawCrew)
            try:
                for member in crew_members:
                    creditId = member.get("credit_id")
                    name = member.get("name")
                    gender = member.get("gender", None)

                    # Append to MovieParticipants
                    bulk_data_participants.append((creditId, tmdbId, name, gender))

                    # Specific data for CrewMember
                    job = member.get("job", None)
                    department = member.get("department", None)
                    if not (job is None and department is None):
                        bulk_data_crew.append((creditId, job, department))
            except Exception as e:
                print(e)
                print(f"error occured crew FORLOOP for tmdbId {tmdbId}")
                print(rawCrew)

        # Bulk insert into MovieParticipants table
        try:
            insert_query_participants = "INSERT IGNORE INTO MovieParticipants (creditId, tmdbId, participantName, gender) VALUES (%s, %s, %s, %s)"
            cursor.executemany(insert_query_participants, bulk_data_participants)
        except Exception as e:
            print(e)
            print(f"error occured participants BULKINSERT for tmdbId {tmdbId}")
            print(bulk_data_participants)

        # Commit the changes
        cnx.commit()

        try:
            # Bulk insert into CastMember table
            insert_query_cast = "INSERT IGNORE INTO CastMember (creditId, characterName, roleProminence) VALUES (%s, %s, %s)"
            cursor.executemany(insert_query_cast, bulk_data_cast)
        except Exception as e:
            print(e)
            print(f"error occured cast BULKINSERT for tmdbId {tmdbId}")
            print(bulk_data_cast)

        # Commit the changes
        cnx.commit()

        try:
            # Bulk insert into CrewMember table
            insert_query_crew = "INSERT IGNORE INTO CrewMember (creditId, crewJob, crewDepartment) VALUES (%s, %s, %s)"
            cursor.executemany(insert_query_crew, bulk_data_crew)
        except Exception as e:
            print(e)
            print(f"error occured crew BULKINSERT for tmdbId {tmdbId}")
            print(bulk_data_crew)

        # Commit the changes
        cnx.commit()

    offset += batch_size

# Close the cursor and connection
cursor.close()
cnx.close()

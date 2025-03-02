import time
import string
import random


option_1_additional_query_filters = [
    "(1) Search movies by title", # will search for movies with titles containing 
    "(2) Search movies by keyword", # search for movies with keywords containing
    "(3) Search movies by genre", # will search for movies with genres containing
    "(4) Search movies by cast member",
    "(5) Search movies by crew member",
    "(6) Search movies by minimum average rating",
    "(7) Search movies by spoken language"
]

genres = [
    "Documentary",
    "Drama",
    "Comedy",
    "Fantasy",
    "Horror",
    "Family",
    "Science Fiction",
    "Romance",
    "Adventure",
    "Action",
    "Western",
    "Music",
    "Animation",
    "Crime",
    "History",
    "Thriller",
    "War",
    "Mystery",
    "Foreign",
    "TV Movie"
]

spoken_languages = [
    "Français", "English", "Italiano", "Pусский", "Deutsch", "Latin", "Magyar", "Português", "العربية", 
    "Español", "普通话", "Latviešu", "Nederlands", "Esperanto", "Cymraeg", "Český", "Srpski", "日本語", 
    "Dansk", "हिन्दी", "svenska", "Polski", "广州话 / 廣州話", "Kiswahili", "ελληνικά", "Gaeilge", 
    "euskera", "বাংলা", "suomi", "ภาษาไทย", "한국어/조선말", "Íslenska", "Türkçe", "Română", 
    "Український", "isiZulu", "shqip", "Bahasa melayu", "Slovenčina", "Norsk", "Tiếng Việt", 
    "עִבְרִית", "Slovenščina", "Malti", "Afrikaans", "беларуская мова", "فارسی", "български език", 
    "Bahasa indonesia", "Català", "Bosanski", "Hrvatski", "اردو", "Lietuvix9akai", "Azərbaycan", 
    "ਪੰਜਾਬੀ", "Somali", "پښتو", "Galego", "қазақ", "தமிழ்", "ქართული", "Eesti", "Wolof"
]

option_2_additional_query_filters = [
    "(1) Search movie performance details",
    "(2) Search movie participants details",
    "(3) Search movie language details",
    "(4) Search movie production details",
    "(5) general movie details",
    "(6) upcoming movie details"
]

option_2_2_additional_query_filters = [
    "(1) View entire cast",
    "(2) View entire crew",
    "(3) View a specific cast role",
    "(4) View a specific crew role"
]

cast_roles = [
    "(1) Primary actor(s)",
    "(2) Secondary actor(s)"
]

crew_roles = [
    "(1) Writing",
    "(2) Directing",
    "(3) Camera",
    "(4) Editing",
    "(5) Art",
    "(6) Costume & Make-Up",
    "(7) Production",
    "(8) Sound",
    "(9) Crew",
    "(10) Lighting",
    "(11) Visual Effects",
    "(12) Actors"
]

avg_ticket_options = [
    "(1) View the entire history of average ticket prices",
    "(2) View the average ticket price of a specific year"
]


# This function allows the user to build a query by applying various filters to search for movies
# The filter options available are below.
# "(1) Search movies by title", # will search for movies with titles containing 
# "(2) Search movies by keyword", # search for movies with keywords containing
# "(3) Search movies by genre", # will search for movies with genres containing
# "(4) Search movies by cast member",
# "(5) Search movies by crew member",
# "(6) Search movies by minimum average rating",
# "(7) Search movies by spoken language"
def create_option_1_query(cnx, cursor):
    max_filters = 5 
    count = 0 
    query_string = "" 
    print("Query type 1 chosen, searching for movies by user provided filters")
    print("You can search for movies with up to 5 filters (repeat filters are allowed) from the 7 listed which will be applied in the order you enter them")
    print()
     
    while True:
        if count >= max_filters:
            print("Max filters of 5 has been reached, executing search for movies with provided filters")
            print()
            break
        for query_filter in option_1_additional_query_filters:
            print(query_filter)
        user_input = input(f"Enter the filter (filter number {count + 1}) from filters(1-7) you would like to use to search movies by or 'DONE' if all filters have been entered: ")
        if user_input.lower() == "done":
            break
        elif user_input == "1":
            title_filter = input("Enter the move title filter you would like to apply: ")
            print()
            if count == 0:
                query_string = f"SELECT * FROM Movies WHERE LOWER(title) LIKE LOWER('%{title_filter}%')"
            else:
                query_string = f"SELECT * FROM ({query_string}) AS m WHERE LOWER(m.title) LIKE LOWER('%{title_filter}%')"
            count += 1
        elif user_input == "2":
            keyword_filter = input("Enter the keyword filter you would like to apply: ")
            print()
            if count == 0: 
                query_string = f""" 
                SELECT m.*
                FROM Movies m
                JOIN MovieLinks ml ON m.imdbId = ml.imdbId
                JOIN MovieKeywords k ON ml.tmdbId = k.tmdbId
                WHERE LOWER(k.keywordName) LIKE LOWER('%{keyword_filter}%')
                """
            else:
                query_string = f"""
                SELECT m.*
                FROM ({query_string}) AS m
                JOIN MovieLinks ml ON m.imdbId = ml.imdbId
                JOIN MovieKeywords k ON ml.tmdbId = k.tmdbId
                WHERE LOWER(k.keywordName) LIKE LOWER('%{keyword_filter}%')
                """
            count += 1
        elif user_input == "3":
            i = 1
            for genre_name in genres:
                print(f"({i}) {genre_name}")
                i += 1
            genre_choice = int(input("Enter the genre filter you would like to apply (1-20): "))
            print()
            genre_filter = genres[genre_choice - 1]
            if count == 0:
                query_string = f""" 
                SELECT m.*
                FROM Movies m
                JOIN MovieGenres mg ON m.imdbId = mg.imdbId
                WHERE LOWER(mg.genreName) = LOWER('{genre_filter}')
                """
            else:
                query_string = f"""
                SELECT m.*
                FROM ({query_string}) AS m
                JOIN MovieGenres mg ON m.imdbId = mg.imdbId
                WHERE LOWER(mg.genreName) = LOWER('{genre_filter}')
                """
            count += 1
        elif user_input == "4":
            cast_member_name = input("Enter the name of the cast member filter you would like to apply: ")
            print()
            if count == 0:
                query_string = f"""
                SELECT m.*
                FROM Movies m
                JOIN MovieLinks ml ON m.imdbId = ml.imdbId
                JOIN MovieParticipants mp ON ml.tmdbId = mp.tmdbId
                JOIN CastMember cm ON mp.creditId = cm.creditId
                WHERE LOWER(mp.participantName) LIKE LOWER('%{cast_member_name}%')
                """
            else:
                query_string = f"""
                SELECT m.*
                FROM ({query_string}) AS m
                JOIN MovieLinks ml ON m.imdbId = ml.imdbId
                JOIN MovieParticipants mp ON ml.tmdbId = mp.tmdbId
                JOIN CastMember cm ON mp.creditId = cm.creditId
                WHERE LOWER(mp.participantName) LIKE LOWER('%{cast_member_name}%')
                """
            count += 1
        elif user_input == "5":
            crew_member_name = input("Enter the name of the crew member filter you would like to apply: ")
            print()
            if count == 0:
                query_string = f"""
                SELECT m.*
                FROM Movies m
                JOIN MovieLinks ml ON m.imdbId = ml.imdbId
                JOIN MovieParticipants mp ON ml.tmdbId = mp.tmdbId
                JOIN CrewMember cm ON mp.creditId = cm.creditId
                WHERE LOWER(mp.participantName) LIKE LOWER('%{crew_member_name}%')
                """
            else:
                query_string = f"""
                SELECT m.*
                FROM ({query_string}) AS m
                JOIN MovieLinks ml ON m.imdbId = ml.imdbId
                JOIN MovieParticipants mp ON ml.tmdbId = mp.tmdbId
                JOIN CrewMember cm ON mp.creditId = cm.creditId
                WHERE LOWER(mp.participantName) LIKE LOWER('%{crew_member_name}%')
                """
            count += 1
        elif user_input == "6":
            minimum_average_rating = float(input("Enter the minimum average rating for the movie(s) (between 1 and 10): "))
            print()
            if count == 0:
                query_string = f"""
                SELECT m.*
                FROM Movies m
                JOIN ReleasedMoviesMetadata rmm ON m.imdbId = rmm.imdbId
                WHERE rmm.voteAverage >= {minimum_average_rating}
                """
            else:
                query_string = f"""
                SELECT m.*
                FROM ({query_string}) AS m
                JOIN ReleasedMoviesMetadata rmm ON m.imdbId = rmm.imdbId
                WHERE rmm.voteAverage >= {minimum_average_rating}
                """
            count += 1
        elif user_input == "7":
            i = 1
            for spoken_language in spoken_languages:
                print(f"({i}) {spoken_language}")
                i += 1
            print()
            language_choice = int(input("Enter the number of the desired language spoken in the movie(s) from one of the options: "))
            print()
            language_filter = spoken_languages[language_choice - 1]
            if count == 0:
                query_string = f"""
                SELECT m.*
                FROM Movies m
                JOIN MovieSpokenLanguages msl ON m.imdbId = msl.imdbId
                WHERE LOWER(msl.languageName) = LOWER('{language_filter}')
                """
            else:
                query_string = f"""
                SELECT m.*
                FROM ({query_string}) AS m
                JOIN MovieSpokenLanguages msl ON m.imdbId = msl.imdbId
                WHERE LOWER(msl.languageName) = LOWER('{language_filter}')
                """
            count += 1
        else:
            print("Invalid movie search filter, please provide a valid movie search filter from the options")
            print()

    query_string += " LIMIT 100;"
    print("Executing Query:")
    print(query_string)
    print()
    
    cursor.execute(query_string)
    columns = [desc[0] for desc in cursor.description]
    result = cursor.fetchall()
    print("Obtained Result:")
    if not result:
        print("Didn't find any matching movies for the provided search filters")
        return 
    # for row in result:
    #     print(row)
    for row in result:
        for col_name, value in zip(columns, row):
            print(f"{col_name}: {value}")
        print("-" * 50)
    print()
    return


# This function allows the user to build a query by applying various filters to search for details on a known movie.
# "(1) Search movie performance details",
# "(2) Search movie participants details",
# "(3) Search movie language details",
# "(4) Search movie production details"
# "(5) general movie details"
# "(6) upcoming movie details"
def create_option_2_query(cnx, cursor):
    useDefault = True
    max_filters = 5 
    count = 0 
    query_string_2 = "" 
    
    print("Query type 2 chosen, search for additional details on a given movie")
    print("The user will be prompted for the details that they are interested in learning about and the movie for which they desire these details")
    print()
    
    while True:
        for query_filter in option_2_additional_query_filters:
            print(query_filter)
        print()
        detail_input = input("Enter your desired detail (1-6): ")
        print()
        if detail_input != "6":
            user_input = input("Enter the title of the movie: ")
        print()
        if detail_input.lower() == "done":
            break
        elif detail_input == "1":
            perform_type = input("Would you like to view all time data (1) or daily statistics (2): ")
            if perform_type == "1":
                query_string_2 = f"""
                SELECT m.title, rm.widestReleases, ar.*
                FROM Movies m
                JOIN ReleasedMoviesMetadata rm ON m.imdbId = rm.imdbId
                JOIN AdditionalRevenueData ar ON rm.imdbId = ar.imdbId
                WHERE LOWER(m.title) LIKE LOWER('{user_input}')
                """
            elif perform_type == "2":
                query_string_2 = f"""
                SELECT m.title, adbo.boxOfficeDate, adbo.dailyTheaterCount, adbo.dailyDomesticGross
                FROM Movies m
                JOIN ReleasedMoviesMetadata rm ON m.imdbId = rm.imdbId
                JOIN AdditionalRevenueData ar ON rm.imdbId = ar.imdbId
                JOIN AdditionalDailyBoxOfficeRevenueData adbo ON ar.releaseIdentifier = adbo.releaseIdentifier
                WHERE LOWER(m.title) LIKE LOWER('{user_input}')
                """
        elif detail_input == "2":
            for option in option_2_2_additional_query_filters:
                print(option)
            print()
            participant_input = input("please select one of the options: ")
            print()
            if participant_input == "1":
                query_string_2 = f"""
                SELECT m.title, cm.creditId, mp.participantName, cm.characterName, cm.roleProminence 
                FROM Movies m
                JOIN MovieLinks ml ON m.imdbId = ml.imdbId
                JOIN MovieParticipants mp ON ml.tmdbId = mp.tmdbId
                JOIN CastMember cm ON mp.creditId = cm.creditId
                WHERE LOWER(m.title) LIKE LOWER('{user_input}')
                """
            elif participant_input == "2":
                query_string_2 = f"""
                SELECT m.title, cm.creditId, mp.participantName, cm.crewJob, cm.crewDepartment 
                FROM Movies m
                JOIN MovieLinks ml ON m.imdbId = ml.imdbId
                JOIN MovieParticipants mp ON ml.tmdbId = mp.tmdbId
                JOIN CrewMember cm ON mp.creditId = cm.creditId
                WHERE LOWER(m.title) LIKE LOWER('{user_input}')
                """
            elif participant_input == "3":
                for role in cast_roles:
                    print(role)
                print()
                individual_input = int(input("Please select the role you are interested in: "))
                print()
                role_prominence = individual_input - 1
                query_string_2 = f"""
                SELECT m.title, cm.creditId, mp.participantName, cm.characterName, cm.roleProminence 
                FROM Movies m
                JOIN MovieLinks ml ON m.imdbId = ml.imdbId
                JOIN MovieParticipants mp ON ml.tmdbId = mp.tmdbId
                JOIN CastMember cm ON mp.creditId = cm.creditId
                WHERE LOWER(m.title) = LOWER('{user_input}')
                AND LOWER(cm.roleProminence) = "{role_prominence}"
                """
            elif participant_input == "4":
                for role in crew_roles:
                    print(role)
                print()
                individual_input = int(input("Please select the role you are interested in: "))
                print()
                department = crew_roles[individual_input - 1].split(') ')[1]
                query_string_2 = f"""
                SELECT m.title, cm.creditId, mp.participantName, cm.crewJob, cm.crewDepartment 
                FROM Movies m
                JOIN MovieLinks ml ON m.imdbId = ml.imdbId
                JOIN MovieParticipants mp ON ml.tmdbId = mp.tmdbId
                JOIN CrewMember cm ON mp.creditId = cm.creditId
                WHERE LOWER(m.title) = LOWER('{user_input}')
                AND LOWER(cm.crewDepartment) LIKE LOWER('{department}')
                """
        elif detail_input == "3":
            query_string_2 = f"""
            SELECT m.title, ml.originalLanguage, ms.languageName
            FROM Movies m
            JOIN MoviesMetadata mm ON m.imdbId = mm.imdbId
            JOIN MoviesLanguageMetadata ml ON mm.imdbId = ml.imdbId
            JOIN MovieSpokenLanguages ms ON ml.imdbId = ms.imdbId
            WHERE LOWER(m.title) LIKE LOWER('{user_input}')
            """
        elif detail_input == "4":
            query_string_2 = f"""
            SELECT m.title, mcom.companyName, mcou.countryName
            FROM Movies m
            JOIN MoviesMetadata mm ON m.imdbId = mm.imdbId
            JOIN MoviesProductionMetadata mpm ON mm.imdbId = mpm.imdbId
            JOIN MovieProductionCompanies mcom ON mpm.imdbId = mcom.imdbId
            JOIN MovieProductionCountries mcou ON mcom.imdbId = mcou.imdbId
            WHERE LOWER(m.title) LIKE LOWER('{user_input}')
            """
        elif detail_input == "5":
            useDefault = False
            query_string_2 = f"""
            SELECT m.title, m.overview, mm.runtime, mpm.releaseDate, rmm.voteAverage
            FROM Movies m
            JOIN ReleasedMoviesMetadata rmm ON m.imdbId = rmm.imdbId
            JOIN MoviesMetadata mm ON rmm.imdbId = mm.imdbId
            JOIN MoviesProductionMetadata mpm ON mm.imdbId = mpm.imdbId
            WHERE LOWER(m.title) LIKE LOWER('{user_input}')
            """
        elif detail_input == "6":
            useDefault = False
            query_string_2 = f"""
            SELECT m.title, m.overview, mpm.releaseStatus, mpm.releaseDate
            FROM Movies m
            JOIN MoviesMetadata mm ON m.imdbId = mm.imdbId
            JOIN MoviesProductionMetadata mpm ON mm.imdbId = mpm.imdbId
            WHERE mpm.releaseStatus = "In Production"
            """
        print()
        
        query_string_2 += " LIMIT 100;"
        print("Executing Query:")
        print(query_string_2)
        print()
        
        cursor.execute(query_string_2)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        if not results:
            print("Didn't find any matching movies for the provided title")
            print()
            return
            
        if useDefault:    
            col_widths = [len(col) for col in columns]
            for row in results:
                for idx, value in enumerate(row):
                    col_widths[idx] = max(col_widths[idx], len(str(value)))
            separator = '+'.join(['-' * (width + 2) for width in col_widths])

            print("Obtained Result:")
            header = '|'.join([f" {col.ljust(col_widths[idx])} " for idx, col in enumerate(columns)])
            print(separator)
            print(header)
            print(separator)
            for row in results:
                row_str = '|'.join([f" {str(value).ljust(col_widths[idx])} " for idx, value in enumerate(row)])
                print(row_str)
                print(separator)
        else:
            for row in results:
                for col_name, value in zip(columns, row):
                    print(f"{col_name}: {value}")
                print("-" * 50)  # Separator between rows
        return


def create_option_3_query(cnx, cursor):
    print("Query type 3 chosen, search for the average ticket price by year")
    print()
    useDefault = True
    query_string_3 = "" 
    
    while True:
        for option in avg_ticket_options:
            print(option)
        print()
        avg_ticket_type = input("Please enter an option (1 or 2): ")
        print()
        if avg_ticket_type == "1":
            query_string_3 = f"""
            SELECT * FROM DomesticAverageTicketPrice
            """
        elif avg_ticket_type == "2":
            year_input = input("Enter the year you would like to see the average ticket price for (yyyy): ")
            query_string_3 = f"""
            SELECT * FROM DomesticAverageTicketPrice WHERE year = {int(year_input)}
            """
        
        query_string_3 += ";"
        print("Executing Query:")
        print(query_string_3)
        print()
        
        cursor.execute(query_string_3)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()
        
        if not results:
            print("Didn't data for the provided year")
            print()
            return
        
        for row in results:
            for col_name, value in zip(columns, row):
                print(f"{col_name}: {value}")
            print("-" * 50)
        return


# handling the functionality for adding a new user rating on a movie
def create_option_4_query(cnx, cursor, userId):
    print("Query type 4 chosen. Creating a new user rating  on a movie.")
    
    # Prompt user for a movie title
    title = input("Enter the title of the movie you want to review: ").strip()
    print()

    # Search for matching Released movies by title from Movies table
    query = """
        SELECT m.imdbId, m.title, m.tagline, m.overview
        FROM Movies m
        JOIN ReleasedMoviesMetadata rmm ON m.imdbId = rmm.imdbId
        WHERE LOWER(m.title) LIKE LOWER(%s)
    """
    cursor.execute(query, (f"%{title}%",))
    movies = cursor.fetchall()

    # Handle no movie found
    if not movies:
        print("No released movie found with the provided title.")
        print()
        return

    # Handle multiple movies found
    if len(movies) > 1:
        print("Multiple movies found. Please select one by entering the corresponding number:")
        for i, movie in enumerate(movies, 1):
            print(f"{i}. {movie[1]} (IMDb ID: {movie[0]})")
            print(f"Overview: {movie[3]}")
        print()
        selected_index = int(input("Enter your choice: ")) - 1
        selected_movie = movies[selected_index]
    else:
        selected_movie = movies[0]

    # Display selected movie details
    print("Selected Movie:")
    print(f"Title: {selected_movie[1]}")
    print(f"IMDb ID: {selected_movie[0]}")
    print(f"Tagline: {selected_movie[2]}")
    print(f"Overview: {selected_movie[3]}")
    print("-" * 50)
    print()
    
    # Check if a review already exists for this user and movie
    cursor.execute("""
        SELECT COUNT(*)
        FROM UserRatings
        WHERE userId = %s AND movieId = (SELECT movieId FROM MovieLinks WHERE imdbId = %s)
    """, (userId, selected_movie[0]))

    if cursor.fetchone()[0] > 0:
        print("You have already reviewed this movie.")
        print()
        return

    # Prompt user for rating value
    rating = None
    while rating is None:
        try:
            rating = float(input("Enter the rating value between 0 and 5: "))
            print()
            if rating < 0 or rating > 5:
                print("Rating must be between 0 and 5.")
                print()
                rating = None
        except ValueError:
            print("Please enter a valid number for the rating.")
            print()

    # Get current timestamp
    ratingTimestamp = int(time.time())

    # Insert new rating
    try:
        insert_query = """
            INSERT INTO UserRatings (userId, movieId, rating, ratingTimestamp)
            VALUES (%s, (SELECT movieId FROM MovieLinks WHERE imdbId = %s), %s, %s)
        """
        print("Executing Query to Create New UserRating: ")
        print(insert_query % (userId, selected_movie[0], rating, ratingTimestamp))
        print()
        cursor.execute(insert_query, (userId, selected_movie[0], rating, ratingTimestamp))
        cnx.commit()
    except Exception as e:
        print(f"An error occurred while inserting the rating: {e}")
        print()
        return

    # Retrieve and display the newly created rating
    cursor.execute("""
        SELECT ur.*, m.title 
        FROM UserRatings ur
        JOIN MovieLinks ml ON ur.movieId = ml.movieId
        JOIN Movies m ON ml.imdbId = m.imdbId
        WHERE ur.userId = %s AND ml.imdbId = %s
    """, (userId, selected_movie[0]))

    new_rating = cursor.fetchone()
    if new_rating:
        columns = [desc[0] for desc in cursor.description]
        print("Newly created UserRating:")
        for col_name, value in zip(columns, new_rating):
            print(f"{col_name}: {value}")
        print("-" * 50)
        print()
    else:
        print("Failed to create a new user rating.")
        print()


# handling functionality for update an existing user rating on a movie
def create_option_5_query(cnx, cursor, userId):
    print("Query type 5 chosen. Update an existing user rating on a movie.")
    print()
    
    # Fetch and display all the user's ratings
    query = """
        SELECT ur.rating, m.title, m.imdbId, ur.ratingTimestamp, ur.movieId
        FROM UserRatings ur
        JOIN MovieLinks ml ON ur.movieId = ml.movieId
        JOIN Movies m ON ml.imdbId = m.imdbId
        WHERE ur.userId = %s
    """
    cursor.execute(query, (userId,))
    user_ratings = cursor.fetchall()

    # Check if the user has any ratings
    if not user_ratings:
        print("You have not reviewed any movies yet. Please create a UserRating first before trying to update.")
        print()
        return

    # Display the ratings to the user
    print("Your current ratings are:")
    for i, rating in enumerate(user_ratings, start=1):
        print(f"{i}. {rating[1]} (IMDb ID: {rating[2]}) - Rating: {rating[0]} on {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(rating[3]))}")
    print()
    
    # Ask the user which rating they want to update
    while True:
        try:
            selection = int(input("\nEnter the number of the rating you want to update: "))
            if 1 <= selection <= len(user_ratings):
                selected_rating = user_ratings[selection - 1]
                break
            else:
                print("Please select a valid rating number.")
                print()
        except ValueError:
            print("Please enter a valid integer.")
            print()

    # Prompt user for new rating value
    while True:
        try:
            new_rating = float(input("Enter the new rating value between 0 and 5: "))
            if 0 <= new_rating <= 5:
                break
            else:
                print("Rating must be between 1 and 5.")
                print()
        except ValueError:
            print("Please enter a valid number for the rating.")
            print()

    # Update the rating in the database
    try:
        update_query = """
            UPDATE UserRatings
            SET rating = %s, ratingTimestamp = %s
            WHERE userId = %s AND movieId = %s
        """
        new_timestamp = int(time.time())
        print("Executing Query to Update Existing UserRating: ")
        print(update_query % (new_rating, new_timestamp, userId, selected_rating[4]))
        print()
        cursor.execute(update_query, (new_rating, new_timestamp, userId, selected_rating[4]))
        cnx.commit()
        print("Your rating has been updated successfully.")
        print()
    except Exception as e:
        print(f"An error occurred while updating the rating: {e}")
        print()
    
    # Query and display the updated UserRating
    cursor.execute("""
        SELECT ur.rating, ur.ratingTimestamp
        FROM UserRatings ur
        WHERE ur.userId = %s AND ur.movieId = %s
    """, (userId, selected_rating[4]))
    
    updated_rating = cursor.fetchone()
    if updated_rating:
        print("Updated UserRating:")
        print(f"New Rating: {updated_rating[0]}")
        print(f"Updated On: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(updated_rating[1]))}")
        print()
    else:
        print("Failed to update the rating.")
        print()


# handling functionality for deleting a UserRating
def create_option_6_query(cnx, cursor, userId):
    print("Query type 6 chosen. Delete an existing user rating on a movie.")
    print()
    # Fetch and display all the user's ratings
    query = """
        SELECT ur.rating, m.title, m.imdbId, ur.ratingTimestamp, ur.movieId
        FROM UserRatings ur
        JOIN MovieLinks ml ON ur.movieId = ml.movieId
        JOIN Movies m ON ml.imdbId = m.imdbId
        WHERE ur.userId = %s
    """
    cursor.execute(query, (userId,))
    user_ratings = cursor.fetchall()

    # Check if the user has any ratings
    if not user_ratings:
        print("You have not reviewed any movies yet.")
        print()
        return

    # Display the ratings to the user
    print("Your current ratings are:")
    for i, rating in enumerate(user_ratings, start=1):
        print(f"{i}. {rating[1]} (IMDb ID: {rating[2]}) - Rating: {rating[0]} on {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(rating[3]))}")
    print()
    
    # Ask the user which rating they want to delete
    while True:
        try:
            selection = int(input("\nEnter the number of the rating you want to delete: "))
            if 1 <= selection <= len(user_ratings):
                selected_rating = user_ratings[selection - 1]
                break
            else:
                print("Please select a valid rating number.")
                print()
        except ValueError:
            print("Please enter a valid integer.")
            print()

    # Confirm deletion
    confirm = input(f"Are you sure you want to delete your rating for '{selected_rating[1]}'? (yes/no): ").lower()
    if confirm != 'yes':
        print("Deletion cancelled.")
        print()
        return

    # Delete the rating from the database
    try:
        delete_query = """
            DELETE FROM UserRatings
            WHERE userId = %s AND movieId = %s
        """
        print("Executing Query to Delete UserRating:")
        print(delete_query % (userId, selected_rating[4]))
        print()
        cursor.execute(delete_query, (userId, selected_rating[4]))
        cnx.commit()
        print("Your rating has been deleted successfully.")
        print()
    except Exception as e:
        print(f"An error occurred while deleting the rating: {e}")
        print()
  
  
# helper function used by create_option_7_query to generate new nonexistent imdbId
def generate_unique_id(table, column, length, cursor):
    unique_id = None
    while unique_id is None:
        potential_id = ''.join(random.choices(string.digits, k=length))
        cursor.execute(f"SELECT COUNT(*) FROM {table} WHERE {column} = %s", (potential_id,))
        if cursor.fetchone()[0] == 0:  # Check if ID already exists
            unique_id = potential_id
    return unique_id

# helper function used by create_option_7_query to generate new nonexistent movieId and tmdbId
def get_next_id(table, column, cursor):
    cursor.execute(f"SELECT MAX({column}) FROM {table}")
    max_id = cursor.fetchone()[0]
    if max_id is not None:
        return max_id + 1
    else:
        return 1  # Start from 1 if no records exist

# handling functionality of allowing Admin users to create new Movies
def create_option_7_query(cnx, cursor):
    print("Query type 7 chosen, creating a new Movie record")
    print("Creating a new movie record...")
    print()

    # Prompt for movie details
    title = input("Enter the movie title: ").strip()
    tagline = input("Enter the movie tagline: ").strip()
    overview = input("Enter the movie overview: ").strip()
    print()

    # Check if title is valid
    if not title:
        print("Title cannot be empty.")
        print()
        return
    # Check if overview is valid
    if not overview:
        print("Overview cannot be empty.")
        print()
        return

    # Generate unique IDs
    imdbId = generate_unique_id("MovieLinks", "imdbId", 7, cursor)  # Generate a 7-digit imdbId
    movieId = get_next_id("MovieLinks", "movieId", cursor)  # Get next movieId
    tmdbId = get_next_id("MovieLinks", "tmdbId", cursor)  # Get next tmdbId


    # Prepare insert query for MovieLinks table
    insert_movie_links_query = """
        INSERT INTO MovieLinks (movieId, imdbId, tmdbId)
        VALUES (%s, %s, %s)
    """
    print(f"Executing Query to Create New MovieLinks Record: \n{insert_movie_links_query % (movieId, imdbId, tmdbId)}")
    print()

    # Execute query to insert into MovieLinks table
    try:
        cursor.execute(insert_movie_links_query, (movieId, imdbId, tmdbId))
    except Exception as e:
        print(f"An error occurred while inserting into MovieLinks: {e}")
        print()
        return

    # Prepare insert query for Movies table
    insert_movies_query = """
        INSERT INTO Movies (imdbId, title, tagline, overview)
        VALUES (%s, %s, %s, %s)
    """
    print(f"Executing Query to Create New Movie Record: \n{insert_movies_query % (imdbId, title, tagline, overview)}")
    print()

    # Execute query to insert into Movies table
    try:
        cursor.execute(insert_movies_query, (imdbId, title, tagline, overview))
        cnx.commit()
    except Exception as e:
        print(f"An error occurred while inserting into Movies: {e}")
        print()
        # Delete the MovieLinks created record if an error occurs with making the Movie
        cursor.execute("DELETE FROM MovieLinks WHERE imdbId = %s", (imdbId,))
        cnx.commit()
        return

    # Query and return the newly created Movies record
    cursor.execute("SELECT * FROM Movies WHERE imdbId = %s", (imdbId,))
    new_movie = cursor.fetchone()
    if new_movie:
        columns = [desc[0] for desc in cursor.description]
        print("Newly created Movie record:")
        for col_name, value in zip(columns, new_movie):
            print(f"{col_name}: {value}")
        print("-" * 50)
        print()
    else:
        print("Failed to retrieve the newly created movie record.")
        print()


# handles functionality of updating the tagline and overview of an existing movie record
def create_option_8_query(cnx, cursor):
    print("Query type 8 chosen, updating an existing movie record")
    print()

    # Prompt for movie title
    title_search = input("Enter the title of the movie you want to update: ").strip()
    print()

    # Search for movies
    cursor.execute("SELECT imdbId, title, overview FROM Movies WHERE LOWER(title) LIKE LOWER(%s)", (f"%{title_search}%",))
    movies = cursor.fetchall()

    if not movies:
        print("No movies found with the given title.")
        print()
        return

    if len(movies) > 1:
        print("Multiple movies found. Please select one by entering the corresponding number:")
        print()
        for i, movie in enumerate(movies, 1):
            print(f"{i}. {movie[1]} (IMDb ID: {movie[0]})")
            print(f"Overview: {movie[2]}")
        print()
        selected_index = int(input("Enter your choice: ")) - 1
        print()
        selected_movie = movies[selected_index]
    else:
        selected_movie = movies[0]
        
    # Display the selected movie details
    print("Selected Movie for Deletion:")
    print(f"Title: {selected_movie[1]}")
    print(f"IMDb ID: {selected_movie[0]}")
    print(f"Overview: {selected_movie[2]}")
    print("-" * 50)
    print()

    # Prompt for new tagline and overview
    new_tagline = input("Enter the new tagline (press enter to keep the current one): ").strip()
    new_overview = input("Enter the new overview: ").strip()
    print()

    if not new_overview:
        print("Overview cannot be empty.")
        print()
        return

    # Prepare the update query
    update_query = """
        UPDATE Movies
        SET tagline = %s, overview = %s
        WHERE imdbId = %s
    """
    update_values = (new_tagline, new_overview, selected_movie[0])
    print(f"Executing Query to Update Movie Record: \n{update_query % update_values}")
    print()

    # Execute the update query
    try:
        cursor.execute(update_query, update_values)
        cnx.commit()
        print("Movie record updated successfully.")
        print()
    except Exception as e:
        print(f"An error occurred while updating the movie: {e}")
        print()
        return

    # Retrieve and display the updated movie record
    cursor.execute("SELECT * FROM Movies WHERE imdbId = %s", (selected_movie[0],))
    updated_movie = cursor.fetchone()
    if updated_movie:
        columns = [desc[0] for desc in cursor.description]
        print("\nUpdated Movie Record:")
        for col_name, value in zip(columns, updated_movie):
            print(f"{col_name}: {value}")
        print("-" * 50)
        print()
    else:
        print("Failed to retrieve the updated movie record.")
        print()


# provides functionality for deleting an existing movie record
# the corresponding MovieLink record should be deleted which should cause all of the referencing
# foreign keys to that MovieLinks record to be deleted according to the cascading
# this means that when a movie record is deleted, all of its corresponding 
# keywords, participants, ratings and metadata will also be deleted
def create_option_9_query(cnx, cursor):
    print("Query type 9 chosen, deleting an existing movie record")
    print()

    # Prompt for movie title
    title_search = input("Enter the title of the movie you want to delete: ").strip()

    # Search for movies
    cursor.execute("SELECT imdbId, title, overview FROM Movies WHERE LOWER(title) LIKE LOWER(%s)", (f"%{title_search}%",))
    movies = cursor.fetchall()

    if not movies:
        print("No movies found with the given title.")
        return

    if len(movies) > 1:
        print("Multiple movies found. Please select one by entering the corresponding number:")
        for i, movie in enumerate(movies, 1):
            print(f"{i}. {movie[1]} (IMDb ID: {movie[0]})")
            print(f"Overview: {movie[2]}")
        selected_index = int(input("Enter your choice: ")) - 1
        print()
        selected_movie = movies[selected_index]
    else:
        selected_movie = movies[0]

    # Display the selected movie details
    print("\nSelected Movie for Deletion:")
    print(f"Title: {selected_movie[1]}")
    print(f"IMDb ID: {selected_movie[0]}")
    print(f"Overview: {selected_movie[2]}")
    print("-" * 50)
    print()

    # Confirm deletion
    confirm = input(f"Are you sure you want to delete '{selected_movie[1]}'? (yes/no): ").lower()
    if confirm != 'yes':
        print("Deletion cancelled.")
        return

    # Prepare the delete query for MovieLinks (which will cascade to Movies and related tables)
    delete_query = "DELETE FROM MovieLinks WHERE imdbId = %s"
    print(f"Executing Query to Delete Movie Record: \n{delete_query % (selected_movie[0],)}")
    print()

    # Execute the delete query
    try:
        cursor.execute(delete_query, (selected_movie[0],))
        cnx.commit()
        print("Movie record and related data deleted successfully.")
    except Exception as e:
        print(f"An error occurred while deleting the movie: {e}")
        return
    
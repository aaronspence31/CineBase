import ast
import json
import mysql.connector  # pip install mysql-connector-python to get this package
import unicodedata
from collections import defaultdict


# Helper function to normalize string by removing diacritics and converting to lowercase
# This will be used for string comparisons
def normalize_string(s):
    return "".join(
        c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn"
    ).lower()


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


# Handling data from TempDomesticAverageTicketPrice
# Fetch data from TempDomesticAverageTicketPrice
query = (
    "SELECT year, averageTicketPriceUsd, sourceUrl FROM TempDomesticAverageTicketPrice"
)
cursor.execute(query)
data = cursor.fetchall()

# Process data
yearly_data = defaultdict(list)
for year, price, url in data:
    yearly_data[year].append((price, url))

# Calculate average price and select the first sourceUrl
final_data = []
for year, values in yearly_data.items():
    avg_price = sum(price for price, _ in values) / len(values)
    first_url = values[0][1]  # Select the first URL for the year
    final_data.append((year, avg_price, first_url))

# Insert data into DomesticAverageTicketPrice
insert_query = "INSERT INTO DomesticAverageTicketPrice (year, averageTicketPriceUsd, sourceUrl) VALUES (%s, %s, %s)"
cursor.executemany(insert_query, final_data)
cnx.commit()


# Handling data from TempKeywords
# Fetch data from TempKeywords
fetch_query = "SELECT tmdbId, rawKeywords FROM TempKeywords"
cursor.execute(fetch_query)
temp_keywords_data = cursor.fetchall()

# Prepare bulk insert data for MovieKeywords
bulk_data_keywords = []

# Process each row in TempKeywords
for tmdbId, raw_keywords in temp_keywords_data:
    try:
        keywords = ast.literal_eval(raw_keywords)

        # Extract and append each keyword to bulk_data_keywords
        for keyword in keywords:
            keyword_name = keyword.get("name")
            if keyword_name and not any(
                tmdb_Id == tmdbId
                and normalize_string(keyword_name)
                == normalize_string(existing_keyword_name)
                for tmdb_Id, existing_keyword_name in bulk_data_keywords
            ):
                bulk_data_keywords.append((tmdbId, keyword_name))
    except json.JSONDecodeError:
        print(f"Invalid JSON format for tmdbId {tmdbId}")

# Bulk insert into MovieKeywords table
insert_query_keywords = (
    "INSERT IGNORE INTO MovieKeywords (tmdbId, keywordName) VALUES (%s, %s)"
)
cursor.executemany(insert_query_keywords, bulk_data_keywords)

# Commit the changes
cnx.commit()


# Handling data from TempJsonStringDataTableMetadata
# Fetch the raw JSON data
query = "SELECT imdbId, rawGenres, rawSpokenLanguages, rawProductionCompanies, rawProductionCountries FROM TempJsonStringDataTableMetadata"
cursor.execute(query)

# Prepare bulk insert data
bulk_data_genres = []
bulk_data_languages = []
bulk_data_companies = []
bulk_data_countries = []

for (
    imdbId,
    rawGenres,
    rawSpokenLanguages,
    rawProductionCompanies,
    rawProductionCountries,
) in cursor:
    # Process genres
    try:
        genres = json.loads(rawGenres)
        for genre in genres:
            genre_name = genre.get("name")
            if genre_name:
                bulk_data_genres.append((imdbId, genre_name))
    except json.JSONDecodeError:
        print(f"Invalid JSON for genres at IMDb ID {imdbId}")

    # Process spoken languages
    try:
        languages = json.loads(rawSpokenLanguages)
        for language in languages:
            language_name = language.get("name")
            if language_name and language_name != "No Language":
                bulk_data_languages.append((imdbId, language_name))
    except json.JSONDecodeError:
        print(f"Invalid JSON for spoken languages at IMDb ID {imdbId}")

    # Process production companies
    try:
        companies = ast.literal_eval(rawProductionCompanies)
        for company in companies:
            company_name = company.get("name")
            # Before appending to bulk_data_companies, check if the tuple already exists
            if company_name and not any(
                imdb_id == imdbId
                and normalize_string(company_name) == normalize_string(company)
                for imdb_id, company in bulk_data_companies
            ):
                bulk_data_companies.append((imdbId, company_name))

    except Exception as e:
        print(e)
        print(f"ast.literal_eval error production companies at IMDb ID {imdbId}")

    # Process production countries
    try:
        countries = ast.literal_eval(rawProductionCountries)
        for country in countries:
            country_name = country.get("name")
            if country_name and (
                imdbId != 3455224  # filtering out problematic data
                and imdbId != "3455224"
                and (
                    not any(
                        imdb_id == imdbId
                        and country_name.lower() == existing_country_name.lower()
                        for imdb_id, existing_country_name in bulk_data_countries
                    )
                )
            ):
                bulk_data_countries.append((imdbId, country_name))
    except Exception as e:
        print(e)
        print(f"ast.literal_eval error production countries at IMDb ID {imdbId}")

# Bulk insert into MovieGenres table
insert_query_genres = "INSERT INTO MovieGenres (imdbId, genreName) VALUES (%s, %s)"
cursor.executemany(insert_query_genres, bulk_data_genres)

# Bulk insert into MovieSpokenLanguages table
insert_query_languages = (
    "INSERT INTO MovieSpokenLanguages (imdbId, languageName) VALUES (%s, %s)"
)
cursor.executemany(insert_query_languages, bulk_data_languages)

# Commit the changes
cnx.commit()

# Bulk insert into MovieProductionCompanies table
insert_query_companies = (
    "INSERT IGNORE INTO MovieProductionCompanies (imdbId, companyName) VALUES (%s, %s)"
)
cursor.executemany(insert_query_companies, bulk_data_companies)

# Commit the changes
cnx.commit()

# Bulk insert into MovieProductionCountries table
insert_query_countries = (
    "INSERT IGNORE INTO MovieProductionCountries (imdbId, countryName) VALUES (%s, %s)"
)
cursor.executemany(insert_query_countries, bulk_data_countries)

# Commit the changes
cnx.commit()

# Close the cursor and connection
cursor.close()
cnx.close()

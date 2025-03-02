drop table if exists DomesticAverageTicketPrice;
drop table if exists TempDomesticAverageTicketPrice;
drop table if exists UserRatings;
drop table if exists Users;
drop table if exists MovieKeywords;
drop table if exists TempKeywords;
drop table if exists CrewMember;
drop table if exists CastMember;
drop table if exists MovieParticipants;
drop table if exists TempJsonStringDataTableCredits;
drop table if exists MovieProductionCountries;
drop table if exists MovieProductionCompanies;
drop table if exists MovieSpokenLanguages;
drop table if exists MovieGenres;
drop table if exists TempJsonStringDataTableMetadata;
drop table if exists MoviesProductionMetadata;
drop table if exists MoviesLanguageMetadata;
drop table if exists TempMoviesMetadata;
drop table if exists MoviesMetadata;
drop table if exists AdditionalDailyBoxOfficeRevenueData;
drop table if exists AdditionalRevenueData;
drop table if exists TempReleasedMovies;
drop table if exists ReleasedMoviesMetadata;
drop table if exists Movies;
drop table if exists MovieLinks;

-- Create MovieLinks Table
-- The MovieLinks table will serve as a central point of reference for all movies
-- This will allow other tables like keywords, ratings and movie participants to reference movies
-- When creating this table we want to make sure that we do not have any duplicate movieIds, imdbIds or tmdbIds
-- We also want to make sure that we do not have any NULL, empty or 0 values for any IDs
-- Going forward, all movies, keywords, ratings and movie participants will have a some sort of reference
-- present in movie links and the data model will enforce this.  
CREATE TABLE MovieLinks (
    movieId INT UNIQUE NOT NULL,
    imdbId CHAR(7) UNIQUE NOT NULL,
    tmdbId INT UNIQUE NOT NULL,  
    PRIMARY KEY (movieId, imdbId, tmdbId)
);
-- LOAD DATA INFILE statement for MovieLinks
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/links.csv'
IGNORE INTO TABLE MovieLinks
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(movieId, imdbId, @tmdbId)
SET tmdbId = CASE
    WHEN TRIM(@tmdbId) IN ('', '0') OR @tmdbId NOT REGEXP '^-?[0-9]+$' THEN NULL
    ELSE CAST(@tmdbId AS UNSIGNED)
END;
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs
DELETE FROM MovieLinks WHERE tmdbId = '0' OR tmdbId = '' OR tmdbId = 0 OR imdbId = '0' OR imdbId = '' OR imdbId = 0 OR movieId = '0' OR movieId = '' OR movieId = 0;



-- At this point MovieLinks does not have any NULL, empty or 0 values for any IDs
-- We verified this through testing
-- Going forward, we will only consider data that has a valid ID translation available in the MovieLinks table
-- Otherwise, tables which use different types of IDs will not be able to reference eachother if a connection
-- cannot be made through MovieLinks



-- For Movies table creation, we need to drop any data that has a Null imdbId, 0 or empty imdbId,, 
-- since we will be using that as the primary key, also need to drop any data that has a Null title
-- as a title is required for a movie. Null overview and tagline do not make a movie useless, so we allow it,
-- we will not drop data that has a Null overview or tagline. 
CREATE TABLE Movies (
    imdbId CHAR(7) NOT NULL,
    title VARCHAR(1000) NOT NULL,
    tagline VARCHAR(1000),
    overview VARCHAR(10000),
    PRIMARY KEY (imdbId)
);
-- LOAD DATA INFILE statement for Movies with IGNORE to skip duplicates
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/movies_metadata.csv'
IGNORE INTO TABLE Movies
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@dummy1, @dummy2, @dummy3, @dummy4, @dummy5, @dummy6, @var_imdbId, @dummy8, @dummy9, overview, @dummy11, @dummy12, @dummy13, @dummy14, @dummy15, @dummy16, @dummy17, @dummy18, @dummy19, tagline, @var_title, @dummy22, @dummy23, @dummy24)
SET imdbId = CASE 
                WHEN TRIM(@var_imdbId) IN ('', '0') THEN NULL
                WHEN LEFT(TRIM(@var_imdbId), 2) = 'tt' THEN SUBSTRING(TRIM(@var_imdbId), 3)
                ELSE TRIM(@var_imdbId)
             END,
    title = NULLIF(TRIM(@var_title), '');
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs and ensuring all rows have a title
-- Also deleting any rows that do not have a corresponding ID translation in MovieLinks
DELETE FROM Movies WHERE imdbId = '0' OR imdbId = '' OR imdbId = 0 OR title = '';
DELETE FROM Movies WHERE imdbId NOT IN (SELECT imdbId FROM MovieLinks);
-- Adding foreign key constraint to Movies table to refernce MovieLinks
ALTER TABLE Movies
ADD CONSTRAINT fk_movies_imdbid
FOREIGN KEY (imdbId) REFERENCES MovieLinks(imdbId)
ON UPDATE CASCADE
ON DELETE CASCADE;



-- At this point movies does not have any NULL, empty or 0 values for any IDs
-- Additionally, title does not have any NULL or empty values
-- There are now around 46,000 movies in the Movies table, all with corresponding
-- ID translations in the MovieLinks table
-- We verified this through testing



-- Now we handle the ReleasedMoviesMetadata specialization table creation which specializes off of Movies
-- The purpose of ReleasedMoviesMetadata is to contain all the movies that have actually been released
-- along with some additional metadata that is only available for released movies
-- Relating to this table there will also be additional revenue data that is only relevant for released movies
-- Note that an additional temp table will be required to copy over the widest release data from boxofficemojo_releases.csv
-- This is because the widest release data is not available in the movies_metadata.csv file
CREATE TABLE ReleasedMoviesMetadata (
    imdbId CHAR(7) NOT NULL,
    popularity FLOAT NOT NULL,
    voteAverage FLOAT NOT NULL,
    voteCount INT NOT NULL,
    widestReleases VarChar(255),
    PRIMARY KEY (imdbId)
);
-- LOAD DATA INFILE statement for ReleasedMoviesMetadata with IGNORE to skip duplicates
-- Here we are making sure that we only load data that has a status of Released
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/movies_metadata.csv'
IGNORE INTO TABLE ReleasedMoviesMetadata
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@dummy1, @dummy2, @dummy3, @dummy4, @dummy5, @dummy6, @var_imdbId, @dummy8, @dummy9, @dummy10, popularity, @dummy12, @dummy13, @dummy14, @dummy15, @dummy16, @dummy17, @dummy18, @var_status, @dummy20, @dummy21, @dummy22, voteAverage, voteCount)
SET imdbId = CASE 
                WHEN @var_status != 'Released' THEN NULL
                WHEN LEFT(TRIM(@var_imdbId), 2) = 'tt' THEN SUBSTRING(TRIM(@var_imdbId), 3)
                ELSE TRIM(@var_imdbId)
             END;
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs and ensuring that any ReleasedMoviesMetadata has a corresponding movie in Movies
-- which it specializes off of.
DELETE FROM ReleasedMoviesMetadata WHERE imdbId = '0' OR imdbId = '' OR imdbId = 0;
DELETE FROM ReleasedMoviesMetadata WHERE imdbId NOT IN (SELECT imdbId FROM Movies);
-- We have still not yet filled in the widestReleases column for ReleasedMoviesMetadata because that data is in a different file
-- called boxofficemojo_releases.csv. This TempReleasedMovies table will hold that data temporarily and then the data will be
-- copied over to ReleasedMoviesMetadata.
-- Create TempReleasedMovies table to hold the widest release data
CREATE TABLE TempReleasedMovies (
    imdbId CHAR(7) NOT NULL,
    widestReleases VarChar(255) NOT NULL,
    PRIMARY KEY (imdbId)
);
-- LOAD DATA INFILE statement for TempReleasedMovies with IGNORE to skip duplicates
-- Load the widest release data from boxofficemojo_releases.csv into TempReleasedMovies
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/hsx_bomojo_data/boxofficemojo_releases.csv'
IGNORE INTO TABLE TempReleasedMovies
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@dummy1, @dummy2, @dummy3, @var_imdbId, @dummy5, @dummy6, @dummy7, @dummy8, @dummy9, @dummy10, @dummy11, @dummy12, widestReleases, @dummy14, @dummy15, @dummy16, @dummy17, @dummy18, @dummy19, @dummy_20, @dummy_21)
SET imdbId = CASE 
                WHEN TRIM(@var_imdbId) = 'None' THEN NULL
                WHEN LEFT(TRIM(@var_imdbId), 2) = 'tt' THEN SUBSTRING(TRIM(@var_imdbId), 3)
                ELSE TRIM(@var_imdbId)
             END;
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs and ensuring that any TempReleasedMovies has a corresponding movie in ReleasedMoviesMetadata
DELETE FROM TempReleasedMovies WHERE imdbId = '0' OR imdbId = '' OR imdbId = 0;
DELETE FROM TempReleasedMovies WHERE imdbId NOT IN (SELECT imdbId FROM ReleasedMoviesMetadata);
-- Now we can copy over the widestReleases data from TempReleasedMovies to ReleasedMoviesMetadata
UPDATE ReleasedMoviesMetadata 
SET widestReleases = (
    SELECT widestReleases 
    FROM TempReleasedMovies 
    WHERE TempReleasedMovies.imdbId = ReleasedMoviesMetadata.imdbId
)
WHERE imdbId IN (
    SELECT imdbId 
    FROM TempReleasedMovies
);
-- Adding foreign key constraint to ReleasedMoviesMetadata table to reference Movies
ALTER TABLE ReleasedMoviesMetadata
ADD CONSTRAINT fk_releasedmoviesmetadata_imdbid
FOREIGN KEY (imdbId) REFERENCES Movies(imdbId)
ON UPDATE CASCADE
ON DELETE CASCADE;
-- Drop the temp table since it has served its purpose after the copy over and we no longer need it. 
drop table if exists TempReleasedMovies;


-- Next we will create the AdditionalRevenueData table which will hold additional revenue data for released movies
-- This means that it must specialize off of ReleasedMoviesMetadata and reference it through a foreign key
-- Create AdditionalRevenueData table
CREATE TABLE AdditionalRevenueData (
    imdbId CHAR(7) UNIQUE NOT NULL,
    releaseIdentifier CHAR(9) UNIQUE NOT NULL,
    domesticRevenue INT NOT NULL,
    internationalRevenue INT NOT NULL,
    worldwideRevenue INT NOT NULL,
    PRIMARY KEY (imdbId, releaseIdentifier)
);
-- LOAD DATA INFILE statement for AdditionalRevenueData with IGNORE to skip duplicates
-- Load the additional revenue data from boxofficemojo_releases.csv into AdditionalRevenueData
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/hsx_bomojo_data/boxofficemojo_releases.csv'
IGNORE INTO TABLE AdditionalRevenueData
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@var_releaseidentifier, @dummy2, @dummy3, @var_imdbId, @dummy5, @dummy6, @dummy7, domesticRevenue, internationalRevenue, worldwideRevenue, @dummy11, @dummy12, @dummy13, @dummy14, @dummy15, @dummy16, @dummy17, @dummy18, @dummy19, @dummy_20, @dummy_21)
SET imdbId = CASE 
                WHEN TRIM(@var_imdbId) = 'None' THEN NULL
                WHEN LEFT(TRIM(@var_imdbId), 2) = 'tt' THEN SUBSTRING(TRIM(@var_imdbId), 3)
                ELSE TRIM(@var_imdbId)
             END,
            releaseIdentifier = CASE 
                WHEN TRIM(@var_releaseidentifier) = 'None' THEN NULL
                WHEN LEFT(TRIM(@var_releaseidentifier), 2) = 'rl' THEN SUBSTRING(TRIM(@var_releaseidentifier), 3)
                ELSE TRIM(@var_releaseidentifier)
             END;
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs and ensuring that any AdditionalRevenueData has a corresponding movie in ReleasedMoviesMetadata
DELETE FROM AdditionalRevenueData WHERE imdbId = '0' OR imdbId = '' OR imdbId = 0 OR releaseIdentifier = '0' OR releaseIdentifier = '' OR releaseIdentifier = 0;
DELETE FROM AdditionalRevenueData WHERE imdbId NOT IN (SELECT imdbId FROM ReleasedMoviesMetadata);
-- Adding foreign key constraint to AdditionalRevenueData table to reference ReleasedMoviesMetadata
ALTER TABLE AdditionalRevenueData
ADD CONSTRAINT fk_additionalrevenuedata_imdbid
FOREIGN KEY (imdbId) REFERENCES ReleasedMoviesMetadata(imdbId)
ON UPDATE CASCADE
ON DELETE CASCADE;


-- Now we need to create the AdditionalDailyBoxOfficeRevenueData table which will hold additional daily box office revenue data for released movies
-- This data will be broken out by date and will reference the AdditionalRevenueData table through a foreign key
-- There will be many rows for each movie in AdditionalRevenueData, one for each day that the movie was in theaters and/or when data was collected
-- Create AdditionalDailyBoxOfficeRevenueData table
CREATE TABLE AdditionalDailyBoxOfficeRevenueData (
    releaseIdentifier CHAR(9) NOT NULL,
    boxOfficeDate DATE NOT NULL,
    dailyDomesticGross INT NOT NULL,
    dailyTheaterCount INT NOT NULL,
    PRIMARY KEY (releaseIdentifier, boxOfficeDate)
);
-- LOAD DATA INFILE statement for AdditionalDailyBoxOfficeRevenueData with IGNORE to skip duplicates
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/hsx_bomojo_data/boxofficemojo_daily_boxoffice.csv'
IGNORE INTO TABLE AdditionalDailyBoxOfficeRevenueData
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@var_boxofficedate, @var_releaseidentifier, dailyDomesticGross, dailyTheaterCount, @dummy5, @dummy6)
SET releaseIdentifier = CASE 
            WHEN TRIM(@var_releaseidentifier) = 'None' THEN NULL
            WHEN LEFT(TRIM(@var_releaseidentifier), 2) = 'rl' THEN SUBSTRING(TRIM(@var_releaseidentifier), 3)
            ELSE TRIM(@var_releaseidentifier)
        END,
    boxOfficeDate = CASE
            WHEN STR_TO_DATE(TRIM(@var_boxofficedate), '%Y-%m-%d') IS NULL THEN NULL
            WHEN TRIM(@var_boxofficedate) = '0000-00-00' THEN NULL
            ELSE STR_TO_DATE(TRIM(@var_boxofficedate), '%Y-%m-%d')
            END;
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs and ensuring that any AdditionalDailyBoxOfficeRevenueData has a corresponding movie in ReleasedMoviesMetadata
DELETE FROM AdditionalDailyBoxOfficeRevenueData WHERE releaseIdentifier = '0' OR releaseIdentifier = '' OR releaseIdentifier = 0;
DELETE FROM AdditionalDailyBoxOfficeRevenueData WHERE releaseIdentifier NOT IN (SELECT releaseIdentifier FROM AdditionalRevenueData);
-- Adding foreign key constraint to AdditionalDailyBoxOfficeRevenueData table to reference AdditionalRevenueData
ALTER TABLE AdditionalDailyBoxOfficeRevenueData
ADD CONSTRAINT fk_additionaldailyboxofficerevenuedata_releaseidentifier
FOREIGN KEY (releaseIdentifier) REFERENCES AdditionalRevenueData(releaseIdentifier)
ON UPDATE CASCADE
ON DELETE CASCADE;


-- Now we handle MoviesMetadata specialization table creation which specializes off of Movies
-- The purpose of MoviesMetadata is to contain all the movies that have metadata available
-- This includes movies that have not been released yet
-- A lot of this metadata is optional and may not be available for all movies so we will allow NULL values
-- Additionally, there will be a MovieGenres table which will contain the genres for each movie that references MoviesMetadata
-- Additionally, because mpaarating and boxofficemojourl are not available in the movies_metadata.csv file
-- but rather come from the boxofficemojo_releases.csv file, we will need to create a temp table to hold that data
-- and then copy it over to MoviesMetadata
CREATE TABLE MoviesMetadata (
    imdbId CHAR(7) NOT NULL,
    runtime FLOAT NOT NULL,
    mpaaRating VARCHAR(255),
    boxOfficeMojoUrl VARCHAR(255),
    posterPath VARCHAR(255),
    PRIMARY KEY (imdbId)
);
-- LOAD DATA INFILE statement for MoviesMetadata with IGNORE to skip duplicates
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/movies_metadata.csv'
IGNORE INTO TABLE MoviesMetadata
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@dummy1, @dummy2, @dummy3, @dummy4, @dummy5, @dummy6, @var_imdbId, @dummy8, @dummy9, @dummy10, @dummy11, posterPath, @dummy13, @dummy14, @dummy13, @dummy16, runtime, @dummy18, @dummy19, @dummy20, @dummy21, @dummy22, @dummy23, @dummy24)
SET imdbId = CASE 
                WHEN LEFT(TRIM(@var_imdbId), 2) = 'tt' THEN SUBSTRING(TRIM(@var_imdbId), 3)
                ELSE TRIM(@var_imdbId)
             END;
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs and ensuring that any MoviesMetadata has a corresponding movie in Movies as it specializes off of it
DELETE FROM MoviesMetadata WHERE imdbId = '0' OR imdbId = '' OR imdbId = 0;
DELETE FROM MoviesMetadata WHERE imdbId NOT IN (SELECT imdbId FROM Movies);
-- Now we create a temp table which will hold the mpaa rating and box office mojo url data
-- this data is not available in the movies_metadata.csv file but rather comes from the boxofficemojo_releases.csv file
-- this table will be used to copy over the data to MoviesMetadata
CREATE TABLE TempMoviesMetadata (
    imdbId CHAR(7) NOT NULL,
    mpaaRating VARCHAR(255),
    boxOfficeMojoUrl VARCHAR(255),
    PRIMARY KEY (imdbId)
);
-- LOAD DATA INFILE statement for TempMoviesMetadata with IGNORE to skip duplicates
-- Loading from the boxofficemojo_releases.csv file into TempMoviesMetadata
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/hsx_bomojo_data/boxofficemojo_releases.csv'
IGNORE INTO TABLE TempMoviesMetadata
FIELDS TERMINATED BY ','
OPTIONALLY ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@dummy1, @dummy2, @dummy3, @var_imdbId, @dummy5, @dummy6, @dummy7, @dummy8, @dummy9, @dummy10, @dummy11, @dummy12, @dummy13, @dummy14, @dummy15, mpaaRating, @dummy17, @dummy18, @dummy19, boxOfficeMojoUrl, @dummy_21)
SET imdbId = CASE 
                WHEN TRIM(@var_imdbId) = 'None' THEN NULL
                WHEN LEFT(TRIM(@var_imdbId), 2) = 'tt' THEN SUBSTRING(TRIM(@var_imdbId), 3)
                ELSE TRIM(@var_imdbId)
             END;
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs and ensuring that any TempMoviesMetadata has a corresponding movie in MoviesMetadata
DELETE FROM TempMoviesMetadata WHERE imdbId = '0' OR imdbId = '' OR imdbId = 0;
DELETE FROM TempMoviesMetadata WHERE imdbId NOT IN (SELECT imdbId FROM MoviesMetadata);
-- Now we can copy over the mpaaRating and boxOfficeMojoUrl data from TempMoviesMetadata to MoviesMetadata
UPDATE MoviesMetadata 
SET mpaaRating = (
    SELECT mpaaRating 
    FROM TempMoviesMetadata 
    WHERE TempMoviesMetadata.imdbId = MoviesMetadata.imdbId
), boxOfficeMojoUrl = (
    SELECT boxOfficeMojoUrl 
    FROM TempMoviesMetadata 
    WHERE TempMoviesMetadata.imdbId = MoviesMetadata.imdbId
)
WHERE imdbId IN (
    SELECT imdbId 
    FROM TempMoviesMetadata
);
-- Adding foreign key constraint to MoviesMetadata table to reference Movies
ALTER TABLE MoviesMetadata
ADD CONSTRAINT fk_moviesmetadata_imdbid
FOREIGN KEY (imdbId) REFERENCES Movies(imdbId)
ON UPDATE CASCADE
ON DELETE CASCADE;
-- Drop the temp table since it has served its purpose after the copy over and we no longer need it.
drop table if exists TempMoviesMetadata;



-- Specializing off of MoviesMetadata, we will have two tables including MoviesLanguageMetadata and MoviesProductionMetadata



-- Create MoviesLanguageMetadata table
-- This table will specialize off of MoviesMetadata and will contain the original language for each movie
-- It will also be referenced by the MoviesSpokenLanguages table which will contain the spoken languages for each movie
CREATE TABLE MoviesLanguageMetadata (
    imdbId CHAR(7) NOT NULL,
    originalLanguage VARCHAR(255) NOT NULL,
    PRIMARY KEY (imdbId)
);
-- LOAD DATA INFILE statement for MoviesMetadata with IGNORE to skip duplicates
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/movies_metadata.csv'
IGNORE INTO TABLE MoviesLanguageMetadata
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@dummy1, @dummy2, @dummy3, @dummy4, @dummy5, @dummy6, @var_imdbId, originalLanguage, @dummy9, @dummy10, @dummy11, @dummy12, @dummy13, @dummy14, @dummy15, @dummy16, @dummy17, @dummy18, @dummy19, @dummy20, @dummy21, @dummy22, @dummy23, @dummy24)
SET imdbId = CASE 
                WHEN LEFT(TRIM(@var_imdbId), 2) = 'tt' THEN SUBSTRING(TRIM(@var_imdbId), 3)
                ELSE TRIM(@var_imdbId)
             END;
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs and ensuring that any MoviesLanguageMetadata has a corresponding movie in MoviesMetadata
-- since it specializes off of it
DELETE FROM MoviesLanguageMetadata WHERE imdbId = '0' OR imdbId = '' OR imdbId = 0 OR originalLanguage = 'xx';
DELETE FROM MoviesLanguageMetadata WHERE imdbId NOT IN (SELECT imdbId FROM MoviesMetadata);
-- Adding foreign key constraint to MoviesLanguageMetadata table to reference MoviesMetadata
ALTER TABLE MoviesLanguageMetadata
ADD CONSTRAINT fk_movieslanguagemetadata_imdbid
FOREIGN KEY (imdbId) REFERENCES MoviesMetadata(imdbId)
ON UPDATE CASCADE
ON DELETE CASCADE;


-- Create MoviesProductionMetadata table
-- This table is the second specialization off of MoviesMetadata and will contain the budget, release date and release status
-- This is all relevant production metadata for each movie
-- It will be referenced by the MovieProductionCompanies and MovieProductionCountries tables as well
CREATE TABLE MoviesProductionMetadata (
    imdbId CHAR(7) NOT NULL,
    budget INT NOT NULL,
    releaseDate DATE NOT NULL,
    releaseStatus VARCHAR(255) NOT NULL,
    PRIMARY KEY (imdbId)
);
-- LOAD DATA INFILE statement for MoviesMetadata with IGNORE to skip duplicates
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/movies_metadata.csv'
IGNORE INTO TABLE MoviesProductionMetadata
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@dummy1, @dummy2, budget, @dummy4, @dummy5, @dummy6, @var_imdbId, @dummy8, @dummy9, @dummy10, @dummy11, @dummy12, @dummy13, @dummy14, @var_releasedate, @dummy16, @dummy17, @dummy18, releaseStatus, @dummy20, @dummy21, @dummy22, @dummy23, @dummy24)
SET imdbId = CASE 
                WHEN LEFT(TRIM(@var_imdbId), 2) = 'tt' THEN SUBSTRING(TRIM(@var_imdbId), 3)
                ELSE TRIM(@var_imdbId)
             END,
    releaseDate = CASE
                    WHEN STR_TO_DATE(TRIM(@var_releasedate), '%Y-%m-%d') IS NULL THEN NULL
                    WHEN TRIM(@var_releasedate) = '0000-00-00' THEN NULL
                    ELSE STR_TO_DATE(TRIM(@var_releasedate), '%Y-%m-%d')
                  END;
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs and ensuring that any MoviesProductionMetadata has a corresponding movie in MoviesMetadata
-- since it specializes off of it
-- Also deleting any rows that have an invalid release date
DELETE FROM MoviesProductionMetadata WHERE imdbId = '0' OR imdbId = '' OR imdbId = 0;
DELETE FROM MoviesProductionMetadata WHERE imdbId NOT IN (SELECT imdbId FROM MoviesMetadata);
-- Update sql_mode so that correct zero dates can be removed from the database
SET sql_mode = 'ONLY_FULL_GROUP_BY,NO_ZERO_IN_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
DELETE FROM MoviesProductionMetadata WHERE releaseDate = null OR releaseDate = '0000-00-00';
-- After making the needed updates, set the sql_mode back to the original
SET sql_mode = 'ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- Adding foreign key constraint to MoviesProductionMetadata table to reference MoviesMetadata
ALTER TABLE MoviesProductionMetadata
ADD CONSTRAINT fk_moviesproductionmetadata_imdbid
FOREIGN KEY (imdbId) REFERENCES MoviesMetadata(imdbId)
ON UPDATE CASCADE
ON DELETE CASCADE;


-- Now we handle the multivalued attributes for the MoviesMetadata, MoviesLanguageMetadata and MoviesProductionMetadata tables
-- These include genres, production companies, production countries, spoken languages which will be stored in their own tables
-- The data for each of these is available in the movies_metadata.csv file, however it is in a broken JSON format
-- A lot of additional processing will be required to extract the data from these incorrectly formatted JSON strings
-- into single attributes that can be stored in their own tables.
-- We will create a temp table to hold the raw JSON strings and then we will parse them in the python script and store them in their own tables
CREATE TABLE TempJsonStringDataTableMetadata (
    imdbId CHAR(7) NOT NULL,
    rawGenres VARCHAR(10000) NOT NULL,
    rawSpokenLanguages TEXT NOT NULL,
    rawProductionCompanies TEXT NOT NULL,
    rawProductionCountries TEXT NOT NULL,
    PRIMARY KEY (imdbId)
);
-- LOAD DATA INFILE statement for TempJsonStringDataTableMetadata with IGNORE to skip duplicates
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/movies_metadata.csv'
IGNORE INTO TABLE TempJsonStringDataTableMetadata
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(@dummy1, @dummy2, @dummy3, rawGenres, @dummy5, @dummy6, @var_imdbId, @dummy8, @dummy9, @dummy10, @dummy11, @dummy12, rawProductionCompanies, rawProductionCountries, @dummy15, @dummy16, @dummy17, rawSpokenLanguages, @dummy19, @dummy20, @dummy21, @dummy22, @dummy23, @dummy24)
SET imdbId = CASE 
                WHEN LEFT(TRIM(@var_imdbId), 2) = 'tt' THEN SUBSTRING(TRIM(@var_imdbId), 3)
                ELSE TRIM(@var_imdbId)
             END;
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs and ensuring that any TempJsonStringDataTableMetadata has a corresponding movie in MoviesMetadata
-- Since all the relevant attributes that we are obtaining are some form of specialization off of MoviesMetadata
-- We also delete any rows that have empty or NULL values for any of the raw JSON strings (these are very few)
DELETE FROM TempJsonStringDataTableMetadata WHERE imdbId = '0' OR imdbId = '' OR imdbId = 0;
DELETE FROM TempJsonStringDataTableMetadata WHERE imdbId NOT IN (SELECT imdbId FROM MoviesMetadata);
DELETE FROM TempJsonStringDataTableMetadata WHERE rawGenres = '[]' OR rawSpokenLanguages = '[]' OR rawProductionCompanies = '[]' OR rawProductionCountries = '[]';
-- Replace single quotes with double quotes and convert to valid JSON in the strings where it is possible
-- Some of the strings have nested single quotes and thus this conversion is not possible for all of them
-- But where it is, we do it to make the processing easier
UPDATE TempJsonStringDataTableMetadata
SET rawGenres = REPLACE(REPLACE(rawGenres, '''', '"'), "'", '"')
WHERE rawGenres IS NOT NULL;
UPDATE TempJsonStringDataTableMetadata
SET rawSpokenLanguages = REPLACE(REPLACE(rawSpokenLanguages, '''', '"'), "'", '"')
WHERE rawSpokenLanguages IS NOT NULL;
-- Modify the columns to be of type JSON that we were able to convert to valid JSON
ALTER TABLE TempJsonStringDataTableMetadata MODIFY rawGenres JSON;
ALTER TABLE TempJsonStringDataTableMetadata MODIFY rawSpokenLanguages JSON;



-- Now we handle multivalued attributes which specialize off of MoviesMetadata, MoviesLanguageMetadata and MoviesProductionMetadata
-- These each have a corresponding attribute in the temp table and the temp table will be processed and the processed data copied over
-- into each of these tables below. 
-- These include genres, production companies, production countries, spoken languages which will be stored in their own tables
-- And will reference the MoviesMetadata, MoviesLanguageMetadata and MoviesProductionMetadata tables



-- Create Genres table which will reference MoviesMetadata
CREATE TABLE MovieGenres (
    imdbId CHAR(7) NOT NULL,
    genreName VARCHAR(255) NOT NULL,
    PRIMARY KEY (imdbId, genreName)
);
-- Create SpokenLanguages table which will reference MoviesLanguageMetadata
CREATE TABLE MovieSpokenLanguages (
    imdbId CHAR(7) NOT NULL,
    languageName VARCHAR(255) NOT NULL,
    PRIMARY KEY (imdbId, languageName)
);
-- Create ProductionCompanies table which will reference MoviesProductionMetadata
CREATE TABLE MovieProductionCompanies (
    imdbId CHAR(7) NOT NULL,
    companyName VARCHAR(255) NOT NULL,
    PRIMARY KEY (imdbId, companyName)
);
-- Create ProductionCountries table which will reference MoviesProductionMetadata
CREATE TABLE MovieProductionCountries (
    imdbId CHAR(7) NOT NULL,
    countryName VARCHAR(255) NOT NULL,
    PRIMARY KEY (imdbId, countryName)
);



-- Next we handle the creation of the MovieParticipants portion of our data model
-- This will include the CastMember and CrewMember tables which will specialize off of MovieParticipants
-- The data is all present in credits.csv but it is in a broken JSON format
-- A lot of additional processing will be required to extract the data from these incorrectly formatted JSON strings
-- First the data will be loaded into the TempJsonStringDataTableCredits table and then it will be processed in the python script
-- and then copied over to the MovieParticipants, CastMember and CrewMember tables



-- Create a temp table to hold credits.csv data which will be parsed
-- This table will be used to copy over the data to MovieParticipants, CastMember and CrewMember
-- Create TempJsonStringDataTableCredits table to hold raw credits data
CREATE TABLE TempJsonStringDataTableCredits (
    tmdbId INT NOT NULL,
    rawCast TEXT NOT NULL,
    rawCrew TEXT NOT NULL,
    PRIMARY KEY (tmdbId)
);
-- LOAD DATA INFILE statement for TempJsonStringDataTableCredits with IGNORE to skip duplicates
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/credits.csv'
IGNORE INTO TABLE TempJsonStringDataTableCredits
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(rawCast, rawCrew, tmdbId);
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs and ensuring that any TempJsonStringDataTableCredits has a corresponding movie in MovieLinks
-- Since all the relevant attributes that we are obtaining are some form of specialization off of MovieLinks
DELETE FROM TempJsonStringDataTableCredits WHERE tmdbId = '0' OR tmdbId = '' OR tmdbId = 0;
DELETE FROM TempJsonStringDataTableCredits WHERE tmdbId NOT IN (SELECT tmdbId FROM MovieLinks);
DELETE FROM TempJsonStringDataTableCredits WHERE rawCast = '[]' OR rawCrew = '[]';



-- Below we create all of the relevant tables for the MovieParticipants portion of our data model as well
-- as the CastMember and CrewMember specialization tables. These will be filled in with data from the 
-- TempJsonStringDataTableCredits table as discussed above. 



-- Create MovieParticipants table
CREATE Table MovieParticipants (
    creditId CHAR(24) UNIQUE NOT NULL,
    tmdbId INT NOT NULL, 
    participantName VARCHAR(255) NOT NULL,
    gender INT,
    PRIMARY KEY (creditId, tmdbId)
);
-- Create CastMember table
CREATE TABLE CastMember (
    creditId CHAR(24) NOT NULL,
    characterName VARCHAR(255),
    roleProminence INT,
    PRIMARY KEY (creditId)
);
-- Create CrewMember table
CREATE TABLE CrewMember (
    creditId CHAR(24) NOT NULL,
    crewJob VARCHAR(255),
    crewDepartment VARCHAR(255),
    PRIMARY KEY (creditId)
);


-- Similar to how we have done in the above, we will create a temp table to hold the raw malformatted JSON strings
-- for keywords.csv and then we will parse them in the python script and store them in their own table
-- Create TempKeywords table to store raw keywords data
CREATE TABLE TempKeywords (
    tmdbId INT NOT NULL,
    rawKeywords TEXT NOT NULL,
    PRIMARY KEY (tmdbId)
);
-- LOAD DATA INFILE statement for TempKeywords with IGNORE to skip duplicates
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/keywords.csv'
IGNORE INTO TABLE TempKeywords
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(tmdbId, rawKeywords);
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs and ensuring that any TempKeywords has a corresponding movie in MovieLinks
DELETE FROM TempKeywords WHERE tmdbId = '0' OR tmdbId = '' OR tmdbId = 0 OR rawKeywords = '[]';
DELETE FROM TempKeywords WHERE tmdbId NOT IN (SELECT tmdbId FROM MovieLinks);

-- Create Keywords table which will be filled by the python script with the processed data from TempKeywords
CREATE TABLE MovieKeywords (
    tmdbId INT NOT NULL,
    keywordName VARCHAR(255) NOT NULL,
    PRIMARY KEY (tmdbId, keywordName)
);


-- Create TempDomesticAverageTicketPrice table
-- Need to make a temp table because duplicate years exist in the data
-- A python script will take the average of the duplicate years and insert the 
-- average into the DomesticAverageTicketPrice table
CREATE TABLE TempDomesticAverageTicketPrice (
    year INT NOT NULL,
    averageTicketPriceUsd FLOAT NOT NULL,
    sourceUrl VARCHAR(255) NOT NULL
);
-- LOAD DATA INFILE statement for TempDomesticAverageTicketPrice with IGNORE to skip duplicates
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/domestic_avg_movie_ticket_prices.csv'
IGNORE INTO TABLE TempDomesticAverageTicketPrice
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(year, averageTicketPriceUsd, sourceUrl);
SHOW WARNINGS;

-- Create the DomesticAverageTicketPrice table which will be filled by the python script with 
-- the processed data from TempDomesticAverageTicketPrice
CREATE TABLE DomesticAverageTicketPrice (
    year INT NOT NULL,
    averageTicketPriceUsd FLOAT NOT NULL,
    sourceUrl VARCHAR(255) NOT NULL,
    PRIMARY KEY (year)
);


-- Create the Users table
-- We will be creating a User for any user that already exisits in the ratings.csv data
-- This is because we want to make sure that any user that has rated a movie has a corresponding User
-- We will also give them a default password of 'password' and a default role of 'User' since 
-- we do not have any other information about them. These fields will become even more useful
-- when new users are created. 
CREATE TABLE Users (
    userId INT NOT NULL AUTO_INCREMENT,
    userFullName VARCHAR(255),
    userPassword VARCHAR(255) NOT NULL,
    userRole Enum('Admin', 'User') NOT NULL,
    PRIMARY KEY (userId)
);
-- LOAD DATA INFILE statement for UserRatings with IGNORE to skip duplicates
-- Make a user for any user rating that already exists for a user
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/ratings_small.csv'
IGNORE INTO TABLE Users
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(userId, @dummy2, @dummy3, @dummy4)
SET userRole = 'User',
    userPassword = 'password';
SHOW WARNINGS;
-- Deleting any rows that have invalid IDs
DELETE FROM Users WHERE userId = '0' OR userId = '' OR userId = 0;


-- Create UserRatings table
CREATE TABLE UserRatings (
    userId INT NOT NULL,
    movieId INT NOT NULL,
    rating FLOAT NOT NULL,
    ratingTimestamp INT NOT NULL,
    PRIMARY KEY (userId, movieId)
);
-- Load data into UserRatings table
LOAD DATA INFILE '/var/lib/mysql-files/03-Movies/ratings_small.csv'
IGNORE INTO TABLE UserRatings
FIELDS TERMINATED BY ',' 
OPTIONALLY ENCLOSED BY '"' 
LINES TERMINATED BY '\n'
IGNORE 1 ROWS
(userId, movieId, rating, ratingTimestamp);
SHOW WARNINGS;
-- Delete any UserRatings with invalid IDs and any UserRatings that do not have a corresponding movieId in the MovieLinks table
DELETE FROM UserRatings WHERE movieId = '0' OR movieId = '' OR movieId = 0 OR userId = '0' OR userId = '' OR userId = 0;
DELETE FROM UserRatings WHERE movieId NOT IN (SELECT movieId FROM MovieLinks);
DELETE FROM UserRatings WHERE userId NOT IN (SELECT userId FROM Users);
-- Delete any user ratings that are not for a movie that has been released
DELETE FROM UserRatings
WHERE NOT EXISTS (
    SELECT 1
    FROM MovieLinks ml
    INNER JOIN ReleasedMoviesMetadata rmm ON ml.imdbId = rmm.imdbId
    WHERE ml.movieId = UserRatings.movieId
);
-- Add foreign key constraints to UserRatings table to reference the Users and MovieLinks tables
ALTER TABLE UserRatings
ADD CONSTRAINT fk_userratings_movieid
FOREIGN KEY (movieId) REFERENCES MovieLinks(movieId)
ON UPDATE CASCADE
ON DELETE CASCADE;
ALTER TABLE UserRatings
ADD CONSTRAINT fk_userratings_userid
FOREIGN KEY (userId) REFERENCES Users(userId)
ON UPDATE CASCADE
ON DELETE CASCADE;

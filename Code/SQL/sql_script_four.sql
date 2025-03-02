drop table if exists TempJsonStringDataTableCredits;
drop table if exists TempJsonStringDataTableMetadata;
drop table if exists TempKeywords;
drop table if exists TempDomesticAverageTicketPrice;

-- This SQL script is to be ran after the python scripts have run and the data processing
-- has been completed. This script will then do the final data cleanup and create all
-- of the necessary foreign keys for the tables that were modified during the data processing.

-- Delete any row with Invalid IDs or that do not have a corresponding imdbId in the MoviesMetadata table
-- which it references
DELETE FROM MovieGenres WHERE imdbId = '0' OR imdbId = '' OR imdbId = 0;
DELETE FROM MovieGenres WHERE imdbId NOT IN (SELECT imdbId FROM MoviesMetadata);
-- Add foreign key constraints to MovieGenres table to reference the MoviesMetadata table
ALTER TABLE MovieGenres
ADD CONSTRAINT fk_moviegenres_imdbid
FOREIGN KEY (imdbId) REFERENCES MoviesMetadata(imdbId)
ON UPDATE CASCADE
ON DELETE CASCADE;


-- Delete any row with Invalid IDs or that do not have a corresponding imdbId in the MoviesLanguageMetadata table
-- which it references
DELETE FROM MovieSpokenLanguages WHERE imdbId = '0' OR imdbId = '' OR imdbId = 0;
DELETE FROM MovieSpokenLanguages WHERE imdbId NOT IN (SELECT imdbId FROM MoviesLanguageMetadata);
-- Add foreign key constraints to MovieSpokenLanguages table to reference the MoviesLanguageMetadata table
ALTER TABLE MovieSpokenLanguages
ADD CONSTRAINT fk_moviespokenlanguages_imdbid
FOREIGN KEY (imdbId) REFERENCES MoviesLanguageMetadata(imdbId)
ON UPDATE CASCADE
ON DELETE CASCADE;


-- Delete any row with Invalid IDs or that do not have a corresponding imdbId in the MoviesProductionMetadata table
-- which it references
DELETE FROM MovieProductionCompanies WHERE imdbId = '0' OR imdbId = '' OR imdbId = 0;
DELETE FROM MovieProductionCompanies WHERE imdbId NOT IN (SELECT imdbId FROM MoviesProductionMetadata);
-- Add foreign key constraints to MovieProductionCompanies table to reference the MoviesProductionMetadata table
ALTER TABLE MovieProductionCompanies
ADD CONSTRAINT fk_movieproductioncompanies_imdbid
FOREIGN KEY (imdbId) REFERENCES MoviesProductionMetadata(imdbId)
ON UPDATE CASCADE
ON DELETE CASCADE;


-- Delete any row with Invalid IDs or that do not have a corresponding imdbId in the MoviesProductionMetadata table
-- which it references
DELETE FROM MovieProductionCountries WHERE imdbId = '0' OR imdbId = '' OR imdbId = 0;
DELETE FROM MovieProductionCountries WHERE imdbId NOT IN (SELECT imdbId FROM MoviesProductionMetadata);
-- Add foreign key constraints to MovieProductionCountries table to reference the MoviesProductionMetadata table
ALTER TABLE MovieProductionCountries
ADD CONSTRAINT fk_movieproductioncountries_imdbid
FOREIGN KEY (imdbId) REFERENCES MoviesProductionMetadata(imdbId)
ON UPDATE CASCADE
ON DELETE CASCADE;


-- Delete any row with Invalid IDs or that do not have a corresponding imdbId in the MovieLinks table
-- which it references
DELETE FROM MovieKeywords WHERE tmdbId = '0' OR tmdbId = '' OR tmdbId = 0;
DELETE FROM MovieKeywords WHERE tmdbId NOT IN (SELECT tmdbId FROM MovieLinks);
-- Add foreign key constraints to MovieKeywords table to reference the MovieLinks table
ALTER TABLE MovieKeywords
ADD CONSTRAINT fk_moviekeywords_tmdbid
FOREIGN KEY (tmdbId) REFERENCES MovieLinks(tmdbId)
ON UPDATE CASCADE
ON DELETE CASCADE;


-- Delete any row with Invalid IDs or that do not have a corresponding tmdbId in the MovieLinks table
-- which it references
DELETE FROM MovieParticipants WHERE tmdbId = '0' OR tmdbId = '' OR tmdbId = 0 OR creditId = '0' OR creditId = '';
DELETE FROM MovieParticipants WHERE tmdbId NOT IN (SELECT tmdbId FROM MovieLinks);
-- Add foreign key constraints to MovieParticipants table to reference the MovieLinks table
ALTER TABLE MovieParticipants
ADD CONSTRAINT fk_movieparticipants_tmdbid
FOREIGN KEY (tmdbId) REFERENCES MovieLinks(tmdbId)
ON UPDATE CASCADE
ON DELETE CASCADE;


-- Delete any row with Invalid IDs or that do not have a corresponding creditId in the MovieParticipants table
-- which it references
DELETE FROM CastMember WHERE creditId = '0' OR creditId = '';
DELETE FROM CastMember WHERE creditId NOT IN (SELECT creditId FROM MovieParticipants);
-- Add foreign key constraints to CastMember table to reference the MovieParticipants table
ALTER TABLE CastMember
ADD CONSTRAINT fk_castmember_creditid
FOREIGN KEY (creditId) REFERENCES MovieParticipants(creditId)
ON UPDATE CASCADE
ON DELETE CASCADE;


-- Delete any row with Invalid IDs or that do not have a corresponding creditId in the MovieParticipants table
-- which it references
DELETE FROM CrewMember WHERE creditId = '0' OR creditId = '';
DELETE FROM CrewMember WHERE creditId NOT IN (SELECT creditId FROM MovieParticipants);
-- Add foreign key constraints to CrewMember table to reference the MovieParticipants table
ALTER TABLE CrewMember
ADD CONSTRAINT fk_crewmember_creditid
FOREIGN KEY (creditId) REFERENCES MovieParticipants(creditId)
ON UPDATE CASCADE
ON DELETE CASCADE;

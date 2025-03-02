# CineBase

# Folder structure

```
.
├── Code
│   ├── ...
│   ├── Client       # containing client code
|   |   |-- client.py
|   |   |-- client_helpers.py
│   ├── SQL          # containing SQL code and python scripts for data processing
|   |   |-- sql_script_one.sql
|   |   |-- temp_data_processing_script_two.py
|   |   |-- temp_data_processing_script_three.py
|   |   |-- sql_script_four.sql
│   └── DataMining   # containing data mining code
|   |   |-- data_analysis.py
|   |   |-- feature_importance_analysis.py
├── Schema-Design
|   |-- entity_relationship_model_diagram.pdf
│   └── relational_schema_diagram.png
└── README.md
```

# Additional Notes

## Instructions for Running Client Code

The client can be ran using the command `python3 client.py` in the `Code/Client` directory.
At this point, the client code will provide clear instructions as to how to use the client app and will guide the user to enter the appropriate commands.

The command `pip install mysql-connector-python` will need to be ran to ensure that the necessary packages are present for the client to work.

## Instructions for Running DataMining Code

The data mining analysis can be ran using the command `python3.9 data_analysis.py` from within the `Code/DataMining` directory. This will generate a summary of the data mining analysis results for which attributes affect the revenue of a movie the most in the terminal. It will also generate two relevant plots as part of the data mining analysis.

The commands `pip install pandas`, `pip install matplotlib`, `pip install seaborn` and `pip install scikit-learn` will need to be ran to ensure that the necessary packages are present for the data mining Python scripts to work.

## Instructions for Running SQL Code for Populating the Database

Four scripts including two SQL scripts and two Python scripts are required to be ran in the order that they are numbered to populate the database with data. I go into detail on how this can be done below.

The command `pip install mysql-connector-python` will need to be ran to ensure that the necessary packages are present for the Python scripts to work.

The first SQL script `sql_script_one.sql` can be ran by first connecting to the database `cinebase_db` and then running the command `source sql_script_one.sql`. This SQL script will create all of the necessary tables and populate them with data along with some temporary tables that will be loaded with raw data to be processed and added to the appropriate tables that follow with the Python scripts.

The next script to run is a Python script `temp_data_processing_script_two.py` which takes care of processing TempDomesticAverageTicketPrice data, TempKeywords data, TempSpokenLanguages data, TempProductionCompanies data and TempProductionCountries data. This script will process the unformatted broken JSON data currently stored in these tables into usable data and then add it to the corresponding tables in the appropriate format by extracting the relevant data. This python script can be ran using the command `python3 temp_data_processing_script_two.py` from within the `Code/SQL` directory.

The next script to run is a Python script `temp_data_processing_script_three.py` which takes care of processing TempMovieParticipants data, TempMovieCastMember data and TempMovieCrewMember data. This script will process the unformatted broken JSON data currently stored in these tables into usable data and then add it to the corresponding tables in the appropriate format by extracting the relevant data. This python script can be ran using the command `python3 temp_data_processing_script_three.py` from within the `Code/SQL` directory.

The final script to run is a SQL script `sql_script_four.sql` which can be ran by first connecting to the database `cinebase_db` and then running the command `source sql_script_four.sql`. This SQL script will finish off the database loading by cleaning up data added by the Python scripts and adding appropriate foreign keys to the tables which were effected by the Python scripts.

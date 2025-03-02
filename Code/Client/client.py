import mysql.connector  # pip install mysql-connector-python to get this package
from client_helpers import create_option_1_query
from client_helpers import create_option_2_query
from client_helpers import create_option_3_query
from client_helpers import create_option_4_query
from client_helpers import create_option_5_query
from client_helpers import create_option_6_query
from client_helpers import create_option_7_query
from client_helpers import create_option_8_query
from client_helpers import create_option_9_query


config = {
    "user": "db_user",
    "password": "your_password",
    "host": "localhost",
    "database": "cinebase_db",
    "raise_on_warnings": True,
}

# contains all of the genereal query options available to all users including non-admin
general_query_options = [
    "(1) Search for movies",
    "(2) Search for details on a given movie",
    "(3) Search for average movie ticket prices by year",
    "(4) Add a new user rating on a movie",
    "(5) Update an existing user rating on a movie",
    "(6) Delete an existing user rating on a movie",
]

# Only show these options if the user has an Admin role
# We only want to allow users to create, update and delete
# Movies if they have Admin permissions
# Adding and updating movies should also come with the options
# to create or modify all of the additional metadata tied
# to a movie, including ReleasedMoviesMetadata, revenue data (general and daily),
# movie metadata (general, language, production), keywords and
# participants (cast and crew)
general_query_options_admin = [
    "(7) Add a new movie",
    "(8) Update an existing movie",
    "(9) Delete an existing Movie",
]

# Connect to the database
cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()


# helper function to handle creating a new user
def create_account(cnx, cursor):
    print("Creating account...")
    print()
    while True:
        # Allow users to skip entering a username
        username = input("Enter your full name (or press enter to skip): ")
        print()

        # Collect password and confirm it
        password = input("Enter your new account password: ")
        confirm_password = input("Confirm your password: ")
        print()

        # Check if passwords match
        if password != confirm_password:
            print("Passwords do not match. Please try again.")
            print()
            continue

        # Get the user role
        role = input("Enter your new account role (Can either be User or Admin): ")
        print()

        # Validate role
        if role != "User" and role != "Admin":
            print("Invalid role. Please try again.")
            print()
            continue

        # Insert new user into the Users table
        insert_query = "INSERT INTO Users (userFullName, userPassword, userRole) VALUES (%s, %s, %s)"
        cursor.execute(insert_query, (username, password, role))
        cnx.commit()
        print("Account created successfully!")
        print()

        # Retrieve the last inserted userId
        retrieve_account_query = "SELECT * FROM Users WHERE userId = LAST_INSERT_ID()"
        cursor.execute(retrieve_account_query)
        account_details = cursor.fetchone()

        print("Your account details are:")
        print(account_details)
        print()
        return


# Helper function to handle signing in a user
def sign_in(cnx, cursor):
    print("Signing in...")
    while True:
        userId = input("Enter your userId: ")
        password = input("Enter your password: ")
        print()

        # Check if the userId and password match in the database
        cursor.execute(
            "SELECT userPassword, userRole FROM Users WHERE userId = %s", (userId,)
        )
        result = cursor.fetchone()

        # If the userId does not exist or password does not match
        if not result or result[0] != password:
            print("Invalid userId or password. Please try again.")
            print()
            continue

        # User is successfully authenticated, retrieve role
        userRole = result[1]

        print("Signed in successfully!")
        print()
        print(userId, userRole)
        return [userId, userRole]


# functionality for managing the user session, once the user signs in they are directed here
# they can logout from this function by entering LOGOUT
def user_session(cnx, cursor, userId, userRole):
    print("Welcome to your session. You can now access application features.")
    print()
    if "Admin" in userRole:
        while True:
            for query_type in general_query_options:
                print(query_type)
            for query_type in general_query_options_admin:
                print(query_type)
            print()
            user_input = input(
                "Enter the type of query you would like to run from the options above (1-9) or type 'LOGOUT' to end session: "
            )
            print()
            if user_input.upper() == "LOGOUT":
                print("Logging out...")
                break
            elif user_input == "1":
                create_option_1_query(cnx, cursor)
                continue
            elif user_input == "2":
                create_option_2_query(cnx, cursor)
                continue
            elif user_input == "3":
                create_option_3_query(cnx, cursor)
                continue
            elif user_input == "4":
                create_option_4_query(cnx, cursor, userId)
                continue
            elif user_input == "5":
                create_option_5_query(cnx, cursor, userId)
                continue
            elif user_input == "6":
                create_option_6_query(cnx, cursor, userId)
                continue
            elif user_input == "7":
                create_option_7_query(cnx, cursor)
                continue
            elif user_input == "8":
                create_option_8_query(cnx, cursor)
                continue
            elif user_input == "9":
                create_option_9_query(cnx, cursor)
                continue
            else:
                print(
                    "Invalid query type, please provide a valid query type between 1 and 9 or enter LOGOUT"
                )
                print()
                continue
    # for regular User permissions
    else:
        while True:
            for query_type in general_query_options:
                print(query_type)
            print()
            user_input = input(
                "Enter the type of query you would like to run from the options above (1-6) or type 'LOGOUT' to end session: "
            )
            print()
            if input.upper() == "LOGOUT":
                print("Logging out...")
                break
            elif user_input == "1":
                create_option_1_query(cnx, cursor)
                continue
            elif user_input == "2":
                create_option_2_query(cnx, cursor)
                continue
            elif user_input == "3":
                continue
            elif user_input == "4":
                create_option_4_query(cnx, cursor, userId)
                continue
            elif user_input == "5":
                create_option_5_query(cnx, cursor, userId)
                continue
            elif user_input == "6":
                create_option_6_query(cnx, cursor, userId)
                continue
            else:
                print(
                    "Invalid query type, please provide a valid query type between 1 and 6"
                )
                print()
                continue


def main():
    if cnx is None or cursor is None:
        print("Failed to connect to the database. Exiting.")
        # Close the cursor and connection
        cursor.close()
        cnx.close()
        return

    while True:
        choice = input(
            "Would you like to (1) create a new account or (2) sign in or (END) end the session? Enter 1 or 2 or END: "
        )
        print()

        if choice == "1":
            create_account(cnx, cursor)
        elif choice == "2":
            # user_details obtained is an array with the userId first and the userRole second
            user_details = sign_in(cnx, cursor)
            # start the session from here after signing
            user_session(cnx, cursor, user_details[0], user_details[1])
            break
        elif choice.upper() == "END":
            print("Ending session...")
            break
        else:
            print("Invalid choice. Please enter 1 or 2 or END.")
            print()

    # Close the cursor and connection
    cursor.close()
    cnx.close()


if __name__ == "__main__":
    main()

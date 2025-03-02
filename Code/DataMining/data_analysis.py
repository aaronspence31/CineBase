# Data Mining for Movies:
# Investigation: Find which attributes are the most impactful in determining the movie profitability, measured through worldwide revenue.
# Algorithm: Decision Tree Regressor
# Data Mining Technique: Predictive Modeling using Regression
## The data mining investigation was carried out by using a known set of data with known outcomes and using this set of data to train a model,
## knowing the preferred outcome. This was done using the Decision Tree Regressor algorithm from the sklearn.tree python library

import mysql.connector
import pandas as pd  # pip install pandas
import matplotlib.pyplot as plt  # pip install matplotlib
import seaborn as sns  # pip install seaborn
from sklearn.model_selection import train_test_split  # pip install scikit-learn
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import feature_importance_analysis


config = {
    "user": "db_user",
    "password": "your_password",
    "host": "localhost",
    "database": "cinebase_db",
    "raise_on_warnings": True,
}

# Connect to the database
print("Connecting to database...")

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

print("Connected to database")

# Query outlining all attributes that we believe would be most relevant to revenue
query = """
SELECT
	mk.keywordName AS keywords,
	mpc.companyName,
	mlm.originalLanguage AS language,
	mg.genreName AS genre,
	CASE
		WHEN cm.crewJob IN ('Director') THEN mp.participantName
		ELSE NULL
	END AS director,
	CASE
		WHEN cast.creditId IS NOT NULL THEN mp.participantName
		ELSE NULL
	END AS actor,
	IFNULL(mpm.budget, NULL) AS budget,
	ard.worldwideRevenue AS revenue
FROM
	MovieGenres mg
JOIN
	MovieLinks ml ON mg.imdbId = ml.imdbId
LEFT JOIN
	MovieKeywords mk ON ml.tmdbId = mk.tmdbId
LEFT JOIN
	MovieProductionCompanies mpc ON ml.imdbId = mpc.imdbId
LEFT JOIN
	MoviesLanguageMetadata mlm ON ml.imdbId = mlm.imdbId
LEFT JOIN
	MovieParticipants mp ON ml.tmdbId = mp.tmdbId
LEFT JOIN
	CrewMember cm ON mp.creditId = cm.creditId
LEFT JOIN
	CastMember cast ON mp.creditId = cast.creditId
LEFT JOIN
	MoviesProductionMetadata mpm ON ml.imdbId = mpm.imdbId
LEFT JOIN
	AdditionalRevenueData ard ON ml.imdbId = ard.imdbId
WHERE
	ard.worldwideRevenue IS NOT NULL
	AND mp.participantName IS NOT NULL
LIMIT 10000000;
"""

print("Executing query...")

cursor.execute(query)
data = cursor.fetchall()

print("Fetched data")

# Create DataFrame from data
columns = [
    "keywords",
    "companyName",
    "language",
    "genre",
    "director",
    "actor",
    "budget",
    "revenue",
]
df = pd.DataFrame(data, columns=columns)

# for missing values, fill with Unknown
df = df.fillna("Unknown")

le = LabelEncoder()
for col in df.columns[:-1]:  # excluding 'genre'
    df[col] = le.fit_transform(df[col])

features = df[
    ["keywords", "companyName", "language", "genre", "director", "actor", "budget"]
]
target = df["revenue"]

# split the data into an 80:20 ratio. 80% of the data collected will be used to train the model.
# The remaining 20% will be used to test the model and compare the results with the known outcomes
X_train, X_test, y_train, y_test = train_test_split(
    features, target, test_size=0.2, random_state=3
)

# classification algorithm - Decision Tree Regressor
regressor = DecisionTreeRegressor()

# train the model
regressor.fit(X_train, y_train)

# make predictions on testing set
predictions = regressor.predict(X_test)

# evaluate the model
# MAE -> absolute difference between actual and predicted values (measures absolute deviation)
# MSE -> squared differences between actual and predicted values. Larger errors given more weight
# R2  -> Coefficient of Determination. Measures the proportion of variance in the dependent var, which is predictable from independent var.
#     -> Ranges from 0->1, where 1 indicates perfect predictions.
mae = mean_absolute_error(y_test, predictions)
mse = mean_squared_error(y_test, predictions)
r2 = r2_score(y_test, predictions)

print(f"Mean Absolute Error: {mae: .2f}")
print(f"Mean Squared Error: {mse: .2f}")
print(f"R-squared: {r2: .2f}")

# convert revenue data to numeric type
df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce")

# Feature Importance Analysis
feature_names = features.columns.tolist()
feature_importance_df = feature_importance_analysis.analyze_feature_importance(
    regressor, feature_names
)

print("Feature Importance Analysis:")
print(feature_importance_df)

# convert predictions and y_test to numeric
predictions_numeric = pd.to_numeric(predictions, errors="coerce")
y_test_numeric = pd.to_numeric(y_test, errors="coerce")

################################################################################################

# Scatter Plot
# predicted revenue on x, actual revenue on y, residual is assessed by looking at line y=x

# plt.figure(figsize=(10, 6))
# plt.scatter(y_test_numeric, predictions_numeric, alpha=0.5)
# plt.plot([y_test_numeric.min(), y_test_numeric.max()], [y_test_numeric.min(), y_test_numeric.max()], 'k--', lw=2)
# plt.xlabel('Actual Revenue')
# plt.ylabel('Predicted Revenue')
# plt.title('Scatter Plot of Actual vs. Predicted Revenue')
# plt.show()

################################################################################################

# Residual Plot
# plotting (differences btwn actual and predicted values) against (actual values)

residuals = y_test_numeric - predictions_numeric
plt.figure(figsize=(10, 6))
plt.scatter(y_test_numeric, residuals, alpha=0.5)
plt.axhline(y=0, color="r", linestyle="--", linewidth=2)
plt.xlabel("Actual Revenue")
plt.ylabel("Residuals")
plt.title("Residual Plot")
plt.show()

################################################################################################

cursor.close()
cnx.close()

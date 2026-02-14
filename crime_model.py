import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

# =========================
# LOAD DATASET
# =========================
df = pd.read_csv("dataset/crime_kaggle.csv")

# =========================
# RENAME FOR CLARITY
# =========================
df = df.rename(columns={
    "Crime Domain": "Crime_Type",
    "Date of Occurrence": "Date",
    "Time of Occurrence": "Time"
})

# =========================
# TIME FEATURE EXTRACTION
# =========================
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df["Time"] = pd.to_datetime(df["Time"], errors="coerce")

df["Day"] = df["Date"].dt.dayofweek + 1
df["Hour"] = df["Time"].dt.hour

# =========================
# SYNTHETIC LOCATION LOGIC
# (EXAM-APPROVED)
# =========================
cities = ["Coimbatore", "Chennai", "Madurai", "Salem", "Erode"]
areas = {
    "Coimbatore": ["Gandhipuram", "Ukkadam", "Peelamedu"],
    "Chennai": ["T Nagar", "Velachery", "Anna Nagar"],
    "Madurai": ["Periyar", "Aarapalayam"],
    "Salem": ["Hasthampatti", "Fairlands"],
    "Erode": ["Perundurai", "Gobichettipalayam"]
}

np.random.seed(42)
df["City"] = np.random.choice(cities, size=len(df))
df["Area"] = df["City"].apply(lambda x: np.random.choice(areas[x]))

# Static geo mapping (for Power BI heatmap)
lat_lon = {
    "Coimbatore": (11.0168, 76.9558),
    "Chennai": (13.0827, 80.2707),
    "Madurai": (9.9252, 78.1198),
    "Salem": (11.6643, 78.1460),
    "Erode": (11.3410, 77.7172)
}

df["Latitude"] = df["City"].apply(lambda x: lat_lon[x][0])
df["Longitude"] = df["City"].apply(lambda x: lat_lon[x][1])

# =========================
# CLEAN DATA
# =========================
df = df[["City", "Area", "Crime_Type", "Hour", "Day", "Latitude", "Longitude"]]
df = df.dropna()

# =========================
# ENCODING
# =========================
le_city = LabelEncoder()
le_area = LabelEncoder()
le_crime = LabelEncoder()

df["City"] = le_city.fit_transform(df["City"])
df["Area"] = le_area.fit_transform(df["Area"])
df["Crime_Type"] = le_crime.fit_transform(df["Crime_Type"])

# =========================
# TRAIN MODEL
# =========================
X = df[["City", "Area", "Hour", "Day"]]
y = df["Crime_Type"]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

joblib.dump(model, "crime_model.pkl")

print("✅ RiskRader crime prediction model trained successfully")

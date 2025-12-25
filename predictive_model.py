# predictive_model.py
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
import joblib

# Generate synthetic training data
np.random.seed(42)
data = pd.DataFrame({
    'time': np.random.randint(0, 24, 500),
    'incidents': np.random.randint(0, 20, 500),
    'crowd': np.random.randint(1, 10, 500),
    'lighting': np.random.randint(1, 4, 500),
})

# Define simple risk levels
data['risk'] = (
    (data['incidents'] > 10).astype(int)
    + (data['lighting'] == 1).astype(int)
    + (data['crowd'] < 3).astype(int)
)

# Convert to categories: 0=Low, 1=Medium, 2=High
data['risk'] = pd.cut(data['risk'], bins=[-1,1,2,3], labels=[0,1,2])

# Train model
X = data[['time', 'incidents', 'crowd', 'lighting']]
y = data['risk']
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X, y)

# Save the model
joblib.dump(model, 'model.pkl')
print("✅ Model trained and saved as model.pkl")

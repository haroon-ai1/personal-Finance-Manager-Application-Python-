import pandas as pd
import numpy as np
import os
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout


KAGGLE_FILE = r"Personal_Finance_Dataset.csv"
MODEL_FILE = "finance_brain.keras"
LOOK_BACK = 30  # Days of history the AI needs to see

def train_network():
    if not os.path.exists(KAGGLE_FILE):
        print(f" Error: '{KAGGLE_FILE}' not found. Please upload it.")
        return

    print("Loading Kaggle Dataset...")
    df = pd.read_csv(KAGGLE_FILE)

    
    
    expense_df = df[df['Type'].astype(str).str.lower() == 'expense'].copy()
    
    
    expense_df['Date'] = pd.to_datetime(expense_df['Date'], dayfirst=False, format='mixed', errors='coerce')
    expense_df = expense_df.dropna(subset=['Date'])
    
    
    daily_data = expense_df.set_index('Date').resample('D')['Amount'].sum().fillna(0)
    
    print(f"✅ Data Processed. Found {len(daily_data)} days of history.")

    
    
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_data = scaler.fit_transform(daily_data.values.reshape(-1, 1))

    
    X, y = [], []
    for i in range(len(scaled_data) - LOOK_BACK):
        X.append(scaled_data[i : i + LOOK_BACK])
        y.append(scaled_data[i + LOOK_BACK])
    
    X, y = np.array(X), np.array(y)

    # 4. Build the LSTM Model (More Neurons as requested)
    print("🧠 Building Neural Network...")
    model = Sequential()
    
    # Layer 1: Heavy Processing (128 Neurons)
    model.add(LSTM(128, return_sequences=True, input_shape=(LOOK_BACK, 1)))
    model.add(Dropout(0.2)) # Prevents 'memorizing' data
    
    # Layer 2: Refinement (64 Neurons)
    model.add(LSTM(64, return_sequences=False))
    model.add(Dropout(0.2))
    
    # Output Layer
    model.add(Dense(1)) 

    model.compile(optimizer='adam', loss='mean_squared_error')

    
    print("Training Model... (This may take a minute)")
    model.fit(X, y, epochs=20, batch_size=32)

    
    model.save(MODEL_FILE)
    print(f"Success! Model saved as '{MODEL_FILE}'. You can now run the App.")

if __name__ == "__main__":
    train_network()
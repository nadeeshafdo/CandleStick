import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import root_mean_squared_error

import torch
import torch.nn as nn
import torch.optim as optim

# 1. Device Configuration
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# 2. Data Loading
ticker = "AAPL"
df = yf.download(ticker, start="2020-01-01")

# Visualize the initial data
plt.figure(figsize=(12, 8))
plt.plot(df['Close'])
plt.title(f"{ticker} Stock Price")
plt.show()

# --- 3. Preprocessing ---
# Flatten the data to ensure it's 1D, regardless of yfinance structure
close_prices = df['Close'].values.reshape(-1, 1)
scaler = StandardScaler()
scaled_data = scaler.fit_transform(close_prices).flatten() # Flatten to 1D

# --- 4. Preparing Data for LSTM ---
sequence_length = 30
data = []

for i in range(len(scaled_data) - sequence_length):
    # Append a slice of the 1D array
    data.append(scaled_data[i : i + sequence_length])

data = np.array(data) # Shape: (Samples, Seq)
data = np.expand_dims(data, axis=2) # Shape: (Samples, Seq, 1) - Now it is 3D

train_size = int(0.8 * len(data))

# Convert to Tensors (These will now be 3D)
X_train = torch.tensor(data[:train_size, :-1, :]).float().to(device)
Y_train = torch.tensor(data[:train_size, -1, :]).float().to(device)

X_test = torch.tensor(data[train_size:, :-1, :]).float().to(device)
Y_test = torch.tensor(data[train_size:, -1, :]).float().to(device)

# 5. Model Architecture
class PredictionModel(nn.Module):
    def __init__(self, input_dim, hidden_dim, num_layers, output_dim):
        super(PredictionModel, self).__init__()
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        
        self.lstm = nn.LSTM(input_dim, hidden_dim, num_layers, batch_first=True)
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        h0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(device)
        c0 = torch.zeros(self.num_layers, x.size(0), self.hidden_dim).to(device)
        
        out, _ = self.lstm(x, (h0.detach(), c0.detach()))
        out = self.fc(out[:, -1, :])
        return out

# 6. Training Setup
model = PredictionModel(input_dim=1, hidden_dim=32, num_layers=2, output_dim=1).to(device)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.01)

# 7. Training Loop
num_epochs = 200
for epoch in range(num_epochs):
    model.train()
    outputs = model(X_train)
    optimizer.zero_grad()
    
    loss = criterion(outputs, Y_train)
    loss.backward()
    optimizer.step()
    
    if (epoch + 1) % 25 == 0:
        print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {loss.item():.4f}")

# 8. Evaluation & Inverse Transformation
model.eval()
with torch.no_grad():
    train_predictions = model(X_train).cpu().numpy()
    test_predictions = model(X_test).cpu().numpy()

# Inverse transform to get actual prices
y_train_actual = scaler.inverse_transform(Y_train.cpu().numpy())
y_train_pred = scaler.inverse_transform(train_predictions)

y_test_actual = scaler.inverse_transform(Y_test.cpu().numpy())
y_test_pred = scaler.inverse_transform(test_predictions)

# Metrics
train_rmse = root_mean_squared_error(y_train_actual, y_train_pred)
test_rmse = root_mean_squared_error(y_test_actual, y_test_pred)

print(f"Train RMSE: {train_rmse:.2f}")
print(f"Test RMSE: {test_rmse:.2f}")

# 9. Visualization of Results
fig = plt.figure(figsize=(12, 10))
gs = fig.add_gridspec(4, 1)

# Price Plot
ax1 = fig.add_subplot(gs[0:3, 0])
# Align dates for the test set
test_dates = df.index[-len(y_test_actual):]
ax1.plot(test_dates, y_test_actual, color='blue', label="Actual Price")
ax1.plot(test_dates, y_test_pred, color='green', label="Predicted Price")
ax1.set_title(f"{ticker} Stock Price Prediction")
ax1.set_xlabel("Date")
ax1.set_ylabel("Price")
ax1.legend()

# Error Plot
ax2 = fig.add_subplot(gs[3, 0])
ax2.axhline(test_rmse, color='blue', linestyle='--', label="RMSE")
errors = np.abs(y_test_actual - y_test_pred)
ax2.plot(test_dates, errors, color='red', label="Prediction Error")
ax2.set_title("Prediction Error")
ax2.set_xlabel("Date")
ax2.set_ylabel("Error")
ax2.legend()

plt.tight_layout()
plt.show()

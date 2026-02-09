import csv
import os
import random
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from abc import ABC


from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import load_model


MODEL_FILE = "finance_brain.keras"
LOOK_BACK = 30


THEME = {'bg_main': '#1A1A2E', 'bg_card': '#16213E', 'text': '#EAEAEA', 'accent_blue': '#53D8FB', 'accent_pink': '#FC4EA3'}

def apply_plot_style():
    plt.style.use('dark_background')
    plt.rcParams.update({'figure.facecolor': THEME['bg_main'], 'axes.facecolor': THEME['bg_card'], 'savefig.facecolor': THEME['bg_main'], 'axes.grid': True, 'grid.alpha': 0.2, 'text.color': THEME['text']})

# DATA HELPERS (User Management) 

def load_all_clients():
    clients = []
    if not os.path.exists("users.txt"): return clients
    try:
        with open("users.txt", "r") as f:
            reader = csv.reader(f); next(reader, None)
            for row in reader:
                if len(row) >= 7:
                    uname, pw, amt, bud, spent, loan, rec_str = row
                    recurring = []
                    if rec_str:
                        for item in rec_str.split(";"):
                            p = item.split("|")
                            if len(p) == 4: recurring.append((float(p[0]), p[1], int(p[2]), datetime.strptime(p[3], '%Y-%m-%d %H:%M:%S')))
                    c = StandardAccount(uname, pw, float(amt))
                    c.set_budget(float(bud)); c.total_spent = float(spent); c.loans = float(loan); c.recurring = recurring
                    clients.append(c)
    except: pass
    return clients

def save_all_clients(clients):
    try:
        temp = "users.txt.tmp"
        with open(temp, "w", newline='') as f:
            w = csv.writer(f); w.writerow(["username", "password", "amount", "budget", "total_spent", "loans", "recurring"])
            for c in clients:
                rec_str = ";".join([f"{i[0]}|{i[1]}|{i[2]}|{i[3].strftime('%Y-%m-%d %H:%M:%S')}" for i in c.recurring])
                w.writerow([c.uname, c.password, c.amount, c.budget, c.total_spent, c.loans, rec_str])
        os.replace(temp, "users.txt")
    except: pass

def create_client(clients, u, p, a):
    if any(c.uname == u.lower() for c in clients): return " User exists."
    clients.append(StandardAccount(u, p, a)); save_all_clients(clients); return " Created!"

def validate(clients, n, p):
    for i, c in enumerate(clients):
        if c.uname == n.lower() and c.validate_pass(p): return i
    return None

def find_client_by_username(clients, n):
    for c in clients:
        if c.uname == n.lower(): return c
    return None

def generate_dummy_data_logic(username):
    # Generates 6 months of data for testing
    data = []
    curr = datetime.now() - timedelta(days=180)
    for _ in range(180):
        if random.random() > 0.3:
            data.append([username, curr.strftime("%Y-%m-%d 12:00:00"), random.randint(500, 5000), "Expense", "Test"])
        curr += timedelta(days=1)
    
    df = pd.DataFrame(data, columns=["username", "timestamp", "amount", "type", "category"])
    if not os.path.exists("transactions.csv"):
        df.to_csv("transactions.csv", index=False)
    else:
        df.to_csv("transactions.csv", mode='a', header=False, index=False)
    return " Demo Data Generated!"

def export_user_data(u): return "Not Implemented"
def generate_report(u): return "Not Implemented"

class Client(ABC):
    def __init__(self, u, p, a): self.uname=u.lower(); self.password=str(p); self.amount=a; self.total_spent=0; self.budget=0; self.loans=0; self.recurring=[]
    def validate_pass(self, p): return self.password == str(p)
    def set_budget(self, b): self.budget = b; return "Set."
    def add_income(self, a): self.amount += a; self.log(a, "Income", "General"); return "Added."
    def withdraw(self, a, c):
        if a > self.amount: return " Funds low."
        self.amount -= a; self.total_spent += a; self.log(a, "Expense", c)
        return " Budget!" if self.budget > 0 and self.total_spent > self.budget else " Spent."
    def transfer(self, rx, a):
        if self.amount < a: return " Funds low."
        self.amount -= a; rx.amount += a; self.log(a, "Transfer Out", rx.uname); rx.log(a, "Transfer In", self.uname)
        return " Sent."
    def request_loan(self, a): self.amount+=a; self.loans+=a; self.log(a,"Loan Received","Bank"); return " Approved."
    def repay_loan(self, a): self.amount-=a; self.loans-=a; self.log(a,"Loan Repayment","Bank"); return " Paid."
    def process_recurring(self): pass 
    def log(self, a, t, c):
        with open("transactions.csv", "a", newline='') as f: csv.writer(f).writerow([self.uname, datetime.now(), a, t, c])
class StandardAccount(Client): pass
class ChildAccount(Client): pass



def get_user_sequence(username):
    """
    1. Loads User Data.
    2. Scales it to 0-1 (matching the Master Brain's language).
    3. Returns the last 30 days as a sequence.
    """
    try:
        if not os.path.exists("transactions.csv"): return None, None, None
        df = pd.read_csv("transactions.csv")
        df_user = df[df['username'] == username.lower()].copy()
        df_user = df_user[df_user['type'].isin(['Expense', 'Recurring Expense'])]
        
        # Robust Date Parse
        df_user['timestamp'] = pd.to_datetime(df_user['timestamp'], dayfirst=True, format='mixed', errors='coerce')
        df_user = df_user.dropna(subset=['timestamp'])
        
        daily = df_user.set_index('timestamp').resample('D')['amount'].sum().fillna(0)
        
        if len(daily) < LOOK_BACK: return None, None, None # Needs 30 days
        
        # Fit Scaler on USER data (Adapts the brain to this user's wealth)
        scaler = MinMaxScaler(feature_range=(0, 1))
        scaler.fit(daily.values.reshape(-1, 1))
        
        last_30 = daily.values[-LOOK_BACK:]
        scaled_seq = scaler.transform(last_30.reshape(-1, 1))
        
        return scaled_seq.reshape(1, LOOK_BACK, 1), scaler, daily
    except: return None, None, None

def predict_next_month_expense(username):
    if not os.path.exists(MODEL_FILE): return " Model not trained! Run train_model.py first."
    
    model = load_model(MODEL_FILE)
    X_user, scaler, _ = get_user_sequence(username)
    
    if X_user is None: return " Not enough data (Need 30 days)."
    
    # Predict 30 days
    curr = X_user
    total = 0
    for _ in range(30):
        p = model.predict(curr, verbose=0)
        val = scaler.inverse_transform(p)[0][0]
        total += val
        curr = np.append(curr[0][1:], p).reshape(1, LOOK_BACK, 1)
        
    return f"AI Forecast (30 Days): PKR {max(0, total):,.2f}"

def predict_future_expense_data(username):
    if not os.path.exists(MODEL_FILE): return {"message": "Model Missing"}
    
    model = load_model(MODEL_FILE)
    X_user, scaler, daily = get_user_sequence(username)
    
    if X_user is None: return {"message": "Need 30 days data"}
    
    apply_plot_style(); plt.switch_backend('Agg')
    
    # Predict 15 days for graph
    preds = []
    curr = X_user
    for _ in range(15):
        p = model.predict(curr, verbose=0)
        preds.append(p[0, 0])
        curr = np.append(curr[0][1:], p).reshape(1, LOOK_BACK, 1)
        
    money_preds = scaler.inverse_transform(np.array(preds).reshape(-1, 1))
    
    fig, ax = plt.subplots(figsize=(10, 5))
    
    # History
    hist_dates = daily.index[-30:]
    hist_vals = daily.values[-30:]
    ax.plot(hist_dates, hist_vals, color=THEME['accent_blue'], marker='o', label="Your History")
    
    # Forecast
    last = daily.index[-1]
    fut_dates = [last + timedelta(days=i+1) for i in range(15)]
    ax.plot(fut_dates, money_preds, color=THEME['accent_pink'], linestyle='--', marker='x', label="AI Forecast")
    
    ax.legend()
    path = f"{username}_prediction.png"
    plt.savefig(path); plt.close()
    return {"message": "Success", "plot_path": path}

def plot_charts(username):
    apply_plot_style(); plt.switch_backend('Agg')
    try:
        df = pd.read_csv("transactions.csv"); df = df[df['username']==username.lower()]
        df['timestamp'] = pd.to_datetime(df['timestamp'], dayfirst=True, format='mixed', errors='coerce')
        df = df.dropna(subset=['timestamp'])
        
        df_exp = df[df['type']=='Expense'].copy(); df_exp['amount'] *= -1
        m = df_exp.resample("M", on="timestamp")['amount'].sum()
        
        fig, ax = plt.subplots(figsize=(8,4))
        ax.plot(m.index, m.values, color=THEME['accent_blue'], marker='o')
        plt.tight_layout(); plt.savefig(f"{username}_monthly_trend.png"); plt.close()
        
        pie = df[df['type']=='Expense'].groupby('category')['amount'].sum()
        if not pie.empty:
            fig, ax = plt.subplots(figsize=(6,6))
            ax.pie(pie, autopct='%1.1f%%', colors=[THEME['accent_pink'], THEME['accent_blue'], THEME['accent_purple']])
            plt.savefig(f"{username}_expense_pie.png"); plt.close()
    except: pass

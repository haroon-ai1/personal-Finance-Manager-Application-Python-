import customtkinter as ctk
from tkinter import messagebox
import csv
import os
import threading
from PIL import Image, ImageTk
import pandas as pd
import matplotlib.pyplot as plt

# Import backend logic
from logic import (
    create_client, validate, generate_report, plot_charts, 
    predict_future_expense_data, predict_next_month_expense, export_user_data,
    load_all_clients, save_all_clients, find_client_by_username, Client, ChildAccount,
    generate_dummy_data_logic # Import the demo data generator
)

# --- Theme Colors ---
PRIMARY_DARK = "#1A1A2E"
SECONDARY_DARK = "#16213E"
TERTIARY_DARK = "#0F3460"
ACCENT_PURPLE = "#8A4EFC"
ACCENT_BLUE = "#53D8FB"
ACCENT_GREEN = "#76E2B3"
ACCENT_RED = "#F95A7E"
ACCENT_PINK = "#FC4EA3"
TEXT_LIGHT = "#EAEAEA"
ENTRY_FIELD = "#2A2F4F"

ctk.set_appearance_mode("Dark")

app = ctk.CTk()
app.geometry("1200x800")
app.title("X-Analytics - Master Brain Edition")
app.configure(fg_color=PRIMARY_DARK)

# Global State
clients = []
current_user = None
prediction_img_label = None 
monthly_img_label = None
pie_img_label = None

# --- Helpers ---
def format_currency(amount):
    try:
        return "PKR {:,.2f}".format(float(amount))
    except:
        return "PKR 0.00"

def ensure_transaction_file():
    if not os.path.exists("transactions.csv"):
        with open("transactions.csv", "w", newline='') as f:
            csv.writer(f).writerow(["username", "timestamp", "amount", "type", "category"])

def load_initial_users():
    global clients
    clients = load_all_clients()

# --- Main Layout ---
main_content = ctk.CTkFrame(app, fg_color=PRIMARY_DARK, corner_radius=0)
main_content.pack(side="right", expand=True, fill="both")
content_frames = {}

def switch_view(name):
    global current_user
    if not current_user and name not in ["Login", "Register"]:
        messagebox.showwarning("Auth", "Please log in first.")
        return

    for frame in content_frames.values(): frame.pack_forget()
    
    if name == "Login": 
        auth_frame.pack(fill="both", expand=True)
        login_sub_frame.place(relx=0.5, rely=0.5, anchor="center")
        register_sub_frame.place_forget()
    elif name == "Register":
        auth_frame.pack(fill="both", expand=True)
        register_sub_frame.place(relx=0.5, rely=0.5, anchor="center")
        login_sub_frame.place_forget()
    elif name in content_frames:
        content_frames[name].pack(fill="both", expand=True, padx=20, pady=20)
        func_name = f"update_{name.lower().replace(' ', '_')}_view"
        if hasattr(app, func_name): 
            getattr(app, func_name)()

# --- Sidebar ---
sidebar = ctk.CTkFrame(app, width=220, fg_color=SECONDARY_DARK, corner_radius=0)

def create_sidebar():
    for w in sidebar.winfo_children(): w.destroy()
    ctk.CTkLabel(sidebar, text="X-Analytics", font=("Arial", 22, "bold"), text_color=ACCENT_PURPLE).pack(pady=30)
    
    buttons = ["Dashboard", "Income", "Expense", "Transfer", "Loans", "Budget", "Graphs", "AI Overview", "Export Data"]
    icons = ["🏠", "➕", "➖", "🔁", "💰", "🎯", "📊", "🤖", "💾"]
    
    for btn, icon in zip(buttons, icons):
        ctk.CTkButton(sidebar, text=f"{icon}  {btn}", width=180, height=40, fg_color="transparent", 
                      hover_color=TERTIARY_DARK, anchor="w", font=("Arial", 14),
                      command=lambda b=btn: switch_view(b)).pack(pady=5)
    
    ctk.CTkButton(sidebar, text="🚪 Logout", width=180, height=40, fg_color="transparent", 
                  text_color=ACCENT_RED, hover_color=TERTIARY_DARK, anchor="w", font=("Arial", 14, "bold"),
                  command=handle_logout).pack(side="bottom", pady=20)

def handle_logout():
    global current_user
    if current_user: save_all_clients(clients)
    current_user = None
    sidebar.pack_forget()
    switch_view("Login")

# --- Authentication ---
auth_frame = ctk.CTkFrame(main_content, fg_color=PRIMARY_DARK)
content_frames["Login"] = auth_frame
content_frames["Register"] = auth_frame

login_sub_frame = ctk.CTkFrame(auth_frame, fg_color=SECONDARY_DARK, corner_radius=15)
ctk.CTkLabel(login_sub_frame, text="Welcome Back", font=("Arial", 28, "bold")).pack(pady=20)
l_user = ctk.CTkEntry(login_sub_frame, placeholder_text="Username", width=250, height=40); l_user.pack(pady=10)
l_pass = ctk.CTkEntry(login_sub_frame, placeholder_text="Password", show="*", width=250, height=40); l_pass.pack(pady=10)

def login_cmd():
    idx = validate(clients, l_user.get(), l_pass.get())
    if idx is not None:
        global current_user
        current_user = clients[idx]
        current_user.process_recurring()
        l_user.delete(0, 'end'); l_pass.delete(0, 'end')
        sidebar.pack(side="left", fill="y"); create_sidebar()
        switch_view("Dashboard")
    else: messagebox.showerror("Error", "Invalid Credentials")
ctk.CTkButton(login_sub_frame, text="Login", command=login_cmd, width=250, height=40, fg_color=ACCENT_PURPLE).pack(pady=20)
ctk.CTkButton(login_sub_frame, text="Register New Account", fg_color="transparent", command=lambda: switch_view("Register")).pack()

register_sub_frame = ctk.CTkFrame(auth_frame, fg_color=SECONDARY_DARK, corner_radius=15)
ctk.CTkLabel(register_sub_frame, text="Create Account", font=("Arial", 28, "bold")).pack(pady=20)
r_user = ctk.CTkEntry(register_sub_frame, placeholder_text="Username", width=250, height=40); r_user.pack(pady=10)
r_pass = ctk.CTkEntry(register_sub_frame, placeholder_text="Password", show="*", width=250, height=40); r_pass.pack(pady=10)
r_amt = ctk.CTkEntry(register_sub_frame, placeholder_text="Initial Deposit (PKR)", width=250, height=40); r_amt.pack(pady=10)

def reg_cmd():
    try: amt = float(r_amt.get())
    except: return messagebox.showerror("Error", "Invalid Amount")
    res = create_client(clients, r_user.get(), r_pass.get(), amt)
    if "✅" in res: 
        r_user.delete(0, 'end'); r_pass.delete(0, 'end'); r_amt.delete(0, 'end')
        switch_view("Login")
        messagebox.showinfo("Success", res)
    else: messagebox.showerror("Error", res)
ctk.CTkButton(register_sub_frame, text="Sign Up", command=reg_cmd, width=250, height=40, fg_color=ACCENT_GREEN).pack(pady=20)
ctk.CTkButton(register_sub_frame, text="Back to Login", fg_color="transparent", command=lambda: switch_view("Login")).pack()


# --- VIEW 1: DASHBOARD ---
dashboard_frame = ctk.CTkFrame(main_content, fg_color=PRIMARY_DARK)
content_frames["Dashboard"] = dashboard_frame

def update_dashboard_view():
    for w in dashboard_frame.winfo_children(): w.destroy()
    ctk.CTkLabel(dashboard_frame, text=f"Hello, {current_user.uname.title()}!", font=("Arial", 32, "bold"), text_color="white").pack(anchor="w", pady=(10,5))
    
    cards_frame = ctk.CTkFrame(dashboard_frame, fg_color="transparent")
    cards_frame.pack(fill="x", pady=20)
    
    bal_card = ctk.CTkFrame(cards_frame, fg_color=SECONDARY_DARK, corner_radius=15)
    bal_card.pack(side="left", fill="both", expand=True, padx=(0,10))
    ctk.CTkLabel(bal_card, text="Current Balance", font=("Arial", 14), text_color="gray").pack(pady=(15,5))
    ctk.CTkLabel(bal_card, text=format_currency(current_user.amount), font=("Arial", 28, "bold"), text_color=ACCENT_GREEN).pack(pady=(0,15))
    
    bud_card = ctk.CTkFrame(cards_frame, fg_color=SECONDARY_DARK, corner_radius=15)
    bud_card.pack(side="left", fill="both", expand=True, padx=(10,0))
    ctk.CTkLabel(bud_card, text="Monthly Budget", font=("Arial", 14), text_color="gray").pack(pady=(15,5))
    spent = current_user.total_spent; budget = current_user.budget
    prog = min(spent/budget, 1.0) if budget > 0 else 0
    rem = budget - spent if budget > 0 else 0
    rem_text = format_currency(rem) if budget > 0 else "No Budget"
    
    ctk.CTkLabel(bud_card, text=f"{rem_text} Remaining", font=("Arial", 20, "bold"), text_color=ACCENT_BLUE).pack(pady=(0,5))
    pb = ctk.CTkProgressBar(bud_card, progress_color=ACCENT_BLUE); pb.pack(pady=10, padx=20, fill="x"); pb.set(prog)
    ctk.CTkLabel(bud_card, text=f"{int(prog*100)}% Used", font=("Arial", 12)).pack(pady=(0,10))

    ctk.CTkLabel(dashboard_frame, text="Recent Transactions", font=("Arial", 20, "bold")).pack(anchor="w", pady=(20,10))
    trans_frame = ctk.CTkFrame(dashboard_frame, fg_color=SECONDARY_DARK)
    trans_frame.pack(fill="both", expand=True)
    try:
        df = pd.read_csv("transactions.csv")
        user_df = df[df['username'] == current_user.uname.lower()].tail(6).iloc[::-1]
        if not user_df.empty:
            for _, row in user_df.iterrows():
                row_f = ctk.CTkFrame(trans_frame, fg_color="transparent", height=40)
                row_f.pack(fill="x", padx=10, pady=5)
                clr = ACCENT_GREEN if row['type'] in ["Income", "Loan Received"] else ACCENT_RED
                ctk.CTkLabel(row_f, text=str(row['timestamp'])[:10], width=100, anchor="w").pack(side="left")
                ctk.CTkLabel(row_f, text=row['category'], width=150, anchor="w", font=("Arial", 14, "bold")).pack(side="left")
                ctk.CTkLabel(row_f, text=format_currency(row['amount']), width=120, anchor="e", text_color=clr, font=("Arial", 14, "bold")).pack(side="right")
        else: ctk.CTkLabel(trans_frame, text="No recent transactions.").pack(pady=20)
    except: ctk.CTkLabel(trans_frame, text="Could not load data.").pack(pady=20)
app.update_dashboard_view = update_dashboard_view


# --- VIEW 2: INCOME ---
income_frame = ctk.CTkFrame(main_content, fg_color=PRIMARY_DARK)
content_frames["Income"] = income_frame
def update_income_view():
    for w in income_frame.winfo_children(): w.destroy()
    ctk.CTkLabel(income_frame, text="Add Income", font=("Arial", 28, "bold"), text_color=ACCENT_GREEN).pack(anchor="w", pady=20)
    ctk.CTkLabel(income_frame, text="Amount:", font=("Arial", 14)).pack(anchor="w", pady=5)
    e_amt = ctk.CTkEntry(income_frame, width=300, height=40, placeholder_text="0.00"); e_amt.pack(anchor="w", pady=5)
    def submit():
        try:
            msg = current_user.add_income(float(e_amt.get()))
            if "✅" in msg: save_all_clients(clients); e_amt.delete(0, 'end'); messagebox.showinfo("Success", msg)
            else: messagebox.showerror("Error", msg)
        except: messagebox.showerror("Error", "Invalid Amount")
    ctk.CTkButton(income_frame, text="Add Income", command=submit, width=300, height=45, fg_color=ACCENT_GREEN, font=("Arial", 15, "bold")).pack(anchor="w", pady=30)
app.update_income_view = update_income_view


# --- VIEW 3: EXPENSE ---
expense_frame = ctk.CTkFrame(main_content, fg_color=PRIMARY_DARK)
content_frames["Expense"] = expense_frame

def update_expense_view():
    for w in expense_frame.winfo_children(): w.destroy()
    
    ctk.CTkLabel(expense_frame, text="Record Expense", font=("Arial", 28, "bold"), text_color=ACCENT_RED).pack(anchor="w", pady=(20, 10))
    
    info_panel = ctk.CTkFrame(expense_frame, fg_color=SECONDARY_DARK, corner_radius=10)
    info_panel.pack(fill="x", pady=(0, 20), ipady=10)
    
    ctk.CTkLabel(info_panel, text="Available Balance:", font=("Arial", 14, "bold"), text_color="gray").pack(side="left", padx=(20, 5))
    ctk.CTkLabel(info_panel, text=format_currency(current_user.amount), font=("Arial", 16, "bold"), text_color=ACCENT_GREEN).pack(side="left")
    
    rem_bud = current_user.budget - current_user.total_spent
    rem_text = format_currency(rem_bud) if current_user.budget > 0 else "Unlimited"
    color_bud = ACCENT_BLUE if rem_bud > 0 or current_user.budget == 0 else ACCENT_RED
    
    ctk.CTkLabel(info_panel, text="Remaining Budget:", font=("Arial", 14, "bold"), text_color="gray").pack(side="left", padx=(40, 5))
    ctk.CTkLabel(info_panel, text=rem_text, font=("Arial", 16, "bold"), text_color=color_bud).pack(side="left")

    ctk.CTkLabel(expense_frame, text="Amount:", font=("Arial", 14)).pack(anchor="w", pady=5)
    e_amt = ctk.CTkEntry(expense_frame, width=300, height=40, placeholder_text="0.00")
    e_amt.pack(anchor="w", pady=5)
    
    ctk.CTkLabel(expense_frame, text="Category:", font=("Arial", 14)).pack(anchor="w", pady=5)
    e_cat = ctk.CTkEntry(expense_frame, width=300, height=40, placeholder_text="e.g. Food")
    e_cat.pack(anchor="w", pady=5)
    
    def submit():
        try:
            amt = float(e_amt.get()); cat = e_cat.get()
            if current_user.budget > 0:
                future_spent = current_user.total_spent + amt
                if future_spent > current_user.budget:
                    if not messagebox.askyesno("Budget Warning", f"⚠️ Proceeding will exceed your budget!\n\nCurrent: {format_currency(current_user.budget)}\nFuture Spend: {format_currency(future_spent)}\n\nContinue?"):
                        return
            msg = current_user.withdraw(amt, cat)
            if "✅" in msg or "⚠️" in msg:
                save_all_clients(clients); e_amt.delete(0, 'end'); e_cat.delete(0, 'end'); update_expense_view(); messagebox.showinfo("Success", msg)
            else: messagebox.showerror("Error", msg)
        except ValueError: messagebox.showerror("Error", "Invalid Amount")
    ctk.CTkButton(expense_frame, text="Record Expense", command=submit, width=300, height=45, fg_color=ACCENT_RED, font=("Arial", 15, "bold")).pack(anchor="w", pady=30)
app.update_expense_view = update_expense_view


# --- VIEW 4: TRANSFER ---
transfer_frame = ctk.CTkFrame(main_content, fg_color=PRIMARY_DARK)
content_frames["Transfer"] = transfer_frame
def update_transfer_view():
    for w in transfer_frame.winfo_children(): w.destroy()
    ctk.CTkLabel(transfer_frame, text="Transfer Funds", font=("Arial", 28, "bold"), text_color=ACCENT_PURPLE).pack(anchor="w", pady=20)
    ctk.CTkLabel(transfer_frame, text="Amount:", font=("Arial", 14)).pack(anchor="w", pady=5)
    e_amt = ctk.CTkEntry(transfer_frame, width=300, height=40, placeholder_text="0.00"); e_amt.pack(anchor="w", pady=5)
    ctk.CTkLabel(transfer_frame, text="Recipient Username:", font=("Arial", 14)).pack(anchor="w", pady=5)
    e_rec = ctk.CTkEntry(transfer_frame, width=300, height=40, placeholder_text="Username"); e_rec.pack(anchor="w", pady=5)
    def submit():
        try:
            rx = find_client_by_username(clients, e_rec.get())
            if rx: 
                msg = current_user.transfer(rx, float(e_amt.get()))
                if "✅" in msg: save_all_clients(clients); e_amt.delete(0, 'end'); e_rec.delete(0, 'end'); messagebox.showinfo("Success", msg)
                else: messagebox.showerror("Error", msg)
            else: messagebox.showerror("Error", "User not found.")
        except: messagebox.showerror("Error", "Invalid Amount")
    ctk.CTkButton(transfer_frame, text="Send Money", command=submit, width=300, height=45, fg_color=ACCENT_PURPLE, font=("Arial", 15, "bold")).pack(anchor="w", pady=30)
app.update_transfer_view = update_transfer_view


# --- VIEW 5: LOANS ---
loans_frame = ctk.CTkFrame(main_content, fg_color=PRIMARY_DARK)
content_frames["Loans"] = loans_frame
def update_loans_view():
    for w in loans_frame.winfo_children(): w.destroy()
    ctk.CTkLabel(loans_frame, text="Loans", font=("Arial", 28, "bold"), text_color=ACCENT_BLUE).pack(anchor="w", pady=20)
    ctk.CTkLabel(loans_frame, text=f"Outstanding: {format_currency(current_user.loans)}", font=("Arial", 20, "bold"), text_color=ACCENT_RED).pack(anchor="w", pady=10)
    grid = ctk.CTkFrame(loans_frame, fg_color="transparent"); grid.pack(fill="x", pady=20)
    f_req = ctk.CTkFrame(grid, fg_color=SECONDARY_DARK); f_req.pack(side="left", fill="both", expand=True, padx=(0,10))
    ctk.CTkLabel(f_req, text="Request", font=("Arial", 18, "bold")).pack(pady=10)
    e_req = ctk.CTkEntry(f_req, placeholder_text="Amount"); e_req.pack(pady=10)
    def do_req():
        try: 
            msg = current_user.request_loan(float(e_req.get())); 
            if "✅" in msg: save_all_clients(clients); update_loans_view(); messagebox.showinfo("Success", msg)
            else: messagebox.showerror("Error", msg)
        except: pass
    ctk.CTkButton(f_req, text="Get Loan", command=do_req, fg_color=ACCENT_BLUE).pack(pady=20)
    f_pay = ctk.CTkFrame(grid, fg_color=SECONDARY_DARK); f_pay.pack(side="left", fill="both", expand=True, padx=(10,0))
    ctk.CTkLabel(f_pay, text="Repay", font=("Arial", 18, "bold")).pack(pady=10)
    e_pay = ctk.CTkEntry(f_pay, placeholder_text="Amount"); e_pay.pack(pady=10)
    def do_pay():
        try:
            msg = current_user.repay_loan(float(e_pay.get()))
            if "✅" in msg: save_all_clients(clients); update_loans_view(); messagebox.showinfo("Success", msg)
            else: messagebox.showerror("Error", msg)
        except: pass
    ctk.CTkButton(f_pay, text="Pay Back", command=do_pay, fg_color=ACCENT_GREEN).pack(pady=20)
app.update_loans_view = update_loans_view


# --- VIEW 6: BUDGET ---
budget_frame = ctk.CTkFrame(main_content, fg_color=PRIMARY_DARK)
content_frames["Budget"] = budget_frame
def update_budget_view():
    for w in budget_frame.winfo_children(): w.destroy()
    ctk.CTkLabel(budget_frame, text="Manage Budget", font=("Arial", 28, "bold"), text_color=ACCENT_PINK).pack(anchor="w", pady=20)
    ctk.CTkLabel(budget_frame, text=f"Current Limit: {format_currency(current_user.budget)}", font=("Arial", 18)).pack(anchor="w")
    ctk.CTkLabel(budget_frame, text="Set New Limit:", font=("Arial", 14)).pack(anchor="w", pady=(20,5))
    e_bud = ctk.CTkEntry(budget_frame, width=300, placeholder_text="Amount"); e_bud.pack(anchor="w")
    def set_bud():
        try:
            msg = current_user.set_budget(float(e_bud.get()))
            save_all_clients(clients); update_budget_view(); messagebox.showinfo("Success", msg)
        except: messagebox.showerror("Error", "Invalid Amount")
    ctk.CTkButton(budget_frame, text="Set Budget", command=set_bud, fg_color=ACCENT_PINK).pack(anchor="w", pady=20)
    def reset_bud():
        if messagebox.askyesno("Confirm Reset", "Remove budget limit?"):
            current_user.set_budget(0); save_all_clients(clients); update_budget_view(); messagebox.showinfo("Reset", "Budget removed.")
    ctk.CTkButton(budget_frame, text="Reset / Remove Budget", command=reset_bud, fg_color=ACCENT_RED, hover_color="#C0392B").pack(anchor="w", pady=10)
app.update_budget_view = update_budget_view


# --- VIEW 7: GRAPHS ---
graphs_frame = ctk.CTkFrame(main_content, fg_color=PRIMARY_DARK)
content_frames["Graphs"] = graphs_frame
def update_graphs_view():
    global monthly_img_label, pie_img_label
    for w in graphs_frame.winfo_children(): w.destroy()
    ctk.CTkLabel(graphs_frame, text="Analytics", font=("Arial", 28, "bold")).pack(anchor="w", pady=20)
    plot_charts(current_user.uname)
    scroll = ctk.CTkScrollableFrame(graphs_frame, fg_color="transparent"); scroll.pack(fill="both", expand=True)
    m_path = f"{current_user.uname.lower()}_monthly_trend.png"
    if os.path.exists(m_path):
        ctk.CTkLabel(scroll, text="Net Flow", font=("Arial", 16, "bold")).pack(pady=10)
        try:
            img = Image.open(m_path); r = min(700/img.width, 1.0); img = img.resize((int(img.width*r), int(img.height*r)), Image.Resampling.BICUBIC)
            i = ImageTk.PhotoImage(img); monthly_img_label = ctk.CTkLabel(scroll, text="", image=i); monthly_img_label.image=i; monthly_img_label.pack(pady=10)
        except: pass
    p_path = f"{current_user.uname.lower()}_expense_pie.png"
    if os.path.exists(p_path):
        ctk.CTkLabel(scroll, text="Breakdown", font=("Arial", 16, "bold")).pack(pady=20)
        try:
            img = Image.open(p_path); r = min(500/img.width, 1.0); img = img.resize((int(img.width*r), int(img.height*r)), Image.Resampling.BICUBIC)
            i = ImageTk.PhotoImage(img); pie_img_label = ctk.CTkLabel(scroll, text="", image=i); pie_img_label.image=i; pie_img_label.pack(pady=10)
        except: pass
app.update_graphs_view = update_graphs_view


# --- VIEW 8: AI OVERVIEW ---
ai_frame = ctk.CTkFrame(main_content, fg_color=PRIMARY_DARK)
content_frames["AI Overview"] = ai_frame
def update_ai_overview_view():
    global prediction_img_label
    for w in ai_frame.winfo_children(): w.destroy()
    ctk.CTkLabel(ai_frame, text="🤖 AI Forecast (Master Brain)", font=("Arial", 28, "bold"), text_color=ACCENT_BLUE).pack(anchor="w", pady=20)
    
    content = ctk.CTkFrame(ai_frame, fg_color="transparent"); content.pack(fill="both", expand=True)
    load = ctk.CTkFrame(content, fg_color="transparent"); load.pack(pady=50)
    spin = ctk.CTkProgressBar(load, mode="indeterminate", progress_color=ACCENT_PINK); spin.pack(pady=15); spin.start()
    ctk.CTkLabel(load, text="AI is analyzing...", text_color="gray").pack()

    def run_ai():
        try:
            txt = predict_next_month_expense(current_user.uname)
            grp = predict_future_expense_data(current_user.uname)
            app.after(0, lambda: show(txt, grp))
        except Exception as e: app.after(0, lambda: err(str(e)))

    def gen_data_cmd():
        res = generate_dummy_data_logic(current_user.uname)
        messagebox.showinfo("Result", res)
        # Refresh current view
        update_ai_overview_view()

    def show(txt, grp):
        spin.stop(); load.destroy()
        
        # Check for Not Enough Data
        if "Need 30 days" in txt or "Need 30 days" in grp.get("message", ""):
             ctk.CTkLabel(content, text="⚠️ Not Enough Data", font=("Arial", 22, "bold"), text_color=ACCENT_RED).pack(pady=10)
             ctk.CTkLabel(content, text="The AI Brain needs at least 30 days of history to detect your patterns.", text_color="gray").pack()
             ctk.CTkButton(content, text="🎲 Generate Demo Data (6 Months)", command=gen_data_cmd, fg_color=ACCENT_PURPLE, height=40).pack(pady=20)
             return

        ctk.CTkLabel(content, text=txt, font=("Arial", 20), text_color="white").pack(anchor="w", pady=(0, 20))
        if grp.get("plot_path") and os.path.exists(grp["plot_path"]):
            try:
                img = Image.open(grp["plot_path"]); r = min(800/img.width, 1.0); img = img.resize((int(img.width*r), int(img.height*r)), Image.Resampling.BICUBIC)
                i = ImageTk.PhotoImage(img); prediction_img_label = ctk.CTkLabel(content, text="", image=i); prediction_img_label.image=i; prediction_img_label.pack(pady=10)
            except: pass
        else: ctk.CTkLabel(content, text=grp.get("message", "Error"), text_color=ACCENT_RED).pack()

    def err(e): spin.stop(); load.destroy(); ctk.CTkLabel(content, text=f"System Error: {e}", text_color=ACCENT_RED).pack()
    threading.Thread(target=run_ai, daemon=True).start()
app.update_ai_overview_view = update_ai_overview_view


# --- VIEW 9: EXPORT ---
export_frame = ctk.CTkFrame(main_content, fg_color=PRIMARY_DARK)
content_frames["Export Data"] = export_frame
def update_export_data_view():
    for w in export_frame.winfo_children(): w.destroy()
    ctk.CTkLabel(export_frame, text="Data Export", font=("Arial", 28, "bold")).pack(anchor="w", pady=20)
    def do_exp():
        msg = export_user_data(current_user.uname)
        messagebox.showinfo("Export", msg) if "✅" in msg else messagebox.showerror("Error", msg)
    ctk.CTkButton(export_frame, text="Download CSV", command=do_exp, height=50, width=200, fg_color=ACCENT_BLUE).pack(anchor="w")
app.update_export_data_view = update_export_data_view


# --- STARTUP ---
ensure_transaction_file()
load_initial_users()
switch_view("Login")
app.mainloop()

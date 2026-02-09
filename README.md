Here is the complete, raw text for your `README.md`. You can copy everything inside the code block below and paste it directly into your file.

```markdown
### AI-Powered Personal Finance Manager (x-analytics)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![TensorFlow](https://img.shields.io/badge/AI-TensorFlow%20%7C%20LSTM-orange?style=for-the-badge&logo=tensorflow)
![CustomTkinter](https://img.shields.io/badge/GUI-CustomTkinter-blueviolet?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Active-success?style=for-the-badge)

**X-Analytics** is a next-generation personal finance application that evolves beyond simple tracking. It features a **"Master Brain"**—a Deep Learning LSTM Neural Network—that analyzes your spending sequence to predict future financial trends with high accuracy.

Wrapped in a modern, professional dark-themed interface, it offers real-time visualization, smart budget enforcement, and deep financial insights.

![Main Dashboard](image_8389ab.png)
*Figure 1: The Modern Dark Dashboard visualizing monthly net flow and recent transactions.*

---

## ✨ Key Features

### 🤖 The "Master Brain" (AI Forecasting)
Unlike standard apps that use simple averages, X-Analytics uses a **Long Short-Term Memory (LSTM)** Neural Network to understand the *sequence* of your spending.
- **Context-Aware:** Recognizes patterns like weekend spikes, monthly bills, or seasonal habits.
- **30-Day Lookback:** Analyzes your last 30 days of history to predict the next month's total expense.
- **Visual Forecast:** Plots a dashed "Future Line" against your historical data to show exactly where your finances are heading.

![AI Prediction](image_8389c3.png)
*Figure 2: The AI "Master Brain" predicting future spending trends based on historical data.*

### 💼 Comprehensive Financial Management
- **Smart Budgeting:** Set monthly limits with visual progress bars.
    - **NEW:** Includes a **"Reset Budget"** feature to clear limits instantly.
    - **Alerts:** Real-time warnings if a transaction will exceed your budget.
- **Loan Tracker:** Dedicated module to manage debts, log "Requests" (borrowing), and "Repayments."
- **Transaction Logging:** Seamlessly add Income, Expenses, and Transfers between accounts.

### 🎨 Modern User Experience
- **Sleek Dark Mode:** Built with `CustomTkinter` for a professional, eye-friendly aesthetic (`#1A1A2E` theme).
- **Interactive Sidebar:** Quick navigation between Dashboard, Income, Expense, Loans, and AI tools.
- **Asynchronous Processing:** The AI runs on background threads, ensuring the app never freezes while "thinking."
- **Demo Mode:** Includes a **Dummy Data Generator** to instantly create 6 months of realistic test data so you can see the AI in action immediately.

---

## 🛠️ Tech Stack

This project is built using a robust stack of Python libraries:

| Component | Library | Purpose |
| :--- | :--- | :--- |
| **GUI** | `customtkinter` | Modern, high-DPI, dark-mode user interface. |
| **AI Core** | `tensorflow` / `keras` | Building and running the LSTM Neural Network. |
| **Data Logic** | `pandas` / `numpy` | High-performance data manipulation and scaling. |
| **Plotting** | `matplotlib` | Generating dynamic financial graphs and trend lines. |
| **Image** | `Pillow` (PIL) | Rendering charts within the GUI. |

---

## 🚀 Installation & Setup

Follow these steps to get the Master Brain running on your local machine.

### 1. Clone the Repository
```bash
git clone [https://github.com/haroon-ai1/personal-Finance-Manager-Application-Python-.git](https://github.com/haroon-ai1/personal-Finance-Manager-Application-Python-.git)
cd personal-Finance-Manager-Application-Python-

```

### 2. Install Dependencies

```bash
pip install customtkinter tensorflow pandas numpy scikit-learn matplotlib pillow

```

### 3. 🧠 CRITICAL STEP: Train the Brain

The application needs a trained "Brain" file to function. You must run the training script **once** before opening the app.

1. Ensure the dataset `Personal_Finance_Dataset.csv` is in the project folder.
2. Run the training script:
```bash
python train_model.py

```


3. Wait for the process to finish. It will generate a file named `finance_brain.keras`.

### 4. Run the Application

Now you can launch the dashboard:

```bash
python gui.py

```

---

## 📂 Project Structure

* **`gui.py`**: The frontend application. Handles the Dark UI, navigation, threading, and user interaction.
* **`logic.py`**: The backend engine. Handles database (CSV) operations, data processing, and loads the AI model for predictions.
* **`train_model.py`**: The "Teacher." Reads raw data, normalizes it, and trains the LSTM Neural Network to create the model file.
* **`users.txt`**: Secure storage for user credentials and account balances.
* **`transactions.csv`**: The ledger containing every income, expense, and transfer.

---

## 🤝 Contributing

Contributions are welcome! If you have ideas for better AI models, new UI themes, or additional features:

1. Fork the repository.
2. Create a feature branch.
3. Submit a Pull Request.

---

## 📜 License

This project is developed by **Haroon** and is available for educational and open-source use.

```

```

# 🏖️ PTO (Paid Time Off) Simulator

A comprehensive Streamlit application for simulating and optimizing your PTO (Paid Time Off) usage across multiple leave categories. Plan your vacation days strategically and avoid losing time off due to expiration!

## Features

### 📈 Simulation & Forecast
- Real-time PTO balance tracking across three categories
- Visual forecasts with interactive charts
- Monthly balance summary with color-coded tables
- Projected balances for up to 24 months ahead

### 💡 Smart Recommendations
- Automatic usage priority recommendations (RTT → Last Year → This Year)
- Expiration alerts with urgency indicators
- Optimal usage strategy based on your current balances
- Days-until-expiration countdown

### 📅 Events Timeline
- Complete history of all PTO events
- Accrual tracking (monthly additions)
- Leave usage breakdown by category
- Expiration notifications

### 🗓️ Planned Leaves Management
- Add multiple planned leaves
- Interactive leave calendar
- Automatic deduction in recommended order
- Insufficient PTO warnings

## PTO Categories

### RTT (Réduction du Temps de Travail)
- **Expires**: December 31st
- **Refills**: January 1st (configurable, typically 8-9 days)
- **Priority**: Use FIRST (highest expiration risk)

### Paid Leave Last Year
- **Expires**: May 31st
- **Source**: Previous year's "This Year" balance rolls over on June 1st
- **Priority**: Use SECOND

### Paid Leave This Year
- **Accrues**: 2.083333 days per month (25 days per year)
- **Rolls over**: Becomes "Last Year" on June 1st
- **Priority**: Use LAST (safest, won't expire soon)

## Installation

1. Clone this repository:
```bash
git clone https://github.com/catherinanen/travelplanner.git
cd travelplanner
```

2. Create a virtual environment (recommended):
```bash
python -m venv .venv
source .venv/bin/activate  # On macOS/Linux
# or
.venv\Scripts\activate  # On Windows
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Run the Streamlit app:
```bash
streamlit run app.py
```

The app will open in your default browser at `http://localhost:8501`

## How to Use

### 1. Set Initial Balances
In the sidebar, enter your current PTO balances:
- **RTT**: Current RTT days available
- **Last Year**: Carried over from previous year
- **This Year**: Current year's accrued PTO

### 2. Configure RTT Refill
Set how many RTT days you receive on January 1st (typically 8-9 days, varies by year)

### 3. Add Planned Leaves
- Click "Add New Leave" in the sidebar
- Select the date and number of days
- The app automatically deducts in optimal order

### 4. Review Simulation
- **Current Balances**: See today's PTO status
- **Projected Balances**: View end-of-period projections
- **Timeline Chart**: Visual representation of balances over time
- **Monthly Summary**: Detailed month-by-month breakdown

### 5. Follow Recommendations
Check the "Recommendations" tab for:
- Which PTO to use first
- Expiration warnings
- Optimal usage strategy

## Key Rules

### Expiration Rules
- **RTT expires**: December 31st → Lost if not used
- **Last Year expires**: May 31st → Lost if not used
- **This Year rolls over**: June 1st → Becomes "Last Year"

### Accrual Rules
- **This Year**: +2.083333 days at end of each month
- **RTT**: Refills on January 1st (configurable amount)

### Usage Priority (Automatic)
1. **RTT** - Most urgent (expires Dec 31)
2. **Last Year** - Urgent (expires May 31)
3. **This Year** - Safe (rolls over to Last Year)

## Technology Stack

- **Streamlit**: Web application framework
- **Pandas**: Data manipulation and analysis
- **NumPy**: Numerical computations
- **Plotly**: Interactive visualizations
- **python-dateutil**: Date calculations
- **Matplotlib**: Styling support

## Project Structure

```
.
├── app.py                 # Main Streamlit application
├── requirements.txt       # Python dependencies
└── README.md             # This file
```

## Tips for Best Results

1. **Update Regularly**: Enter your current PTO balances monthly
2. **Plan Ahead**: Add your planned leaves to see future impact
3. **Check Recommendations**: Follow the app's advice to avoid expiration
4. **Adjust RTT Refill**: Update the refill amount based on your company's policy for the year
5. **Use Priority Order**: The app automatically deducts in the safest order

## Example Scenarios

### Scenario 1: End of Year Rush
If you have 5 RTT days in November:
- ⚠️ **Urgent**: Use all 5 RTT days before December 31st or lose them!

### Scenario 2: May Deadline
If you have 10 "Last Year" days in April:
- ⚠️ **Urgent**: Use all 10 days before May 31st or lose them!

### Scenario 3: Safe Planning
If you have 15 "This Year" days:
- ✅ **Safe**: These will roll over to "Last Year" on June 1st

## License

This project is open source and available for educational and personal use.

## Deployment

### Deploy to Streamlit Cloud (Free)

1. **Fork or use this repository**
2. **Go to [share.streamlit.io](https://share.streamlit.io/)**
3. **Sign in with GitHub**
4. **Click "New app"**
5. **Select:**
   - Repository: `catherinanen/pto_simulator`
   - Branch: `main`
   - Main file path: `app.py`
6. **Click "Deploy"**
7. **Share your URL** with friends!

Your app will be live at: `https://pto-simulator-[yourname].streamlit.app`

### Notes on Cloud Deployment
- Each user will have their own session
- Settings are saved locally when running on your computer
- On Streamlit Cloud, settings persist only during the session
- Users should bookmark their simulation parameters or save them manually

## Contributing

Feel free to fork, modify, and enhance this application for your specific needs. Pull requests are welcome!

---

Built with ❤️ using Streamlit | Smart PTO management since 2026

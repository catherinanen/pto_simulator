import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
import os

st.set_page_config(page_title="PTO Simulator", layout="wide", page_icon="🏖️")

# Custom CSS for better styling
st.markdown("""
<style>
    /* Smaller X button in sidebar */
    [data-testid="stSidebar"] button[kind="secondary"] {
        padding: 0.15rem 0.3rem;
        font-size: 0.8rem;
        min-height: 1.5rem;
    }
    
    /* Better table styling */
    .stDataFrame {
        border-radius: 8px;
    }
    
    /* Metric styling */
    [data-testid="stMetricValue"] {
        font-size: 1.5rem;
    }
</style>
""", unsafe_allow_html=True)

# File to store user preferences
SETTINGS_FILE = "pto_settings.json"

def load_settings():
    """Load saved settings from JSON file"""
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_settings(settings):
    """Save settings to JSON file"""
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump(settings, f, indent=2)
    except:
        pass

# Load previous settings
saved_settings = load_settings()

# Title and description
st.title("🏖️ PTO (Paid Time Off) Simulator")
st.markdown("""
This app helps you simulate and optimize your PTO usage across three categories:
- **RTT**: Expires in December, refills at year start (configurable, typically 8-9 days)
- **Paid Leave Last Year**: Expires end of May
- **Paid Leave This Year**: Accrues 2.083333 days/month (25 days/year), becomes "Last Year" on June 1st
""")

# Helper functions
def get_accrual_for_month(year, month):
    """Returns the accrual for a given month (2.083333 days)"""
    return 2.083333

def get_expiration_dates(current_date):
    """Returns expiration dates for each PTO type"""
    current_year = current_date.year
    
    # RTT expires December 31st
    rtt_expiry = datetime(current_year, 12, 31)
    
    # Paid Leave Last Year expires May 31st
    if current_date.month <= 5:
        last_year_expiry = datetime(current_year, 5, 31)
    else:
        last_year_expiry = datetime(current_year + 1, 5, 31)
    
    return rtt_expiry, last_year_expiry

def simulate_pto(start_date, initial_rtt, initial_last_year, initial_this_year, 
                 planned_leaves, simulation_months=12, rtt_refill=8.0):
    """
    Simulates PTO balances over time
    Returns a dataframe with monthly balances and events
    """
    results = []
    events = []
    
    # Current balances
    rtt = initial_rtt
    last_year = initial_last_year
    this_year = initial_this_year
    
    current_date = start_date
    end_date = start_date + relativedelta(months=simulation_months)
    
    # Sort planned leaves by date
    planned_leaves_sorted = sorted(planned_leaves, key=lambda x: x['date'])
    leave_index = 0
    
    # Track month-by-month
    while current_date <= end_date:
        is_month_end = (current_date + timedelta(days=1)).day == 1
        
        # Record daily snapshot
        results.append({
            'date': current_date,
            'rtt': round(rtt, 2),
            'last_year': round(last_year, 2),
            'this_year': round(this_year, 2),
            'total': round(rtt + last_year + this_year, 2)
        })
        
        # Check for expiration at end of May (Paid Leave Last Year)
        if current_date.month == 5 and is_month_end:
            if last_year > 0:
                events.append({'date': current_date, 'event': f'❌ Lost {round(last_year, 2)} Last Year days (expired)'})
                last_year = 0
            
        # Check for rollover on June 1st
        if current_date.month == 6 and current_date.day == 1:
            if this_year > 0:
                events.append({'date': current_date, 'event': f'🔄 {round(this_year, 2)} This Year days → Last Year'})
                last_year = this_year
                this_year = 0
            
        # Check for RTT expiration at end of December
        if current_date.month == 12 and is_month_end:
            if rtt > 0:
                events.append({'date': current_date, 'event': f'❌ Lost {round(rtt, 2)} RTT days (expired)'})
                rtt = 0
            
        # Check for RTT refill on January 1st
        if current_date.month == 1 and current_date.day == 1 and current_date != start_date:
            rtt = rtt_refill
            events.append({'date': current_date, 'event': f'✨ RTT refilled ({rtt_refill} days)'})
        
        # Accrue this year's PTO at end of month
        if is_month_end:
            accrual = get_accrual_for_month(current_date.year, current_date.month)
            this_year += accrual
            events.append({'date': current_date, 'event': f'➕ Accrued {round(accrual, 2)} This Year days'})
        
        # Process planned leaves for this day
        if leave_index < len(planned_leaves_sorted) and planned_leaves_sorted[leave_index]['date'] == current_date:
            leave = planned_leaves_sorted[leave_index]
            days_needed = leave['days']
            original_days = days_needed
            breakdown_text = []
            
            # Use PTO in recommended order: RTT -> Last Year -> This Year
            if rtt >= days_needed:
                rtt -= days_needed
                breakdown_text.append(f"RTT: {days_needed:.1f}")
                days_needed = 0
            elif rtt > 0:
                breakdown_text.append(f"RTT: {rtt:.1f}")
                days_needed -= rtt
                rtt = 0
            
            if days_needed > 0:
                if last_year >= days_needed:
                    last_year -= days_needed
                    breakdown_text.append(f"Last Year: {days_needed:.1f}")
                    days_needed = 0
                elif last_year > 0:
                    breakdown_text.append(f"Last Year: {last_year:.1f}")
                    days_needed -= last_year
                    last_year = 0
            
            if days_needed > 0:
                if this_year >= days_needed:
                    this_year -= days_needed
                    breakdown_text.append(f"This Year: {days_needed:.1f}")
                    days_needed = 0
                elif this_year > 0:
                    breakdown_text.append(f"This Year: {this_year:.1f}")
                    days_needed -= this_year
                    this_year = 0
            
            # Get note if available
            note_text = f" - {leave.get('note')}" if leave.get('note') else ""
            
            if days_needed > 0:
                events.append({
                    'date': current_date, 
                    'event': f'⚠️ LEAVE: {original_days} days{note_text} - INSUFFICIENT PTO! Short by {days_needed:.1f} days'
                })
            else:
                events.append({
                    'date': current_date, 
                    'event': f'🏖️ LEAVE: {original_days} days{note_text} ({', '.join(breakdown_text)})'
                })
            
            leave_index += 1
        
        current_date += timedelta(days=1)
    
    df_results = pd.DataFrame(results)
    df_events = pd.DataFrame(events)
    
    return df_results, df_events

def get_recommendations(rtt, last_year, this_year, current_date):
    """Returns recommendations on which PTO to use first"""
    recommendations = []
    
    current_year = current_date.year
    current_month = current_date.month
    
    # Calculate days until expiration
    days_until_dec_31 = (datetime(current_year, 12, 31) - current_date).days
    if current_month <= 5:
        days_until_may_31 = (datetime(current_year, 5, 31) - current_date).days
    else:
        days_until_may_31 = (datetime(current_year + 1, 5, 31) - current_date).days
    
    # Priority recommendations
    if rtt > 0 and days_until_dec_31 <= 90:
        recommendations.append(f"⚠️ **URGENT**: Use {rtt:.2f} RTT days before Dec 31 ({days_until_dec_31} days left)")
    elif rtt > 0:
        recommendations.append(f"✅ Use RTT days first: {rtt:.2f} days available (expires Dec 31)")
    
    if last_year > 0 and days_until_may_31 <= 60:
        recommendations.append(f"⚠️ **URGENT**: Use {last_year:.2f} Last Year days before May 31 ({days_until_may_31} days left)")
    elif last_year > 0:
        recommendations.append(f"📅 Use Last Year days second: {last_year:.2f} days available (expires May 31)")
    
    if this_year > 0:
        recommendations.append(f"💚 This Year days are safe: {this_year:.2f} days (rolls over to Last Year on June 1st)")
    
    return recommendations

# Sidebar for inputs
st.sidebar.header("📊 Initial PTO Balances")
st.sidebar.markdown("Enter your current PTO days:")
st.sidebar.caption("💾 Auto-saved locally | Use Download/Upload for cloud")

# Date input
default_start_date = saved_settings.get('start_date', datetime.now().strftime('%Y-%m-%d'))
simulation_start_date = st.sidebar.date_input(
    "Simulation Start Date",
    value=datetime.strptime(default_start_date, '%Y-%m-%d').date() if isinstance(default_start_date, str) else datetime.now(),
    help="The date to start the simulation from"
)

simulation_start_date = datetime.combine(simulation_start_date, datetime.min.time())

# Initial balances
col1, col2, col3 = st.sidebar.columns(3)
with col1:
    initial_rtt = st.number_input(
        "RTT", 
        min_value=0.0, 
        max_value=50.0, 
        value=float(saved_settings.get('initial_rtt', 5.0)), 
        step=0.5
    )
with col2:
    initial_last_year = st.number_input(
        "Last Year", 
        min_value=0.0, 
        max_value=50.0, 
        value=float(saved_settings.get('initial_last_year', 10.0)), 
        step=0.5
    )
with col3:
    initial_this_year = st.number_input(
        "This Year", 
        min_value=0.0, 
        max_value=50.0, 
        value=float(saved_settings.get('initial_this_year', 8.0)), 
        step=0.5
    )

# RTT refill amount
rtt_refill_days = st.sidebar.number_input(
    "RTT Refill (days per year)", 
    min_value=0.0, 
    max_value=20.0, 
    value=float(saved_settings.get('rtt_refill_days', 9.0)), 
    step=0.5,
    help="Number of RTT days added on January 1st (usually 8-9 days)"
)

simulation_months = st.sidebar.slider(
    "Simulation Period (months)", 
    min_value=3, 
    max_value=24, 
    value=int(saved_settings.get('simulation_months', 12))
)

# Save current settings
current_settings = {
    'start_date': simulation_start_date.strftime('%Y-%m-%d'),
    'initial_rtt': initial_rtt,
    'initial_last_year': initial_last_year,
    'initial_this_year': initial_this_year,
    'rtt_refill_days': rtt_refill_days,
    'simulation_months': simulation_months
}
save_settings(current_settings)

# Planned leaves section
st.sidebar.markdown("---")
st.sidebar.header("🗓️ Planned Leaves")

# Initialize session state for planned leaves from saved settings
if 'planned_leaves' not in st.session_state:
    saved_leaves = saved_settings.get('planned_leaves', [])
    # Convert saved string dates back to datetime objects
    st.session_state.planned_leaves = [
        {
            'date': datetime.strptime(leave['date'], '%Y-%m-%d'),
            'days': leave['days'],
            'note': leave.get('note', '')
        }
        for leave in saved_leaves
    ]

# Initialize form counter for resetting
if 'form_counter' not in st.session_state:
    st.session_state.form_counter = 0

# Upload settings section - at the top
st.sidebar.markdown("**📂 Load Saved Settings**")
uploaded_file = st.sidebar.file_uploader(
    "Upload your settings file",
    type=['json'],
    help="Restore previously saved PTO configuration",
    key="settings_uploader"
)
if uploaded_file is not None:
    try:
        uploaded_settings = json.loads(uploaded_file.read())
        # Update session state and save
        save_settings(uploaded_settings)
        # Convert leaves
        st.session_state.planned_leaves = [
            {
                'date': datetime.strptime(leave['date'], '%Y-%m-%d'),
                'days': leave['days'],
                'note': leave.get('note', '')
            }
            for leave in uploaded_settings.get('planned_leaves', [])
        ]
        st.sidebar.success("✅ Settings loaded successfully!")
        st.rerun()
    except Exception as e:
        st.sidebar.error(f"❌ Error loading file: {str(e)[:50]}")

st.sidebar.markdown("")

# Add new leave
with st.sidebar.form(f"add_leave_form_{st.session_state.form_counter}"):
    st.markdown("**Add New Leave:**")
    leave_date = st.date_input("Leave Date", value=datetime.now() + timedelta(days=30))
    leave_days = st.number_input("Days", min_value=0.5, max_value=30.0, value=1.0, step=0.5)
    leave_note = st.text_input("Note (optional)", placeholder="e.g., Trip to Barcelona", max_chars=50)
    
    col1, col2 = st.columns(2)
    with col1:
        add_button = st.form_submit_button("➕ Add", use_container_width=True)
    with col2:
        clear_button = st.form_submit_button("🗑️ Clear All", use_container_width=True)
    
    if add_button:
        st.session_state.planned_leaves.append({
            'date': datetime.combine(leave_date, datetime.min.time()),
            'days': leave_days,
            'note': leave_note
        })
        # Save to settings file
        current_settings['planned_leaves'] = [
            {'date': leave['date'].strftime('%Y-%m-%d'), 'days': leave['days'], 'note': leave.get('note', '')}
            for leave in st.session_state.planned_leaves
        ]
        save_settings(current_settings)
        # Increment counter to reset form
        st.session_state.form_counter += 1
        st.rerun()
    
    if clear_button:
        st.session_state.planned_leaves = []
        # Save empty list to settings
        current_settings['planned_leaves'] = []
        save_settings(current_settings)
        st.session_state.form_counter += 1
        st.rerun()

# Download settings button - below the add form
st.sidebar.markdown("")
st.sidebar.markdown("**💾 Save Current Settings**")
settings_to_download = {
    'start_date': simulation_start_date.strftime('%Y-%m-%d'),
    'initial_rtt': initial_rtt,
    'initial_last_year': initial_last_year,
    'initial_this_year': initial_this_year,
    'rtt_refill_days': rtt_refill_days,
    'simulation_months': simulation_months,
    'planned_leaves': [
        {'date': leave['date'].strftime('%Y-%m-%d'), 'days': leave['days'], 'note': leave.get('note', '')}
        for leave in st.session_state.planned_leaves
    ]
}
st.sidebar.download_button(
    label="💾 Download Settings",
    data=json.dumps(settings_to_download, indent=2),
    file_name=f"pto_settings_{datetime.now().strftime('%Y%m%d')}.json",
    mime="application/json",
    use_container_width=True,
    help="Save all your PTO settings and planned leaves to a file",
    type="primary"
)
st.sidebar.caption("💡 Save your settings to restore them later or share with others")
st.sidebar.markdown("---")

# Display planned leaves in sidebar (compact)
if st.session_state.planned_leaves:
    st.sidebar.markdown(f"**Planned Leaves:** ({len(st.session_state.planned_leaves)})")
    for idx, leave in enumerate(sorted(st.session_state.planned_leaves, key=lambda x: x['date'])):
        col1, col2 = st.sidebar.columns([9, 1])
        with col1:
            leave_text = f"{leave['date'].strftime('%m/%d')}: {leave['days']}d"
            if leave.get('note'):
                leave_text += f" - {leave['note'][:20]}"
            st.caption(leave_text)
        with col2:
            if st.button("×", key=f"sidebar_remove_{idx}", help="Remove this leave"):
                st.session_state.planned_leaves.pop(idx)
                # Save updated list
                current_settings['planned_leaves'] = [
                    {'date': leave['date'].strftime('%Y-%m-%d'), 'days': leave['days'], 'note': leave.get('note', '')}
                    for leave in st.session_state.planned_leaves
                ]
                save_settings(current_settings)
                st.rerun()
else:
    st.sidebar.caption("No planned leaves yet")

# Main content
tab1, tab2, tab3, tab4 = st.tabs(["📈 Simulation & Forecast", "🗓️ Planned Leaves", "📅 Events Timeline", "💡 Recommendations"])

with tab1:
    st.header("PTO Balance Forecast")
    
    # Run simulation
    df_results, df_events = simulate_pto(
        simulation_start_date, 
        initial_rtt, 
        initial_last_year, 
        initial_this_year,
        st.session_state.planned_leaves,
        simulation_months,
        rtt_refill_days
    )
    
    # Current balance metrics
    st.subheader("Current Balances")
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("RTT", f"{initial_rtt:.2f} days", help="Expires Dec 31")
    col2.metric("Last Year", f"{initial_last_year:.2f} days", help="Expires May 31")
    col3.metric("This Year", f"{initial_this_year:.2f} days", help="Accrues monthly")
    col4.metric("Total", f"{initial_rtt + initial_last_year + initial_this_year:.2f} days")
    
    # Future balance metrics (at end of simulation)
    st.subheader("Projected Balances (End of Period)")
    final_row = df_results.iloc[-1]
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("RTT", f"{final_row['rtt']:.2f} days", f"{final_row['rtt'] - initial_rtt:+.2f}")
    col2.metric("Last Year", f"{final_row['last_year']:.2f} days", f"{final_row['last_year'] - initial_last_year:+.2f}")
    col3.metric("This Year", f"{final_row['this_year']:.2f} days", f"{final_row['this_year'] - initial_this_year:+.2f}")
    col4.metric("Total", f"{final_row['total']:.2f} days", f"{final_row['total'] - (initial_rtt + initial_last_year + initial_this_year):+.2f}")
    
    # Visualization
    st.subheader("📊 PTO Balance Over Time")
    
    # Create stacked area chart
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=df_results['date'],
        y=df_results['rtt'],
        name='RTT',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(255, 127, 80, 0.7)',
        line=dict(width=0.5, color='rgba(255, 127, 80, 1)')
    ))
    
    fig.add_trace(go.Scatter(
        x=df_results['date'],
        y=df_results['last_year'],
        name='Last Year',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(255, 215, 0, 0.7)',
        line=dict(width=0.5, color='rgba(255, 215, 0, 1)')
    ))
    
    fig.add_trace(go.Scatter(
        x=df_results['date'],
        y=df_results['this_year'],
        name='This Year',
        mode='lines',
        stackgroup='one',
        fillcolor='rgba(50, 205, 50, 0.7)',
        line=dict(width=0.5, color='rgba(50, 205, 50, 1)')
    ))
    
    # Add total line
    fig.add_trace(go.Scatter(
        x=df_results['date'],
        y=df_results['total'],
        name='Total',
        mode='lines',
        line=dict(width=3, color='rgba(0, 0, 139, 0.8)', dash='dot')
    ))
    
    fig.update_layout(
        title="PTO Balance Over Time",
        xaxis_title="Date",
        yaxis_title="Days",
        hovermode='x unified',
        height=500,
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Monthly summary table
    st.subheader("📅 Monthly Summary")
    
    # Sample monthly (show first day of each month)
    df_monthly = df_results[df_results['date'].dt.day == 1].copy()
    df_monthly['Month'] = df_monthly['date'].dt.strftime('%Y-%m')
    df_monthly = df_monthly[['Month', 'rtt', 'last_year', 'this_year', 'total']]
    df_monthly.columns = ['Month', 'RTT', 'Last Year', 'This Year', 'Total']
    
    st.dataframe(
        df_monthly.style.format({
            'RTT': '{:.2f}',
            'Last Year': '{:.2f}',
            'This Year': '{:.2f}',
            'Total': '{:.2f}'
        }).background_gradient(cmap='RdYlGn', subset=['Total']),
        use_container_width=True,
        hide_index=True
    )

with tab2:
    st.header("�️ Planned Leaves Manager")
    
    if st.session_state.planned_leaves:
        # Sort leaves by date
        sorted_leaves = sorted(st.session_state.planned_leaves, key=lambda x: x['date'])
        
        # Create a nice table view
        st.subheader("📋 Your Planned Leaves")
        
        # Create DataFrame for display
        leaves_data = []
        for leave in sorted_leaves:
            leaves_data.append({
                'Date': leave['date'].strftime('%Y-%m-%d'),
                'Day': leave['date'].strftime('%A'),
                'Days': leave['days'],
                'Note': leave.get('note', '-'),
                'Weeks Away': f"{((leave['date'] - simulation_start_date).days // 7)} weeks"
            })
        
        df_leaves = pd.DataFrame(leaves_data)
        
        # Display with styling
        st.dataframe(
            df_leaves,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Date": st.column_config.DateColumn("📅 Date", width="medium"),
                "Day": st.column_config.TextColumn("Day", width="small"),
                "Days": st.column_config.NumberColumn("⏱️ Days", width="small", format="%.1f"),
                "Note": st.column_config.TextColumn("📝 Note", width="large"),
                "Weeks Away": st.column_config.TextColumn("⏳ Time", width="small")
            }
        )
        
        # Statistics
        st.markdown("---")
        st.subheader("📊 Leave Statistics")
        col1, col2, col3, col4 = st.columns(4)
        
        total_days = sum(leave['days'] for leave in sorted_leaves)
        next_leave = sorted_leaves[0] if sorted_leaves else None
        leaves_this_year = [l for l in sorted_leaves if l['date'].year == simulation_start_date.year]
        
        col1.metric("Total Planned Days", f"{total_days:.1f}")
        col2.metric("Number of Leaves", len(sorted_leaves))
        if next_leave:
            days_until = (next_leave['date'] - simulation_start_date).days
            col3.metric("Next Leave", f"in {days_until} days")
        col4.metric("Leaves This Year", len(leaves_this_year))
        
        # Timeline visualization
        st.markdown("---")
        st.subheader("📅 Timeline View")
        
        # Create timeline chart
        timeline_data = []
        for leave in sorted_leaves:
            timeline_data.append({
                'Leave': leave.get('note', 'Leave') if leave.get('note') else f"{leave['days']}d off",
                'Start': leave['date'],
                'End': leave['date'] + timedelta(days=int(leave['days'])),
                'Days': leave['days']
            })
        
        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            
            fig_timeline = go.Figure()
            
            for idx, row in df_timeline.iterrows():
                fig_timeline.add_trace(go.Scatter(
                    x=[row['Start'], row['End']],
                    y=[row['Leave'], row['Leave']],
                    mode='lines+markers',
                    name=row['Leave'],
                    line=dict(width=20, color=f'rgba({50 + idx * 40}, {150 + idx * 20}, {200 - idx * 30}, 0.7)'),
                    marker=dict(size=10),
                    hovertemplate=f"<b>{row['Leave']}</b><br>{row['Days']} days<br>%{{x|%Y-%m-%d}}<extra></extra>"
                ))
            
            fig_timeline.update_layout(
                title="",
                xaxis_title="Date",
                yaxis_title="",
                hovermode='closest',
                height=300,
                showlegend=False,
                xaxis=dict(
                    gridcolor='rgba(200, 200, 200, 0.3)',
                ),
                yaxis=dict(
                    gridcolor='rgba(200, 200, 200, 0.3)',
                )
            )
            
            st.plotly_chart(fig_timeline, use_container_width=True)
        
        # Edit/Delete section
        st.markdown("---")
        st.subheader("✏️ Edit or Remove Leaves")
        
        for idx, leave in enumerate(sorted_leaves):
            with st.expander(f"{leave['date'].strftime('%Y-%m-%d')} - {leave['days']} days - {leave.get('note', 'No note')}"):
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**Date:** {leave['date'].strftime('%A, %B %d, %Y')}")
                    st.write(f"**Duration:** {leave['days']} days")
                    st.write(f"**Note:** {leave.get('note', 'None')}")
                    st.write(f"**Days from now:** {(leave['date'] - simulation_start_date).days} days")
                with col2:
                    if st.button("🗑️ Remove", key=f"remove_detail_{idx}", use_container_width=True):
                        st.session_state.planned_leaves.pop(idx)
                        current_settings['planned_leaves'] = [
                            {'date': l['date'].strftime('%Y-%m-%d'), 'days': l['days'], 'note': l.get('note', '')}
                            for l in st.session_state.planned_leaves
                        ]
                        save_settings(current_settings)
                        st.rerun()
    else:
        st.info("📝 No planned leaves yet. Add some using the sidebar form!")
        st.markdown("""
        **How to add a leave:**
        1. Use the form in the sidebar on the left
        2. Select a date
        3. Enter the number of days
        4. Optionally add a note (e.g., "Trip to Barcelona")
        5. Click **Add**
        """)

with tab3:
    st.header("📅 Events Timeline")
    
    # Get recommendations
    recommendations = get_recommendations(
        initial_rtt, 
        initial_last_year, 
        initial_this_year, 
        simulation_start_date
    )
    
    st.markdown("### Usage Priority")
    st.markdown("""
    To avoid losing PTO days, always use them in this order:
    1. **RTT** (expires December 31st)
    2. **Last Year** (expires May 31st)
    3. **This Year** (safest, rolls over to Last Year on June 1st)
    """)
    
    st.markdown("### Your Current Situation")
    for rec in recommendations:
        st.markdown(rec)
    
    # Expiration warnings
    st.markdown("---")
    st.subheader("⚠️ Expiration Alerts")
    
    current_year = simulation_start_date.year
    current_month = simulation_start_date.month
    
    # Check for potential losses
    warnings = []
    
    # Check RTT
    if initial_rtt > 0:
        days_until_dec = (datetime(current_year, 12, 31) - simulation_start_date).days
        if days_until_dec <= 60:
            warnings.append({
                'Type': 'RTT',
                'Days': initial_rtt,
                'Expires': 'Dec 31',
                'Days Until': days_until_dec,
                'Urgency': '🔴 URGENT' if days_until_dec <= 30 else '🟡 SOON'
            })
    
    # Check Last Year
    if initial_last_year > 0:
        if current_month <= 5:
            days_until_may = (datetime(current_year, 5, 31) - simulation_start_date).days
        else:
            days_until_may = (datetime(current_year + 1, 5, 31) - simulation_start_date).days
        
        if days_until_may <= 90:
            warnings.append({
                'Type': 'Last Year',
                'Days': initial_last_year,
                'Expires': 'May 31',
                'Days Until': days_until_may,
                'Urgency': '🔴 URGENT' if days_until_may <= 30 else '🟡 SOON'
            })
    
    if warnings:
        df_warnings = pd.DataFrame(warnings)
        st.dataframe(df_warnings, use_container_width=True, hide_index=True)
    else:
        st.success("✅ No urgent expirations! All your PTO is safe for now.")
    
    # Optimal usage strategy
    st.markdown("---")
    st.subheader("📋 Optimal Usage Strategy")
    
    total_pto = initial_rtt + initial_last_year + initial_this_year
    st.info(f"You have **{total_pto:.2f}** total PTO days available.")
    
    strategy = []
    if initial_rtt > 0:
        strategy.append(f"1. Use **{initial_rtt:.2f}** RTT days before December 31st")
    if initial_last_year > 0:
        strategy.append(f"2. Use **{initial_last_year:.2f}** Last Year days before May 31st")
    if initial_this_year > 0:
        strategy.append(f"3. Use **{initial_this_year:.2f}** This Year days anytime (they're safe)")
    
    for item in strategy:
        st.markdown(item)

with tab3:
    st.header("📅 Events Timeline")
    
    if not df_events.empty:
        # Display events chronologically
        df_events_sorted = df_events.sort_values('date', ascending=False)
        
        st.markdown("### All Events")
        for _, event in df_events_sorted.iterrows():
            date_str = event['date'].strftime('%Y-%m-%d')
            with st.expander(f"{date_str} - {event['event']}", expanded=False):
                st.write(f"**Date:** {date_str}")
                st.write(f"**Event:** {event['event']}")
        
        # Summary statistics
        st.markdown("---")
        st.subheader("📊 Event Summary")
        
        col1, col2, col3 = st.columns(3)
        
        leave_events = df_events[df_events['event'].str.contains('LEAVE', na=False)]
        accrual_events = df_events[df_events['event'].str.contains('Accrued', na=False)]
        expiration_events = df_events[df_events['event'].str.contains('Lost', na=False)]
        
        col1.metric("Planned Leaves", len(leave_events))
        col2.metric("Accrual Events", len(accrual_events))
        col3.metric("Expirations", len(expiration_events))
        
    else:
        st.info("No events yet. Add some planned leaves to see how they affect your PTO balance!")

with tab4:
    st.header("💡 Smart Recommendations")

# Footer
st.markdown("---")
st.markdown("**PTO Simulator** | Built with Streamlit | Smart PTO management for 2026")

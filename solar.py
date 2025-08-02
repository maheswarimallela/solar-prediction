import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Set Streamlit page settings
st.set_page_config(page_title="Solar Energy Dashboard", layout="wide")

st.title("🔆 Solar Energy Monitoring Dashboard")

# ===============================
# File Upload
# ===============================
uploaded_file = st.sidebar.file_uploader("📥 Upload Your Solar CSV File", type=["csv"])

@st.cache_data
def load_data(file):
    df = pd.read_csv(file)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['Hour'] = df['Timestamp'].dt.hour
    df['Month'] = df['Timestamp'].dt.month
    return df

if uploaded_file:
    df = load_data(uploaded_file)
else:
    st.info("Upload a dataset to begin. Example: `solar_iot_energy_data_AZrAL5DeeQ.csv`")
    st.stop()

# ===============================
# Sidebar Filters
# ===============================
st.sidebar.header("⏱️ Time Filter")
start_time = st.sidebar.time_input("Start Time", value=df["Timestamp"].min().time())
end_time = st.sidebar.time_input("End Time", value=df["Timestamp"].max().time())

df_filtered = df[
    (df["Timestamp"].dt.time >= start_time) &
    (df["Timestamp"].dt.time <= end_time)
]

# ===============================
# KPI Cards
# ===============================
st.markdown("## 🔢 Key Performance Indicators")
col1, col2, col3, col4 = st.columns(4)
col1.metric("⚡ Energy Saved", f"{df_filtered['Energy_Saved_kWh'].sum():.2f} kWh")
col2.metric("🌱 CO₂ Saved", f"{df_filtered['CO2_Emissions_Saved_kg'].sum():.2f} kg")
col3.metric("🌡️ Avg Panel Temp", f"{df_filtered['Panel_Temperature_C'].mean():.1f} °C")
col4.metric("🔋 Max Power", f"{df_filtered['Power_Output_W'].max():.1f} W")

# ===============================
# Efficiency Calculation
# ===============================
PANEL_AREA = 1.6  # m², assumed
df_filtered['Efficiency'] = df_filtered['Power_Output_W'] / (df_filtered['Solar_Irradiance_W/m2'] * PANEL_AREA)

# ===============================
# Preview and Summary
# ===============================
st.write("### 🔍 Preview of Filtered Dataset", df_filtered.head())
st.write("### 📊 Summary Statistics")
st.write(df_filtered.describe())

# ===============================
# Visualizations
# ===============================
st.markdown("## 📈 Time-Series Plots")

def line_plot(df, y, title, ylabel, color):
    fig, ax = plt.subplots()
    ax.plot(df["Timestamp"], df[y], color=color, marker='o')
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Time")
    plt.xticks(rotation=45)
    st.pyplot(fig)

line_plot(df_filtered, "Power_Output_W", "⚡ Power Output Over Time", "Power Output (W)", "orange")
line_plot(df_filtered, "Solar_Irradiance_W/m2", "🔆 Solar Irradiance Over Time", "Irradiance (W/m²)", "red")
line_plot(df_filtered, "Battery_Charge_Level_%", "🔋 Battery Charge Level Over Time", "Charge (%)", "green")
line_plot(df_filtered, "CO2_Emissions_Saved_kg", "🌍 CO₂ Emissions Saved Over Time", "CO₂ Saved (kg)", "brown")
line_plot(df_filtered, "Efficiency", "⚙️ Panel Efficiency Over Time", "Efficiency (decimal)", "purple")

# ===============================
# Load vs Power Comparison
# ===============================
st.markdown("## ⚖️ Load Consumption vs Power Output")
fig, ax = plt.subplots()
ax.plot(df_filtered["Timestamp"], df_filtered["Load_Consumption_W"], label="Load Consumption", color='blue')
ax.plot(df_filtered["Timestamp"], df_filtered["Power_Output_W"], label="Power Output", color='orange')
ax.legend()
ax.set_ylabel("Watt (W)")
ax.set_title("Load vs Power Output")
plt.xticks(rotation=45)
st.pyplot(fig)

# ===============================
# Hourly Bar Chart
# ===============================
st.markdown("## 🕒 Average Power Output by Hour")
hourly_avg = df_filtered.groupby('Hour')["Power_Output_W"].mean()
st.bar_chart(hourly_avg)

# ===============================
# Fault Analysis
# ===============================
st.markdown("## ⚠️ Fault Status Report")
faults = df_filtered[df_filtered["Fault_Status"] != "No Fault"]
if not faults.empty:
    st.warning("⚠️ Faults detected!")
    st.dataframe(faults)
else:
    st.success("✅ No faults detected in the selected time range.")

# ===============================
# Data Download
# ===============================
csv = df_filtered.to_csv(index=False)
st.download_button(
    label="📤 Download Filtered Data as CSV",
    data=csv,
    file_name='filtered_solar_data.csv',
    mime='text/csv'
)

st.write("Made with ❤️ by [You] using Streamlit")

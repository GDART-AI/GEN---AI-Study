import streamlit as st

# ------------------------------
# Conversion Functions
# ------------------------------

# Currency (basic static rates for demo, can be connected to API later)
def convert_currency(amount, from_currency, to_currency):
    rates = {
        "USD": 1,
        "INR": 83,
        "EUR": 0.92,
        "GBP": 0.79
    }
    if from_currency not in rates or to_currency not in rates:
        return "Unsupported Currency"
    return round(amount * (rates[to_currency] / rates[from_currency]), 2)

# Temperature
def convert_temperature(value, from_unit, to_unit):
    if from_unit == "Celsius":
        if to_unit == "Fahrenheit":
            return (value * 9/5) + 32
        elif to_unit == "Kelvin":
            return value + 273.15
    elif from_unit == "Fahrenheit":
        if to_unit == "Celsius":
            return (value - 32) * 5/9
        elif to_unit == "Kelvin":
            return (value - 32) * 5/9 + 273.15
    elif from_unit == "Kelvin":
        if to_unit == "Celsius":
            return value - 273.15
        elif to_unit == "Fahrenheit":
            return (value - 273.15) * 9/5 + 32
    return value

# Length (meters as base)
def convert_length(value, from_unit, to_unit):
    units = {
        "Meter": 1,
        "Kilometer": 1000,
        "Centimeter": 0.01,
        "Millimeter": 0.001,
        "Mile": 1609.34,
        "Yard": 0.9144,
        "Foot": 0.3048,
        "Inch": 0.0254
    }
    return value * units[from_unit] / units[to_unit]

# Weight (grams as base)
def convert_weight(value, from_unit, to_unit):
    units = {
        "Gram": 1,
        "Kilogram": 1000,
        "Milligram": 0.001,
        "Pound": 453.592,
        "Ounce": 28.3495
    }
    return value * units[from_unit] / units[to_unit]

# ------------------------------
# Streamlit UI
# ------------------------------
st.set_page_config(page_title="Unit Converter 🔄", page_icon="🔄")

st.title("🔄 Universal Unit Converter")
st.write("Convert **Currency, Temperature, Length, and Weight** instantly.")

# Sidebar selection
option = st.sidebar.selectbox("Choose Conversion Type", ["Currency", "Temperature", "Length", "Weight"])

if option == "Currency":
    st.subheader("💱 Currency Converter")
    amount = st.number_input("Enter amount", min_value=0.0, step=0.01)
    from_curr = st.selectbox("From", ["USD", "INR", "EUR", "GBP"])
    to_curr = st.selectbox("To", ["USD", "INR", "EUR", "GBP"])
    if st.button("Convert"):
        result = convert_currency(amount, from_curr, to_curr)
        st.success(f"{amount} {from_curr} = {result} {to_curr}")

elif option == "Temperature":
    st.subheader("🌡️ Temperature Converter")
    temp = st.number_input("Enter Temperature", step=0.1)
    from_unit = st.selectbox("From", ["Celsius", "Fahrenheit", "Kelvin"])
    to_unit = st.selectbox("To", ["Celsius", "Fahrenheit", "Kelvin"])
    if st.button("Convert"):
        result = convert_temperature(temp, from_unit, to_unit)
        st.success(f"{temp} {from_unit} = {round(result, 2)} {to_unit}")

elif option == "Length":
    st.subheader("📏 Length Converter")
    length = st.number_input("Enter Length", step=0.1)
    from_unit = st.selectbox("From", ["Meter", "Kilometer", "Centimeter", "Millimeter", "Mile", "Yard", "Foot", "Inch"])
    to_unit = st.selectbox("To", ["Meter", "Kilometer", "Centimeter", "Millimeter", "Mile", "Yard", "Foot", "Inch"])
    if st.button("Convert"):
        result = convert_length(length, from_unit, to_unit)
        st.success(f"{length} {from_unit} = {round(result, 4)} {to_unit}")

elif option == "Weight":
    st.subheader("⚖️ Weight Converter")
    weight = st.number_input("Enter Weight", step=0.1)
    from_unit = st.selectbox("From", ["Gram", "Kilogram", "Milligram", "Pound", "Ounce"])
    to_unit = st.selectbox("To", ["Gram", "Kilogram", "Milligram", "Pound", "Ounce"])
    if st.button("Convert"):
        result = convert_weight(weight, from_unit, to_unit)
        st.success(f"{weight} {from_unit} = {round(result, 4)} {to_unit}")

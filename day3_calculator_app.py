import streamlit as st

# Title
st.title("🧮 Simple Calculator")

# Input numbers
num1 = st.number_input("Enter first number", step=1.0)
num2 = st.number_input("Enter second number", step=1.0)

# Choose operation
operation = st.selectbox(
    "Select operation",
    ("Addition", "Subtraction", "Multiplication", "Division")
)

# Calculate result
if st.button("Calculate"):
    if operation == "Addition":
        result = num1 + num2
        st.success(f"✅ Result: {num1} + {num2} = {result}")
    elif operation == "Subtraction":
        result = num1 - num2
        st.success(f"✅ Result: {num1} - {num2} = {result}")
    elif operation == "Multiplication":
        result = num1 * num2
        st.success(f"✅ Result: {num1} × {num2} = {result}")
    elif operation == "Division":
        if num2 != 0:
            result = num1 / num2
            st.success(f"✅ Result: {num1} ÷ {num2} = {result}")
        else:
            st.error("❌ Division by zero is not allowed")

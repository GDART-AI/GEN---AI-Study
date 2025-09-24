import streamlit as st

# ---------- Config ----------
st.set_page_config(page_title="💱 Currency Converter Pro", layout="wide")

# ---------- Static Exchange Rates ----------
exchange_rates = {
    "USD": {"rate": 1.0, "symbol": "$", "name": "US Dollar", "flag": "🇺🇸"},
    "INR": {"rate": 83.0, "symbol": "₹", "name": "Indian Rupee", "flag": "🇮🇳"},
    "EUR": {"rate": 0.92, "symbol": "€", "name": "Euro", "flag": "🇪🇺"},
    "GBP": {"rate": 0.79, "symbol": "£", "name": "British Pound", "flag": "🇬🇧"},
    "JPY": {"rate": 150.0, "symbol": "¥", "name": "Japanese Yen", "flag": "🇯🇵"},
}

currencies = list(exchange_rates.keys())

# ---------- Styling ----------
st.markdown(
    """
    <style>
    .main {
        background: linear-gradient(135deg, #1f1c2c, #928DAB);
        color: white;
    }
    .title {
        font-size: 2.5rem; font-weight: 700; text-align:center;
        background: -webkit-linear-gradient(#f5af19, #f12711);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    }
    .card {
        padding: 20px; border-radius: 15px; text-align: center;
        background: linear-gradient(135deg, rgba(255,255,255,0.08), rgba(255,255,255,0.05));
        border: 1px solid rgba(255,255,255,0.2);
        box-shadow: 0 8px 24px rgba(0,0,0,0.4);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------- Header ----------
st.markdown('<div class="title">💱 Currency Converter Pro</div>', unsafe_allow_html=True)
st.markdown("<p style='text-align:center;'>Convert between INR, USD, EUR, GBP, JPY with style ✨</p>", unsafe_allow_html=True)

# ---------- Layout ----------
col1, col2, col3 = st.columns([1.5, 1, 1.5])

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🌍 From Currency")
    from_currency = st.selectbox(
        "Choose source currency",
        currencies,
        format_func=lambda x: f"{exchange_rates[x]['flag']} {x} - {exchange_rates[x]['name']}",
    )
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("💵 Amount")
    amount = st.number_input("Enter amount", min_value=0.0, value=100.0, step=1.0, format="%.2f")
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("🎯 To Currency")
    to_currency = st.selectbox(
        "Choose target currency",
        currencies,
        index=1,
        format_func=lambda x: f"{exchange_rates[x]['flag']} {x} - {exchange_rates[x]['name']}",
    )
    st.markdown('</div>', unsafe_allow_html=True)

# ---------- Conversion ----------
def convert(amount: float, from_cur: str, to_cur: str) -> float:
    usd_amount = amount / exchange_rates[from_cur]["rate"]
    return usd_amount * exchange_rates[to_cur]["rate"]

if st.button("🚀 Convert Now", use_container_width=True):
    result = convert(amount, from_currency, to_currency)

    st.markdown(
        f"""
        <div class="card" style="margin-top:20px;">
            <h2>✨ Result ✨</h2>
            <p style="font-size:1.2rem;">
                {exchange_rates[from_currency]['flag']} {amount:.2f} {exchange_rates[from_currency]['symbol']} 
                = <b style="font-size:2rem; color:#00ffcc;">
                {exchange_rates[to_currency]['flag']} {result:.2f} {exchange_rates[to_currency]['symbol']}
                </b>
            </p>
            <p style="font-size:0.9rem; color:#ddd;">
                Rate: 1 {from_currency} = {(exchange_rates[to_currency]["rate"] / exchange_rates[from_currency]["rate"]):.4f} {to_currency}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

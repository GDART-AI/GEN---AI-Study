import streamlit as st
import pandas as pd
from datetime import datetime
import base64
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
import json

# Configuration
TAX_RATE = 0.18  # 18% GST for India
SERVICE_CHARGE = 0.10
RESTAURANT_NAME = "Spice Palace Restaurant"
RESTAURANT_ADDRESS = "123 MG Road, Dharmapuri, Tamil Nadu - 636701"
RESTAURANT_PHONE = "+91 98765 43210"

# Menu Data Structure - Indian Restaurant Menu
MENU_ITEMS = {
    "🥗 Starters": {
        "Samosa": {"price": 120, "description": "Crispy pastry filled with spiced potatoes and peas", "icon": "🥟", "vegetarian": True},
        "Chicken Tikka": {"price": 280, "description": "Marinated chicken grilled in tandoor", "icon": "🍗", "spicy": True},
        "Paneer Tikka": {"price": 250, "description": "Grilled cottage cheese with spices", "icon": "🧀", "vegetarian": True},
        "Fish Amritsari": {"price": 320, "description": "Crispy fried fish with Punjabi spices", "icon": "🐟"}
    },
    "🍛 Main Course": {
        "Butter Chicken": {"price": 380, "description": "Creamy tomato curry with tender chicken", "icon": "🍛"},
        "Paneer Butter Masala": {"price": 320, "description": "Rich cottage cheese curry", "icon": "🍛", "vegetarian": True},
        "Dal Makhani": {"price": 280, "description": "Creamy black lentils cooked overnight", "icon": "🍲", "vegetarian": True},
        "Biryani (Chicken)": {"price": 420, "description": "Aromatic basmati rice with spiced chicken", "icon": "🍚"},
        "Biryani (Veg)": {"price": 350, "description": "Fragrant rice with mixed vegetables", "icon": "🍚", "vegetarian": True},
        "Roti/Naan": {"price": 60, "description": "Fresh Indian bread", "icon": "🫓", "vegetarian": True}
    },
    "🥤 Beverages": {
        "Lassi (Sweet)": {"price": 80, "description": "Traditional yogurt drink", "icon": "🥛", "vegetarian": True},
        "Masala Chai": {"price": 50, "description": "Spiced Indian tea", "icon": "☕", "vegetarian": True},
        "Fresh Lime Water": {"price": 60, "description": "Refreshing lime drink", "icon": "🍋", "vegetarian": True},
        "Kingfisher Beer": {"price": 180, "description": "Premium Indian beer", "icon": "🍺"},
        "Mango Juice": {"price": 90, "description": "Fresh mango juice", "icon": "🥭", "vegetarian": True}
    },
    "🍨 Desserts": {
        "Gulab Jamun": {"price": 120, "description": "Sweet milk dumplings in sugar syrup", "icon": "🍯", "vegetarian": True},
        "Kulfi": {"price": 100, "description": "Traditional Indian ice cream", "icon": "🍨", "vegetarian": True},
        "Rasgulla": {"price": 110, "description": "Soft cottage cheese balls in syrup", "icon": "🍡", "vegetarian": True},
        "Kheer": {"price": 130, "description": "Rice pudding with nuts and cardamom", "icon": "🍮", "vegetarian": True}
    }
}

def initialize_session_state():
    """Initialize session state variables"""
    if 'order' not in st.session_state:
        st.session_state.order = {}
    if 'customer_info' not in st.session_state:
        st.session_state.customer_info = {}
    if 'order_history' not in st.session_state:
        st.session_state.order_history = []

def display_menu():
    """Display the restaurant menu with categories"""
    st.header("🍽️ Restaurant Menu")
    
    for category, items in MENU_ITEMS.items():
        st.subheader(category)
        
        # Create columns for better layout
        cols = st.columns(2)
        
        for idx, (item_name, item_info) in enumerate(items.items()):
            col = cols[idx % 2]
            
            with col:
                with st.container():
                    # Item header with icon and name
                    item_header = f"{item_info['icon']} {item_name}"
                    
                    # Add dietary indicators
                    indicators = []
                    if item_info.get('vegetarian'):
                        indicators.append("🌱")
                    if item_info.get('spicy'):
                        indicators.append("🌶️")
                    
                    if indicators:
                        item_header += " " + "".join(indicators)
                    
                    st.markdown(f"**{item_header}**")
                    st.markdown(f"*{item_info['description']}*")
                    
                    # Price and quantity selector
                    col1, col2, col3 = st.columns([2, 1, 1])
                    
                    with col1:
                        st.markdown(f"**₹{item_info['price']:.0f}**")
                    
                    with col2:
                        quantity = st.number_input(
                            "Qty",
                            min_value=0,
                            max_value=20,
                            value=st.session_state.order.get(item_name, 0),
                            key=f"qty_{item_name}",
                            label_visibility="collapsed"
                        )
                    
                    with col3:
                        if st.button("Add", key=f"add_{item_name}", use_container_width=True):
                            if quantity > 0:
                                st.session_state.order[item_name] = quantity
                                st.success(f"Added {quantity}x {item_name}")
                    
                    # Update order when quantity changes
                    if quantity > 0:
                        st.session_state.order[item_name] = quantity
                    elif item_name in st.session_state.order:
                        del st.session_state.order[item_name]
                    
                    st.markdown("---")

def calculate_totals():
    """Calculate order totals"""
    subtotal = 0
    
    for item_name, quantity in st.session_state.order.items():
        # Find item price
        for category_items in MENU_ITEMS.values():
            if item_name in category_items:
                price = category_items[item_name]['price']
                subtotal += price * quantity
                break
    
    tax_amount = subtotal * TAX_RATE
    service_amount = subtotal * SERVICE_CHARGE if subtotal > 0 else 0
    total = subtotal + tax_amount + service_amount
    
    return {
        'subtotal': subtotal,
        'tax_amount': tax_amount,
        'service_amount': service_amount,
        'total': total
    }

def display_order_summary():
    """Display order summary in sidebar"""
    st.sidebar.header("🛒 Order Summary")
    
    if not st.session_state.order:
        st.sidebar.info("No items in order")
        return
    
    # Display ordered items
    for item_name, quantity in st.session_state.order.items():
        for category_items in MENU_ITEMS.values():
            if item_name in category_items:
                price = category_items[item_name]['price']
                item_total = price * quantity
                
                col1, col2 = st.sidebar.columns([3, 1])
                with col1:
                    st.write(f"{quantity}x {item_name}")
                    st.caption(f"₹{price:.0f} each")
                with col2:
                    st.write(f"₹{item_total:.0f}")
                
                # Remove item button
                if st.sidebar.button(f"❌", key=f"remove_{item_name}", help=f"Remove {item_name}"):
                    del st.session_state.order[item_name]
                    st.rerun()
                
                st.sidebar.markdown("---")
                break
    
    # Calculate and display totals
    totals = calculate_totals()
    
    st.sidebar.subheader("💰 Bill Summary")
    st.sidebar.metric("Subtotal", f"₹{totals['subtotal']:.0f}")
    st.sidebar.metric("Tax (18% GST)", f"₹{totals['tax_amount']:.0f}")
    st.sidebar.metric("Service Charge (10%)", f"₹{totals['service_amount']:.0f}")
    st.sidebar.metric("**TOTAL**", f"₹{totals['total']:.0f}")
    
    return totals

def get_customer_info():
    """Get customer information"""
    st.subheader("👤 Customer Information (Optional)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        name = st.text_input("Customer Name", value=st.session_state.customer_info.get('name', ''))
        phone = st.text_input("Phone Number", value=st.session_state.customer_info.get('phone', ''))
    
    with col2:
        email = st.text_input("Email", value=st.session_state.customer_info.get('email', ''))
        table = st.text_input("Table Number", value=st.session_state.customer_info.get('table', ''))
    
    st.session_state.customer_info = {
        'name': name,
        'phone': phone,
        'email': email,
        'table': table
    }

def generate_csv_invoice(totals):
    """Generate CSV invoice"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create invoice data
    invoice_data = []
    invoice_data.append([f"Restaurant Name: {RESTAURANT_NAME}"])
    invoice_data.append([f"Address: {RESTAURANT_ADDRESS}"])
    invoice_data.append([f"Phone: {RESTAURANT_PHONE}"])
    invoice_data.append([f"Order Date: {timestamp}"])
    invoice_data.append([""])
    
    # Customer info if available
    if any(st.session_state.customer_info.values()):
        invoice_data.append(["Customer Information:"])
        for key, value in st.session_state.customer_info.items():
            if value:
                invoice_data.append([f"{key.title()}: {value}"])
        invoice_data.append([""])
    
    # Header
    invoice_data.append(["Item", "Quantity", "Unit Price", "Total Price"])
    invoice_data.append(["---", "---", "---", "---"])
    
    # Order items
    for item_name, quantity in st.session_state.order.items():
        for category_items in MENU_ITEMS.values():
            if item_name in category_items:
                price = category_items[item_name]['price']
                total_price = price * quantity
                invoice_data.append([item_name, quantity, f"₹{price:.0f}", f"₹{total_price:.0f}"])
                break
    
    # Totals
    invoice_data.append(["---", "---", "---", "---"])
    invoice_data.append(["Subtotal", "", "", f"₹{totals['subtotal']:.0f}"])
    invoice_data.append(["Tax (18% GST)", "", "", f"₹{totals['tax_amount']:.0f}"])
    invoice_data.append(["Service Charge (10%)", "", "", f"₹{totals['service_amount']:.0f}"])
    invoice_data.append(["TOTAL", "", "", f"₹{totals['total']:.0f}"])
    
    # Convert to DataFrame
    df = pd.DataFrame(invoice_data)
    
    # Convert to CSV string
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, header=False)
    return csv_buffer.getvalue()

def generate_pdf_invoice(totals):
    """Generate PDF invoice"""
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Header
    p.setFont("Helvetica-Bold", 20)
    p.drawString(50, height - 50, RESTAURANT_NAME)
    
    p.setFont("Helvetica", 12)
    p.drawString(50, height - 75, RESTAURANT_ADDRESS)
    p.drawString(50, height - 90, RESTAURANT_PHONE)
    
    # Date and Invoice number
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    p.drawString(50, height - 115, f"Date: {timestamp}")
    p.drawString(50, height - 130, f"Invoice #: INV-{datetime.now().strftime('%Y%m%d%H%M%S')}")
    
    # Customer info
    y_pos = height - 160
    if any(st.session_state.customer_info.values()):
        p.setFont("Helvetica-Bold", 12)
        p.drawString(50, y_pos, "Customer Information:")
        y_pos -= 20
        
        p.setFont("Helvetica", 10)
        for key, value in st.session_state.customer_info.items():
            if value:
                p.drawString(50, y_pos, f"{key.title()}: {value}")
                y_pos -= 15
        y_pos -= 10
    
    # Order items header
    p.setFont("Helvetica-Bold", 12)
    p.drawString(50, y_pos, "Item")
    p.drawString(250, y_pos, "Qty")
    p.drawString(300, y_pos, "Price")
    p.drawString(400, y_pos, "Total")
    y_pos -= 20
    
    # Draw line
    p.line(50, y_pos, 500, y_pos)
    y_pos -= 20
    
    # Order items
    p.setFont("Helvetica", 10)
    for item_name, quantity in st.session_state.order.items():
        for category_items in MENU_ITEMS.values():
            if item_name in category_items:
                price = category_items[item_name]['price']
                total_price = price * quantity
                
                p.drawString(50, y_pos, item_name)
                p.drawString(250, y_pos, str(quantity))
                p.drawString(300, y_pos, f"₹{price:.0f}")
                p.drawString(400, y_pos, f"₹{total_price:.0f}")
                y_pos -= 20
                break
    
    # Totals section
    y_pos -= 20
    p.line(250, y_pos, 500, y_pos)
    y_pos -= 20
    
    p.drawString(300, y_pos, f"Subtotal: ₹{totals['subtotal']:.0f}")
    y_pos -= 15
    p.drawString(300, y_pos, f"Tax (18% GST): ₹{totals['tax_amount']:.0f}")
    y_pos -= 15
    p.drawString(300, y_pos, f"Service (10%): ₹{totals['service_amount']:.0f}")
    y_pos -= 20
    
    p.setFont("Helvetica-Bold", 12)
    p.drawString(300, y_pos, f"TOTAL: ₹{totals['total']:.0f}")
    
    # Footer
    p.setFont("Helvetica", 10)
    p.drawString(50, 50, "Thank you for dining with us!")
    
    p.save()
    buffer.seek(0)
    return buffer.getvalue()

def process_order():
    """Process the order and generate invoices"""
    if not st.session_state.order:
        st.warning("Please add items to your order first!")
        return
    
    totals = calculate_totals()
    
    st.success("🎉 Order Confirmed!")
    st.balloons()
    
    # Display final bill
    st.subheader("📄 Final Bill")
    
    # Order details
    for item_name, quantity in st.session_state.order.items():
        for category_items in MENU_ITEMS.values():
            if item_name in category_items:
                price = category_items[item_name]['price']
                total_price = price * quantity
                
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    st.write(item_name)
                with col2:
                    st.write(quantity)
                with col3:
                    st.write(f"₹{price:.0f}")
                with col4:
                    st.write(f"₹{total_price:.0f}")
                break
    
    st.markdown("---")
    
    # Final totals
    col1, col2 = st.columns([3, 1])
    with col2:
        st.metric("Subtotal", f"₹{totals['subtotal']:.0f}")
        st.metric("Tax (18% GST)", f"₹{totals['tax_amount']:.0f}")
        st.metric("Service Charge (10%)", f"₹{totals['service_amount']:.0f}")
        st.metric("**TOTAL**", f"₹{totals['total']:.0f}")
    
    # Download buttons
    st.subheader("📥 Download Invoice")
    
    col1, col2 = st.columns(2)
    
    with col1:
        csv_data = generate_csv_invoice(totals)
        st.download_button(
            label="Download CSV Invoice",
            data=csv_data,
            file_name=f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv",
            use_container_width=True
        )
    
    with col2:
        pdf_data = generate_pdf_invoice(totals)
        st.download_button(
            label="Download PDF Invoice",
            data=pdf_data,
            file_name=f"invoice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
            mime="application/pdf",
            use_container_width=True
        )
    
    # Add to order history
    order_record = {
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'order': st.session_state.order.copy(),
        'customer': st.session_state.customer_info.copy(),
        'totals': totals
    }
    st.session_state.order_history.append(order_record)
    
    # Clear order option
    if st.button("🆕 Start New Order", use_container_width=True):
        st.session_state.order = {}
        st.session_state.customer_info = {}
        st.rerun()

def main():
    """Main application function"""
    # Page configuration
    st.set_page_config(
        page_title="Restaurant Order & Billing",
        page_icon="🍔",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Main title
    st.title("🍔 Restaurant Order & Billing System")
    st.markdown(f"**{RESTAURANT_NAME}**")
    st.markdown(f"📍 {RESTAURANT_ADDRESS} | 📞 {RESTAURANT_PHONE}")
    st.markdown("---")
    
    # Create tabs
    tab1, tab2, tab3 = st.tabs(["🍽️ Menu & Order", "🧾 Checkout", "📊 Order History"])
    
    with tab1:
        display_menu()
    
    with tab2:
        if st.session_state.order:
            get_customer_info()
            st.markdown("---")
            
            # Payment simulation
            st.subheader("💳 Payment")
            payment_method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Debit Card", "Digital Wallet"])
            
            if st.button("🛒 Confirm Order & Generate Invoice", use_container_width=True):
                process_order()
        else:
            st.info("No items in your order. Please go to the Menu tab to add items.")
    
    with tab3:
        st.subheader("📊 Order History")
        if st.session_state.order_history:
            for idx, order in enumerate(reversed(st.session_state.order_history)):
                with st.expander(f"Order #{len(st.session_state.order_history) - idx} - {order['timestamp']}"):
                    if order['customer']['name']:
                        st.write(f"**Customer:** {order['customer']['name']}")
                    
                    st.write("**Items:**")
                    for item, qty in order['order'].items():
                        st.write(f"- {qty}x {item}")
                    
                    st.write(f"**Total:** ₹{order['totals']['total']:.0f}")
        else:
            st.info("No order history available.")
    
    # Sidebar - Order Summary
    display_order_summary()

if __name__ == "__main__":
    main()
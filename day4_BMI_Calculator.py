import streamlit as st
import plotly.graph_objects as go
import plotly.express as px

# Page configuration
st.set_page_config(
    page_title="💪 Creative BMI Calculator",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #2E86AB;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .bmi-card {
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .underweight {
        background: linear-gradient(135deg, #74b9ff, #0984e3);
        color: white;
    }
    
    .normal {
        background: linear-gradient(135deg, #00b894, #00a085);
        color: white;
    }
    
    .overweight {
        background: linear-gradient(135deg, #fdcb6e, #e17055);
        color: white;
    }
    
    .obese {
        background: linear-gradient(135deg, #fd79a8, #e84393);
        color: white;
    }
    
    .bmi-number {
        font-size: 3rem;
        font-weight: bold;
        margin: 1rem 0;
    }
    
    .category-text {
        font-size: 1.5rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .tip-text {
        font-size: 1.1rem;
        line-height: 1.6;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

def calculate_bmi(weight, height):
    """Calculate BMI from weight (kg) and height (cm)"""
    height_m = height / 100  # Convert cm to meters
    bmi = weight / (height_m ** 2)
    return round(bmi, 1)

def get_bmi_category(bmi):
    """Determine BMI category and return styling info"""
    if bmi < 18.5:
        return {
            'category': 'Underweight',
            'emoji': '⚠️',
            'css_class': 'underweight',
            'color': '#74b9ff',
            'tips': [
                "🥗 Add more proteins and healthy fats to your diet",
                "🏋️‍♂️ Include strength training exercises",
                "🍎 Eat nutrient-dense foods regularly",
                "💤 Ensure adequate sleep for muscle recovery",
                "👨‍⚕️ Consider consulting a nutritionist"
            ]
        }
    elif 18.5 <= bmi < 25:
        return {
            'category': 'Normal Weight',
            'emoji': '✅',
            'css_class': 'normal',
            'color': '#00b894',
            'tips': [
                "🎉 You're in the healthy range! Keep it up!",
                "🚶‍♂️ Maintain regular physical activity",
                "🥙 Continue balanced nutrition habits",
                "💧 Stay well hydrated throughout the day",
                "😊 Focus on overall wellness and mental health"
            ]
        }
    elif 25 <= bmi < 30:
        return {
            'category': 'Overweight',
            'emoji': '🍔',
            'css_class': 'overweight',
            'color': '#fdcb6e',
            'tips': [
                "🚶‍♂️ Try daily walking for 30-45 minutes",
                "🥗 Reduce portion sizes and processed foods",
                "💧 Drink water before meals",
                "🏃‍♀️ Include cardio exercises 3-4 times weekly",
                "📱 Track your food intake and activity"
            ]
        }
    else:  # BMI >= 30
        return {
            'category': 'Obese',
            'emoji': '🚨',
            'css_class': 'obese',
            'color': '#fd79a8',
            'tips': [
                "👨‍⚕️ Consider consulting with a healthcare provider",
                "🥬 Focus on whole foods and vegetables",
                "🏊‍♂️ Start with low-impact exercises like swimming",
                "📊 Set small, achievable weekly goals",
                "👥 Consider joining a support group or program"
            ]
        }

def create_bmi_gauge(bmi, category_info):
    """Create an interactive BMI gauge chart"""
    fig = go.Figure(go.Indicator(
        mode = "gauge+number+delta",
        value = bmi,
        domain = {'x': [0, 1], 'y': [0, 1]},
        title = {'text': "BMI Value", 'font': {'size': 24}},
        delta = {'reference': 22.5, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge = {
            'axis': {'range': [None, 40], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': category_info['color'], 'thickness': 0.3},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 18.5], 'color': '#74b9ff'},
                {'range': [18.5, 25], 'color': '#00b894'},
                {'range': [25, 30], 'color': '#fdcb6e'},
                {'range': [30, 40], 'color': '#fd79a8'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': bmi
            }
        }
    ))
    
    fig.update_layout(
        height=350,
        font={'color': "darkblue", 'family': "Arial"},
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)"
    )
    
    return fig

# Main app header
st.markdown('<h1 class="main-header">💪 Creative BMI Calculator ⚖️</h1>', unsafe_allow_html=True)

# Sidebar for inputs
with st.sidebar:
    st.header("📊 Enter Your Details")
    
    # Unit selection
    units = st.radio("Choose your preferred units:", ["Metric (kg/cm)", "Imperial (lbs/ft-in)"])
    
    if units == "Metric (kg/cm)":
        weight = st.number_input("Weight (kg)", min_value=1.0, max_value=500.0, value=70.0, step=0.1)
        height = st.number_input("Height (cm)", min_value=50.0, max_value=250.0, value=175.0, step=0.1)
    else:
        weight_lbs = st.number_input("Weight (lbs)", min_value=1.0, max_value=1000.0, value=154.0, step=0.1)
        feet = st.number_input("Height (feet)", min_value=1, max_value=8, value=5, step=1)
        inches = st.number_input("Height (inches)", min_value=0, max_value=11, value=9, step=1)
        
        # Convert to metric
        weight = weight_lbs * 0.453592
        height = (feet * 12 + inches) * 2.54
    
    st.markdown("---")
    st.markdown("### BMI Categories Reference")
    st.markdown("""
    - **Underweight**: < 18.5
    - **Normal**: 18.5 - 24.9
    - **Overweight**: 25.0 - 29.9
    - **Obese**: ≥ 30.0
    """)

# Main content area
col1, col2 = st.columns([1, 1])

if weight and height:
    bmi = calculate_bmi(weight, height)
    category_info = get_bmi_category(bmi)
    
    with col1:
        # BMI Result Card
        st.markdown(f"""
        <div class="bmi-card {category_info['css_class']}">
            <div style="font-size: 4rem;">{category_info['emoji']}</div>
            <div class="bmi-number">{bmi}</div>
            <div class="category-text">{category_info['category']}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Progress bar for visual representation
        if bmi < 18.5:
            progress = bmi / 18.5
        elif bmi < 25:
            progress = (bmi - 18.5) / (25 - 18.5)
        elif bmi < 30:
            progress = (bmi - 25) / (30 - 25)
        else:
            progress = min((bmi - 30) / 10, 1.0)
        
        st.progress(progress, text=f"BMI: {bmi}")
    
    with col2:
        # BMI Gauge Chart
        fig = create_bmi_gauge(bmi, category_info)
        st.plotly_chart(fig, use_container_width=True)

    # Health Tips Section
    st.markdown("## 💡 Personalized Health Tips")
    
    tips_cols = st.columns(len(category_info['tips']))
    for i, tip in enumerate(category_info['tips']):
        with tips_cols[i % len(tips_cols)]:
            st.info(tip)
    
    # Additional Information
    st.markdown("---")
    col3, col4, col5 = st.columns(3)
    
    with col3:
        st.metric(
            label="Your BMI",
            value=f"{bmi}",
            delta=f"{bmi - 22.5:.1f} from ideal"
        )
    
    with col4:
        ideal_weight_min = 18.5 * ((height/100) ** 2)
        ideal_weight_max = 24.9 * ((height/100) ** 2)
        st.metric(
            label="Ideal Weight Range",
            value=f"{ideal_weight_min:.1f} - {ideal_weight_max:.1f} kg"
        )
    
    with col5:
        calories_maintain = int(weight * 24)  # Rough estimate
        st.metric(
            label="Est. Daily Calories",
            value=f"{calories_maintain} kcal",
            help="Rough estimate for maintenance"
        )

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <small>
    💡 <strong>Disclaimer:</strong> This BMI calculator is for informational purposes only. 
    Please consult with healthcare professionals for personalized medical advice.
    <br>
    Made with ❤️ using Streamlit
    </small>
</div>
""", unsafe_allow_html=True)

# --- Custom CSS for Compactness (Scroll Reduction and Narrow Layout) ---
st.markdown("""
<style>
    /* 1. Force a Maximum Width on the main content block and center it */
    .block-container {
        /* VERTICAL SQUEEZE: Reduced from 1rem to 0.5rem */
        padding-top: 0.5rem; 
        padding-bottom: 0.5rem; 
        padding-left: 1rem;
        padding-right: 1rem;
        
        /* FIX: Max-Width set to 1200px to ensure title fits and prevents jagged edges */
        max-width: 1200px; 
        
        /* Set margin to 'auto' for centering */
        margin-left: auto;
        margin-right: auto;
    }
    
    /* 2. Standard Compactness Rules (from original code) */
    
    /* 🔥 FIX: Increased margin-top to push headings/sections down (Text Niche Karna) */
    h1, h2, h3, h4, h5, h6 {
        margin-top: 0.5rem; /* Increased to 0.5rem for more top spacing */
        margin-bottom: 0.25rem;
    }
    
    /* FIX FOR TITLE (h1): Font size reduced to fit in one line */
    h1 {
        font-size: 2.25rem;
        line-height: 1.1; 
        /* Added more top margin for title */
        margin-top: 1.0rem; 
    }

    /* VERTICAL SQUEEZE: Reduce vertical spacing around st.divider() */
    hr {
        margin: 0.5rem 0 !important;
    }
    
    /* Reduce space in metric elements */
    [data-testid="stMetric"] {
        padding-top: 0px;
        padding-bottom: 0px;
    }
    [data-testid="stMetricLabel"] {
        margin-bottom: -0.1rem; /* Move label closer to value */
        font-size: 0.8rem; /* Slightly smaller label font */
    }
    [data-testid="stMetricValue"] {
        font-size: 1.5rem; /* Slightly smaller value font */
    }
    /* Reduce space around columns */
    .st-emotion-cache-12quz0q { 
        gap: 0.5rem;
    }
    
    /* REMOVED: Sidebar CSS is now unnecessary */
    /* section[data-testid="stSidebar"] {
        width: 190px !important;
        min-width: 190px !important;
    } */

</style>
""", unsafe_allow_html=True)
# ... (Calculation Logic Functions remain unchanged)
# --- 2. STREAMLIT APP STRUCTURE ---

st.title("🛍️ " + FULL_TITLE)
st.markdown("###### **1. Input and Configuration**")

# --- PLATFORM SELECTOR ---
platform_selector = st.radio(
    "Select Platform:",
    ('Myntra', 'FirstCry', 'Ajio'), # Options updated here
    index=0, 
    horizontal=True
)

# --- CONFIGURATION (MOVED FROM SIDEBAR) ---
st.markdown("##### **Configuration Settings**")
col_config_1, col_config_2 = st.columns(2)

# Column 1: Mode, Royalty, Marketing
with col_config_1:
    # Calculation Mode Selector
    calculation_mode = st.radio(
        "Calculation Mode:",
        ('Profit Calculation (for given Discount)', 'Target Discount Finder (for given Profit)'),
        index=0, 
        label_visibility="visible"
    )
    
    # Royalty Fee Radio Button 
    royalty_base = 'CPA' if platform_selector == 'Myntra' else 'Sale Price'
    royalty_label = f"Royalty Fee (10% of {royalty_base})?"
    
    # Royalty Fee is applicable to all
    apply_royalty = st.radio(
        royalty_label,
        ('Yes', 'No'),
        index=0, 
        horizontal=True,
        label_visibility="visible"
    )

    # Marketing Fee Radio Button 
    apply_marketing_fee_default = 'Yes (4%)' if platform_selector == 'Myntra' else 'No (0%)'
    apply_marketing_fee = st.radio(
        "Marketing Fee (Myntra 4% of CPA)?", 
        ('Yes (4%)', 'No (0%)'),
        index=0 if apply_marketing_fee_default.startswith('Yes') else 1,
        horizontal=True,
        label_visibility="visible"
    )

# Column 2: Product Cost, Target Profit
with col_config_2:
    # Product Cost Input
    product_cost = st.number_input(
        "Product Cost (₹)",
        min_value=0.0,
        value=1000.0,
        step=10.0,
        label_visibility="visible"
    )
    
    # Target Margin Input (Used in both modes)
    product_margin_target_rs = st.number_input(
        "Target Net Profit (₹)",
        min_value=0.0,
        value=200.0,
        step=10.0,
        label_visibility="visible"
    )
    # Added vertical spacer to align inputs better
    st.markdown("<div style='height: 4.5rem;'></div>", unsafe_allow_html=True) 

st.divider() 

# --- INPUT FIELDS (Main Body) ---
col_mrp_in, col_discount_in = st.columns(2)

new_mrp = col_mrp_in.number_input(
# ... (rest of the code remains the same from here)

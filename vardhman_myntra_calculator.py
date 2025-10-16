import pandas as pd
import streamlit as st
import numpy as np

# Set page config for wide layout and minimum gaps, using the specified full title
FULL_TITLE = "Vardhman Wool Store E.com Calculator" 
st.set_page_config(layout="wide", page_title=FULL_TITLE, page_icon="🛍️")

# --- Custom CSS for Compactness (Keeping only compactness, removing all column CSS) ---
st.markdown("""
<style>
    /* 1. Force a Maximum Width on the main content block and center it */
    .block-container {
        padding-top: 1.25rem; 
        padding-bottom: 0.5rem; 
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1840px; 
        margin-left: auto;
        margin-right: auto;
    }
    
    /* 2. Standard Compactness Rules */
    h1, h2, h3, h4, h5, h6 {
        margin-top: 0.5rem; 
        margin-bottom: 0.25rem;
    }
    h1 {
        font-size: 2.25rem;
        line-height: 1.1;  
        margin-top: 1.0rem; 
    }
    hr {
        margin: 0.5rem 0 !important;
    }
    [data-testid="stMetric"] {
        padding-top: 0px;
        padding-bottom: 0px;
    }
    [data-testid="stMetricLabel"] {
        margin-bottom: -0.1rem; 
        font-size: 0.8rem; 
    }
    [data-testid="stMetricValue"] {
        font-size: 1.5rem; 
    }
    /* Set a tighter gap for the new two-column main results area */
    .st-emotion-cache-12quz0q { 
        gap: 0.75rem; /* Slightly wider gap for major sections */
    }
    
</style>
""", unsafe_allow_html=True)

# --- CALCULATION LOGIC FUNCTIONS (No Change) ---

# Myntra Specific GT Charges
def calculate_myntra_gt_charges(sale_price):
    if sale_price <= 500:
        return 54.00
    elif sale_price <= 1000:
        return 94.00
    else:
        return 171.00

# Myntra Specific Commission Rate (Slab-based)
def get_myntra_commission_rate(customer_paid_amount):
    if customer_paid_amount <= 200:
        return 0.33 
    elif customer_paid_amount <= 300:
        return 0.22 
    elif customer_paid_amount <= 400:
        return 0.19 
    elif customer_paid_amount <= 500:
        return 0.22 
    elif customer_paid_amount <= 800:
        return 0.24 
    else:
        return 0.29 

# GST Taxable Value (Common)
def calculate_taxable_amount_value(customer_paid_amount):
    # GST Logic is common for all platforms based on Invoice Value (CPA/Sale Price)
    if customer_paid_amount >= 2500:
        tax_rate = 0.12 
        divisor = 1.12
    else:
        tax_rate = 0.05
        divisor = 1.05
    taxable_amount = customer_paid_amount / divisor
    return taxable_amount, tax_rate

def perform_calculations(mrp, discount, apply_royalty, marketing_fee_rate, product_cost, platform):
    """Performs all sequential calculations for profit analysis based on platform."""
    sale_price = mrp - discount
    if sale_price < 0:
        return (sale_price, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -99999999.0, 0.0, 0.0, 0.0)
    
    gt_charge = 0.0
    royalty_fee = 0.0
    marketing_fee_base = 0.0
    final_commission = 0.0
    commission_rate = 0.0 
    customer_paid_amount = sale_price 
    
    # --- PLATFORM SPECIFIC LOGIC ---
    if platform == 'Myntra':
        gt_charge = calculate_myntra_gt_charges(sale_price)
        customer_paid_amount = sale_price - gt_charge
        commission_rate = get_myntra_commission_rate(customer_paid_amount)
        commission_amount_base = customer_paid_amount * commission_rate
        royalty_fee = customer_paid_amount * 0.10 if apply_royalty == 'Yes' else 0.0
        marketing_fee_base = customer_paid_amount * marketing_fee_rate
        commission_tax = commission_amount_base * 0.18
        final_commission = commission_amount_base + commission_tax
        
    elif platform == 'FirstCry': 
        commission_rate = 0.42 
        final_commission = sale_price * commission_rate
        royalty_fee = sale_price * 0.10 if apply_royalty == 'Yes' else 0.0
        gt_charge = 0.0 
        marketing_fee_base = 0.0 
        customer_paid_amount = sale_price 
        marketing_fee_rate = 0.0
        
    elif platform == 'Ajio':
        commission_rate = 0.20
        commission_base = sale_price * commission_rate
        commission_tax = commission_base * 0.18
        final_commission = commission_base + commission_tax
        scm_base = 95.0
        scm_tax = scm_base * 0.18
        gt_charge = scm_base + scm_tax 
        customer_paid_amount = sale_price
        royalty_fee = sale_price * 0.10 if apply_royalty == 'Yes' else 0.0
        marketing_fee_base = 0.0
        marketing_fee_rate = 0.0
        
    # --- COMMON TAX AND FINAL SETTLEMENT LOGIC ---
    taxable_amount_value, invoice_tax_rate = calculate_taxable_amount_value(sale_price) 
    tax_amount = customer_paid_amount - taxable_amount_value
    tcs = tax_amount * 0.10
    tds = taxable_amount_value * 0.001 
    settled_amount = customer_paid_amount - final_commission - royalty_fee - marketing_fee_base - tds + tcs
    net_profit = settled_amount - product_cost
    
    return (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
            marketing_fee_base, marketing_fee_rate, final_commission, 
            commission_rate, settled_amount, taxable_amount_value, 
            net_profit, tds, tcs, invoice_tax_rate)

# --- NEW FUNCTION: Find Discount for Target Profit (No Change) ---
def find_discount_for_target_profit(mrp, target_profit, apply_royalty, marketing_fee_rate, product_cost, platform):
    """Finds the maximum discount allowed (in 1.0 steps) to achieve at least the target profit."""
    (_, _, _, _, _, _, _, _, _, _, initial_profit, _, _, _) = perform_calculations(mrp, 0.0, apply_royalty, marketing_fee_rate, product_cost, platform)

    if initial_profit < target_profit:
        return None, initial_profit, 0.0

    discount_step = 1.0
    required_discount = 0.0
    
    while required_discount <= mrp:
        (_, _, _, _, _, _, _, _, _, _, current_profit, _, _, _) = perform_calculations(mrp, required_discount, apply_royalty, marketing_fee_rate, product_cost, platform)
        
        if current_profit < target_profit:
            final_discount = max(0.0, required_discount - discount_step)
            (_, _, _, _, _, _, _, _, _, _, final_profit, _, _, _) = perform_calculations(mrp, final_discount, apply_royalty, marketing_fee_rate, product_cost, platform)
            discount_percent = (final_discount / mrp) * 100
            return final_discount, final_profit, discount_percent
        
        required_discount += discount_step

    (_, _, _, _, _, _, _, _, _, _, final_profit, _, _, _) = perform_calculations(mrp, mrp, apply_royalty, marketing_fee_rate, product_cost, platform)
    return mrp, final_profit, 100.0


# --- 2. STREAMLIT APP STRUCTURE ---

st.title("🛍️ " + FULL_TITLE)
st.markdown("###### **1. Input and Configuration**")

# --- PLATFORM & CONFIGURATION (No Change) ---
platform_selector = st.radio(
    "Select Platform:",
    ('Myntra', 'FirstCry', 'Ajio'),
    index=0, 
    horizontal=True
)

st.markdown("##### **Configuration Settings**")
col_mode, col_royalty, col_marketing = st.columns(3)

with col_mode:
    calculation_mode = st.radio(
        "Calculation Mode:",
        ('Profit Calculation', 'Target Discount'),
        index=0, 
        label_visibility="visible"
    )

with col_royalty:
    royalty_base = 'CPA' if platform_selector == 'Myntra' else 'Sale Price'
    apply_royalty = st.radio(
        f"Royalty Fee (10% of {royalty_base})?",
        ('Yes', 'No'),
        index=0, 
        horizontal=True,
        label_visibility="visible"
    )

with col_marketing:
    marketing_options = ['0%', '4%', '5%']
    default_index = marketing_options.index('4%') if platform_selector == 'Myntra' else marketing_options.index('0%')
    selected_marketing_fee_str = st.selectbox(
        "Marketing Fee Rate:", 
        marketing_options,
        index=default_index,
        help="Rate applied to CPA (Customer Paid Amount) on Myntra.",
        key="marketing_fee_selector"
    )
    marketing_fee_rate = float(selected_marketing_fee_str.strip('%')) / 100.0

col_cost, col_target = st.columns(2)
with col_cost:
    product_cost = st.number_input(
        "Product Cost (₹)",
        min_value=0.0,
        value=1000.0,
        step=10.0,
        label_visibility="visible"
    )
    
with col_target:
    product_margin_target_rs = st.number_input(
        "Target Net Profit (₹)",
        min_value=0.0,
        value=200.0,
        step=10.0,
        label_visibility="visible"
    )

st.divider() 

# --- INPUT FIELDS (No Change) ---
col_mrp_in, col_discount_in = st.columns(2)

new_mrp = col_mrp_in.number_input(
    "Product MRP (₹)",
    min_value=1.0,
    value=2500.0,
    step=100.0,
    key="new_mrp",
    label_visibility="visible"
) 

if calculation_mode == 'Profit Calculation':
    new_discount = col_discount_in.number_input(
        "Discount Amt (₹)",
        min_value=0.0,
        max_value=new_mrp,
        value=500.0,
        step=10.0,
        key="new_discount_manual",
        label_visibility="visible"
    )
else:
    col_discount_in.info(f"Targeting a Net Profit of ₹ {product_margin_target_rs:,.2f}...")
    new_discount = 0.0

st.divider() 

if new_mrp > 0 and product_cost > 0:
    try:
        # --- CALCULATION BLOCK ---
        if calculation_mode == 'Target Discount':
            target_profit = product_margin_target_rs
            calculated_discount, initial_max_profit, calculated_discount_percent = find_discount_for_target_profit(
                new_mrp, target_profit, apply_royalty, marketing_fee_rate, product_cost, platform_selector
            )
            if calculated_discount is None:
                st.error(f"Cannot achieve the Target Profit of ₹ {target_profit:,.2f}. The maximum possible Net Profit at 0% discount is ₹ {initial_max_profit:,.2f}.")
                st.stop()
            new_discount = calculated_discount
            
        (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
         marketing_fee_base, current_marketing_fee_rate, final_commission, 
         commission_rate, settled_amount, taxable_amount_value, 
         net_profit, tds, tcs, invoice_tax_rate) = perform_calculations(new_mrp, new_discount, apply_royalty, marketing_fee_rate, product_cost, platform_selector)
        
        target_profit = product_margin_target_rs
        delta_value = net_profit - target_profit
        current_margin_percent = (net_profit / product_cost) * 100 if product_cost > 0 else 0.0
        delta_label = f"vs Target: ₹ {delta_value:,.2f}"
        delta_color = "normal" if net_profit >= target_profit else "inverse"
            
        # --- DISPLAY RESULTS (MODIFIED FOR TWO-COLUMN COMPACT LAYOUT) ---
        
        # Create two main columns for the output display
        col_left, col_right = st.columns(2)
        
        # =========== LEFT COLUMN: Sales, Fixed Charges, Invoice Value ===========
        with col_left:
            st.markdown("###### **2. Sales, Fixed Charges & Invoice Value**")
            
            # Sub-row 1: Sales (3 columns)
            col1_l, col2_l, col3_l = st.columns(3)
            
            col1_l.metric(label="Product MRP (₹)", value=f"₹ {new_mrp:,.2f}", delta_color="off")
            
            discount_percent = (new_discount / new_mrp) * 100 if new_mrp > 0 else 0.0
            col2_l.metric(
                label="Discount Amt", 
                value=f"₹ {new_discount:,.2f}",
                delta=f"{discount_percent:,.2f}% of MRP",
                delta_color="off"
            )
            col3_l.metric(label="Sale Price (₹)", value=f"₹ {sale_price:,.2f}")
            
            st.markdown("---") # Custom Divider within the column
            
            # Sub-row 2: Fixed Charges & CPA (2 columns)
            col4_l, col5_l = st.columns(2)

            if platform_selector == 'Myntra':
                col4_l.metric(
                    label="GT Charge (Deducted from Sale Price)", 
                    value=f"₹ {gt_charge:,.2f}",
                    delta="Myntra Only",
                    delta_color="off"
                )
            elif platform_selector == 'FirstCry': 
                col4_l.metric(
                    label="Fixed Charges", 
                    value=f"₹ {gt_charge:,.2f}", 
                    delta_color="off"
                )
            else: # Ajio (New) display
                col4_l.metric(
                    label="SCM Charges (₹95 + 18% GST)", 
                    value=f"₹ {gt_charge:,.2f}", 
                    delta_color="off"
                )
                
            col5_l.metric(label="**Invoice Value (CPA)**", value=f"₹ {customer_paid_amount:,.2f}")
        
        # =========== RIGHT COLUMN: Deductions and Final Payout ===========
        with col_right:
            st.markdown("###### **3. Deductions (Charges)**")
            
            # Sub-row 1: Commission, Marketing, Royalty (3 columns)
            col1_r, col2_r, col3_r = st.columns(3)
            
            # Commission
            if platform_selector == 'Myntra':
                col1_r.metric(label=f"Commission ({commission_rate*100:.0f}%+Tax)", value=f"₹ {final_commission:,.2f}")
            elif platform_selector == 'FirstCry': 
                col1_r.metric(label="**Flat Deduction (42%)**", value=f"₹ {final_commission:,.2f}")
            else: # Ajio (New) display
                col1_r.metric(label=f"Commission (20%+Tax)", value=f"₹ {final_commission:,.2f}")
            
            # Marketing Fee
            col2_r.metric(
                label=f"Marketing Fee ({marketing_fee_rate*100:.0f}%)",
                value=f"₹ {marketing_fee_base:,.2f}",
            )
            
            # Royalty Fee
            col3_r.metric(
                label=f"Royalty Fee ({'10%' if apply_royalty=='Yes' else '0%'})",
                value=f"₹ {royalty_fee:,.2f}",
            )
            
            # Sub-row 2: Taxable Value, TDS, TCS (3 columns)
            col4_r, col5_r, col6_r = st.columns(3)

            col4_r.metric(
                label=f"Taxable Value (GST @ {invoice_tax_rate*100:.0f}%)",
                value=f"₹ {taxable_amount_value:,.2f}",
            )
            col5_r.metric(label="TDS (0.1%)", value=f"₹ {abs(tds):,.2f}")
            col6_r.metric(label="TCS (10% on Tax Amt)", value=f"₹ {abs(tcs):,.2f}")
            
            st.markdown("---") # Custom Divider within the column
            
            # Sub-row 3: Final Payout and Profit (2 columns)
            st.markdown("###### **4. Final Payout and Profit**")
            col7_r, col8_r = st.columns(2)

            col7_r.metric(
                label="**FINAL SETTLED AMOUNT**",
                value=f"₹ {settled_amount:,.2f}",
                delta_color="off"
            )
            
            col8_r.metric(
                label=f"**NET PROFIT ({current_margin_percent:,.2f}% Margin)**",
                value=f"₹ {net_profit:,.2f}",
                delta=delta_label,
                delta_color=delta_color
            )

    except ValueError as e:
        st.error(str(e))
else:
    st.info("Please enter a valid MRP and Product Cost to start the calculation.")

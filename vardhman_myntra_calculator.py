import pandas as pd
import streamlit as st
import numpy as np

# Set page config for wide layout and minimum gaps, using the specified full title
FULL_TITLE = "Myntra Profit Calculator For Vardhman Wool Store"
st.set_page_config(layout="wide", page_title=FULL_TITLE, page_icon="🛍️")

# --- Custom CSS for Compactness (Scroll Reduction) ---
# This CSS section ensures the app fits on one page in 100% zoom.
st.markdown("""
<style>
    /* Reduce padding around the entire app */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    /* Reduce padding/margin in markdown headers */
    h1, h2, h3, h4, h5, h6 {
        margin-top: 0.5rem;
        margin-bottom: 0.5rem;
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
</style>
""", unsafe_allow_html=True)

# --- CALCULATION LOGIC FUNCTIONS (No Change) ---

def calculate_gt_charges(sale_price):
    if sale_price <= 500:
        return 54.00
    elif sale_price <= 1000:
        return 94.00
    else:
        return 171.00

def get_commission_rate(customer_paid_amount):
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

def calculate_taxable_amount_value(customer_paid_amount):
    if customer_paid_amount >= 2500:
        tax_rate = 0.12 
        divisor = 1.12
    else:
        tax_rate = 0.05
        divisor = 1.05
    taxable_amount = customer_paid_amount / divisor
    return taxable_amount, tax_rate

def perform_calculations(mrp, discount, apply_royalty, product_cost):
    sale_price = mrp - discount
    if sale_price < 0:
        raise ValueError("Discount Amount cannot be greater than MRP.")
        
    gt_charge = calculate_gt_charges(sale_price)
    customer_paid_amount = sale_price - gt_charge
    
    royalty_fee = 0.0
    if apply_royalty == 'Yes':
        royalty_fee = customer_paid_amount * 0.10
        marketing_fee_rate = 0.05
    else:
        marketing_fee_rate = 0.04
        
    marketing_fee_base = customer_paid_amount * marketing_fee_rate
    
    commission_rate = get_commission_rate(customer_paid_amount)
    commission_amount_base = customer_paid_amount * commission_rate
    commission_tax = commission_amount_base * 0.18
    final_commission = commission_amount_base + commission_tax
    
    taxable_amount_value, invoice_tax_rate = calculate_taxable_amount_value(customer_paid_amount)
    
    tax_amount = customer_paid_amount - taxable_amount_value
    tcs = tax_amount * 0.10  
    tds = taxable_amount_value * 0.001 
    
    settled_amount = customer_paid_amount - final_commission - royalty_fee - marketing_fee_base - tds - tcs
    
    net_profit = settled_amount - product_cost
    
    return (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
            marketing_fee_base, marketing_fee_rate, final_commission, 
            commission_rate, settled_amount, taxable_amount_value, 
            net_profit, tds, tcs, invoice_tax_rate)


# --- 2. STREAMLIT APP STRUCTURE ---

# Title is set here
st.title("🛍️ " + FULL_TITLE)
st.markdown("###### **1. Input and Configuration**")

# --- CONFIGURATION BAR (Sidebar) ---
st.sidebar.header("Settings")

# Royalty Fee Radio Button 
apply_royalty = st.sidebar.radio(
    "Royalty Fee (10% of CPA)?",
    ('Yes', 'No'),
    index=0, 
    horizontal=True,
    label_visibility="visible"
)

# Product Cost Input
product_cost = st.sidebar.number_input(
    "Product Cost (₹)",
    min_value=0.0,
    value=0.0,
    step=10.0,
    label_visibility="visible"
)

# Margin Target Input in Rupees
product_margin_target_rs = st.sidebar.number_input(
    "Target Margin (₹)",
    min_value=0.0,
    value=100.0,
    step=10.0,
    label_visibility="visible"
)

st.sidebar.divider() 

# --- INPUT FIELDS (Main Body) ---
col_mrp_in, col_discount_in = st.columns(2)

new_mrp = col_mrp_in.number_input(
    "Product MRP (₹)",
    min_value=1.0,
    value=1500.0,
    step=100.0,
    key="new_mrp",
    label_visibility="visible"
)

new_discount = col_discount_in.number_input(
    "Discount Amt (₹)",
    min_value=0.0,
    max_value=new_mrp,
    value=0.0,
    step=10.0,
    key="new_discount",
    label_visibility="visible"
)

st.divider() 

if new_mrp > 0:
    try:
        # Perform calculations
        (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
         marketing_fee_base, marketing_fee_rate, final_commission, 
         commission_rate, settled_amount, taxable_amount_value, 
         net_profit, tds, tcs, invoice_tax_rate) = perform_calculations(new_mrp, new_discount, apply_royalty, product_cost)
         
        # Calculate Margin Difference for display
        target_profit = product_margin_target_rs
        delta_value = net_profit - target_profit
        
        current_margin_percent = (net_profit / product_cost) * 100 if product_cost > 0 else 0.0

        delta_label = f"vs Target: ₹ {delta_value:,.2f}"
        delta_color = "normal" if net_profit >= target_profit else "inverse"
            
        # --- DISPLAY RESULTS ---
        
        # Section 2: Sales and Revenue (3 columns)
        st.markdown("###### **2. Sales and Revenue**")
        col_sale, col_gt, col_customer = st.columns(3)
        
        col_sale.metric(label="Sale Price", value=f"₹ {sale_price:,.2f}")
        col_gt.metric(label="GT Charge", value=f"₹ {gt_charge:,.2f}")
        col_customer.metric(label="**Customer Paid Amt (CPA)**", value=f"₹ {customer_paid_amount:,.2f}")

        st.divider() # <<< --- NEW LINE ADDED HERE --- >>>
        
        # Section 3: Deductions (Charges) - 3 COLUMNS, 2 ROWS
        st.markdown("###### **3. Deductions (Charges)**")
        
        # Row 1 (3 columns): Commission, Marketing, Royalty
        col1_r1, col2_r1, col3_r1 = st.columns(3)
        
        col1_r1.metric(
            label=f"Commission ({commission_rate*100:.0f}%+Tax)",
            value=f"₹ {final_commission:,.2f}",
        )
        col2_r1.metric(
            label=f"Marketing Fee ({marketing_fee_rate*100:.0f}%)",
            value=f"₹ {marketing_fee_base:,.2f}",
        )
        col3_r1.metric(
            label=f"Royalty Fee ({'10%' if apply_royalty=='Yes' else '0%'})",
            value=f"₹ {royalty_fee:,.2f}",
        )
        
        # Row 2 (3 columns): Taxable Value, TDS, TCS
        col1_r2, col2_r2, col3_r2 = st.columns(3)

        col1_r2.metric(
            label=f"Taxable Value (GST @ {invoice_tax_rate*100:.0f}%)",
            value=f"₹ {taxable_amount_value:,.2f}",
        )
        col2_r2.metric(
            label="TDS (0.1%)",
            value=f"₹ {tds:,.2f}"
        )
        col3_r2.metric(
            label="TCS (10% on Tax Amt)",
            value=f"₹ {tcs:,.2f}"
        )

        st.divider() 
        
        # Section 4: Final Settlement and Profit
        st.markdown("###### **4. Final Payout and Profit**")

        col_settled, col_net_profit = st.columns(2)

        col_settled.metric(
            label="**FINAL SETTLED AMOUNT**",
            value=f"₹ {settled_amount:,.2f}",
            delta_color="off"
        )
        
        col_net_profit.metric(
            label=f"**NET PROFIT ({current_margin_percent:,.2f}% Margin)**",
            value=f"₹ {net_profit:,.2f}",
            delta=delta_label,
            delta_color=delta_color
        )

    except ValueError as e:
        st.error(str(e))
else:
    st.info("Please enter a valid MRP to start the calculation.")

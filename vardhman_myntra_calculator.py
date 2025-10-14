import pandas as pd
import streamlit as st
import numpy as np

# --- 1. CONFIGURATION AND DATA SETUP ---
st.set_page_config(layout="wide", page_title="Myntra Calculator for Vardhman Wool Store", page_icon="🛍️")

# --- CALCULATION LOGIC FUNCTIONS ---

def calculate_gt_charges(sale_price):
    """Calculates GT Charge based on Sale Price tiers."""
    if sale_price <= 500:
        return 54.00
    elif sale_price <= 1000:
        return 94.00
    else:
        return 171.00

def get_commission_rate(customer_paid_amount):
    """Determines the commission rate based on Customer Paid Amount."""
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
    """Calculates Taxable Value and Invoice Tax Rate (GST)."""
    if customer_paid_amount >= 2500:
        tax_rate = 0.12 
        divisor = 1.12
    else:
        tax_rate = 0.05
        divisor = 1.05
        
    taxable_amount = customer_paid_amount / divisor
    
    return taxable_amount, tax_rate

def perform_calculations(mrp, discount, apply_royalty, product_cost):
    """Performs all sequential calculations for profit analysis, including Marketing Fee."""
    sale_price = mrp - discount
    if sale_price < 0:
        raise ValueError("Discount Amount cannot be greater than MRP.")
        
    gt_charge = calculate_gt_charges(sale_price)
    customer_paid_amount = sale_price - gt_charge
    
    # 1. Royalty Fee Logic & Marketing Fee Rate
    royalty_fee = 0.0
    if apply_royalty == 'Yes':
        royalty_fee = customer_paid_amount * 0.10
        marketing_fee_rate = 0.05  # 5% Marketing Fee if Royalty is ON
    else:
        marketing_fee_rate = 0.04  # 4% Marketing Fee if Royalty is OFF
        
    # 2. Marketing Fee Calculation
    marketing_fee_base = customer_paid_amount * marketing_fee_rate
    
    # 3. Commission (Rate determined dynamically, then 18% tax added)
    commission_rate = get_commission_rate(customer_paid_amount)
    commission_amount_base = customer_paid_amount * commission_rate
    commission_tax = commission_amount_base * 0.18
    final_commission = commission_amount_base + commission_tax
    
    # 4. Taxable Amount Value (for GST)
    taxable_amount_value, invoice_tax_rate = calculate_taxable_amount_value(customer_paid_amount)
    
    # 5. TDS and TCS 
    tax_amount = customer_paid_amount - taxable_amount_value
    tcs = tax_amount * 0.10  
    tds = taxable_amount_value * 0.001 
    
    # 6. Final Payment (Settled Amount)
    settled_amount = customer_paid_amount - final_commission - royalty_fee - marketing_fee_base - tds - tcs
    
    # 7. Net Profit
    net_profit = settled_amount - product_cost
    
    return (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
            marketing_fee_base, marketing_fee_rate, final_commission, 
            commission_rate, settled_amount, taxable_amount_value, 
            net_profit, tds, tcs, invoice_tax_rate)


# --- 2. STREAMLIT APP STRUCTURE ---

st.title("🛍️ Myntra Calculator for **Vardhman Wool Store**")
st.header("Profitability Simulation (Manual Input)")
st.info("Simply enter the **MRP** and the desired **Discount Amount** to calculate the profit.")

# --- CONFIGURATION BAR ---
st.sidebar.header("Calculation Settings")

# Royalty Fee Radio Button 
apply_royalty = st.sidebar.radio(
    "Apply Royalty Fee (10% of CPA)?",
    ('Yes', 'No'),
    index=0, 
    horizontal=True
)

# Product Cost Input
product_cost = st.sidebar.number_input(
    "Enter Product Cost (₹)",
    min_value=0.0,
    value=0.0,
    step=10.0,
    help="This cost is deducted at the end to calculate Net Profit."
)

# NEW: Margin Target Input in Rupees
product_margin_target_rs = st.sidebar.number_input(
    "Desired Margin Target (₹)",
    min_value=0.0,
    value=100.0,  # Default value set to 100 Rs
    step=10.0,
    help="Enter your target profit amount in Rupees."
)

st.sidebar.markdown("---")


# --- INPUT FIELDS ---

col_mrp_in, col_discount_in = st.columns(2)

new_mrp = col_mrp_in.number_input(
    "1. Enter Product **MRP** (₹)",
    min_value=1.0,
    value=1500.0,
    step=100.0,
    key="new_mrp"
)

new_discount = col_discount_in.number_input(
    "2. Enter Discount **Amount** (₹)",
    min_value=0.0,
    max_value=new_mrp,
    value=0.0,
    step=10.0,
    key="new_discount"
)

st.markdown("---")

if new_mrp > 0:
    try:
        # Perform calculations
        (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
         marketing_fee_base, marketing_fee_rate, final_commission, 
         commission_rate, settled_amount, taxable_amount_value, 
         net_profit, tds, tcs, invoice_tax_rate) = perform_calculations(new_mrp, new_discount, apply_royalty, product_cost)
         
        # Calculate Margin Difference for display using the new Rupee target
        target_profit = product_margin_target_rs
        delta_value = net_profit - target_profit
        
        # Determine current margin % for display
        current_margin_percent = (net_profit / product_cost) * 100 if product_cost > 0 else 0.0

        # Set Delta appearance
        delta_label = f"vs Target: ₹ {delta_value:,.2f}"
        delta_color = "normal" if net_profit >= target_profit else "inverse"
            
        # --- DISPLAY RESULTS ---
        st.subheader("3. Calculated Financial Metrics")
        
        col_sale, col_gt, col_customer = st.columns(3)
        col_sale.metric(label="Sale Price (MRP - Discount)", value=f"₹ {sale_price:,.2f}")
        col_gt.metric(label="GT Charge", value=f"₹ {gt_charge:,.2f}")
        col_customer.metric(label="Customer Paid Amount (CPA)", value=f"₹ {customer_paid_amount:,.2f}")

        st.markdown("<br>", unsafe_allow_html=True) 
        
        # Display Charges in 4 Columns
        col_comm, col_royalty, col_marketing, col_taxable = st.columns(4)
        
        col_comm.metric(
            label=f"Commission ({commission_rate*100:.0f}%, Incl. 18% Tax)",
            value=f"₹ {final_commission:,.2f}",
        )
        col_royalty.metric(
            label=f"Royalty Fee ({apply_royalty})",
            value=f"₹ {royalty_fee:,.2f}",
        )
        col_marketing.metric(
            label=f"Marketing Fee ({marketing_fee_rate*100:.0f}% of CPA)",
            value=f"₹ {marketing_fee_base:,.2f}",
        )
        col_taxable.metric(
            label=f"Taxable Value (GST @ {invoice_tax_rate*100:.0f}%)",
            value=f"₹ {taxable_amount_value:,.2f}",
        )
        
        st.markdown("<br>", unsafe_allow_html=True) 
        
        col_tds, col_tcs, col_placeholder1, col_placeholder2 = st.columns(4)
        
        col_tds.metric(
            label="TDS (0.1% on Taxable Value)",
            value=f"₹ {tds:,.2f}"
        )
        
        col_tcs.metric(
            label="TCS (10% on Tax Amount)",
            value=f"₹ {tcs:,.2f}"
        )
        
        st.markdown("---")

        col_settled, col_net_profit = st.columns(2)

        col_settled.metric(
            label="FINAL SETTLED AMOUNT (Payout after ALL Deductions)",
            value=f"₹ {settled_amount:,.2f}",
            delta_color="off"
        )
        
        col_net_profit.metric(
            label=f"**NET PROFIT ({current_margin_percent:,.2f}% Margin on Cost)**",
            value=f"₹ {net_profit:,.2f}",
            delta=delta_label,
            delta_color=delta_color
        )

    except ValueError as e:
        st.error(str(e))
else:
    st.info("Please enter a valid MRP to start the calculation.")

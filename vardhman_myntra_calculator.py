import streamlit as st
import numpy as np

# --- 1. CONFIGURATION ---
st.set_page_config(layout="wide", page_title="Myntra Payout Calculator (Manual)", page_icon="💰")

# --- 2. CALCULATION LOGIC FUNCTIONS ---

def calculate_gt_charges(sale_price):
    """Calculates GT Charge based on Sale Price tiers (0-500: 54, 500-1000: 94, 1000+: 171)."""
    if sale_price <= 500:
        return 54.00
    elif sale_price <= 1000:
        return 94.00
    else:
        return 171.00

def get_commission_rate(customer_paid_amount):
    """Determines the commission rate based on Customer Paid Amount tiers."""
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
    """Calculates the Taxable Amount (Invoice Tax) tax value (5% for <=2500, 12% for >2500)."""
    if customer_paid_amount >= 2500:
        tax_rate = 0.12
    else:
        tax_rate = 0.05
    taxable_value = customer_paid_amount * tax_rate
    return taxable_value

# --- MAIN CALCULATION FUNCTION ---
def perform_calculations(mrp, discount):
    """Performs all sequential calculations for a given MRP and Discount."""
    
    sale_price = mrp - discount
    if sale_price < 0:
        raise ValueError("Discount Amount cannot be greater than MRP.")
        
    gt_charge = calculate_gt_charges(sale_price)
    customer_paid_amount = sale_price - gt_charge
    
    # Royalty Fee (10% of Customer Paid Amount)
    royalty_fee = customer_paid_amount * 0.10
    
    # Commission (Base + 18% Tax)
    commission_rate = get_commission_rate(customer_paid_amount)
    commission_amount_base = customer_paid_amount * commission_rate
    commission_tax = commission_amount_base * 0.18
    final_commission = commission_amount_base + commission_tax
    
    # Taxable Amount Value
    taxable_amount_value = calculate_taxable_amount_value(customer_paid_amount)
    
    # Final Payment
    settled_amount_before_royalty = customer_paid_amount - final_commission
    payment_after_royalty = settled_amount_before_royalty - royalty_fee
    
    return (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
            final_commission, commission_rate, payment_after_royalty, 
            taxable_amount_value)


# --- 3. STREAMLIT APP STRUCTURE (DASHBOARD) ---

st.title("💸 Myntra Payout Calculator (Manual)")
st.caption("Enter MRP and Discount to see the final settled amount.")

st.markdown("---")

st.subheader("1. Input Values")

# Input fields for MRP and Discount (side-by-side)
col_mrp_in, col_discount_in = st.columns(2)

new_mrp = col_mrp_in.number_input(
    "Enter Product **MRP** (₹)",
    min_value=1.0,
    value=1500.0,
    step=100.0,
    key="new_mrp"
)

new_discount = col_discount_in.number_input(
    "Enter Discount **Amount** (₹)",
    min_value=0.0,
    max_value=new_mrp, # This prevents the sale price from being negative
    value=0.0,
    step=10.0,
    key="new_discount"
)

st.markdown("---")

if new_mrp > 0:
    try:
        # Perform calculations
        (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
         final_commission, commission_rate, payment_after_royalty, 
         taxable_amount_value) = perform_calculations(new_mrp, new_discount)
         
        # --- 2. Calculated Metrics (As per sample image) ---
        st.subheader("2. Calculated Financial Metrics")
        
        # Row 1: Sale Price, GT Charge, Customer Paid Amount
        col_sale, col_gt, col_customer = st.columns(3)
        col_sale.metric(label="Sale Price (MRP - Discount)", value=f"₹ {sale_price:,.2f}")
        col_gt.metric(label="GT Charge", value=f"₹ {gt_charge:,.2f}")
        col_customer.metric(label="Customer Paid Amount", value=f"₹ {customer_paid_amount:,.2f}")

        st.markdown("<br>", unsafe_allow_html=True) # Adding some space

        # Row 2: Commission, Royalty, Taxable Value
        col_commission, col_royalty, col_taxable = st.columns(3)
        
        col_commission.metric(
            label="Total Commission (Incl. 18% Tax)",
            value=f"₹ {final_commission:,.2f}",
            delta=f"Base Rate: {commission_rate*100:.0f}%"
        )
        col_royalty.metric(
            label="Royalty Fee (10% of C.P.A)",
            value=f"₹ {royalty_fee:,.2f}",
        )
        col_taxable.metric(
            label="Taxable Value (Invoice Tax)",
            value=f"₹ {taxable_amount_value:,.2f}",
        )
        
        st.markdown("---")

        # Row 3: Final Payout (Large Metric)
        st.metric(
            label="**FINAL PAYMENT (NET PAYOUT)**",
            value=f"₹ {payment_after_royalty:,.2f}",
            delta_color="normal"
        )


    except ValueError as e:
        # This handles the error if discount somehow exceeds the MRP
        st.error(str(e))

import pandas as pd
import streamlit as st
import numpy as np

# --- 1. CONFIGURATION AND DATA LOADING ---
st.set_page_config(layout="wide", page_title="Myntra Calculator for Vardhman Wool Store", page_icon="🛍️")

# Ensure your CSV file is in the same folder as this script
FILE_NAME = "Calculator For Gemini.xlsx - Working.csv" 

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
    """Calculates the Taxable Amount (Invoice Tax) tax value."""
    if customer_paid_amount >= 2500:
        tax_rate = 0.12
    else:
        tax_rate = 0.05
    taxable_value = customer_paid_amount * tax_rate
    return taxable_value

# --- MAIN CALCULATION FUNCTION (FIXED against TypeError) ---
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


# --- DATA LOADING FOR EXISTING LISTINGS MODE ---
@st.cache_data
def load_data(file_name):
    """Loads and cleans the Myntra data for Existing Listings."""
    try:
        df = pd.read_csv(file_name)
        df.columns = df.columns.str.strip().str.lower()
        df['mrp'] = pd.to_numeric(df['mrp'], errors='coerce')
        df.dropna(subset=['seller sku code', 'mrp'], inplace=True)
        df = df.drop_duplicates(subset=['seller sku code'], keep='first')
        return df
    except FileNotFoundError:
        st.error(f"Error: The data file '{file_name}' was not found. Please ensure the file is in the correct directory.")
        st.stop()
    except Exception as e:
        st.error(f"An unexpected error occurred during data loading: {e}")
        st.stop()

# --- 3. STREAMLIT APP STRUCTURE ---

st.title("🛍️ Myntra Calculator for **Vardhman Wool Store**")

# Top-level selection: Exiting Listings vs. New Listings
mode = st.selectbox(
    "Select Calculation Mode:",
    ("Existing Listings (Search SKU)", "New Listings (Manual Input)"),
    index=0 
)

st.markdown("---")

# --- MODE 1: EXISTING LISTINGS (SKU Select with Search Box) ---
if mode == "Existing Listings (Search SKU)":
    
    df = load_data(FILE_NAME) 
    st.header("Analyze Existing Product Profitability")

    unique_skus = sorted(df['seller sku code'].unique().tolist())
    
    # The required SKU search box
    selected_sku = st.selectbox(
        "**1. Search & Select SKU:** (Type to filter list)",
        unique_skus
    )

    if selected_sku:
        sku_data = df[df['seller sku code'] == selected_sku].iloc[0]
        
        st.subheader("2. Input Values")
        
        mrp_from_data = sku_data['mrp']
        
        col_mrp, col_discount = st.columns(2)
        
        col_mrp.metric(label="Product MRP (from data)", value=f"₹ {mrp_from_data:,.2f}")
        
        discount = col_discount.number_input(
            "Enter Discount **Amount** (₹)",
            min_value=0.0,
            max_value=mrp_from_data,
            value=0.0,
            step=10.0,
            key="existing_discount"
        )
        
        try:
            # Perform calculations
            (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
             final_commission, commission_rate, payment_after_royalty, 
             taxable_amount_value) = perform_calculations(mrp_from_data, discount)
             
            # Display Results
            st.markdown("---")
            st.subheader("3. Calculated Financial Metrics")
            
            # Row 1
            col_sale, col_gt, col_customer = st.columns(3)
            col_sale.metric(label="Sale Price", value=f"₹ {sale_price:,.2f}")
            col_gt.metric(label="GT Charge", value=f"₹ {gt_charge:,.2f}")
            col_customer.metric(label="Customer Paid Amount", value=f"₹ {customer_paid_amount:,.2f}")

            st.markdown("<br>", unsafe_allow_html=True) 

            # Row 2
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

            # Final Payout
            st.metric(
                label="**FINAL PAYMENT (NET PAYOUT)**",
                value=f"₹ {payment_after_royalty:,.2f}",
                delta_color="normal"
            )
        
        except ValueError as e:
            st.error(str(e))


    else:
        st.info("Please select a SKU to begin the calculation.")


# --- MODE 2: NEW LISTINGS (Manual Entry) ---
elif mode == "New Listings (Manual Input)":
    st.header("New Listing Profitability Simulation")
    st.info("Enter your desired MRP and Discount to calculate the final payout.")

    # Input fields for MRP and Discount
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
        max_value=new_mrp,
        value=0.0,
        step=10.0,
        key="new_discount"
    )

    if new_mrp > 0:
        try:
            # Perform calculations
            (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
             final_commission, commission_rate, payment_after_royalty, 
             taxable_amount_value) = perform_calculations(new_mrp, new_discount)
             
            # Display Results
            st.markdown("---")
            st.subheader("2. Calculated Financial Metrics")
            
            # Row 1
            col_sale, col_gt, col_customer = st.columns(3)
            col_sale.metric(label="Sale Price (MRP - Discount)", value=f"₹ {sale_price:,.2f}")
            col_gt.metric(label="GT Charge", value=f"₹ {gt_charge:,.2f}")
            col_customer.metric(label="Customer Paid Amount", value=f"₹ {customer_paid_amount:,.2f}")

            st.markdown("<br>", unsafe_allow_html=True) 

            # Row 2
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

            # Final Payout
            st.metric(
                label="**FINAL PAYMENT (NET PAYOUT)**",
                value=f"₹ {payment_after_royalty:,.2f}",
                delta_color="normal"
            )

        except ValueError as e:
            st.error(str(e))

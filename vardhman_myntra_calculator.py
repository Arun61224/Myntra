import pandas as pd
import streamlit as st
import numpy as np

# --- 1. CONFIGURATION AND DATA LOADING ---
st.set_page_config(layout="wide", page_title="Myntra Calculator for Vardhman Wool Store", page_icon="🛍️")

# --- CALCULATION LOGIC FUNCTIONS (No Change) ---

def calculate_gt_charges(sale_price):
    # GT Charge logic
    if sale_price <= 500:
        return 54.00
    elif sale_price <= 1000:
        return 94.00
    else:
        return 171.00

def get_commission_rate(customer_paid_amount):
    # Commission rate logic
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
    # Taxable value logic
    if customer_paid_amount >= 2500:
        tax_rate = 0.12 
        divisor = 1.12
    else:
        tax_rate = 0.05
        divisor = 1.05
        
    taxable_amount = customer_paid_amount / divisor
    
    return taxable_amount, tax_rate


# --- MAIN CALCULATION FUNCTION (No Change) ---
def perform_calculations(mrp, discount, apply_royalty, product_cost):
    # Performs all calculations
    sale_price = mrp - discount
    if sale_price < 0:
        raise ValueError("Discount Amount cannot be greater than MRP.")
        
    gt_charge = calculate_gt_charges(sale_price)
    customer_paid_amount = sale_price - gt_charge
    
    # 1. Royalty Fee Logic
    royalty_fee = 0.0
    if apply_royalty == 'Yes':
        royalty_fee = customer_paid_amount * 0.10
    
    # 2. Commission 
    commission_rate = get_commission_rate(customer_paid_amount)
    commission_amount_base = customer_paid_amount * commission_rate
    commission_tax = commission_amount_base * 0.18
    final_commission = commission_amount_base + commission_tax
    
    # 3. Taxable Amount Value
    taxable_amount_value, invoice_tax_rate = calculate_taxable_amount_value(customer_paid_amount)
    
    # 4. TDS and TCS 
    tax_amount = customer_paid_amount - taxable_amount_value
    tcs = tax_amount * 0.10  
    tds = taxable_amount_value * 0.001 
    
    # 5. Final Payment (Settled Amount)
    settled_amount = customer_paid_amount - final_commission - royalty_fee - tds - tcs
    
    # 6. Net Profit
    net_profit = settled_amount - product_cost
    
    return (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
            final_commission, commission_rate, settled_amount, 
            taxable_amount_value, net_profit, tds, tcs, invoice_tax_rate)


# --- DATA LOADING (CSV File - Reads UPLOADED file) ---
@st.cache_data
def load_data(uploaded_file):
    """Loads and cleans the Myntra data from the uploaded CSV file."""
    if uploaded_file is None:
        return None
        
    try:
        df = pd.read_csv(uploaded_file)
        
        # FIX 1: Check if DataFrame is empty right after reading
        if df.empty:
            st.error("Data Error: The uploaded file is empty or contains no data rows.")
            return None
        
        # Clean column names (strip whitespace and convert to lower)
        df.columns = df.columns.str.strip().str.lower()
        
        required_columns = ['seller sku code', 'mrp']
        
        # FIX 2: Check for required columns and provide debug info if missing
        if not all(col in df.columns for col in required_columns):
            st.error("Data Error: Required columns 'seller sku code' or 'mrp' are missing after cleaning.")
            st.warning(f"**Available Column Names (All):** {df.columns.tolist()}")
            st.warning("Please ensure the column names are exactly 'mrp' and 'seller sku code' (case-insensitive in the original file).")
            return None
            
        df['mrp'] = pd.to_numeric(df['mrp'], errors='coerce')
        df.dropna(subset=required_columns, inplace=True)
        df = df.drop_duplicates(subset=['seller sku code'], keep='first')
        
        return df
        
    except pd.errors.EmptyDataError:
        st.error("Data Error: The uploaded file is empty.")
        return None
    except Exception as e:
        # Catch other errors during file reading
        st.error(f"An unexpected error occurred during file processing: {e}")
        st.warning("Please verify that the file is saved correctly as a **CSV** file.")
        return None


# --- 2. STREAMLIT APP STRUCTURE ---

st.title("🛍️ Myntra Calculator for **Vardhman Wool Store**")

# --- CONFIGURATION BAR (Includes File Uploader) ---
st.sidebar.header("Data Upload")

# FILE UPLOADER
uploaded_file = st.sidebar.file_uploader(
    "Upload Myntra Data CSV File", 
    type=["csv"]
)

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

st.sidebar.markdown("---")

# Top-level selection: Exiting Listings vs. New Listings
mode = st.selectbox(
    "Select Calculation Mode:",
    ("Existing Listings (Search SKU)", "New Listings (Manual Input)"),
    index=0 
)

st.markdown("---")


# --- MODE 1: EXISTING LISTINGS (SKU Select with Search Box) ---
if mode == "Existing Listings (Search SKU)":
    
    # CHECK IF FILE IS UPLOADED
    if uploaded_file is None:
        st.info("⚠️ Please upload your data file using the **'Upload Myntra Data CSV File'** option in the sidebar to use Existing Listings mode.")
        st.stop()
        
    # Load data - load_data will return None if an error occurs
    df = load_data(uploaded_file)
    
    if df is None:
        st.stop() # Stop execution if data loading failed
        
    st.header("Analyze Existing Product Profitability")

    # Loading ALL unique SKUs from the uploaded CSV
    unique_skus = sorted(df['seller sku code'].unique().tolist())
    
    if not unique_skus:
        st.error("No valid SKUs found in the data file to display.")
        st.stop()

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
             final_commission, commission_rate, settled_amount, 
             taxable_amount_value, net_profit, tds, tcs, invoice_tax_rate) = perform_calculations(mrp_from_data, discount, apply_royalty, product_cost)
             
            # Display Results
            st.markdown("---")
            st.subheader("3. Calculated Financial Metrics")
            
            # Row 1: Sale Price, GT Charge, Customer Paid Amount
            col_sale, col_gt, col_customer = st.columns(3)
            col_sale.metric(label="Sale Price", value=f"₹ {sale_price:,.2f}")
            col_gt.metric(label="GT Charge", value=f"₹ {gt_charge:,.2f}")
            col_customer.metric(label="Customer Paid Amount", value=f"₹ {customer_paid_amount:,.2f}")

            st.markdown("<br>", unsafe_allow_html=True) 

            # Row 2: Commission, Royalty, Taxable Value
            col_commission, col_royalty, col_taxable = st.columns(3)
            
            col_commission.metric(
                label="Total Commission (Incl. 18% Tax)",
                value=f"₹ {final_commission:,.2f}",
            )
            col_royalty.metric(
                label=f"Royalty Fee ({apply_royalty})",
                value=f"₹ {royalty_fee:,.2f}",
            )
            col_taxable.metric(
                label=f"Taxable Value (GST @ {invoice_tax_rate*100:.0f}%)",
                value=f"₹ {taxable_amount_value:,.2f}",
            )
            
            st.markdown("<br>", unsafe_allow_html=True) 
            
            # Row 3: TDS and TCS
            col_tds, col_tcs, col_placeholder = st.columns(3)
            
            col_tds.metric(
                label="TDS (Taxable Value * 0.1%)",
                value=f"₹ {tds:,.2f}"
            )
            
            col_tcs.metric(
                label="TCS (Tax Amount * 10%)",
                value=f"₹ {tcs:,.2f}"
            )
            
            st.markdown("---")

            # Final Payout & Net Profit 
            col_settled, col_net_profit = st.columns(2)

            col_settled.metric(
                label="FINAL SETTLED AMOUNT (Payout after TDS/TCS)",
                value=f"₹ {settled_amount:,.2f}",
                delta_color="off"
            )
            
            col_net_profit.metric(
                label="**NET PROFIT (After Product Cost)**",
                value=f"₹ {net_profit:,.2f}",
                delta=-product_cost,
                delta_color="inverse"
            )
        
        except ValueError as e:
            st.error(str(e))
        except KeyError as e:
            st.error(f"Calculation Error: Column not found: {e}. Please check the column name in your data.")


    else:
        st.info("Please select a SKU to begin the calculation.")


# --- MODE 2: NEW LISTINGS (Manual Entry) (No Change) ---
elif mode == "New Listings (Manual Input)":
    st.header("New Listing Profitability Simulation")
    st.info("Enter your desired MRP and Discount to calculate the net profit.")

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
             final_commission, commission_rate, settled_amount, 
             taxable_amount_value, net_profit, tds, tcs, invoice_tax_rate) = perform_calculations(new_mrp, new_discount, apply_royalty, product_cost)
             
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
            )
            col_royalty.metric(
                label=f"Royalty Fee ({apply_royalty})",
                value=f"₹ {royalty_fee:,.2f}",
            )
            col_taxable.metric(
                label=f"Taxable Value (GST @ {invoice_tax_rate*100:.0f}%)",
                value=f"₹ {taxable_amount_value:,.2f}",
            )
            
            st.markdown("<br>", unsafe_allow_html=True) 
            
            # Row 3: TDS and TCS
            col_tds, col_tcs, col_placeholder = st.columns(3)
            
            col_tds.metric(
                label="TDS (Taxable Value * 0.1%)",
                value=f"₹ {tds:,.2f}"
            )
            
            col_tcs.metric(
                label="TCS (Tax Amount * 10%)",
                value=f"₹ {tcs:,.2f}"
            )
            
            st.markdown("---")

            # Final Payout & Net Profit
            col_settled, col_net_profit = st.columns(2)

            col_settled.metric(
                label="FINAL SETTLED AMOUNT (Payout after TDS/TCS)",
                value=f"₹ {settled_amount:,.2f}",
                delta_color="off"
            )
            
            col_net_profit.metric(
                label="**NET PROFIT (After Product Cost)**",
                value=f"₹ {net_profit:,.2f}",
                delta=-product_cost,
                delta_color="inverse"
            )

        except ValueError as e:
            st.error(str(e))

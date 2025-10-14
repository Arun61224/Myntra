import pandas as pd
import streamlit as st
import numpy as np

# --- 1. CONFIGURATION AND DATA SETUP ---
st.set_page_config(layout="wide", page_title="Myntra Calculator for Vardhman Wool Store", page_icon="🛍️")

# 🚀 GITHUB RAW URL MAPPED HERE 🚀
SKU_FILE_NAME = "https://raw.githubusercontent.com/Arun61224/Myntra/refs/heads/main/sku.txt" 

# Flexible Column Names (to handle variations like 'MRP', 'mrp', 'Product MRP', etc.)
MRP_COLUMNS = ['mrp', 'price', 'product mrp', 'list price'] 
SKU_COLUMNS = ['seller sku code', 'sku', 'sku code', 'seller sku'] 
DISCOUNT_COLUMNS = ['discount', 'discount amount', 'sale discount']

# --- CALCULATION LOGIC FUNCTIONS (No Change) ---

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
    """Performs all sequential calculations for profit analysis."""
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


# --- DATA LOADING (Loads File from GitHub URL) ---
@st.cache_data
def load_data(file_url):
    """Loads and cleans the Myntra data from the GitHub URL (assuming CSV structure)."""
    
    st.info(f"Attempting to load data from: **{file_url}**")
        
    try:
        # pd.read_csv can directly read from a URL
        df = pd.read_csv(file_url) 
        
        if df.empty:
            st.error("Data Error: The loaded file is empty or contains no data rows.")
            return None
        
        # Clean column names
        df.columns = df.columns.str.strip().str.lower()
        
        # --- FLEXIBLE COLUMN DETECTION ---
        mrp_col_name = next((col for col in MRP_COLUMNS if col in df.columns), None)
        sku_col_name = next((col for col in SKU_COLUMNS if col in df.columns), None)
        discount_col_name = next((col for col in DISCOUNT_COLUMNS if col in df.columns), None)
        
        required = {'MRP': mrp_col_name, 'SKU': sku_col_name, 'Discount': discount_col_name}
        missing = [key for key, val in required.items() if val is None]
        
        if missing:
            st.error(f"Data Error: Could not find required columns in the GitHub file.")
            st.warning(f"Missing Columns: {', '.join(missing)}. Please check column names in your sku.txt (e.g., must contain 'mrp', 'sku code', 'discount').")
            return None
            
        # Rename columns to standard names
        df.rename(columns={mrp_col_name: 'mrp', sku_col_name: 'seller sku code', discount_col_name: 'discount'}, inplace=True)

        # Clean data and convert to numeric
        df['mrp'] = pd.to_numeric(df['mrp'], errors='coerce')
        df['discount'] = pd.to_numeric(df['discount'], errors='coerce').fillna(0) 
        
        df.dropna(subset=['mrp', 'seller sku code'], inplace=True)
        df = df.drop_duplicates(subset=['seller sku code'], keep='first')
        
        st.success(f"Data loaded successfully! Total {len(df)} unique SKUs found.")
        return df
        
    except Exception as e:
        st.error(f"An error occurred while loading data from GitHub: {e}")
        st.warning("Please ensure the GitHub file is **public** and the URL is the correct **RAW** link.")
        return None


# --- 2. STREAMLIT APP STRUCTURE ---

st.title("🛍️ Myntra Calculator for **Vardhman Wool Store**")

# Load data automatically at the start of the app
df = load_data(SKU_FILE_NAME)

# --- CONFIGURATION BAR ---
st.sidebar.header("Data Source")
if df is not None:
    st.sidebar.success("Data loaded from GitHub URL.")
else:
    st.sidebar.error("Data loading failed. Check error above.")

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


# --- MODE 1: EXISTING LISTINGS (Reads from GitHub Data) ---
if mode == "Existing Listings (Search SKU)":
    
    if df is None:
        st.error("Cannot proceed. Data loading from GitHub failed.")
        st.stop()
        
    st.header("Analyze Existing Product Profitability")

    unique_skus = sorted(df['seller sku code'].unique().tolist())
    
    if not unique_skus:
        st.error("No valid SKUs found in the loaded data to display.")
        st.stop()

    selected_sku = st.selectbox(
        "**1. Search & Select SKU:** (Type to filter list)",
        unique_skus
    )

    if selected_sku:
        sku_data = df[df['seller sku code'] == selected_sku].iloc[0]
        
        st.subheader("2. Input Values")
        
        mrp_from_data = sku_data['mrp']
        discount_from_data = sku_data['discount'] 

        col_mrp, col_discount = st.columns(2)
        
        col_mrp.metric(label="Product MRP (from data)", value=f"₹ {mrp_from_data:,.2f}")
        
        discount = col_discount.number_input(
            "Enter Discount **Amount** (₹) (Value from data loaded)",
            min_value=0.0,
            max_value=mrp_from_data,
            value=discount_from_data, 
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
            
            col_sale, col_gt, col_customer = st.columns(3)
            col_sale.metric(label="Sale Price", value=f"₹ {sale_price:,.2f}")
            col_gt.metric(label="GT Charge", value=f"₹ {gt_charge:,.2f}")
            col_customer.metric(label="Customer Paid Amount", value=f"₹ {customer_paid_amount:,.2f}")

            st.markdown("<br>", unsafe_allow_html=True) 

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
            (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
             final_commission, commission_rate, settled_amount, 
             taxable_amount_value, net_profit, tds, tcs, invoice_tax_rate) = perform_calculations(new_mrp, new_discount, apply_royalty, product_cost)
             
            st.markdown("---")
            st.subheader("2. Calculated Financial Metrics")
            
            col_sale, col_gt, col_customer = st.columns(3)
            col_sale.metric(label="Sale Price (MRP - Discount)", value=f"₹ {sale_price:,.2f}")
            col_gt.metric(label="GT Charge", value=f"₹ {gt_charge:,.2f}")
            col_customer.metric(label="Customer Paid Amount", value=f"₹ {customer_paid_amount:,.2f}")

            st.markdown("<br>", unsafe_allow_html=True) 

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


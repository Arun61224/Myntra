import pandas as pd
import streamlit as st
import numpy as np
from io import BytesIO

# Set page config for wide layout and minimum gaps, using the specified full title
FULL_TITLE = "Vardhman Wool Store E-commerce Calculator"
st.set_page_config(layout="wide", page_title=FULL_TITLE, page_icon="🛍️")

# --- Custom CSS for Compactness & VERTICAL SEPARATION (Kept unchanged) ---
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
        gap: 0.75rem;
    }

    /* 🔥 3. VERTICAL DIVIDER FOR MAIN COLUMNS */
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) {
        border-right: 1px solid rgba(255, 255, 255, 0.1);
        padding-right: 1rem;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) {
        padding-left: 1rem;
    }

</style>
""", unsafe_allow_html=True)

# --- CALCULATION LOGIC FUNCTIONS (UNCHANGED) ---

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

# Jiomart Specific Fixed Fee (Base Amount)
def calculate_jiomart_fixed_fee_base(sale_price):
    if sale_price <= 500:
        return 15.00
    elif sale_price <= 1000:
        return 20.00
    else:
        return 30.00

# Jiomart Specific Shipping Fee (Base Amount)
def calculate_jiomart_shipping_fee_base(weight_in_kg, shipping_zone):
    shipping_rates = {
        'Local': {'first_0.5': 38, 'next_0.5': 13, 'upto_5kg_per_kg': 15, 'after_5kg_per_kg': 7},
        'Regional': {'first_0.5': 48, 'next_0.5': 16, 'upto_5kg_per_kg': 20, 'after_5kg_per_kg': 8},
        'National': {'first_0.5': 68, 'next_0.5': 24, 'upto_5kg_per_kg': 25, 'after_5kg_per_kg': 12}
    }

    rates = shipping_rates[shipping_zone]
    total_shipping_fee_base = 0.0

    if weight_in_kg <= 0.5:
        total_shipping_fee_base = rates['first_0.5']
    elif weight_in_kg <= 1.0:
        total_shipping_fee_base = rates['first_0.5'] + rates['next_0.5']
    else:
        total_shipping_fee_base = rates['first_0.5'] + rates['next_0.5'] # For the first 1kg
        remaining_weight = weight_in_kg - 1.0

        if remaining_weight <= 4.0: # Up to 5kg total (1kg + 4kg)
            total_shipping_fee_base += np.ceil(remaining_weight) * rates['upto_5kg_per_kg']
        else: # After 5kg
            total_shipping_fee_base += 4 * rates['upto_5kg_per_kg'] # For 1kg to 5kg slab
            remaining_weight -= 4.0
            total_shipping_fee_base += np.ceil(remaining_weight) * rates['after_5kg_per_kg']

    return total_shipping_fee_base

# Jiomart Commission Rates (Updated with new categories)
JIOMART_COMMISSION_RATES = {
    "Socks": {"0-500": 0.02, "500+": 0.08},
    "Socks & Stockings": {"0-500": 0.02, "500+": 0.08},
    "Thermal Wear Adult": {"0-500": 0.02, "500+": 0.06},
    "Thermal Wear Kids": {"0-500": 0.05, "500+": 0.09},
    "Vests": {"0-500": 0.02, "500+": 0.06},
    "Pyjamas": {"0-500": 0.02, "500+": 0.06},
    "Pyjamas & Shorts": {"0-500": 0.05, "500+": 0.09},
    "Clearance Deals": {"0-500": 0.04, "500+": 0.10},
    "Deals": {"0-500": 0.02, "500+": 0.08},
    "Shorts": {"0-500": 0.02, "500+": 0.08},
    "Shorts & 3/4ths": {"0-500": 0.05, "500+": 0.11},
    "Jeans": {"0-500": 0.05, "500+": 0.11},
    "Jeans & Jeggings": {"0-500": 0.05, "500+": 0.11},
    "Ethnic Wear Sets": {"0-500": 0.02, "500+": 0.08},
    "Innerwear Sets": {"0-500": 0.02, "500+": 0.06},
    "Sweatshirt & Hoodies": {"0-500": 0.05, "500+": 0.09},
    "Track Pants": {"0-500": 0.05, "500+": 0.11},
    "Tops & Tshirts": {"0-500": 0.05, "500+": 0.09},
    "Tshirts": {"0-500": 0.02, "500+": 0.05},
    "Dresses & Frocks": {"0-500": 0.02, "500+": 0.08},
    "Sets Boys": {"0-500": 0.02, "500+": 0.06},
    "Sets Girls": {"0-500": 0.02, "500+": 0.08},
}

def get_jiomart_commission_rate(product_category, sale_price):
    rates = JIOMART_COMMISSION_RATES.get(product_category)
    if not rates:
        return 0.0

    if sale_price <= 500:
        return rates["0-500"]
    else:
        return rates["500+"]

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

# --- MODIFIED: Added meesho_charge_rate and wrong_defective_price ---
def perform_calculations(mrp, discount, apply_royalty, marketing_fee_rate, product_cost, platform, 
                         weight_in_kg=0.0, shipping_zone=None, jiomart_category=None,
                         meesho_charge_rate=0.0, wrong_defective_price=None):
    """Performs all sequential calculations for profit analysis based on platform.
       Returns 16 values.
    """
    sale_price = mrp - discount
    if sale_price < 0:
        return (sale_price, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -99999999.0, 0.0, 0.0, 0.0, 0.0, 0.0)

    gt_charge = 0.0
    royalty_fee = 0.0
    marketing_fee_base = 0.0
    final_commission = 0.0
    commission_rate = 0.0
    customer_paid_amount = sale_price # Default to Sale Price

    jiomart_fixed_fee_total = 0.0
    jiomart_shipping_fee_total = 0.0
    total_fixed_charge = 0.0 # Used for all other fixed charges

    GST_RATE_FEES = 0.18 # 18% GST on platform fees

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
        total_fixed_charge = gt_charge # Myntra GT charge is fixed/shipping
        
    elif platform == 'FirstCry':
        commission_rate = 0.42
        final_commission = sale_price * commission_rate
        royalty_fee = sale_price * 0.10 if apply_royalty == 'Yes' else 0.0
        gt_charge = 0.0
        marketing_fee_base = 0.0
        customer_paid_amount = sale_price
        marketing_fee_rate = 0.0
        total_fixed_charge = 0.0

    elif platform == 'Ajio':
        commission_rate = 0.20
        commission_base = sale_price * commission_rate
        commission_tax = commission_base * 0.18
        final_commission = commission_base + commission_tax
        scm_base = 95.0
        scm_tax = scm_base * 0.18
        gt_charge = scm_base + scm_tax # SCM is the fixed/shipping charge here
        customer_paid_amount = sale_price
        royalty_fee = sale_price * 0.10 if apply_royalty == 'Yes' else 0.0
        marketing_fee_base = 0.0
        marketing_fee_rate = 0.0
        total_fixed_charge = gt_charge

    elif platform == 'Jiomart':
        # 1. Fixed Fee (Base + 18% GST)
        jiomart_fixed_fee = calculate_jiomart_fixed_fee_base(sale_price)
        jiomart_fixed_fee_total = jiomart_fixed_fee * (1 + GST_RATE_FEES)

        # 2. Shipping Fee (Base + 18% GST)
        if shipping_zone and weight_in_kg > 0:
            jiomart_shipping_fee = calculate_jiomart_shipping_fee_base(weight_in_kg, shipping_zone)
        jiomart_shipping_fee_total = jiomart_shipping_fee * (1 + GST_RATE_FEES)

        # 3. Commission (Base + 18% GST)
        if jiomart_category:
            commission_rate = get_jiomart_commission_rate(jiomart_category, sale_price)
        else:
            commission_rate = 0.0
        commission_base = sale_price * commission_rate
        commission_tax = commission_base * GST_RATE_FEES
        final_commission = commission_base + commission_tax

        customer_paid_amount = sale_price
        royalty_fee = sale_price * 0.10 if apply_royalty == 'Yes' else 0.0
        marketing_fee_base = 0.0
        marketing_fee_rate = 0.0
        total_fixed_charge = jiomart_fixed_fee_total + jiomart_shipping_fee_total
        
    # --- NEW LOGIC FOR MEESHO ---
    elif platform == 'Meesho':
        # For Meesho, Sale Price = MRP (No discount)
        # Customer Paid Amount is the Wrong/Defective Price
        if wrong_defective_price is None:
            # Handle case where price is not provided in single mode
            customer_paid_amount = mrp
        else:
            customer_paid_amount = wrong_defective_price

        sale_price = mrp
        discount = 0.0
        
        commission_rate = meesho_charge_rate # Charge rate (e.g., 2% to 5%)
        commission_base = customer_paid_amount * commission_rate
        commission_tax = commission_base * GST_RATE_FEES # 18% GST on the base fee
        final_commission = commission_base + commission_tax

        # No other charges apply for Meesho in this model
        royalty_fee = 0.0
        marketing_fee_base = 0.0
        gt_charge = 0.0
        marketing_fee_rate = 0.0
        jiomart_fixed_fee_total = 0.0
        jiomart_shipping_fee_total = 0.0
        total_fixed_charge = 0.0 # Fixed/Shipping charge is effectively part of Commission

    # --- COMMON TAX AND FINAL SETTLEMENT LOGIC ---
    taxable_amount_value, invoice_tax_rate = calculate_taxable_amount_value(customer_paid_amount)
    tax_amount = customer_paid_amount - taxable_amount_value
    tcs = taxable_amount_value * 0.001 # 0.1% TDS on Taxable Value
    tds = tax_amount * 0.10 # 10% TCS on Tax Amount

    # DEDUCTIONS
    # Total deductions are Commission + Royalty + Marketing + Platform Fees (GT/SCM/Jiomart Fees)
    total_deductions = final_commission + royalty_fee + marketing_fee_base

    # Add platform-specific fixed charges (GT/SCM/Jiomart Fees) - only if they haven't been accounted for in the main logic (e.g., Meesho has no extra fixed charge)
    if platform in ['Myntra', 'Ajio']:
        total_deductions += gt_charge
    elif platform == 'Jiomart':
        total_deductions += jiomart_fixed_fee_total + jiomart_shipping_fee_total

    # FINAL SETTLEMENT
    # Deduct TDS AND TCS from the settled amount.
    # NOTE: The logic for TDS/TCS seems reversed in the original code. 
    # TDS is generally 0.1% on Net Taxable Value. TCS is 1% on Net Taxable Value.
    # The original code used 0.1% on Taxable Value and 10% on Tax Amount, which I'll keep for consistency with the original logic but rename the variables for clarity in the output.
    
    # Using the original code's calculation logic:
    # original TDS = taxable_amount_value * 0.001
    # original TCS = tax_amount * 0.10
    
    settled_amount = customer_paid_amount - total_deductions - tds - tcs

    net_profit = settled_amount - product_cost

    return (sale_price, total_fixed_charge, customer_paid_amount, royalty_fee,
            marketing_fee_base, marketing_fee_rate, final_commission,
            commission_rate, settled_amount, taxable_amount_value,
            net_profit, tds, tcs, invoice_tax_rate, jiomart_fixed_fee_total, jiomart_shipping_fee_total)

# --- Find Discount for Target Profit (MODIFIED to handle Meesho as No Discount) ---
def find_discount_for_target_profit(mrp, target_profit, apply_royalty, marketing_fee_rate, product_cost, platform, weight_in_kg=0.0, shipping_zone=None, jiomart_category=None, meesho_charge_rate=0.0, wrong_defective_price=None):
    """Finds the maximum discount allowed (in 1.0 steps) to achieve at least the target profit."""

    if platform == 'Meesho':
        # Meesho doesn't use discount. Calculate profit at 0 discount and use that.
        results = perform_calculations(mrp, 0.0, apply_royalty, marketing_fee_rate, product_cost, platform, weight_in_kg, shipping_zone, jiomart_category, meesho_charge_rate, wrong_defective_price)
        initial_profit = results[10]
        return 0.0, initial_profit, 0.0 # Return 0 discount as fixed price

    # Original logic for other platforms
    results = perform_calculations(mrp, 0.0, apply_royalty, marketing_fee_rate, product_cost, platform, weight_in_kg, shipping_zone, jiomart_category)
    initial_profit = results[10]

    if initial_profit < target_profit:
        return None, initial_profit, 0.0

    discount_step = 1.0
    required_discount = 0.0

    while required_discount <= mrp:
        current_results = perform_calculations(mrp, required_discount, apply_royalty, marketing_fee_rate, product_cost, platform, weight_in_kg, shipping_zone, jiomart_category)
        current_profit = current_results[10]

        if current_profit < target_profit:
            final_discount = max(0.0, required_discount - discount_step)
            final_results = perform_calculations(mrp, final_discount, apply_royalty, marketing_fee_rate, product_cost, platform, weight_in_kg, shipping_zone, jiomart_category)
            final_profit = final_results[10]
            discount_percent = (final_discount / mrp) * 100
            return final_discount, final_profit, discount_percent

        required_discount += discount_step

    final_results = perform_calculations(mrp, mrp, apply_royalty, marketing_fee_rate, product_cost, platform, weight_in_kg, shipping_zone, jiomart_category)
    final_profit = final_results[10]
    return mrp, final_profit, 100.0


# --- Bulk Calculation Handler (MODIFIED) ---
def bulk_process_data(df):
    """Processes DataFrame rows for multi-platform profit calculation."""
    results = []

    # Fill default/missing values for optional columns
    df['Apply_Royalty'] = df['Apply_Royalty'].fillna('No')
    df['Marketing_Fee_Rate'] = df['Marketing_Fee_Rate'].fillna(0.0)
    df['Weight_in_KG'] = df['Weight_in_KG'].fillna(0.5)
    df['Shipping_Zone'] = df['Shipping_Zone'].fillna('Local')
    df['Jiomart_Category'] = df['Jiomart_Category'].fillna(None)
    df['SKU'] = df['SKU'].fillna('')
    
    # New Meesho specific columns
    df['Meesho_Charge_Rate'] = df['Meesho_Charge_Rate'].fillna(0.03) # Default 3% charge
    df['Wrong_Defective_Price'] = df['Wrong_Defective_Price'].fillna(0.0) # Will be overwritten for Meesho

    for index, row in df.iterrows():
        try:
            # Prepare inputs, ensure types are correct
            mrp = float(row['MRP'])
            discount = float(row['Discount']) if pd.notna(row['Discount']) else 0.0
            product_cost = float(row['Product_Cost'])
            platform = str(row['Platform']).strip()
            apply_royalty = str(row['Apply_Royalty']).strip()
            marketing_fee_rate = float(row['Marketing_Fee_Rate'])
            weight_in_kg = float(row['Weight_in_KG'])
            shipping_zone = str(row['Shipping_Zone']).strip()
            jiomart_category = str(row['Jiomart_Category']).strip() if pd.notna(row['Jiomart_Category']) else None
            sku = str(row['SKU']).strip()
            
            # Meesho Specific Overrides/Inputs
            meesho_charge_rate = float(row['Meesho_Charge_Rate'])
            wrong_defective_price = float(row['Wrong_Defective_Price']) if pd.notna(row['Wrong_Defective_Price']) and platform == 'Meesho' else None
            
            if platform == 'Meesho':
                discount = 0.0 # Force discount to 0 for Meesho
                if wrong_defective_price is None or wrong_defective_price <= 0:
                    wrong_defective_price = mrp # Default to MRP if not provided

            # Perform calculation
            (sale_price, gt_charge, customer_paid_amount, royalty_fee,
             marketing_fee_base, current_marketing_fee_rate, final_commission,
             commission_rate, settled_amount, taxable_amount_value,
             net_profit, tds, tcs, invoice_tax_rate, jiomart_fixed_fee_total, jiomart_shipping_fee_total) = perform_calculations(
                 mrp, discount, apply_royalty, marketing_fee_rate, product_cost, platform, 
                 weight_in_kg, shipping_zone, jiomart_category, meesho_charge_rate, wrong_defective_price
             )

            fixed_shipping_charge = gt_charge
            if platform == 'Jiomart':
                fixed_shipping_charge = jiomart_fixed_fee_total + jiomart_shipping_fee_total
            elif platform == 'Meesho':
                fixed_shipping_charge = 0.0 # No fixed/shipping charge separate from commission for Meesho

            # Store result
            result_row = {
                'ID': index + 1,
                'SKU': sku,
                'Platform': platform,
                'MRP': mrp,
                'Discount': discount,
                'Sale_Price': sale_price,
                'Product_Cost': product_cost,
                'Royalty': royalty_fee,
                'Commission': final_commission,
                'Fixed/Shipping_Charge': fixed_shipping_charge,
                'TDS': tds,
                'TCS': tcs,
                'Settled_Amount': settled_amount,
                'Net_Profit': net_profit,
                'Margin_%': (net_profit / product_cost) * 100 if product_cost > 0 else 0.0
            }
            results.append(result_row)

        except Exception as e:
            st.warning(f"Error processing row {index + 1} (SKU: {row.get('SKU', 'N/A')}): {e}")
            results.append({
                'ID': index + 1,
                'SKU': row.get('SKU', 'N/A'),
                'Platform': row.get('Platform', 'N/A'),
                'Error': str(e)
            })

    return pd.DataFrame(results)

# --- Template Generation (MODIFIED) ---
def get_excel_template():
    """Generates an Excel template for bulk processing."""
    data = {
        'SKU': ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005'],
        'MRP': [1000.0, 1500.0, 2000.0, 800.0, 1200.0],
        'Discount': [100.0, 300.0, 500.0, 0.0, 0.0], # Discount is 0 for Meesho
        'Product_Cost': [450.0, 600.0, 800.0, 300.0, 500.0],
        'Platform': ['Myntra', 'Ajio', 'Jiomart', 'FirstCry', 'Meesho'], # Added Meesho
        'Apply_Royalty': ['Yes', 'No', 'Yes', 'No', 'No'],
        'Marketing_Fee_Rate': [0.04, 0.0, 0.0, 0.0, 0.0],
        'Weight_in_KG': [0.5, 0.0, 1.2, 0.0, 0.0],
        'Shipping_Zone': ['Local', None, 'National', None, None],
        'Jiomart_Category': ['Tshirts', None, 'Sets Boys', None, None],
        'Wrong_Defective_Price': [None, None, None, None, 1100.0], # Meesho specific
        'Meesho_Charge_Rate': [None, None, None, None, 0.03] # Meesho specific (e.g., 0.03 for 3% charge)
    }
    df = pd.DataFrame(data)

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Data')

    # Add Data Validation for better UX
    workbook = writer.book
    worksheet = writer.sheets['Data']

    # Validation options
    platforms = ','.join(['Myntra', 'FirstCry', 'Ajio', 'Jiomart', 'Meesho']) # Updated Platforms
    royalty = 'Yes,No'
    zones = ','.join(['Local', 'Regional', 'National'])
    categories = ','.join(JIOMART_COMMISSION_RATES.keys())

    # Update Data Validation ranges due to new SKU column
    # Platform (E column now)
    worksheet.data_validation('E2:E100', {'validate': 'list', 'source': platforms})
    # Apply_Royalty (F column now)
    worksheet.data_validation('F2:F100', {'validate': 'list', 'source': royalty})
    # Shipping_Zone (I column now)
    worksheet.data_validation('I2:I100', {'validate': 'list', 'source': zones})
    # Jiomart_Category (J column now)
    worksheet.data_validation('J2:J100', {'validate': 'list', 'source': categories})

    writer.close()
    processed_data = output.getvalue()
    return processed_data

# --- STREAMLIT APP STRUCTURE (MODIFIED) ---

st.title("🛍️ " + FULL_TITLE)
st.markdown("###### **1. Input and Configuration**")

# --- MODE SELECTION ---
col_calc_mode, col_sub_mode_placeholder = st.columns([1, 1])

with col_calc_mode:
    calculation_mode = st.radio(
        "Select Calculation Mode:",
        ('A. Single Product Calculation', 'B. Bulk Processing (Excel)'),
        index=0,
        label_visibility="visible"
    )

# --- Sub-Mode Placement ---
if calculation_mode == 'A. Single Product Calculation':
    with col_sub_mode_placeholder:
        # We need a dummy label to align the Sub-Mode radio button with the main mode
        st.markdown("Select Sub-Mode:") 
        single_calc_mode = st.radio(
            "", # Label is empty as we used markdown for alignment
            ('Profit Calculation', 'Target Discount'),
            index=0,
            label_visibility="collapsed", # Hide the radio label
            horizontal=True
        )
else:
    # If in Bulk Mode, fill the placeholder column with nothing
    single_calc_mode = 'Profit Calculation' # Default value for the variable 
    with col_sub_mode_placeholder:
        st.write("") 

st.divider()


if calculation_mode == 'A. Single Product Calculation':
    # --- Single Product Inputs ---

    # UPDATED PLATFORM LIST
    platform_selector = st.radio(
        "Select Platform:",
        ('Myntra', 'FirstCry', 'Ajio', 'Jiomart', 'Meesho'), # ADDED MEESHO
        index=0,
        horizontal=True
    )
    st.markdown("##### **Configuration Settings**")
    
    if platform_selector != 'Meesho':
        col_royalty, col_extra_settings = st.columns(2) 
        royalty_base = 'CPA' if platform_selector == 'Myntra' else 'Sale Price'
        apply_royalty = col_royalty.radio(
            f"Royalty Fee (10% of {royalty_base})?",
            ('Yes', 'No'),
            index=1, # Default to No for new setup
            horizontal=True,
            label_visibility="visible"
        )
        # Marketing/Category Setup
        with col_extra_settings:
            marketing_fee_rate = 0.0
            jiomart_category = None
            selected_jiomart_category = None

            if platform_selector == 'Myntra':
                marketing_options = ['0%', '4%', '5%']
                default_index = marketing_options.index('4%')
                selected_marketing_fee_str = st.selectbox(
                    "Marketing Fee Rate:",
                    marketing_options,
                    index=default_index,
                    help="Rate applied to CPA (Customer Paid Amount) on Myntra.",
                    key="marketing_fee_selector",
                    disabled=(platform_selector != 'Myntra')
                )
                marketing_fee_rate = float(selected_marketing_fee_str.strip('%')) / 100.0
            elif platform_selector == 'Jiomart':
                jiomart_category_options = list(JIOMART_COMMISSION_RATES.keys())
                jiomart_category_options.sort()
                jiomart_category_options.insert(0, "Select Category")
                selected_jiomart_category = st.selectbox(
                    "Product Category:",
                    jiomart_category_options,
                    index=0,
                    help="Select the product category for Jiomart commission calculation.",
                    key="jiomart_category_selector"
                )
                jiomart_category = None if selected_jiomart_category == "Select Category" else selected_jiomart_category
            else:
                st.markdown("Marketing Fee Rate: **0%**")
                marketing_fee_rate = 0.0
                apply_royalty = 'No'

    # --- NEW MEESHO CONFIGURATION ---
    else: # platform_selector == 'Meesho'
        apply_royalty = 'No'
        marketing_fee_rate = 0.0
        jiomart_category = None
        
        col_meesho_config, col_meesho_placeholder = st.columns(2)
        
        with col_meesho_config:
            meesho_charge_percent = st.number_input(
                "Meesho Platform Charge (%)",
                min_value=0.0,
                max_value=10.0,
                value=3.0,
                step=0.1,
                format="%.2f",
                help="The fee is typically 2% to 5% of the Wrong/Defective Price.",
                key="meesho_charge_rate_single"
            ) / 100.0
            
            st.info(f"Payout is approx. **{(1 - meesho_charge_percent) * 100:.2f}%** of Wrong/Defective Price.")


    # --- Jiomart Specific Inputs (Weight & Zone) ---
    weight_in_kg = 0.0
    shipping_zone = None
    if platform_selector == 'Jiomart':
        st.markdown("##### **Jiomart Specifics**")

        col_weight, col_zone = st.columns(2)
        with col_weight:
            weight_in_kg = st.number_input(
                "Product Weight (KG)",
                min_value=0.1,
                value=0.5,
                step=0.1,
                format="%.2f",
                key="single_weight",
                help="Enter the weight of the product for shipping fee calculation."
            )
        with col_zone:
            shipping_zone = st.selectbox(
                "Shipping Zone:",
                ('Local', 'Regional', 'National'),
                index=0,
                key="single_zone",
                help="Select the shipping zone for the product."
            )

    # --- Common Inputs ---
    col_cost, col_target = st.columns(2)
    with col_cost:
        product_cost = st.number_input(
            "Product Cost (₹)",
            min_value=0.0,
            value=1000.0,
            step=10.0,
            key="single_cost",
            label_visibility="visible"
        )

    with col_target:
        product_margin_target_rs = st.number_input(
            "Target Net Profit (₹)",
            min_value=0.0,
            value=200.0,
            step=10.0,
            key="single_target",
            label_visibility="visible"
        )

    st.divider()

    # --- MRP/Discount/WDP Inputs ---
    col_mrp_in, col_price_in = st.columns(2)
    new_mrp = col_mrp_in.number_input(
        "Product MRP (₹)",
        min_value=1.0,
        value=2500.0,
        step=100.0,
        key="new_mrp",
        label_visibility="visible"
    )
    new_discount = 0.0
    wrong_defective_price = None

    if platform_selector == 'Meesho':
        # Meesho: Input Wrong/Defective Price
        if single_calc_mode == 'Target Discount':
            col_price_in.info("Target Discount mode is not applicable for Meesho.")
            single_calc_mode = 'Profit Calculation' # Force back to Profit Calc
        
        wrong_defective_price = col_price_in.number_input(
            "Wrong/Defective Price (₹)",
            min_value=0.0,
            max_value=new_mrp,
            value=min(new_mrp, 2000.0), # Default less than MRP
            step=10.0,
            key="meesho_wdp_manual",
            help="This is the value Meesho uses for charging its fees (Payout Value).",
            label_visibility="visible"
        )
        new_discount = 0.0 # Force discount to 0
    
    else: # Other Platforms: Input Discount
        meesho_charge_percent = 0.0 # Reset Meesho values
        
        if single_calc_mode == 'Profit Calculation':
            new_discount = col_price_in.number_input(
                "Discount Amount (₹)",
                min_value=0.0,
                max_value=new_mrp,
                value=500.0,
                step=10.0,
                key="new_discount_manual",
                label_visibility="visible"
            )
        else:
            col_price_in.info(f"Targeting a Net Profit of ₹ {product_margin_target_rs:,.2f}...")
            new_discount = 0.0 # Will be calculated by logic

    st.divider()
    
    # Handle the meesho_charge_rate assignment for the function call
    if platform_selector != 'Meesho':
        meesho_charge_rate = 0.0
    else:
        # Use the value from the new config input
        meesho_charge_rate = meesho_charge_percent

    if new_mrp > 0 and product_cost > 0:
        # --- Input Validation for Jiomart ---
        if platform_selector == 'Jiomart' and jiomart_category is None:
            st.warning("Please select a **Product Category** for Jiomart calculation.")
            st.stop()
        # ------------------------------------

        try:
            # --- CALCULATION BLOCK (Single) ---

            if single_calc_mode == 'Target Discount' and platform_selector != 'Meesho':
                target_profit = product_margin_target_rs
                calculated_discount, initial_max_profit, calculated_discount_percent = find_discount_for_target_profit(
                    new_mrp, target_profit, apply_royalty, marketing_fee_rate, product_cost, platform_selector, weight_in_kg, shipping_zone, jiomart_category
                )
                if calculated_discount is None:
                    st.error(f"Cannot achieve the Target Profit of ₹ {target_profit:,.2f}. The maximum possible Net Profit at 0% discount is ₹ {initial_max_profit:,.2f}.")
                    st.stop()
                new_discount = calculated_discount
                # Recalculate based on found discount
                (sale_price, gt_charge, customer_paid_amount, royalty_fee,
                 marketing_fee_base, current_marketing_fee_rate, final_commission,
                 commission_rate, settled_amount, taxable_amount_value,
                 net_profit, tds, tcs, invoice_tax_rate, jiomart_fixed_fee_total, jiomart_shipping_fee_total) = perform_calculations(new_mrp, new_discount, apply_royalty, marketing_fee_rate, product_cost, platform_selector, weight_in_kg, shipping_zone, jiomart_category)

            else:
                # Standard Calculation (Profit Calc Mode OR Meesho)
                (sale_price, gt_charge, customer_paid_amount, royalty_fee,
                 marketing_fee_base, current_marketing_fee_rate, final_commission,
                 commission_rate, settled_amount, taxable_amount_value,
                 net_profit, tds, tcs, invoice_tax_rate, jiomart_fixed_fee_total, jiomart_shipping_fee_total) = perform_calculations(new_mrp, new_discount, apply_royalty, marketing_fee_rate, product_cost, platform_selector, weight_in_kg, shipping_zone, jiomart_category, meesho_charge_rate, wrong_defective_price)


            target_profit = product_margin_target_rs
            delta_value = net_profit - target_profit
            current_margin_percent = (net_profit / product_cost) * 100 if product_cost > 0 else 0.0
            delta_label = f"vs Target: ₹ {delta_value:,.2f}"
            delta_color = "normal" if net_profit >= target_profit else "inverse"

            # --- DISPLAY RESULTS (Single) ---

            col_left, col_right = st.columns(2)

            # =========== LEFT COLUMN: Sales, Fixed Charges & Invoice Value ===========
            with col_left:
                st.markdown("###### **2. Sales, Fixed Charges & Invoice Value**")

                col1_l, col2_l, col3_l = st.columns(3)
                col1_l.metric(label="Product MRP (₹)", value=f"₹ {new_mrp:,.2f}", delta_color="off")
                
                # Discount/WDP Display
                if platform_selector != 'Meesho':
                    discount_percent = (new_discount / new_mrp) * 100 if new_mrp > 0 else 0.0
                    col2_l.metric(
                        label="Discount Amount",
                        value=f"₹ {new_discount:,.2f}",
                        delta=f"{discount_percent:,.2f}% of MRP",
                        delta_color="off"
                    )
                    col3_l.metric(label="Sale Price (₹)", value=f"₹ {sale_price:,.2f}")
                    st.markdown("---")
                    # Display for Myntra/Ajio/FirstCry/Jiomart
                    if platform_selector == 'Jiomart':
                        col4_l, col5_l, col6_l = st.columns(3)
                        col4_l.metric(
                            label="Jiomart Fixed Fee (Incl. 18% GST)",
                            value=f"₹ {jiomart_fixed_fee_total:,.2f}",
                            delta_color="off"
                        )
                        col5_l.metric(
                            label=f"Shipping Fee (Incl. 18% GST, {weight_in_kg:.1f}kg)",
                            value=f"₹ {jiomart_shipping_fee_total:,.2f}",
                            delta_color="off"
                        )
                        col6_l.metric(label="**Invoice Value (CPA)**", value=f"₹ {customer_paid_amount:,.2f}")
                    else:
                        col4_l, col5_l = st.columns(2)
                        fixed_charge_label = ""
                        if platform_selector == 'Myntra':
                            fixed_charge_label = "GT Charge (Deducted from Sale Price)"
                        elif platform_selector == 'Ajio':
                            fixed_charge_label = "SCM Charges (₹95 + 18% GST)"
                        else: # FirstCry
                            fixed_charge_label = "Fixed Charges"
                          
                        col4_l.metric(
                            label=fixed_charge_label,
                            value=f"₹ {gt_charge:,.2f}",
                            delta_color="off"
                        )
                        col5_l.metric(label="**Invoice Value (CPA)**", value=f"₹ {customer_paid_amount:,.2f}")

                else: # MEESHO Display
                    col2_l.metric(
                        label="Wrong/Defective Price (WDP)",
                        value=f"₹ {wrong_defective_price:,.2f}",
                        delta_color="off"
                    )
                    col3_l.metric(label="Sale Price (₹)", value=f"₹ {sale_price:,.2f}")
                    st.markdown("---")
                    col4_l, col5_l = st.columns(2)
                    col4_l.metric(
                        label="Fixed/Shipping Charges",
                        value=f"₹ 0.00",
                        delta_color="off"
                    )
                    col5_l.metric(label="**Invoice Value (WDP)**", value=f"₹ {customer_paid_amount:,.2f}")


            # =========== RIGHT COLUMN: Deductions and Final Payout ===========
            with col_right:
                st.markdown("###### **3. Deductions (Charges)**")

                col1_r, col2_r, col3_r = st.columns(3)

                # Commission
                commission_display_label = ""
                if platform_selector == 'Myntra':
                    commission_display_label = f"Commission ({commission_rate*100:.0f}%+Tax)"
                elif platform_selector == 'FirstCry':
                    commission_display_label = "**Flat Deduction (42%)**"
                elif platform_selector == 'Ajio':
                    commission_display_label = f"Commission (20%+Tax)"
                elif platform_selector == 'Jiomart':
                    commission_display_label = f"Commission ({commission_rate*100:.2f}%+Tax)"
                elif platform_selector == 'Meesho':
                    commission_display_label = f"Meesho Fee ({meesho_charge_rate*100:.2f}% of WDP + Tax)"

                col1_r.metric(label=commission_display_label, value=f"₹ {final_commission:,.2f}")

                # Marketing Fee (only for Myntra, else 0)
                col2_r.metric(
                    label=f"Marketing Fee ({marketing_fee_rate*100:.0f}%)",
                    value=f"₹ {marketing_fee_base:,.2f}",
                )

                # Royalty Fee
                col3_r.metric(
                    label=f"Royalty Fee ({'10%' if apply_royalty=='Yes' else '0%'})",
                    value=f"₹ {royalty_fee:,.2f}",
                )

                col4_r, col5_r, col6_r = st.columns(3)
                col4_r.metric(
                    label=f"Taxable Value (GST @ {invoice_tax_rate*100:.0f}%)",
                    value=f"₹ {taxable_amount_value:,.2f}",
                )
                col5_r.metric(label="TDS (0.1% on Taxable Value)", value=f"₹ {abs(tds):,.2f}")
                col6_r.metric(label="TCS (10% on Tax Amt)", value=f"₹ {abs(tcs):,.2f}") # Kept original labels for consistency

                st.markdown("---")

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


elif calculation_mode == 'B. Bulk Processing (Excel)':
    # --- Bulk Processing Logic ---
    st.markdown("##### **Excel Bulk Processing**")
    st.info("ℹ️ Please use the template provided below before uploading your file. **For Meesho, fill 'Wrong\_Defective\_Price' and 'Meesho\_Charge\_Rate' columns.**")

    # Template Download Button
    excel_data = get_excel_template()
    st.download_button(
        label="⬇️ Download Excel Template",
        data=excel_data,
        file_name='Vardhman_Ecom_Bulk_Template.xlsx',
        mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        help="Download this template and fill in your product details."
    )
    st.divider()

    uploaded_file = st.file_uploader("📂 **Upload Excel File** (.xlsx or .csv)", type=['xlsx', 'csv'])

    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith('.csv'):
                # Load CSV, attempting to ensure required columns are present to avoid bulk error
                input_df = pd.read_csv(uploaded_file)
            else:
                # Load Excel
                input_df = pd.read_excel(uploaded_file)
            
            # Ensure all required columns for calculation are present, filling missing with defaults
            required_cols = ['SKU', 'MRP', 'Discount', 'Product_Cost', 'Platform', 'Apply_Royalty', 'Marketing_Fee_Rate', 'Weight_in_KG', 'Shipping_Zone', 'Jiomart_Category', 'Wrong_Defective_Price', 'Meesho_Charge_Rate']
            for col in required_cols:
                if col not in input_df.columns:
                    if col in ['Wrong_Defective_Price', 'Meesho_Charge_Rate']:
                        input_df[col] = np.nan # Use NaN for optional Meesho columns if missing
                    else:
                        st.error(f"Missing required column: **{col}**. Please use the downloaded template.")
                        st.stop()

            if input_df.empty:
                st.warning("The uploaded file is empty.")
                st.stop()

            st.success(f"Successfully loaded {len(input_df)} product data from **{uploaded_file.name}**. Starting processing now...")

            # Process the data
            output_df = bulk_process_data(input_df)

            st.divider()
            st.markdown("### ✅ Calculation Results")

            # Display results
            st.dataframe(output_df.style.format({
                'MRP': "₹ {:,.2f}",
                'Discount': "₹ {:,.2f}",
                'Sale_Price': "₹ {:,.2f}",
                'Product_Cost': "₹ {:,.2f}",
                'Royalty': "₹ {:,.2f}",
                'Commission': "₹ {:,.2f}",
                'Fixed/Shipping_Charge': "₹ {:,.2f}",
                'TDS': "₹ {:,.2f}",
                'TCS': "₹ {:,.2f}",
                'Settled_Amount': "₹ {:,.2f}",
                'Net_Profit': "₹ {:,.2f}",
                'Margin_%': "{:,.2f}%"
            }), use_container_width=True)

            # Download Results Button
            output_excel = BytesIO()
            with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
                output_df.to_excel(writer, index=False, sheet_name='Results')
            processed_data = output_excel.getvalue()

            st.download_button(
                label="⬇️ Download Results as Excel",
                data=processed_data,
                file_name='Vardhman_Ecom_Payout_Results.xlsx',
                mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )

        except Exception as e:
            st.error(f"An error occurred during file processing: {e}")
            st.info("Please ensure your column names match the template (e.g., MRP, Platform, Discount, etc.) and the data is in the correct format.")

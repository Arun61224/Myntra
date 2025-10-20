import pandas as pd
import streamlit as st
import numpy as np
from io import BytesIO

# Set page config for wide layout and minimum gaps, using the specified full title
FULL_TITLE = "Vardhman Wool Store E-commerce Calculator"
st.set_page_config(layout="wide", page_title=FULL_TITLE, page_icon="🛍️")

# --- Custom CSS for Compactness & VERTICAL SEPARATION (Cleaned U+00A0) ---
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

# --- Myntra Brand/Category/Commission Data Structure ---
MYNTRA_COMMISSION_RATES = {
    # --- ONLY NEW BRANDS KEPT ---
    "Disney By Miss and Chief": {
        "Wool/Knitwear": 0.18,
        "Thermal Wear": 0.15,
        "Shawls/Stoles": 0.22,
        "Generic Apparel": 0.25
    },
    "KUCHIPOO": {
        "Wool/Knitwear": 0.18,
        "Thermal Wear": 0.15,
        "Shawls/Stoles": 0.22,
        "Generic Apparel": 0.25
    },
    "Marvel by Miss and Chief": {
        "Wool/Knitwear": 0.18,
        "Thermal Wear": 0.15,
        "Shawls/Stoles": 0.22,
        "Generic Apparel": 0.25
    },
    "YK": {
        "Wool/Knitwear": 0.18,
        "Thermal Wear": 0.15,
        "Shawls/Stoles": 0.22,
        "Generic Apparel": 0.25
    },
    "YK Disney": {
        "Wool/Knitwear": 0.18,
        "Thermal Wear": 0.15,
        "Shawls/Stoles": 0.22,
        "Generic Apparel": 0.25
    },
    "YK Marvel": {
        "Wool/Knitwear": 0.18,
        "Thermal Wear": 0.15,
        "Shawls/Stoles": 0.22,
        "Generic Apparel": 0.25
    }
    # ----------------------------
}


# Myntra Specific GT Charges
def calculate_myntra_gt_charges(sale_price):
    if sale_price <= 500:
        return 54.00
    elif sale_price <= 1000:
        return 94.00
    else:
        return 171.00

# Myntra Commission Rate (Robust Fallback)
def get_myntra_commission_by_category(brand, category):
    """Retrieves Myntra commission rate based on selected brand and category."""
    DEFAULT_RATE = 0.25
    brand_rates = MYNTRA_COMMISSION_RATES.get(brand)
    if brand_rates is None: return DEFAULT_RATE
    rate = brand_rates.get(category)
    if rate is None: return DEFAULT_RATE
    return rate

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

    rates = shipping_rates.get(shipping_zone, shipping_rates['Local'])
    total_shipping_fee_base = 0.0

    if weight_in_kg <= 0.5:
        total_shipping_fee_base = rates['first_0.5']
    elif weight_in_kg <= 1.0:
        total_shipping_fee_base = rates['first_0.5'] + rates['next_0.5']
    else:
        total_shipping_fee_base = rates['first_0.5'] + rates['next_0.5']
        remaining_weight = weight_in_kg - 1.0

        if remaining_weight <= 4.0:
            total_shipping_fee_base += np.ceil(remaining_weight) * rates['upto_5kg_per_kg']
        else:
            total_shipping_fee_base += 4 * rates['upto_5kg_per_kg']
            remaining_weight -= 4.0
            total_shipping_fee_base += np.ceil(remaining_weight) * rates['after_5kg_per_kg']

    return total_shipping_fee_base

# Jiomart Commission Rates
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

# --- CORE CALCULATION LOGIC ---
def perform_calculations(mrp, discount, apply_royalty, marketing_fee_rate, product_cost, platform,
                             weight_in_kg=0.0, shipping_zone=None, jiomart_category=None,
                             meesho_charge_rate=0.0, wrong_defective_price=None,
                             myntra_brand=None, myntra_category=None, 
                             jiomart_benefit_rate=0.0): # CONSOLIDATED PARAMETER
    """Performs all sequential calculations for profit analysis based on platform.
        Returns 20 values.
    """
    
    gt_charge = 0.0
    royalty_fee = 0.0
    marketing_fee_base = 0.0
    final_commission = 0.0
    commission_rate = 0.0
    
    # Jiomart Fee Breakdown Variables - Initialized for safe return
    jiomart_comm_fee_base = 0.0
    jiomart_fixed_fee_base = 0.0
    jiomart_shipping_fee_base = 0.0
    jiomart_total_fee_base = 0.0
    jiomart_benefit_amount = 0.0 
    jiomart_final_applicable_fee_base = 0.0
    jiomart_gst_on_fees = 0.0
    total_platform_deduction = 0.0
    
    total_fixed_charge = 0.0
    GST_RATE_FEES = 0.18 # 18% GST on platform fees

    # --- PLATFORM SPECIFIC LOGIC ---
    if platform == 'Meesho':
        if wrong_defective_price is None or wrong_defective_price <= 0:
            customer_paid_amount = mrp
        else:
            customer_paid_amount = wrong_defective_price
            
        sale_price = customer_paid_amount
        discount = mrp - sale_price

        commission_rate = meesho_charge_rate
        commission_base = customer_paid_amount * commission_rate
        commission_tax = commission_base * GST_RATE_FEES
        final_commission = commission_base + commission_tax

        marketing_fee_base = 0.0
        gt_charge = 0.0
        marketing_fee_rate = 0.0
        total_fixed_charge = 0.0

    else:
        sale_price = mrp - discount
        
        if sale_price < 0:
            return (sale_price, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -99999999.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        customer_paid_amount = sale_price

        if platform == 'Myntra':
            gt_charge = calculate_myntra_gt_charges(sale_price)
            customer_paid_amount = sale_price - gt_charge
            
            commission_rate = get_myntra_commission_by_category(myntra_brand, myntra_category)
            
            commission_amount_base = customer_paid_amount * commission_rate
            marketing_fee_base = customer_paid_amount * marketing_fee_rate
            commission_tax = commission_amount_base * 0.18
            final_commission = commission_amount_base + commission_tax
            total_fixed_charge = gt_charge
            
        elif platform == 'FirstCry':
            commission_rate = 0.42
            final_commission = sale_price * commission_rate
            gt_charge = 0.0
            marketing_fee_base = 0.0
            marketing_fee_rate = 0.0
            total_fixed_charge = 0.0

        elif platform == 'Ajio':
            commission_rate = 0.20
            commission_base = sale_price * commission_rate
            commission_tax = commission_base * 0.18
            final_commission = commission_base + commission_tax
            scm_base = 95.0
            scm_tax = scm_base * 0.18
            gt_charge = scm_base + scm_tax
            marketing_fee_base = 0.0
            marketing_fee_rate = 0.0
            total_fixed_charge = gt_charge

        elif platform == 'Jiomart':
            
            # 1. Base Fees
            if jiomart_category:
                commission_rate = get_jiomart_commission_rate(jiomart_category, sale_price)
            else:
                commission_rate = 0.0
            
            jiomart_comm_fee_base = sale_price * commission_rate
            jiomart_fixed_fee_base = calculate_jiomart_fixed_fee_base(sale_price)
            
            jiomart_shipping_fee_base = 0.0
            if shipping_zone and weight_in_kg > 0:
                jiomart_shipping_fee_base = calculate_jiomart_shipping_fee_base(weight_in_kg, shipping_zone)

            # 2. Total Fee (1+2+3)
            jiomart_total_fee_base = jiomart_comm_fee_base + jiomart_fixed_fee_base + jiomart_shipping_fee_base

            # 3. Brand Fee Benefit (Deduction from Fees, hence negative)
            benefit_rate = jiomart_benefit_rate
            
            # jiomart_benefit_amount is stored as a negative value (the deduction)
            jiomart_benefit_amount = -(sale_price * benefit_rate)
            
            # 4. Final Applicable Fee (B)
            jiomart_final_applicable_fee_base = jiomart_total_fee_base + jiomart_benefit_amount
            
            # 5. GST @ 18% (C) - Applied ONLY to the Final Applicable Fee (B)
            jiomart_gst_on_fees = jiomart_final_applicable_fee_base * GST_RATE_FEES

            # 6. Total Platform Deduction
            total_platform_deduction = jiomart_final_applicable_fee_base + jiomart_gst_on_fees

            # Proxies for common fields (Base values for P&L tracking)
            final_commission = jiomart_comm_fee_base
            total_fixed_charge = jiomart_fixed_fee_base + jiomart_shipping_fee_base
            
            customer_paid_amount = sale_price
            
    # --- Apply Royalty universally based on Sale Price (Selling Price) ---
    if apply_royalty == 'Yes':
        royalty_fee = sale_price * 0.10

    # --- COMMON TAX AND FINAL SETTLEMENT LOGIC (Based on Customer Paid Amount) ---
    taxable_amount_value, invoice_tax_rate = calculate_taxable_amount_value(customer_paid_amount)
    tax_amount = customer_paid_amount - taxable_amount_value
    tds = taxable_amount_value * 0.001
    tcs = tax_amount * 0.10

    # DEDUCTIONS
    if platform == 'Jiomart':
        total_deductions = total_platform_deduction + royalty_fee + marketing_fee_base
    else:
        total_deductions = final_commission + royalty_fee + marketing_fee_base
        if platform in ['Myntra', 'Ajio']:
            total_deductions += gt_charge

        
    # FINAL SETTLEMENT
    settled_amount = customer_paid_amount - total_deductions - tds - tcs
    net_profit = settled_amount - product_cost

    return (sale_price, total_fixed_charge, customer_paid_amount, royalty_fee,
            marketing_fee_base, marketing_fee_rate, final_commission, 
            commission_rate, settled_amount, taxable_amount_value,
            net_profit, tds, tcs, invoice_tax_rate, 
            jiomart_fixed_fee_base, jiomart_shipping_fee_base,
            jiomart_benefit_amount, # Brand Fee Benefit (negative value)
            jiomart_total_fee_base, # Total Base Fee (1+2+3)
            jiomart_final_applicable_fee_base, # Final Applicable Fee (B) base
            jiomart_gst_on_fees # GST @ 18% (C)
            )

# --- Other Helper Functions (Updated for single Jiomart rate) ---
def find_discount_for_target_profit(mrp, target_profit, apply_royalty, marketing_fee_rate, product_cost, platform, weight_in_kg=0.0, shipping_zone=None, jiomart_category=None, meesho_charge_rate=0.0, wrong_defective_price=None, myntra_brand=None, myntra_category=None, jiomart_benefit_rate=0.0): # CONSOLIDATED PARAMETER
    """Finds the maximum discount allowed (in 1.0 steps) to achieve at least the target profit."""

    # Helper function to get the 11th return value (net_profit)
    def get_profit(disc, wdp=None):
        results = perform_calculations(mrp, disc, apply_royalty, marketing_fee_rate, product_cost, platform, weight_in_kg, shipping_zone, jiomart_category, meesho_charge_rate, wdp, myntra_brand, myntra_category, jiomart_benefit_rate)
        return results[10]

    if platform == 'Meesho':
        max_profit = get_profit(0.0, mrp)
        if max_profit < target_profit:
            return None, max_profit, 0.0
            
        wdp_step = 1.0
        required_wdp = mrp

        while required_wdp >= 0:
            current_profit = get_profit(mrp - required_wdp, round(required_wdp, 2))

            if current_profit < target_profit:
                final_wdp = required_wdp + wdp_step
                target_wdp = min(final_wdp, mrp)
                discount_amount = mrp - target_wdp
                discount_percent = (discount_amount / mrp) * 100 if mrp > 0 else 0.0
                final_profit = get_profit(discount_amount, target_wdp)
                return discount_amount, final_profit, discount_percent 

            required_wdp -= wdp_step
            
        final_profit = get_profit(mrp, 0.0)
        return mrp, final_profit, 100.0


    # Original logic for other platforms
    initial_profit = get_profit(0.0)

    if initial_profit < target_profit:
        return None, initial_profit, 0.0

    discount_step = 1.0
    required_discount = 0.0

    while required_discount <= mrp:
        current_profit = get_profit(required_discount)

        if current_profit < target_profit:
            final_discount = max(0.0, required_discount - discount_step)
            final_profit = get_profit(final_discount)
            discount_percent = (final_discount / mrp) * 100
            return final_discount, final_profit, discount_percent

        required_discount += discount_step

    final_profit = get_profit(mrp)
    return mrp, final_profit, 100.0


# --- Bulk Calculation Handler (Modified for single Jiomart rate) ---
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
    df['Meesho_Charge_Rate'] = df['Meesho_Charge_Rate'].fillna(0.03)
    df['Wrong_Defective_Price'] = df['Wrong_Defective_Price'].fillna(0.0)
    df['Myntra_Brand'] = df['Myntra_Brand'].fillna(None)
    df['Myntra_Category'] = df['Myntra_Category'].fillna(None)
    # Single Jiomart Benefit Rate
    df['Jiomart_Benefit_Rate'] = df['Jiomart_Benefit_Rate'].fillna(0.0) 

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
            meesho_charge_rate = float(row['Meesho_Charge_Rate'])
            wrong_defective_price = float(row['Wrong_Defective_Price']) if pd.notna(row['Wrong_Defective_Price']) else None
            myntra_brand = str(row['Myntra_Brand']).strip() if pd.notna(row['Myntra_Brand']) else None
            myntra_category = str(row['Myntra_Category']).strip() if pd.notna(row['Myntra_Category']) else None
            
            # Jiomart Benefit Handling (Single Rate)
            jiomart_benefit_rate_bulk = float(row['Jiomart_Benefit_Rate'])

            # Platform-specific variable cleaning
            if platform == 'Meesho':
                myntra_brand = None
                myntra_category = None
                jiomart_category = None
                discount = 0.0
                weight_in_kg = 0.0
                shipping_zone = None
                
            elif platform == 'Myntra':
                jiomart_category = None
                meesho_charge_rate = 0.0
                wrong_defective_price = None
                weight_in_kg = 0.0
                shipping_zone = None
                jiomart_benefit_rate_bulk = 0.0
                
            elif platform == 'Jiomart':
                myntra_brand = None
                myntra_category = None
                meesho_charge_rate = 0.0
                wrong_defective_price = None
            
            else: # Ajio, FirstCry
                myntra_brand = None
                myntra_category = None
                meesho_charge_rate = 0.0
                wrong_defective_price = None
                jiomart_category = None
                weight_in_kg = 0.0
                shipping_zone = None
                jiomart_benefit_rate_bulk = 0.0

            # Perform calculation 
            (sale_price, gt_charge, customer_paid_amount, royalty_fee,
             marketing_fee_base, current_marketing_fee_rate, final_commission,
             commission_rate, settled_amount, taxable_amount_value,
             net_profit, tds, tcs, invoice_tax_rate, jiomart_fixed_fee_base, jiomart_shipping_fee_base,
             jiomart_benefit_amount, jiomart_total_fee_base, jiomart_final_applicable_fee_base, jiomart_gst_on_fees) = perform_calculations(
                 mrp, discount, apply_royalty, marketing_fee_rate, product_cost, platform,
                 weight_in_kg, shipping_zone, jiomart_category, meesho_charge_rate, wrong_defective_price, myntra_brand, myntra_category,
                 jiomart_benefit_rate_bulk # Pass the single bulk rate
                )

            # Determine fixed/shipping for display
            fixed_shipping_charge = 0.0
            if platform == 'Ajio' or platform == 'Myntra':
                fixed_shipping_charge = gt_charge
            elif platform == 'Jiomart':
                fixed_shipping_charge = jiomart_fixed_fee_base + jiomart_shipping_fee_base
            
            # Determine the Commission/Platform fee to display
            display_commission_fee = final_commission
            if platform == 'Jiomart':
                display_commission_fee = jiomart_final_applicable_fee_base + jiomart_gst_on_fees
            
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
                'Platform_Fee_Incl_GST': display_commission_fee, 
                'Fixed/Shipping_Charge': fixed_shipping_charge,
                'Jiomart_Benefit': abs(jiomart_benefit_amount) if platform == 'Jiomart' else 0.0,
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

# --- Template Generation (CLEANED) ---
def get_excel_template():
    """Generates an Excel template for bulk processing."""
    data = {
        'SKU': ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005'],
        'MRP': [1000.0, 1500.0, 2000.0, 800.0, 1200.0],
        'Discount': [100.0, 300.0, 500.0, 0.0, 0.0],
        'Product_Cost': [450.0, 600.0, 800.0, 300.0, 500.0],
        'Platform': ['Myntra', 'Ajio', 'Jiomart', 'FirstCry', 'Meesho'],
        'Apply_Royalty': ['Yes', 'No', 'Yes', 'No', 'No'],
        'Marketing_Fee_Rate': [0.04, 0.0, 0.0, 0.0, 0.0],
        'Weight_in_KG': [0.5, 0.0, 1.2, 0.0, 0.0],
        'Shipping_Zone': ['Local', None, 'National', None, None],
        'Jiomart_Category': ['Tshirts', None, 'Sets Boys', None, None],
        'Wrong_Defective_Price': [None, None, None, None, 1100.0],
        'Meesho_Charge_Rate': [None, None, None, None, 0.03],
        'Myntra_Brand': ['KUCHIPOO', None, None, None, None],
        'Myntra_Category': ['Generic Apparel', None, None, None, None],
        'Jiomart_Benefit_Rate': [None, None, 0.01, None, None] # Example 1% benefit rate
    }
    df = pd.DataFrame(data)

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name='Data')

    # Add Data Validation for better UX
    workbook = writer.book
    worksheet = writer.sheets['Data']

    platforms = ','.join(['Myntra', 'FirstCry', 'Ajio', 'Jiomart', 'Meesho'])
    royalty = 'Yes,No'
    zones = ','.join(['Local', 'Regional', 'National'])
    categories = ','.join(JIOMART_COMMISSION_RATES.keys())
    myntra_brands = ','.join(MYNTRA_COMMISSION_RATES.keys())
    all_myntra_categories = set(cat for rates in MYNTRA_COMMISSION_RATES.values() for cat in rates.keys())
    myntra_categories = ','.join(all_myntra_categories)

    worksheet.data_validation('E2:E100', {'validate': 'list', 'source': platforms})
    worksheet.data_validation('F2:F100', {'validate': 'list', 'source': royalty})
    worksheet.data_validation('I2:I100', {'validate': 'list', 'source': zones})
    worksheet.data_validation('J2:J100', {'validate': 'list', 'source': categories})
    worksheet.data_validation('L2:L100', {'validate': 'list', 'source': myntra_brands})
    worksheet.data_validation('M2:M100', {'validate': 'list', 'source': myntra_categories})
    # UPDATED: Max value for excel validation changed to 0.5 (50%)
    worksheet.data_validation('N2:N100', {'validate': 'decimal', 'criteria': 'between', 'minimum': 0.0, 'maximum': 0.5}) 

    writer.close()
    processed_data = output.getvalue()
    return processed_data

# --- STREAMLIT APP STRUCTURE (FIXED JIOMART INPUT MAX) ---

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
        st.markdown("Select Sub-Mode:")
        single_calc_mode = st.radio(
            "",
            ('Profit Calculation', 'Target Discount'),
            index=0,
            label_visibility="collapsed",
            horizontal=True
        )
else:
    single_calc_mode = 'Profit Calculation'
    with col_sub_mode_placeholder:
        st.write("")

st.divider()


if calculation_mode == 'A. Single Product Calculation':
    # --- Single Product Inputs ---

    platform_selector = st.radio(
        "Select Platform:",
        ('Myntra', 'FirstCry', 'Ajio', 'Jiomart', 'Meesho'),
        index=0,
        horizontal=True
    )
    st.markdown("##### **Configuration Settings**")
    
    # Define the two columns for main settings
    col_royalty, col_extra_settings = st.columns(2)

    # --- Royalty --- (ALWAYS VISIBLE)
    with col_royalty:
        royalty_base = 'Sale Price'
        apply_royalty = st.radio(
            f"Royalty Fee (10% of {royalty_base})?",
            ('Yes', 'No'),
            index=1,
            horizontal=True,
            label_visibility="visible"
        )

    is_wdp_calculated = (platform_selector == 'Meesho' and single_calc_mode == 'Target Discount')
    
    # --- Platform Specific Configuration ---
    # Initializing Jiomart Benefit Rate for Single Calculation Mode
    jiomart_benefit_rate = 0.0

    with col_extra_settings:
        marketing_fee_rate = 0.0
        jiomart_category = None
        meesho_charge_rate = 0.0
        myntra_brand = None
        myntra_category = None

        if platform_selector == 'Myntra':
            marketing_options = ['0%', '4%', '5%']
            selected_marketing_fee_str = st.selectbox("Marketing Fee Rate:", marketing_options, index=marketing_options.index('4%'), key="marketing_fee_selector", help="Rate applied to CPA (Customer Paid Amount) on Myntra.")
            marketing_fee_rate = float(selected_marketing_fee_str.strip('%')) / 100.0
            
            st.markdown("---")
            col_brand, col_cat = st.columns(2)
            myntra_brand_options = list(MYNTRA_COMMISSION_RATES.keys())
            myntra_brand = col_brand.selectbox("Select Brand:", myntra_brand_options, index=0, key="myntra_brand_selector")

            if myntra_brand:
                myntra_category_options = list(MYNTRA_COMMISSION_RATES.get(myntra_brand, {}).keys())
                myntra_category = col_cat.selectbox("Select Category:", myntra_category_options, index=0, key="myntra_category_selector")
            
            if myntra_brand and myntra_category:
                current_rate = get_myntra_commission_by_category(myntra_brand, myntra_category)
                st.info(f"Commission Rate for **{myntra_brand} - {myntra_category}**: **{current_rate*100:,.2f}%**")

        elif platform_selector == 'Jiomart':
            # JIOMART: Category Selection
            st.markdown("##### **Jiomart Category**")
            
            jiomart_category_options = list(JIOMART_COMMISSION_RATES.keys())
            jiomart_category_options.sort()
            jiomart_category_options.insert(0, "Select Category")
            selected_jiomart_category = st.selectbox(
                "Product Category for Commission Rate:",
                jiomart_category_options,
                index=0,
                key="jiomart_category_selector",
                help="This determines the base commission percentage."
            )
            jiomart_category = None if selected_jiomart_category == "Select Category" else selected_jiomart_category
            

        elif platform_selector == 'Meesho':
            meesho_charge_percent = st.number_input(
                "Meesho Platform Charge (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.1, format="%.2f",
                help="The fee is typically 2% to 5% of the Wrong/Defective Price.", key="meesho_charge_rate_single"
            ) / 100.0
            st.info(f"Payout is approx. **{(1 - meesho_charge_percent) * 100:.2f}%** of Wrong/Defective Price.")
            meesho_charge_rate = meesho_charge_percent
            
        else: # FirstCry, Ajio
            st.markdown("Marketing Fee Rate: **0%**")
            marketing_fee_rate = 0.0

    # --- Jiomart Specific Inputs (Shipping & Single Flat Brand Benefit Rate) ---
    weight_in_kg = 0.0
    shipping_zone = None
    if platform_selector == 'Jiomart':
        
        # 1. Shipping & Logistics
        st.markdown("##### **Jiomart Shipping & Logistics**")

        col_weight, col_zone = st.columns(2)
        with col_weight:
            weight_in_kg = st.number_input(
                "Product Weight (KG)", min_value=0.1, value=0.5, step=0.1, format="%.2f", key="single_weight",
                help="Enter the weight of the product for shipping fee calculation."
            )
        with col_zone:
            shipping_zone = st.selectbox(
                "Shipping Zone:", ('Local', 'Regional', 'National'), index=0, key="single_zone",
                help="Select the shipping zone for the product."
            )
        
        # 2. Single Flat Brand Fee Benefit Rate
        st.markdown("##### **Flat Brand Fee Benefit Rate (as % of Sale Price)**")
        
        jiomart_benefit_rate = st.number_input(
            "Benefit Rate (%)", min_value=0.0, **max_value=50.0**, value=1.0, step=0.1, format="%.2f", 
            help="Flat Brand Fee Benefit Rate applied to Sale Price across all zones.", key="flat_benefit_rate"
        ) / 100.0
        
    
    # --- Common Inputs ---
    col_cost, col_target = st.columns(2)
    with col_cost:
        product_cost = st.number_input("Product Cost (₹)", min_value=0.0, value=1000.0, step=10.0, key="single_cost")

    with col_target:
        product_margin_target_rs = st.number_input("Target Net Profit (₹)", min_value=0.0, value=200.0, step=10.0, key="single_target")

    st.divider()

    # --- MRP/Discount/WDP Inputs ---
    col_mrp_in, col_price_in = st.columns(2)
    new_mrp = col_mrp_in.number_input("Product MRP (₹)", min_value=1.0, value=2500.0, step=100.0, key="new_mrp")
    new_discount = 0.0
    wrong_defective_price = None
    
    calculated_wdp_for_target = None 

    if platform_selector == 'Meesho':
        if is_wdp_calculated:
            col_price_in.info(f"WDP will be calculated to achieve Target Profit of ₹ {product_margin_target_rs:,.2f}")
        else:
            wrong_defective_price = col_price_in.number_input(
                "Wrong/Defective Price (₹)", min_value=0.0, max_value=new_mrp, value=min(new_mrp, 2000.0), step=10.0, 
                key="meesho_wdp_manual", help="This is the value Meesho uses for charging its fees (Payout Value). This is treated as the Sale Price."
            )
            new_discount = 0.0
    
    else:
        if single_calc_mode == 'Profit Calculation':
            new_discount = col_price_in.number_input("Discount Amount (₹)", min_value=0.0, max_value=new_mrp, value=500.0, step=10.0, key="new_discount_manual")
        else:
            col_price_in.info(f"Targeting a Net Profit of ₹ {product_margin_target_rs:,.2f}...")

    st.divider()

    if new_mrp > 0 and product_cost > 0:
        # --- Input Validation ---
        if platform_selector == 'Jiomart' and jiomart_category is None:
            st.warning("Please select a **Product Category** for Jiomart Commission calculation.")
            st.stop()
        if platform_selector == 'Myntra' and (myntra_brand is None or myntra_category is None):
            st.warning("Please select a **Brand and Category** for Myntra calculation.")
            st.stop()
        # ------------------------

        try:
            # --- CALCULATION BLOCK (Single) ---
            
            if single_calc_mode == 'Target Discount':
                # Pass the single rate for Jiomart
                calculated_discount, initial_max_profit, calculated_discount_percent = find_discount_for_target_profit(
                    new_mrp, product_margin_target_rs, apply_royalty, marketing_fee_rate, product_cost, platform_selector,
                    weight_in_kg, shipping_zone, jiomart_category, meesho_charge_rate, wrong_defective_price,
                    myntra_brand, myntra_category, jiomart_benefit_rate
                )
                
                if calculated_discount is None:
                    st.error(f"Cannot achieve the Target Profit of ₹ {product_margin_target_rs:,.2f}. The maximum possible Net Profit at 0% discount is ₹ {initial_max_profit:,.2f}.")
                    st.stop()
                    
                new_discount = calculated_discount
                if platform_selector == 'Meesho':
                    wrong_defective_price = new_mrp - calculated_discount
                    calculated_wdp_for_target = wrong_defective_price 

            # Perform final calculation 
            (sale_price, gt_charge, customer_paid_amount, royalty_fee,
             marketing_fee_base, current_marketing_fee_rate, final_commission,
             commission_rate, settled_amount, taxable_amount_value,
             net_profit, tds, tcs, invoice_tax_rate, jiomart_fixed_fee_base, jiomart_shipping_fee_base,
             jiomart_benefit_amount, jiomart_total_fee_base, jiomart_final_applicable_fee_base, jiomart_gst_on_fees) = perform_calculations(
                 new_mrp, new_discount, apply_royalty, marketing_fee_rate, product_cost, platform_selector,
                 weight_in_kg, shipping_zone, jiomart_category, meesho_charge_rate, wrong_defective_price,
                 myntra_brand, myntra_category, jiomart_benefit_rate # Pass the single rate
                )


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
                        label="Discount Amount", value=f"₹ {new_discount:,.2f}",
                        delta=f"{discount_percent:,.2f}% of MRP", delta_color="off"
                    )
                    col3_l.metric(label="Sale Price (₹)", value=f"₹ {sale_price:,.2f}")
                    st.markdown("---")
                    
                    # Display Fixed/Shipping Charges
                    if platform_selector == 'Jiomart':
                        
                        st.markdown("###### **Jiomart Fee Breakup (Base)**")
                        col4_l, col5_l, col6_l, col7_l = st.columns(4)
                        
                        comm_base_display = jiomart_total_fee_base - jiomart_fixed_fee_base - jiomart_shipping_fee_base
                        col4_l.metric(label="1. Comm Fee Base", value=f"₹ {comm_base_display:,.2f}")
                        col5_l.metric(label="2. Fixed Fee Base", value=f"₹ {jiomart_fixed_fee_base:,.2f}")
                        col6_l.metric(label="3. Shipping Fee Base", value=f"₹ {jiomart_shipping_fee_base:,.2f}")
                        col7_l.metric(label="Total Fee (1+2+3)", value=f"₹ {jiomart_total_fee_base:,.2f}")
                        
                        st.markdown("---")
                        col8_l, col9_l, col10_l = st.columns(3)
                        
                        col8_l.metric(
                            label=f"Benefit ({jiomart_benefit_rate * 100:,.2f}%)",
                            value=f"₹ {abs(jiomart_benefit_amount):,.2f}",
                            delta="Deduction from Fees", delta_color="normal"
                        )
                        
                        col9_l.metric(label="Final Applicable Fee (B)", value=f"₹ {jiomart_final_applicable_fee_base:,.2f}")
                        col10_l.metric(label="GST @ 18% (C) on (B)", value=f"₹ {jiomart_gst_on_fees:,.2f}")

                        st.markdown("---")
                        st.metric(label="**Invoice Value (CPA) / Net Sale**", value=f"₹ {customer_paid_amount:,.2f}")
                        
                    else:
                        col4_l, col5_l = st.columns(2)
                        fixed_charge_label = ""
                        if platform_selector == 'Myntra':
                            fixed_charge_label = "GT Charge (Deducted from Sale Price)"
                        elif platform_selector == 'Ajio':
                            fixed_charge_label = "SCM Charges (₹95 + 18% GST)"
                        else: # FirstCry
                            fixed_charge_label = "Fixed Charges"
                            
                        col4_l.metric(label=fixed_charge_label, value=f"₹ {gt_charge:,.2f}", delta_color="off")
                        col5_l.metric(label="**Invoice Value (CPA)**", value=f"₹ {customer_paid_amount:,.2f}")

                else: # MEESHO Display (WDP = Sale Price = CPA)
                    display_wdp = calculated_wdp_for_target if calculated_wdp_for_target is not None else wrong_defective_price
                    calculated_discount = new_mrp - display_wdp
                    discount_percent = (calculated_discount / new_mrp) * 100 if new_mrp > 0 else 0.0
                    
                    col2_l.metric(label="Discount Amount (MRP - WDP)", value=f"₹ {calculated_discount:,.2f}", delta=f"{discount_percent:,.2f}% of MRP", delta_color="off")
                    col3_l.metric(label="Sale Price (WDP)", value=f"₹ {sale_price:,.2f}")
                    st.markdown("---")
                    
                    if is_wdp_calculated:
                         col4_l, col5_l = st.columns(2)
                         col4_l.metric(label="Target WDP (Required for Profit)", value=f"₹ {display_wdp:,.2f}", delta_color="off")
                         col5_l.metric(label="**Invoice Value (CPA)**", value=f"₹ {customer_paid_amount:,.2f}")
                    else:
                         col4_l, col5_l = st.columns(2)
                         col4_l.metric(label="Fixed/Shipping Charges", value=f"₹ 0.00", delta_color="off")
                         col5_l.metric(label="**Invoice Value (CPA)**", value=f"₹ {customer_paid_amount:,.2f}")


            # =========== RIGHT COLUMN: Deductions and Final Payout ===========
            with col_right:
                st.markdown("###### **3. Deductions (Charges)**")

                col1_r, col2_r, col3_r = st.columns(3)

                # Commission/Platform Fee
                if platform_selector == 'Jiomart':
                    platform_fee_label = "**Total Platform Fee (B+C)**"
                    platform_fee_value = jiomart_final_applicable_fee_base + jiomart_gst_on_fees
                else:
                    platform_fee_label = f"Platform Fee / Commission (Incl. GST)"
                    platform_fee_value = final_commission + gt_charge
                    if platform_selector == 'FirstCry':
                        platform_fee_label = "**Flat Deduction (42%)**"
                        platform_fee_value = final_commission
                    elif platform_selector == 'Meesho':
                         platform_fee_label = f"Meesho Fee ({meesho_charge_rate*100:.2f}% of WDP + Tax)"
                         platform_fee_value = final_commission

                col1_r.metric(label=platform_fee_label, value=f"₹ {platform_fee_value:,.2f}")

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
                col6_r.metric(label="TCS (10% on Tax Amt)", value=f"₹ {abs(tcs):,.2f}")

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

        except Exception as e:
            st.error(f"An error occurred during calculation: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    else:
        st.info("Please enter a valid MRP and Product Cost to start the calculation.")


elif calculation_mode == 'B. Bulk Processing (Excel)':
    # ... [Bulk Processing Logic Remains] ...
    st.markdown("##### **Excel Bulk Processing**")
    st.info("ℹ️ Please use the template provided below before uploading your file. **Note: For Jiomart, the 'Jiomart\_Benefit\_Rate' column is the single percentage rate applied across all shipping zones.**")

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
                try:
                    input_df = pd.read_csv(uploaded_file)
                except UnicodeDecodeError:
                    input_df = pd.read_csv(uploaded_file, encoding='latin1')
            else:
                input_df = pd.read_excel(uploaded_file)
            
            # Ensure all required columns for calculation are present
            required_cols = ['SKU', 'MRP', 'Discount', 'Product_Cost', 'Platform', 'Apply_Royalty', 'Marketing_Fee_Rate', 'Weight_in_KG', 'Shipping_Zone', 'Jiomart_Category', 'Wrong_Defective_Price', 'Meesho_Charge_Rate', 'Myntra_Brand', 'Myntra_Category', 'Jiomart_Benefit_Rate']
            for col in required_cols:
                if col not in input_df.columns:
                    if col in ['Wrong_Defective_Price', 'Meesho_Charge_Rate', 'Myntra_Brand', 'Myntra_Category', 'Jiomart_Benefit_Rate']:
                        input_df[col] = np.nan
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

            # Rename 'Platform_Fee' column for clarity in bulk view
            output_df = output_df.rename(columns={'Platform_Fee_Incl_GST': 'Platform_Fee_Incl_GST'})

            # Display results
            st.dataframe(output_df.style.format({
                'MRP': "₹ {:,.2f}",
                'Discount': "₹ {:,.2f}",
                'Sale_Price': "₹ {:,.2f}",
                'Product_Cost': "₹ {:,.2f}",
                'Royalty': "₹ {:,.2f}",
                'Platform_Fee_Incl_GST': "₹ {:,.2f}", # Updated name
                'Fixed/Shipping_Charge': "₹ {:,.2f}",
                'Jiomart_Benefit': "₹ {:,.2f}", 
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
            st.info("Please ensure your column names match the template and the data is in the correct format.")

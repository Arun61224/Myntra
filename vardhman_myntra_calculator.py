import pandas as pd
import streamlit as st
import numpy as np
from io import BytesIO

# Set page config for wide layout and minimum gaps, using the specified full title
FULL_TITLE = "Vardhman Wool Store E-commerce Calculator"
st.set_page_config(layout="wide", page_title=FULL_TITLE, page_icon="🛍️")

# --- Custom CSS for Compactness & VERTICAL SEPARATION ---
st.markdown("""
<style>
    /* ... (CSS code remains the same as your original file) ... */
    .block-container {
        padding-top: 1.25rem; padding-bottom: 0.5rem; padding-left: 1rem;
        padding-right: 1rem; max-width: 1840px; margin-left: auto; margin-right: auto;
    }
    h1, h2, h3, h4, h5, h6 { margin-top: 0.5rem; margin-bottom: 0.25rem; }
    h1 { font-size: 2.25rem; line-height: 1.1; margin-top: 1.0rem; }
    hr { margin: 0.5rem 0 !important; }
    [data-testid="stMetric"] { padding-top: 0px; padding-bottom: 0px; }
    [data-testid="stMetricLabel"] { margin-bottom: -0.1rem; font-size: 0.8rem; }
    [data-testid="stMetricValue"] { font-size: 1.5rem; }
    .st-emotion-cache-12quz0q { gap: 0.75rem; }
    div[data-testid="stHorizontalBlock"] > div:nth-child(1) {
        border-right: 1px solid rgba(255, 255, 255, 0.1); padding-right: 1rem;
    }
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) { padding-left: 1rem; }
</style>
""", unsafe_allow_html=True)


# ==============================================================================
# --- (NEW) MYNTRA COMMISSION & DATA STRUCTURE (v3) ---
# YEH DATA AAP FUTURE MEIN AASANI SE EDIT KAR SAKTE HO
# ==============================================================================

# Structure: Brand -> Category -> Gender -> Price Slabs
MYNTRA_COMMISSION_DATA = {
    "KUCHIPOO": {
        "Sweatshirts": {
            "Boys": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29},
            "Girls": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29}
        },
        "Clothing Set": {
            "Boys": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29},
            "Girls": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29}
        },
        "Tshirts": {
            "Boys": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29},
            "Girls": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29}
        },
        "Track Pants": {
            "Boys": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29},
            "Girls": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29}
        },
        "Shorts": {
            "Boys": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29},
            "Girls": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29}
        },
        "Dresses": {
            "Girls": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29}
        },
        "Sweaters": {
            "Boys": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29},
            "Girls": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29}
        },
        "Jeans": {
            "Boys": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29},
            "Girls": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29}
        },
        "Kurta Sets": {
            "Boys": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29},
            "Girls": {"0-200": 0.33, "200-300": 0.22, "300-400": 0.19, "400-500": 0.22, "500-800": 0.24, "800+": 0.29}
        }
    },
    "YK": {
        "Clothing Set": {
            "Boys": {"0-300": 0.05, "300-500": 0.05, "500-1000": 0.06, "1000-2000": 0.04, "2000+": 0.04},
            "Girls": {"0-300": 0.04, "300-500": 0.05, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.07}
        },
        "Dresses": {
            "Girls": {"0-300": 0.07, "300-500": 0.05, "500-1000": 0.04, "1000-2000": 0.00, "2000+": 0.00}
        },
        "Lounge Pants": { # Assuming this applies to both, as per image
            "Boys": {"0-300": 0.09, "300-500": 0.09, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.06},
            "Girls": {"0-300": 0.09, "300-500": 0.09, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.06}
        },
        "Shorts": {
            "Boys": {"0-300": 0.09, "300-500": 0.09, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.08},
            "Girls": {"0-300": 0.09, "300-500": 0.09, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.08}
        },
        "Sweatshirts": {
            "Boys": {"0-300": 0.01, "300-500": 0.03, "500-1000": 0.07, "1000-2000": 0.07, "2000+": 0.09},
            "Girls": {"0-300": 0.01, "300-500": 0.03, "500-1000": 0.05, "1000-2000": 0.06, "2000+": 0.08}
        },
        "Track Pants": {
            "Boys": {"0-300": 0.08, "300-500": 0.08, "500-1000": 0.07, "1000-2000": 0.06, "2000+": 0.08},
            "Girls": {"0-300": 0.05, "300-500": 0.08, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.08}
        },
        "Tshirts": {
            "Boys": {"0-300": 0.10, "300-500": 0.10, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.08},
            "Girls": {"0-300": 0.10, "300-500": 0.10, "500-1000": 0.06, "1000-2000": 0.07, "2000+": 0.08}
        }
    },
    "YK Disney": {
        "Clothing Set": {
            "Boys": {"0-300": 0.09, "300-500": 0.09, "500-1000": 0.05, "1000-2000": 0.06, "2000+": 0.08},
            "Girls": {"0-300": 0.09, "300-500": 0.09, "500-1000": 0.06, "1000-2000": 0.05, "2000+": 0.08}
        },
        "Dresses": {
            "Girls": {"0-300": 0.08, "300-500": 0.08, "500-1000": 0.06, "1000-2000": 0.04, "2000+": 0.08}
        },
        "Lounge Pants": {
            "Boys": {"0-300": 0.09, "300-500": 0.09, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.06},
            "Girls": {"0-300": 0.09, "300-500": 0.09, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.06}
        },
        "Shorts": {
            "Boys": {"0-300": 0.09, "300-500": 0.09, "500-1000": 0.06, "1000-2000": 0.05, "2000+": 0.08},
            "Girls": {"0-300": 0.09, "300-500": 0.09, "500-1000": 0.06, "1000-2000": 0.05, "2000+": 0.08}
        },
        "Sweatshirts": {
            "Boys": {"0-300": 0.01, "300-500": 0.03, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.08},
            "Girls": {"0-300": 0.01, "300-500": 0.03, "500-1000": 0.06, "1000-2000": 0.04, "2000+": 0.08}
        },
        "Track Pants": {
            "Boys": {"0-300": 0.08, "300-500": 0.08, "500-1000": 0.06, "1000-2000": 0.04, "2000+": 0.08},
            "Girls": {"0-300": 0.08, "300-500": 0.08, "500-1000": 0.05, "1000-2000": 0.05, "2000+": 0.08}
        },
        "Tshirts": {
            "Boys": {"0-300": 0.10, "300-500": 0.10, "500-1000": 0.06, "1000-2000": 0.05, "2000+": 0.08},
            "Girls": {"0-300": 0.10, "300-500": 0.10, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.08}
        }
    },
    "YK Marvel": {
        "Clothing Set": {
            "Boys": {"0-300": 0.09, "300-500": 0.09, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.08}
        },
        "Lounge Pants": {
            "Boys": {"0-300": 0.09, "300-500": 0.09, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.06}
        },
        "Shorts": {
            "Boys": {"0-300": 0.09, "300-500": 0.09, "500-1000": 0.06, "1000-2000": 0.03, "2000+": 0.08}
        },
        "Sweatshirts": {
            "Boys": {"0-300": 0.01, "300-500": 0.03, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.08}
        },
        "Track Pants": {
            "Boys": {"0-300": 0.08, "300-500": 0.08, "500-1000": 0.05, "1000-2000": 0.04, "2000+": 0.08}
        },
        "Tshirts": {
            "Boys": {"0-300": 0.10, "300-500": 0.10, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.08}
        }
    }
}

# --- (NEW) Helper function to get Myntra commission rate ---
def get_myntra_new_commission_rate(brand, category, gender, seller_price):
    try:
        brand_data = MYNTRA_COMMISSION_DATA.get(brand)
        if not brand_data: return 0.0
        
        category_data = brand_data.get(category)
        if not category_data: return 0.0
        
        gender_data = category_data.get(gender)
        if not gender_data: return 0.0
        
        # Find the correct slab
        if brand == "KUCHIPOO":
            if seller_price <= 200: return gender_data["0-200"]
            elif seller_price <= 300: return gender_data["200-300"]
            elif seller_price <= 400: return gender_data["300-400"]
            elif seller_price <= 500: return gender_data["400-500"]
            elif seller_price <= 800: return gender_data["500-800"]
            else: return gender_data["800+"]
        else: # YK, YK Disney, YK Marvel
            if seller_price <= 300: return gender_data["0-300"]
            elif seller_price <= 500: return gender_data["300-500"]
            elif seller_price <= 1000: return gender_data["500-1000"]
            elif seller_price <= 2000: return gender_data["1000-2000"]
            else: return gender_data["2000+"]
            
    except Exception:
        return 0.0 # Fail safe

# --- (NEW) Helper function to get Myntra Fixed Fee (incl. GST) ---
def calculate_myntra_new_fixed_fee(brand, sale_price):
    GST_RATE_FEES = 0.18
    base_fee = 0.0
    
    if brand == "KUCHIPOO":
        base_fee = 0.0
    else: # YK, YK Disney, YK Marvel
        if sale_price <= 1000:
            base_fee = 27.0
        elif sale_price <= 2000:
            base_fee = 45.0
        else: # 2000+
            base_fee = 61.0
            
    final_fee = base_fee * (1 + GST_RATE_FEES)
    return final_fee

# --- (NEW) Helper function to get Myntra Royalty ---
def calculate_myntra_new_royalty(brand, sale_price, apply_kuchipoo_royalty_flag):
    royalty_rate = 0.0
    
    if brand == "YK":
        royalty_rate = 0.01 # 1%
    elif brand == "YK Disney":
        royalty_rate = 0.07 # 7%
    elif brand == "YK Marvel":
        royalty_rate = 0.07 # 7%
    elif brand == "KUCHIPOO" and apply_kuchipoo_royalty_flag == 'Yes':
        royalty_rate = 0.10 # 10%
        
    return sale_price * royalty_rate


# --- (EXISTING) Jiomart Functions (No Change) ---
def calculate_jiomart_fixed_fee_base(sale_price):
    if sale_price <= 500: return 15.00
    elif sale_price <= 1000: return 20.00
    else: return 30.00

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
    if not rates: return 0.0
    if sale_price <= 500: return rates["0-500"]
    else: return rates["500+"]

# --- (EXISTING) Common Tax Function (No Change) ---
def calculate_taxable_amount_value(customer_paid_amount):
    if customer_paid_amount >= 2500:
        tax_rate = 0.12
        divisor = 1.12
    else:
        tax_rate = 0.05
        divisor = 1.05
    taxable_amount = customer_paid_amount / divisor
    return taxable_amount, tax_rate

# ==============================================================================
# --- (HEAVILY MODIFIED) CORE CALCULATION LOGIC ---
# ==============================================================================
def perform_calculations(mrp, discount, 
                             # Common Params
                             product_cost, platform,
                             # Myntra v3 Params
                             myntra_new_brand=None, myntra_new_category=None, myntra_new_gender=None,
                             apply_kuchipoo_royalty='No',
                             # Jiomart Params
                             weight_in_kg=0.0, shipping_zone=None, jiomart_category=None, jiomart_benefit_rate=0.0,
                             # Meesho Params
                             meesho_charge_rate=0.0, wrong_defective_price=None,
                             # --- (DEPRECATED PARAMS - kept for safety, but not used by Myntra) ---
                             apply_royalty='No', marketing_fee_rate=0.0):
    
    # Initialize common variables
    gt_charge = 0.0 # This will store the FINAL Fixed Fee (incl. GST)
    royalty_fee = 0.0
    marketing_fee_base = 0.0 # Myntra v3 mein use nahi hoga
    final_commission = 0.0
    commission_rate = 0.0
    
    # Jiomart specific
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
        if wrong_defective_price is not None and wrong_defective_price > 0:
            customer_paid_amount = wrong_defective_price
        else:
            # If no WDP is given, assume it's same as MRP (0 discount)
            customer_paid_amount = mrp
            
        sale_price = customer_paid_amount
        discount = mrp - sale_price # Recalculate discount based on WDP

        commission_rate = meesho_charge_rate
        commission_base = customer_paid_amount * commission_rate
        commission_tax = commission_base * GST_RATE_FEES
        final_commission = commission_base + commission_tax
        # (Other fees are 0 for Meesho in this logic)
        gt_charge = 0.0
        marketing_fee_base = 0.0
        royalty_fee = 0.0
        total_fixed_charge = 0.0

    else:
        # --- All other platforms start with Sale Price ---
        sale_price = mrp - discount
        
        if sale_price < 0:
            # Return empty/error values
            return (sale_price, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -99999999.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)

        # Invoice value is Sale Price for all non-Meesho platforms
        customer_paid_amount = sale_price

        if platform == 'Myntra':
            # --- (NEW) MYNTRA v3 LOGIC ---
            
            # 1. Calculate New Fixed Fee (GT Charge)
            # gt_charge mein FINAL fee (incl. GST) store hogi
            gt_charge = calculate_myntra_new_fixed_fee(myntra_new_brand, sale_price)
            total_fixed_charge = gt_charge # For display
            
            # 2. Calculate "Seller Price" (Base for Commission)
            seller_price = sale_price - gt_charge
            
            # 3. Get Commission Rate based on Seller Price
            commission_rate = get_myntra_new_commission_rate(myntra_new_brand, myntra_new_category, myntra_new_gender, seller_price)
            
            # 4. Calculate Final Commission (Base + GST)
            commission_base = seller_price * commission_rate
            commission_tax = commission_base * GST_RATE_FEES
            final_commission = commission_base + commission_tax
            
            # 5. Calculate New Royalty (Base is Sale Price)
            royalty_fee = calculate_myntra_new_royalty(myntra_new_brand, sale_price, apply_kuchipoo_royalty)
            
            # 6. Marketing fee 0 hai (as per new rules)
            marketing_fee_base = 0.0
            
            
        elif platform == 'FirstCry':
            commission_rate = 0.42
            final_commission = sale_price * commission_rate
            gt_charge = 0.0
            marketing_fee_base = 0.0
            total_fixed_charge = 0.0
            royalty_fee = sale_price * 0.10 if apply_royalty == 'Yes' else 0.0 # Old royalty logic

        elif platform == 'Ajio':
            commission_rate = 0.20
            commission_base = sale_price * commission_rate
            commission_tax = commission_base * 0.18
            final_commission = commission_base + commission_tax
            scm_base = 95.0
            scm_tax = scm_base * 0.18
            gt_charge = scm_base + scm_tax
            marketing_fee_base = 0.0
            total_fixed_charge = gt_charge
            royalty_fee = sale_price * 0.10 if apply_royalty == 'Yes' else 0.0 # Old royalty logic

        elif platform == 'Snapdeal':
            # --- SNAPDEAL LOGIC (from previous update) ---
            commission_rate = 0.24
            commission_base = round(sale_price * commission_rate)
            commission_tax = round(commission_base * GST_RATE_FEES)
            final_commission = commission_base + commission_tax
            
            ro_base = round(sale_price * 0.08)
            ro_tax = round(ro_base * 0.14)
            gt_charge = ro_base + ro_tax
            
            marketing_fee_base = 0.0
            total_fixed_charge = gt_charge
            royalty_fee = sale_price * 0.10 if apply_royalty == 'Yes' else 0.0 # Old royalty logic

        elif platform == 'Jiomart':
            
            # 1. Base Fees
            commission_rate = get_jiomart_commission_rate(jiomart_category, sale_price) if jiomart_category else 0.0
            jiomart_comm_fee_base = sale_price * commission_rate
            jiomart_fixed_fee_base = calculate_jiomart_fixed_fee_base(sale_price)
            jiomart_shipping_fee_base = calculate_jiomart_shipping_fee_base(weight_in_kg, shipping_zone) if shipping_zone and weight_in_kg > 0 else 0.0
            
            # 2. Total Fee (1+2+3)
            jiomart_total_fee_base = jiomart_comm_fee_base + jiomart_fixed_fee_base + jiomart_shipping_fee_base
            
            # 3. Brand Fee Benefit
            jiomart_benefit_amount = -(sale_price * jiomart_benefit_rate)
            
            # 4. Final Applicable Fee (B)
            jiomart_final_applicable_fee_base = jiomart_total_fee_base + jiomart_benefit_amount
            
            # 5. GST @ 18% (C) - Applied ONLY to the Final Applicable Fee (B)
            jiomart_gst_on_fees = jiomart_final_applicable_fee_base * GST_RATE_FEES
            
            # 6. Total Platform Deduction
            total_platform_deduction = jiomart_final_applicable_fee_base + jiomart_gst_on_fees
            
            # Proxies for common fields
            final_commission = jiomart_comm_fee_base # Storing base comm
            total_fixed_charge = jiomart_fixed_fee_base + jiomart_shipping_fee_base
            gt_charge = total_fixed_charge # Using gt_charge for deduction logic
            
            # Old royalty logic
            royalty_fee = sale_price * 0.10 if apply_royalty == 'Yes' else 0.0

            
    # --- COMMON TAX AND FINAL SETTLEMENT LOGIC ---
    # Based on Customer Paid Amount (Invoice Value)
    taxable_amount_value, invoice_tax_rate = calculate_taxable_amount_value(customer_paid_amount)
    tax_amount = customer_paid_amount - taxable_amount_value
    tds = taxable_amount_value * 0.001
    tcs = tax_amount * 0.10 # Your script had 0.10 (10%)

    # DEDUCTIONS
    if platform == 'Jiomart':
        total_deductions = total_platform_deduction + royalty_fee # Marketing fee is 0
    elif platform == 'Myntra':
         total_deductions = final_commission + royalty_fee + gt_charge # gt_charge is new fixed fee
    elif platform == 'Meesho':
        total_deductions = final_commission # Royalty, GT, Marketing are 0
    else: # Ajio, FirstCry, Snapdeal
        total_deductions = final_commission + royalty_fee + marketing_fee_base + gt_charge
        
    # FINAL SETTLEMENT
    settled_amount = customer_paid_amount - total_deductions - tds - tcs
    net_profit = settled_amount - product_cost

    return (sale_price, total_fixed_charge, customer_paid_amount, royalty_fee,
            marketing_fee_base, 0.0, # Marketing rate is 0 for Myntra v3
            final_commission, 
            commission_rate, settled_amount, taxable_amount_value,
            net_profit, tds, tcs, invoice_tax_rate, 
            jiomart_fixed_fee_base, jiomart_shipping_fee_base,
            jiomart_benefit_amount, # Brand Fee Benefit (negative value)
            jiomart_total_fee_base, # Total Base Fee (1+2+3)
            jiomart_final_applicable_fee_base, # Final Applicable Fee (B) base
            jiomart_gst_on_fees # GST @ 18% (C)
            )

# --- (MODIFIED) Target Discount Function ---
def find_discount_for_target_profit(mrp, target_profit, product_cost, platform,
                                        # Myntra v3
                                        myntra_new_brand=None, myntra_new_category=None, myntra_new_gender=None,
                                        apply_kuchipoo_royalty='No',
                                        # Jiomart
                                        weight_in_kg=0.0, shipping_zone=None, jiomart_category=None, jiomart_benefit_rate=0.0,
                                        # Meesho
                                        meesho_charge_rate=0.0, wrong_defective_price=None, # WDP is NOT used for finding, only for final calc
                                        # Deprecated
                                        apply_royalty='No'):
    """Finds the maximum discount allowed (in 1.0 steps) to achieve at least the target profit."""

    # Helper function to get the 11th return value (net_profit)
    def get_profit(disc, wdp=None):
        results = perform_calculations(mrp, disc, product_cost, platform,
                                           myntra_new_brand, myntra_new_category, myntra_new_gender,
                                           apply_kuchipoo_royalty,
                                           weight_in_kg, shipping_zone, jiomart_category, jiomart_benefit_rate,
                                           meesho_charge_rate, wdp,
                                           apply_royalty, 0.0) # Pass 0 for deprecated marketing fee
        return results[10]

    if platform == 'Meesho':
        # Calculate profit at WDP=MRP (0 discount)
        max_profit = get_profit(0.0, mrp) 
        if max_profit < target_profit:
            return None, max_profit, 0.0 # Return (None, MaxProfit, 0% discount)
            
        wdp_step = 1.0
        required_wdp = mrp

        while required_wdp >= 0:
            current_profit = get_profit(0.0, round(required_wdp, 2)) # Pass 0 for discount, WDP for wdp
            if current_profit < target_profit:
                # We went one step too far. Go back one step.
                final_wdp = required_wdp + wdp_step
                target_wdp = min(final_wdp, mrp) # Don't go above MRP
                
                discount_amount = mrp - target_wdp # This is the "discount"
                discount_percent = (discount_amount / mrp) * 100 if mrp > 0 else 0.0
                final_profit = get_profit(0.0, target_wdp)
                return discount_amount, final_profit, discount_percent 
            required_wdp -= wdp_step
            
        # If loop finishes, it means even at WDP=0, profit is >= target
        final_profit = get_profit(0.0, 0.0)
        return mrp, final_profit, 100.0 # Return (Full Discount, Profit at 0 WDP, 100% discount)

    # Original logic for other platforms
    initial_profit = get_profit(0.0) # Profit at 0 discount
    if initial_profit < target_profit:
        return None, initial_profit, 0.0 # Return (None, MaxProfit, 0% discount)

    discount_step = 1.0
    required_discount = 0.0
    while required_discount <= mrp:
        current_profit = get_profit(required_discount)
        if current_profit < target_profit:
            # We went one step too far. Go back one step.
            final_discount = max(0.0, required_discount - discount_step)
            final_profit = get_profit(final_discount)
            discount_percent = (final_discount / mrp) * 100
            return final_discount, final_profit, discount_percent
        required_discount += discount_step

    # If loop finishes, it means even at 100% discount, profit is >= target
    final_profit = get_profit(mrp)
    return mrp, final_profit, 100.0


# --- (MODIFIED) Bulk Calculation Handler ---
def bulk_process_data(df, mode='Profit Calculation'):
    """Processes DataFrame rows for multi-platform profit calculation."""
    results = []
    
    # --- (FIX v3.8) NORMALISE ALL COLUMN NAMES (case-insensitive) ---
    df.columns = [str(col).strip().title() for col in df.columns]

    # --- (FIX v4.1) Force ALL columns to string type first to avoid date conversion errors ---
    for col in df.columns:
        df[col] = df[col].astype(str)

    # --- (FIX v3.9) Coerce all numeric columns to numbers, non-numeric text becomes NaN ---
    # This fixes errors if columns contain empty strings '' or text 'NA'
    num_cols = ['Mrp', 'Discount', 'Product_Cost', 'Target_Profit', 'Weight_In_Kg', 
                'Jiomart_Benefit_Rate', 'Wrong_Defective_Price', 'Meesho_Charge_Rate', 
                'Marketing_Fee_Rate']
    for col in num_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce') # This turns '', 'NA' etc. into np.nan
        # No need for else, fillna will handle missing columns later if we add them to check

    # --- (FIX v3.8 & v3.9) Fill default/missing values (np.nan) for ALL columns using TitleCase ---
    df['Apply_Royalty'] = df['Apply_Royalty'].fillna('No')
    df['Marketing_Fee_Rate'] = df['Marketing_Fee_Rate'].fillna(0.0) 
    df['Weight_In_Kg'] = df['Weight_In_Kg'].fillna(0.5) # Renamed
    df['Shipping_Zone'] = df['Shipping_Zone'].fillna('Local')
    df['Jiomart_Category'] = df['Jiomart_Category'].fillna(value=None) 
    df['Sku'] = df['Sku'].fillna('') # Renamed
    df['Meesho_Charge_Rate'] = df['Meesho_Charge_Rate'].fillna(0.03)
    df['Wrong_Defective_Price'] = df['Wrong_Defective_Price'].fillna(0.0)
    df['Jiomart_Benefit_Rate'] = df['Jiomart_Benefit_Rate'].fillna(0.0) 
    df['Target_Profit'] = df['Target_Profit'].fillna(0.0) 
    df['Mrp'] = df['Mrp'].fillna(0.0) # Fill NaN Mrp with 0
    df['Product_Cost'] = df['Product_Cost'].fillna(0.0) # Fill NaN Product_Cost with 0
    df['Discount'] = df['Discount'].fillna(0.0) # Fill NaN Discount with 0
    
    # Old Myntra (Deprecated)
    df['Myntra_Brand'] = df['Myntra_Brand'].fillna(value=None) 
    df['Myntra_Category'] = df['Myntra_Category'].fillna(value=None) 
    # (NEW) Myntra v3 Cols
    df['Myntra_New_Brand'] = df['Myntra_New_Brand'].fillna(value=None) 
    df['Myntra_New_Category'] = df['Myntra_New_Category'].fillna(value=None) 
    df['Myntra_New_Gender'] = df['Myntra_New_Gender'].fillna(value=None) 
    df['Apply_Kuchipoo_Royalty'] = df['Apply_Kuchipoo_Royalty'].fillna('No')
    df['Platform'] = df['Platform'].fillna('Unknown') # Add fillna for Platform


    for index, row in df.iterrows():
        try:
            # --- (FIX v3.9) Access columns using TitleCase and check for > 0 ---
            if not pd.notna(row['Mrp']) or row['Mrp'] <= 0 or not pd.notna(row['Product_Cost']) or row['Product_Cost'] <= 0:
                st.warning(f"Skipping row {index + 1} (SKU: {row.get('Sku', 'N/A')}): Missing or invalid (0) required value for Mrp or Product_Cost.")
                results.append({
                    'ID': index + 1,
                    'SKU': row.get('Sku', 'N/A'),
                    'Platform': row.get('Platform', 'N/A'),
                    'Error': 'Missing or invalid (0) Mrp or Product_Cost'
                })
                continue # Skip to the next row

            # --- Prepare ALL inputs ---
            mrp = float(row['Mrp'])
            product_cost = float(row['Product_Cost'])
            platform = str(row['Platform']).strip()
            
            # (NEW) Myntra v3
            myntra_new_brand_bulk = str(row['Myntra_New_Brand']).strip() if pd.notna(row['Myntra_New_Brand']) else None
            myntra_new_category_bulk = str(row['Myntra_New_Category']).strip() if pd.notna(row['Myntra_New_Category']) else None
            myntra_new_gender_bulk = str(row['Myntra_New_Gender']).strip() if pd.notna(row['Myntra_New_Gender']) else None
            apply_kuchipoo_royalty_bulk = str(row['Apply_Kuchipoo_Royalty']).strip()
            
            # Jiomart
            weight_in_kg_bulk = float(row['Weight_In_Kg']) # Renamed
            shipping_zone_bulk = str(row['Shipping_Zone']).strip()
            jiomart_category_bulk = str(row['Jiomart_Category']).strip() if pd.notna(row['Jiomart_Category']) else None
            jiomart_benefit_rate_bulk = float(row['Jiomart_Benefit_Rate'])
            
            # Meesho
            meesho_charge_rate_bulk = float(row['Meesho_Charge_Rate'])
            
            # Other
            sku_bulk = str(row['Sku']).strip() # Renamed
            apply_royalty_bulk = str(row['Apply_Royalty']).strip() # For non-Myntra
            
            # --- (NEW) Mode-based logic ---
            target_profit_bulk = float(row['Target_Profit'])
            discount_from_sheet = float(row['Discount']) if pd.notna(row['Discount']) else 0.0
            wdp_from_sheet = float(row['Wrong_Defective_Price']) if pd.notna(row['Wrong_Defective_Price']) and row['Wrong_Defective_Price'] > 0 else None
            
            discount_to_use = 0.0
            wdp_to_use = None

            if mode == 'Target Discount':
                # --- Target Discount Mode ---
                (calculated_discount, final_profit_at_target, _) = find_discount_for_target_profit(
                    mrp, target_profit_bulk, product_cost, platform,
                    myntra_new_brand_bulk, myntra_new_category_bulk, myntra_new_gender_bulk, apply_kuchipoo_royalty_bulk,
                    weight_in_kg_bulk, shipping_zone_bulk, jiomart_category_bulk, jiomart_benefit_rate_bulk,
                    meesho_charge_rate_bulk, None, # Pass None for WDP, let function calculate it
                    apply_royalty_bulk
                )
                
                if calculated_discount is None:
                    # Cannot achieve target
                    discount_to_use = 0.0 # Use 0 discount
                    if platform == 'Meesho':
                        wdp_to_use = mrp # WDP = MRP (0 discount)
                else:
                    discount_to_use = calculated_discount
                    if platform == 'Meesho':
                        wdp_to_use = mrp - calculated_discount # Set WDP for final calc
            
            else:
                # --- Profit Calculation Mode ---
                discount_to_use = discount_from_sheet
                wdp_to_use = wdp_from_sheet # Use WDP from sheet
            
            # --- Platform-specific variable cleaning (run AFTER mode logic) ---
            if platform != 'Myntra':
                myntra_new_brand_bulk = None
                myntra_new_category_bulk = None
                myntra_new_gender_bulk = None
                apply_kuchipoo_royalty_bulk = 'No'
            if platform != 'Jiomart':
                weight_in_kg_bulk = 0.0
                shipping_zone_bulk = None
                jiomart_category_bulk = None
                jiomart_benefit_rate_bulk = 0.0
            if platform != 'Meesho':
                meesho_charge_rate_bulk = 0.0
                # wdp_to_use = None # Keep this, it's set by target logic
            if platform in ['Myntra', 'Meesho']:
                apply_royalty_bulk = 'No' # Use new Myntra logic or 0 for Meesho


            # --- Perform calculation ---
            (sale_price, gt_charge, customer_paid_amount, royalty_fee,
             marketing_fee_base, current_marketing_fee_rate, final_commission,
             commission_rate, settled_amount, taxable_amount_value,
             net_profit, tds, tcs, invoice_tax_rate, jiomart_fixed_fee_base, jiomart_shipping_fee_base,
             jiomart_benefit_amount, jiomart_total_fee_base, jiomart_final_applicable_fee_base, jiomart_gst_on_fees
             ) = perform_calculations(
                 mrp, discount_to_use, product_cost, platform,
                 myntra_new_brand_bulk, myntra_new_category_bulk, myntra_new_gender_bulk, apply_kuchipoo_royalty_bulk,
                 weight_in_kg_bulk, shipping_zone_bulk, jiomart_category_bulk, jiomart_benefit_rate_bulk,
                 meesho_charge_rate_bulk, wdp_to_use,
                 apply_royalty_bulk, 0.0 # Pass deprecated params
                )
            
            # Recalculate final discount for display (esp. for Meesho)
            final_discount_display = mrp - sale_price

            # Determine fixed/shipping for display
            fixed_shipping_charge = gt_charge # gt_charge now holds the final fixed fee for all platforms
            
            # Determine the Commission/Platform fee to display
            display_commission_fee = final_commission
            if platform == 'Jiomart':
                display_commission_fee = jiomart_final_applicable_fee_base + jiomart_gst_on_fees
            elif platform in ['Ajio', 'Snapdeal', 'Myntra']:
                display_commission_fee = final_commission + gt_charge # Total deduction
            
            # Store result
            result_row = {
                'ID': index + 1,
                'SKU': sku_bulk, # Display 'SKU'
                'Platform': platform,
                'MRP': mrp,
                'Discount': final_discount_display,
                'Sale_Price': sale_price,
                'Target_Profit_In': target_profit_bulk if mode == 'Target Discount' else np.nan,
                'Product_Cost': product_cost,
                'Royalty': royalty_fee,
                'Platform_Fee_Incl_GST': display_commission_fee, 
                'Fixed/Shipping_Charge(Internal)': fixed_shipping_charge,
                'Jiomart_Benefit': abs(jiomart_benefit_amount) if platform == 'Jiomart' else 0.0,
                'TDS': tds,
                'TCS': tcs,
                'Settled_Amount': settled_amount,
                'Net_Profit': net_profit,
                'Margin_%': (net_profit / product_cost) * 100 if product_cost > 0 else 0.0,
                'Error': np.nan # (NEW) Add Error column as nan for successful rows
            }
            results.append(result_row)

        except Exception as e:
            st.warning(f"Error processing row {index + 1} (SKU: {row.get('Sku', 'N/A')}): {e}")
            results.append({
                'ID': index + 1,
                'SKU': row.get('Sku', 'N/A'),
                'Platform': row.get('Platform', 'N/A'),
                'Error': str(e)
            })

    # --- (NEW) Return both dataframes ---
    results_df = pd.DataFrame(results)
    
    # Filter for rows that do NOT have a value in the 'Error' column
    successful_df = results_df[results_df['Error'].isna()].copy()
    
    selling_price_columns = ['SKU', 'Platform', 'MRP', 'Discount', 'Sale_Price', 'Net_Profit']
    # Ensure columns exist before trying to select them
    final_selling_price_cols = [col for col in selling_price_columns if col in successful_df.columns]
    
    selling_price_df = successful_df[final_selling_price_cols]
    
    return results_df, selling_price_df

# --- (NEW) Helper functions for Commission Download ---
def flatten_myntra_data():
    """Converts the nested MYNTRA_COMMISSION_DATA dict to a flat DataFrame."""
    records = []
    for brand, categories in MYNTRA_COMMISSION_DATA.items():
        for category, genders in categories.items():
            for gender, slabs in genders.items():
                for slab, rate in slabs.items():
                    records.append({
                        "Brand": brand,
                        "Category": category,
                        "Gender": gender,
                        "Price_Slab": slab,
                        "Commission_Rate": rate
                    })
    return pd.DataFrame(records)

def get_commission_rates_excel():
    """Generates an Excel file (in-memory) of the Myntra commission rates."""
    df = flatten_myntra_data()
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Myntra_Commission_Rates')
        
        # Auto-format columns
        workbook = writer.book
        worksheet = writer.sheets['Myntra_Commission_Rates']
        worksheet.autofit()
        
        # Add percentage formatting to the rate column
        percent_format = workbook.add_format({'num_format': '0.0%'})
        worksheet.set_column('E:E', 18, percent_format) # Column E is 'Commission_Rate'
        
    processed_data = output.getvalue()
    return processed_data


# --- (MODIFIED) Template Generation ---
def get_excel_template():
    """Generates an Excel template for bulk processing."""
    # --- (FIX v3.8) Use TitleCase for all column names ---
    data = {
        'Sku': ['SKU001', 'SKU002', 'SKU003', 'SKU004', 'SKU005', 'SKU006', 'SKU007'],
        'Mrp': [1000.0, 1500.0, 2000.0, 800.0, 1200.0, 900.0, 1999.0],
        'Discount': [100.0, 300.0, 500.0, 0.0, 0.0, 0.0, 500.0],
        'Product_Cost': [450.0, 600.0, 800.0, 300.0, 500.0, 400.0, 700.0],
        'Target_Profit': [100.0, 150.0, 200.0, 50.0, 120.0, 80.0, 250.0], 
        'Platform': ['Myntra', 'Ajio', 'Jiomart', 'FirstCry', 'Meesho', 'Snapdeal', 'Myntra'],
        'Weight_In_Kg': [0.0, 0.0, 1.2, 0.0, 0.0, 0.0, 0.0], # Renamed
        'Shipping_Zone': [None, None, 'National', None, None, None, None],
        'Jiomart_Category': [None, None, 'Sets Boys', None, None, None, None],
        'Jiomart_Benefit_Rate': [None, None, 0.01, None, None, None, None],
        'Wrong_Defective_Price': [None, None, None, None, 1100.0, None, None],
        'Meesho_Charge_Rate': [None, None, None, None, 0.03, None, None],
        'Marketing_Fee_Rate': [None, None, None, None, None, None, None], 
        'Apply_Royalty': ['No', 'No', 'Yes', 'No', 'No', 'No', 'No'], # For non-Myntra
        'Myntra_New_Brand': ['KUCHIPOO', None, None, None, None, None, 'YK Disney'],
        'Myntra_New_Category': ['Sweatshirts', None, None, None, None, None, 'Tshirts'],
        'Myntra_New_Gender': ['Boys', None, None, None, None, None, 'Girls'],
        'Apply_Kuchipoo_Royalty': ['Yes', 'No', 'No', 'No', 'No', 'No', 'No']
    }
    df = pd.DataFrame(data)

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    
    # --- Sheet 1: Data ---
    df.to_excel(writer, index=False, sheet_name='Data')
    workbook = writer.book
    worksheet = writer.sheets['Data']

    platforms = ','.join(['Myntra', 'FirstCry', 'Ajio', 'Jiomart', 'Meesho', 'Snapdeal'])
    royalty_yes_no = 'Yes,No'
    zones = ','.join(['Local', 'Regional', 'National'])
    jio_categories = ','.join(JIOMART_COMMISSION_RATES.keys())
    
    # New Myntra Validations
    myntra_brands = ','.join(MYNTRA_COMMISSION_DATA.keys())
    all_myntra_categories = set(cat for brand in MYNTRA_COMMISSION_DATA.values() for cat in brand.keys())
    myntra_categories_list = ','.join(all_myntra_categories)
    myntra_genders = 'Boys,Girls'
    
    # --- (FIX v3.8) Data validation column mapping (columns shifted) ---
    worksheet.data_validation('F2:F100', {'validate': 'list', 'source': platforms})
    worksheet.data_validation('G2:G100', {'validate': 'decimal', 'criteria': 'between', 'minimum': 0.0, 'maximum': 99.0}) # Weight_In_Kg
    worksheet.data_validation('H2:H100', {'validate': 'list', 'source': zones}) 
    worksheet.data_validation('I2:I100', {'validate': 'list', 'source': jio_categories}) 
    worksheet.data_validation('J2:J100', {'validate': 'decimal', 'criteria': 'between', 'minimum': 0.0, 'maximum': 0.5}) 
    # M is Marketing_Fee_Rate
    worksheet.data_validation('N2:N100', {'validate': 'list', 'source': royalty_yes_no}) 
    worksheet.data_validation('O2:O100', {'validate': 'list', 'source': myntra_brands})
    worksheet.data_validation('P2:P100', {'validate': 'list', 'source': myntra_categories_list})
    worksheet.data_validation('Q2:Q100', {'validate': 'list', 'source': myntra_genders}) 
    worksheet.data_validation('R2:R100', {'validate': 'list', 'source': royalty_yes_no}) 

    # --- (NEW) Sheet 2: Instructions ---
    instructions_data = [
        {"Platform": "All Platforms", "Required Columns": "Sku, Mrp, Product_Cost, Platform", "Notes": "Yeh columns hamesha bharne hain (Mrp/Cost 0 nahi ho sakte)."},
        {"Platform": "All (Mode: Profit Calc)", "Required Columns": "Discount", "Notes": "Agar 'Profit Calculation' mode select kiya hai. (Meesho ke liye 'Wrong_Defective_Price')"},
        {"Platform": "All (Mode: Target Discount)", "Required Columns": "Target_Profit", "Notes": "Agar 'Target Discount' mode select kiya hai."},
        {"Platform": "---", "Required Columns": "---", "Notes": "---"},
        {"Platform": "Myntra", "Required Columns": "Myntra_New_Brand, Myntra_New_Category, Myntra_New_Gender", "Notes": "Myntra calculations ke liye zaroori."},
        {"Platform": "Myntra (KUCHIPOO)", "Required Columns": "Apply_Kuchipoo_Royalty", "Notes": "Agar brand KUCHIPOO hai, toh 'Yes' ya 'No' select karein."},
        {"Platform": "Jiomart", "Required Columns": "Weight_In_Kg, Shipping_Zone, Jiomart_Category", "Notes": "Jiomart shipping aur commission ke liye zaroori."},
        {"Platform": "Meesho", "Required Columns": "Meesho_Charge_Rate", "Notes": "Default 3% hai, aap badal sakte hain."},
        {"Platform": "Ajio / FirstCry / Snapdeal", "Required Columns": "Apply_Royalty", "Notes": "Optional hai, default 'No' hai."},
        {"Platform": "---", "Required Columns": "---", "Notes": "---"},
        {"Platform": "General Note 1", "Required Columns": "Column Names", "Notes": "Column names (jaise Sku, Mrp) template jaise hi hone chahiye. (Case/space se farak nahi padega)"},
        {"Platform": "General Note 2", "Required Columns": "Blank Cells", "Notes": "Mrp aur Product_Cost ke alawa baaki columns khaali (blank) chhod sakte hain."},
    ]
    instructions_df = pd.DataFrame(instructions_data)
    instructions_df.to_excel(writer, index=False, sheet_name='Instructions')
    
    # Format instructions sheet
    worksheet_instructions = writer.sheets['Instructions']
    worksheet_instructions.set_column('A:A', 25) # Platform
    worksheet_instructions.set_column('B:B', 45) # Required Columns
    worksheet_instructions.set_column('C:C', 70) # Notes

    # --- Close writer ---
    writer.close()
    processed_data = output.getvalue()
    return processed_data

# ==============================================================================
# --- (MODIFIED) STREAMLIT APP STRUCTURE ---
# ==============================================================================

st.title("🛍️ " + FULL_TITLE)
st.markdown("###### **1. Input and Configuration**")

# --- MODE SELECTION ---
col_calc_mode, col_sub_mode_placeholder = st.columns([1, 1])
with col_calc_mode:
    calculation_mode = st.radio(
        "Select Calculation Mode:",
        ('A. Single Product Calculation', 'B. Bulk Processing (Excel)'),
        index=0, label_visibility="visible"
    )

# --- Sub-Mode Placement ---
if calculation_mode == 'A. Single Product Calculation':
    with col_sub_mode_placeholder:
        st.markdown("Select Sub-Mode:")
        single_calc_mode = st.radio(
            "", ('Profit Calculation', 'Target Discount'),
            index=0, label_visibility="collapsed", horizontal=True
        )
else:
    single_calc_mode = 'Profit Calculation' # Default for bulk
    with col_sub_mode_placeholder:
        st.write("") # Keep space
st.divider()

# ==============================================================================
# --- (MODIFIED) SINGLE PRODUCT CALCULATION UI ---
# ==============================================================================
if calculation_mode == 'A. Single Product Calculation':

    platform_selector = st.radio(
        "Select Platform:",
        ('Myntra', 'FirstCry', 'Ajio', 'Jiomart', 'Meesho', 'Snapdeal'),
        index=0, horizontal=True
    )
    st.markdown("##### **Configuration Settings**")
    
    # --- (NEW) Myntra v3 Inputs ---
    myntra_new_brand = None
    myntra_new_category = None
    myntra_new_gender = None
    apply_kuchipoo_royalty = 'No'
    
    # --- (EXISTING) Other Platform Inputs ---
    jiomart_category = None
    jiomart_benefit_rate = 0.0
    weight_in_kg = 0.0
    shipping_zone = None
    meesho_charge_rate = 0.0
    apply_royalty = 'No' # For old platforms
    
    
    if platform_selector == 'Myntra':
        st.info("Myntra calculation is based on new v3 rules (Slab-based Fixed Fee & Commission).")
        
        # --- New Cascading Dropdowns ---
        col_brand, col_cat, col_gen = st.columns(3)
        
        # 1. Brand
        brand_options = list(MYNTRA_COMMISSION_DATA.keys())
        myntra_new_brand = col_brand.selectbox("Select Brand:", brand_options, index=0, key="myntra_brand_v3")
        
        # 2. Category
        try:
            category_options = list(MYNTRA_COMMISSION_DATA[myntra_new_brand].keys())
            myntra_new_category = col_cat.selectbox("Select Category:", category_options, index=0, key="myntra_cat_v3")
        except KeyError:
            st.error(f"No categories found for brand '{myntra_new_brand}'. Please check MYNTRA_COMMISSION_DATA.")
            st.stop()
            
        # 3. Gender
        try:
            gender_options = list(MYNTRA_COMMISSION_DATA[myntra_new_brand][myntra_new_category].keys())
            myntra_new_gender = col_gen.selectbox("Select Gender:", gender_options, index=0, key="myntra_gen_v3")
        except KeyError:
             st.error(f"No genders found for '{myntra_new_brand}' -> '{myntra_new_category}'. Please check MYNTRA_COMMISSION_DATA.")
             st.stop()
        
        # 4. Kuchipoo Royalty Option
        if myntra_new_brand == 'KUCHIPOO':
            apply_kuchipoo_royalty = st.radio(
                "Apply Kuchipoo Royalty (10% of Sale Price)?",
                ('Yes', 'No'), index=1, horizontal=True, key="kuchipoo_royalty_radio"
            )
        
    
    elif platform_selector == 'Jiomart':
        # --- Jiomart Inputs ---
        col_jio_cat, col_jio_benefit = st.columns(2)
        jiomart_category_options = ["Select Category"] + sorted(list(JIOMART_COMMISSION_RATES.keys()))
        selected_jiomart_category = col_jio_cat.selectbox(
            "Product Category for Commission Rate:",
            jiomart_category_options, index=0, key="jiomart_category_selector"
        )
        jiomart_category = None if selected_jiomart_category == "Select Category" else selected_jiomart_category
        
        jiomart_benefit_rate = col_jio_benefit.number_input(
            "Benefit Rate (%)", min_value=0.0, max_value=50.0, value=1.0, step=0.1, format="%.2f", 
            help="Flat Brand Fee Benefit Rate applied to Sale Price.", key="flat_benefit_rate"
        ) / 100.0
        
        st.markdown("##### **Jiomart Shipping & Logistics**")
        col_weight, col_zone = st.columns(2)
        weight_in_kg = col_weight.number_input(
            "Product Weight (KG)", min_value=0.1, value=0.5, step=0.1, format="%.2f", key="single_weight"
        )
        shipping_zone = col_zone.selectbox(
            "Shipping Zone:", ('Local', 'Regional', 'National'), index=0, key="single_zone"
        )

    elif platform_selector == 'Meesho':
        # --- Meesho Inputs ---
        meesho_charge_percent = st.number_input(
            "Meesho Platform Charge (%)", min_value=0.0, max_value=10.0, value=3.0, step=0.1, format="%.2f",
            key="meesho_charge_rate_single"
        ) / 100.0
        meesho_charge_rate = meesho_charge_percent
        
    else:
        # --- Other Platforms (Ajio, FirstCry, Snapdeal) ---
        apply_royalty = st.radio(
            f"Royalty Fee (10% of Sale Price)?",
            ('Yes', 'No'), index=1, horizontal=True, key="old_royalty_radio"
        )

    
    # --- Common Inputs ---
    col_cost, col_target = st.columns(2)
    product_cost = col_cost.number_input("Product Cost (₹)", min_value=0.0, value=1000.0, step=10.0, key="single_cost")
    product_margin_target_rs = col_target.number_input("Target Net Profit (₹)", min_value=0.0, value=200.0, step=10.0, key="single_target")
    st.divider()

    # --- MRP/Discount/WDP Inputs ---
    col_mrp_in, col_price_in = st.columns(2)
    new_mrp = col_mrp_in.number_input("Product MRP (₹)", min_value=1.0, value=2500.0, step=100.0, key="new_mrp")
    new_discount = 0.0
    wrong_defective_price = None
    
    if platform_selector == 'Meesho':
        if single_calc_mode == 'Target Discount':
            col_price_in.info(f"WDP will be calculated to achieve Target Profit of ₹ {product_margin_target_rs:,.2f}")
        else:
            wrong_defective_price = col_price_in.number_input(
                "Wrong/Defective Price (₹)", min_value=0.0, max_value=new_mrp, value=min(new_mrp, 2000.0), step=10.0, 
                key="meesho_wdp_manual"
            )
    
    else:
        if single_calc_mode == 'Profit Calculation':
            new_discount = col_price_in.number_input("Discount Amount (₹)", min_value=0.0, max_value=new_mrp, value=500.0, step=10.0, key="new_discount_manual")
        else:
            col_price_in.info(f"Targeting a Net Profit of ₹ {product_margin_target_rs:,.2f}...")

    st.divider()

    # --- Validation & Calculation Trigger ---
    if new_mrp > 0 and product_cost > 0:
        
        # --- Input Validation ---
        if platform_selector == 'Jiomart' and jiomart_category is None:
            st.warning("Please select a **Product Category** for Jiomart Commission calculation.")
            st.stop()
        if platform_selector == 'Myntra' and not all([myntra_new_brand, myntra_new_category, myntra_new_gender]):
            st.warning("Please select a **Brand, Category, and Gender** for Myntra calculation.")
            st.stop()
        # ------------------------

        try:
            # --- CALCULATION BLOCK (Single) ---
            
            if single_calc_mode == 'Target Discount':
                calculated_discount, initial_max_profit, calculated_discount_percent = find_discount_for_target_profit(
                    new_mrp, product_margin_target_rs, product_cost, platform_selector,
                    myntra_new_brand, myntra_new_category, myntra_new_gender, apply_kuchipoo_royalty,
                    weight_in_kg, shipping_zone, jiomart_category, jiomart_benefit_rate,
                    meesho_charge_rate, None, # Pass None for WDP
                    apply_royalty
                )
                
                if calculated_discount is None:
                    st.error(f"Cannot achieve the Target Profit of ₹ {product_margin_target_rs:,.2f}. The maximum possible Net Profit at 0% discount is ₹ {initial_max_profit:,.2f}.")
                    st.stop()
                    
                new_discount = calculated_discount
                if platform_selector == 'Meesho':
                    wrong_defective_price = new_mrp - calculated_discount

            # Perform final calculation 
            (sale_price, gt_charge, customer_paid_amount, royalty_fee,
             marketing_fee_base, current_marketing_fee_rate, final_commission,
             commission_rate, settled_amount, taxable_amount_value,
             net_profit, tds, tcs, invoice_tax_rate, jiomart_fixed_fee_base, jiomart_shipping_fee_base,
             jiomart_benefit_amount, jiomart_total_fee_base, jiomart_final_applicable_fee_base, jiomart_gst_on_fees
             ) = perform_calculations(
                 new_mrp, new_discount, product_cost, platform_selector,
                 myntra_new_brand, myntra_new_category, myntra_new_gender, apply_kuchipoo_royalty,
                 weight_in_kg, shipping_zone, jiomart_category, jiomart_benefit_rate,
                 meesho_charge_rate, wrong_defective_price,
                 apply_royalty, 0.0 # Pass 0 for deprecated marketing fee
                )

            # --- Result Metrics ---
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
                col1_l.metric(label="Product MRP (₹)", value=f"₹ {new_mrp:,.2f}")
                
                if platform_selector == 'Meesho':
                    display_wdp = sale_price # sale_price is WDP for meesho
                    calculated_discount = new_mrp - display_wdp
                    discount_percent = (calculated_discount / new_mrp) * 100 if new_mrp > 0 else 0.0
                    col2_l.metric(label="Discount Amount (MRP - WDP)", value=f"₹ {calculated_discount:,.2f}", delta=f"{discount_percent:,.2f}% of MRP", delta_color="off")
                    col3_l.metric(label="Sale Price (WDP)", value=f"₹ {sale_price:,.2f}")
                    st.markdown("---")
                    col4_l, col5_l = st.columns(2)
                    col4_l.metric(label="Fixed/Shipping Charges", value="₹ 0.00")
                    col5_l.metric(label="**Invoice Value (CPA)**", value=f"₹ {customer_paid_amount:,.2f}")
                
                else:
                    discount_percent = (new_discount / new_mrp) * 100 if new_mrp > 0 else 0.0
                    col2_l.metric(label="Discount Amount", value=f"₹ {new_discount:,.2f}", delta=f"{discount_percent:,.2f}% of MRP", delta_color="off")
                    col3_l.metric(label="Sale Price (₹)", value=f"₹ {sale_price:,.2f}")
                    st.markdown("---")
                    
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
                        col8_l.metric(label=f"Benefit ({jiomart_benefit_rate * 100:,.2f}%)", value=f"₹ {abs(jiomart_benefit_amount):,.2f}", delta="Deduction from Fees", delta_color="normal")
                        col9_l.metric(label="Final Applicable Fee (B)", value=f"₹ {jiomart_final_applicable_fee_base:,.2f}")
                        col10_l.metric(label="GST @ 18% (C) on (B)", value=f"₹ {jiomart_gst_on_fees:,.2f}")
                        st.markdown("---")
                        st.metric(label="**Invoice Value (CPA)**", value=f"₹ {customer_paid_amount:,.2f}")
                        
                    else:
                        col4_l, col5_l = st.columns(2)
                        fixed_charge_label = "Fixed/Shipping Charge"
                        if platform_selector == 'Myntra':
                            fixed_charge_label = "GT Charge (Incl. GST)"
                        elif platform_selector == 'Ajio':
                            fixed_charge_label = "SCM Charges (Incl. GST)"
                        elif platform_selector == 'Snapdeal':
                            fixed_charge_label = "RO Fee (Incl. Tax)"
                        elif platform_selector == 'FirstCry':
                            fixed_charge_label = "Fixed Charges"
                            
                        col4_l.metric(label=fixed_charge_label, value=f"₹ {gt_charge:,.2f}")
                        col5_l.metric(label="**Invoice Value (CPA)**", value=f"₹ {customer_paid_amount:,.2f}")

            # =========== RIGHT COLUMN: Deductions and Final Payout ===========
            with col_right:
                st.markdown("###### **3. Deductions (Charges)**")
                col1_r, col2_r, col3_r = st.columns(3)

                # Commission/Platform Fee
                platform_fee_label = "Platform Fee (Incl. GST)"
                platform_fee_value = final_commission
                
                if platform_selector == 'Jiomart':
                    platform_fee_label = "**Total Platform Fee (B+C)**"
                    platform_fee_value = jiomart_final_applicable_fee_base + jiomart_gst_on_fees
                elif platform_selector == 'FirstCry':
                    platform_fee_label = "**Flat Deduction (42%)**"
                elif platform_selector == 'Meesho':
                     platform_fee_label = f"Meesho Fee ({meesho_charge_rate*100:.2f}% + Tax)"
                elif platform_selector == 'Ajio':
                    platform_fee_label = "Commission (Incl. GST)"
                elif platform_selector == 'Snapdeal':
                    platform_fee_label = "Commission (Incl. GST)"
                elif platform_selector == 'Myntra':
                    platform_fee_label = "Commission (Incl. GST)"

                col1_r.metric(label=platform_fee_label, value=f"₹ {platform_fee_value:,.2f}")
                col2_r.metric(label="Marketing Fee", value=f"₹ {marketing_fee_base:,.2f}")
                col3_r.metric(label="Royalty Fee", value=f"₹ {royalty_fee:,.2f}")

                col4_r, col5_r, col6_r = st.columns(3)
                col4_r.metric(label=f"Taxable Value (GST @ {invoice_tax_rate*100:.0f}%)", value=f"₹ {taxable_amount_value:,.2f}")
                col5_r.metric(label="TDS (0.1% on Taxable)", value=f"₹ {abs(tds):,.2f}")
                col6_r.metric(label="TCS (10% on Tax Amt)", value=f"₹ {abs(tcs):,.2f}")
                st.markdown("---")
                
                st.markdown("###### **4. Final Payout and Profit**")
                col7_r, col8_r = st.columns(2)
                col7_r.metric(label="**FINAL SETTLED AMOUNT**", value=f"₹ {settled_amount:,.2f}")
                col8_r.metric(
                    label=f"**NET PROFIT ({current_margin_percent:,.2f}% Margin)**",
                    value=f"₹ {net_profit:,.2f}",
                    delta=delta_label, delta_color=delta_color
                )

        except Exception as e:
            st.error(f"An error occurred during calculation: {str(e)}")
            import traceback
            st.code(traceback.format_exc())
    else:
        st.info("Please enter a valid MRP and Product Cost to start the calculation.")


# ==============================================================================
# --- (MODIFIED) BULK PROCESSING UI ---
# ==============================================================================
elif calculation_mode == 'B. Bulk Processing (Excel)':
    st.markdown("##### **Excel Bulk Processing**")
    
    # --- (NEW) Bulk Mode Selection ---
    bulk_calc_mode = st.radio(
        "Select Bulk Calculation Type:",
        ('Profit Calculation', 'Target Discount'),
        index=0, horizontal=True, key="bulk_mode_radio",
        help="**Profit Calculation:** Uses the 'Discount' column to calculate profit.\n"
             "**Target Discount:** Uses the 'Target_Profit' column to calculate the required discount."
    )
    
    st.info(
        f"**Mode Selected: {bulk_calc_mode}**\n\n"
        f"- **Profit Calculation:** Please ensure the `Discount` (or `Wrong_Defective_Price` for Meesho) column is filled. The `Target_Profit` column will be ignored.\n"
        f"- **Target Discount:** Please ensure the `Target_Profit` column is filled. The `Discount` and `Wrong_Defective_Price` columns will be ignored."
    )

    # --- (NEW) Columns for Download Buttons ---
    col_template, col_rates = st.columns(2)

    with col_template:
        # Template Download Button
        excel_data = get_excel_template()
        st.download_button(
            label="⬇️ Download Excel Template (v4.2)",
            data=excel_data,
            file_name='Vardhman_Ecom_Bulk_Template_v4.2.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            help="Download this template (with Instructions sheet) and fill in your product details.",
            use_container_width=True
        )
        
    with col_rates:
        # --- (NEW) Download Commission Rates Button ---
        commission_data_excel = get_commission_rates_excel()
        st.download_button(
            label="📊 Download Myntra Commission Rates",
            data=commission_data_excel,
            file_name='Myntra_Commission_Rates_v3.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            help="Download the current Myntra commission rates stored in the calculator.",
            use_container_width=True
        )
        
    st.divider()

    # --- (MODIFIED) File Uploader: .xlsx only ---
    uploaded_file = st.file_uploader("📂 **Upload Excel File** (.xlsx only)", type=['xlsx'])

    if uploaded_file is not None:
        try:
            # --- (FIX v3.9) Read only .xlsx, specify sheet_name='Data', read all as string ---
            try:
                input_df = pd.read_excel(uploaded_file, sheet_name='Data', dtype=str)
            except ValueError as e:
                if 'Worksheet named' in str(e):
                    st.error(f"Error: Worksheet 'Data' not found in the Excel file. Please make sure your data is on a sheet named 'Data'.")
                    st.stop()
                else:
                    raise e
            
            # --- (FIX v3.8) Clean column names (case-insensitive and strip spaces) ---
            input_df.columns = [str(col).strip().title() for col in input_df.columns]
            
            # --- (FIX v3.8) Check for TitleCase column names ---
            required_cols = ['Sku', 'Mrp', 'Discount', 'Product_Cost', 'Platform']
            optional_cols = [
                'Target_Profit', 
                'Weight_In_Kg', # Renamed
                'Shipping_Zone', 
                'Jiomart_Category', 
                'Jiomart_Benefit_Rate',
                'Wrong_Defective_Price', 
                'Meesho_Charge_Rate', 
                'Marketing_Fee_Rate', 
                'Apply_Royalty', # Old royalty
                'Myntra_New_Brand', 
                'Myntra_New_Category', 
                'Myntra_New_Gender', 
                'Apply_Kuchipoo_Royalty' # New Myntra
            ]
            
            missing_req_cols = [col for col in required_cols if col not in input_df.columns]
            if missing_req_cols:
                st.error(f"Missing required column(s): **{', '.join(missing_req_cols)}**. Please use the downloaded template. (Note: column names are now case-insensitive, e.g. 'sku' or 'SKU' is OK)")
                st.stop()
            
            for col in optional_cols:
                if col not in input_df.columns:
                    input_df[col] = np.nan # Add missing optional columns
            
            # --- (Removed old Myntra col check) ---

            if input_df.empty:
                st.warning("The uploaded file is empty.")
                st.stop()
            
            # --- (FIX v3.8) Check for Target_Profit column if in Target Discount mode ---
            if bulk_calc_mode == 'Target Discount' and 'Target_Profit' not in input_df.columns:
                st.error("Missing required column for this mode: **Target_Profit**. Please download the new template and fill this column.")
                st.stop()


            st.success(f"Successfully loaded {len(input_df)} product data from **{uploaded_file.name}**. Starting processing in **{bulk_calc_mode}** mode...")

            # --- (MODIFIED) Process data and get both dataframes ---
            output_df, selling_price_output_df = bulk_process_data(input_df, bulk_calc_mode) # (NEW) Pass the mode

            st.divider()
            st.markdown("### ✅ Calculation Results")

            # Rename columns for clarity
            output_df = output_df.rename(columns={
                'Platform_Fee_Incl_GST': 'Total_Platform_Fee',
                'Fixed/Shipping_Charge(Internal)': 'Fixed_Fee_Component',
                'Sku': 'SKU', # Rename back for display
                'Mrp': 'MRP',
                'Product_Cost': 'Product_Cost'
            })
            
            # Also rename for selling price df
            selling_price_output_df = selling_price_output_df.rename(columns={
                'Sku': 'SKU',
                'Mrp': 'MRP'
            })


            # Reorder columns
            display_columns = [
                'ID', 'SKU', 'Platform', 'MRP', 'Discount', 'Sale_Price', 'Product_Cost',
                'Target_Profit_In', # (NEW)
                'Royalty', 'Total_Platform_Fee', 'Fixed_Fee_Component',
                'Jiomart_Benefit', 'TDS', 'TCS', 'Settled_Amount', 'Net_Profit', 'Margin_%'
            ]
            # --- (FIX) Add Error column to display ---
            if 'Error' in output_df.columns:
                display_columns.append('Error')
            
            display_columns = [col for col in display_columns if col in output_df.columns]
            
            output_df_display = output_df[display_columns]

            # Display results
            st.dataframe(output_df_display.style.format({
                'MRP': "₹ {:,.2f}",
                'Discount': "₹ {:,.2f}",
                'Sale_Price': "₹ {:,.2f}",
                'Product_Cost': "₹ {:,.2f}",
                'Target_Profit_In': "₹ {:,.2f}", # (NEW)
                'Royalty': "₹ {:,.2f}",
                'Total_Platform_Fee': "₹ {:,.2f}",
                'Fixed_Fee_Component': "₹ {:,.2f}",
                'Jiomart_Benefit': "₹ {:,.2f}", 
                'TDS': "₹ {:,.2f}",
                'TCS': "₹ {:,.2f}",
                'Settled_Amount': "₹ {:,.2f}",
                'Net_Profit': "₹ {:,.2f}",
                'Margin_%': "{:,.2f}%"
            }), use_container_width=True)

            # --- (NEW) Download Buttons in Columns ---
            col_download1, col_download2 = st.columns(2)

            with col_download1:
                # Existing Download Results Button
                output_excel = BytesIO()
                with pd.ExcelWriter(output_excel, engine='xlsxwriter') as writer:
                    output_df_display.to_excel(writer, index=False, sheet_name='Results')
                processed_data = output_excel.getvalue()

                st.download_button(
                    label="⬇️ Download Full Results (with Errors)",
                    data=processed_data,
                    file_name=f"Vardhman_Ecom_Full_Results_{bulk_calc_mode.replace(' ', '_')}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True
                )
            
            with col_download2:
                # New Selling Price Download Button
                output_selling_price_excel = BytesIO()
                with pd.ExcelWriter(output_selling_price_excel, engine='xlsxwriter') as writer:
                    selling_price_output_df.to_excel(writer, index=False, sheet_name='Selling_Prices')
                    # Add formatting
                    workbook = writer.book
                    worksheet = writer.sheets['Selling_Prices']
                    money_format = workbook.add_format({'num_format': '₹ {:,.2f}'})
                    # Format: C=MRP, D=Discount, E=Sale_Price, F=Net_Profit
                    worksheet.set_column('C:F', 12, money_format) 
                    worksheet.autofit()
                processed_data_selling_price = output_selling_price_excel.getvalue()

                st.download_button(
                    label="✅ Download Successful Rows (Selling Price)",
                    data=processed_data_selling_price,
                    file_name=f"Vardhman_Ecom_Selling_Prices_{bulk_calc_mode.replace(' ', '_')}.xlsx",
                    mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                    use_container_width=True,
                    help="Downloads only the successfully calculated rows with their selling prices."
                )

        except Exception as e:
            st.error(f"An error occurred during file processing: {e}")
            st.info("Please ensure your column names match the template and the data is in the correct format.")


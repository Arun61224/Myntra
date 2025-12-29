import pandas as pd
import streamlit as st
import numpy as np
from io import BytesIO

FULL_TITLE = "Vardhman Wool Store E-commerce Calculator"
st.set_page_config(layout="wide", page_title=FULL_TITLE, page_icon="🛍️")

# --- Password State ---
if 'password_correct' not in st.session_state:
    st.session_state.password_correct = False

st.markdown("""
<style>
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
        "Lounge Pants": { 
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
            "Girls": {"0-3D": 0.01, "300-500": 0.03, "500-1000": 0.06, "1000-2000": 0.04, "2000+": 0.08}
        },
        "Track Pants": {
            "Boys": {"0-300": 0.08, "300-500": 0.08, "500-1000": 0.06, "1000-2000": 0.04, "2000+": 0.08},
            "Girls": {"0-300": 0.08, "300-500": 0.08, "500-1000": 0.05, "1000-2000": 0.05, "2000+": 0.08}
        },
        "Tshirts": {
            "Boys": {"0-300": 0.1, "300-500": 0.1, "500-1000": 0.06, "1000-2000": 0.05, "2000+": 0.08},
            "Girls": {"0-300": 0.1, "300-500": 0.1, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.08}
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
            "Boys": {"0-300": 0.1, "300-500": 0.1, "500-1000": 0.06, "1000-2000": 0.06, "2000+": 0.08}
        }
    }
}

def get_myntra_new_commission_rate(brand, category, gender, seller_price):
    try:
        brand_data = MYNTRA_COMMISSION_DATA.get(brand)
        if not brand_data: return 0.0
        
        category_data = brand_data.get(category)
        if not category_data: return 0.0
        
        gender_data = category_data.get(gender)
        if not gender_data: return 0.0
        
        if brand == "KUCHIPOO":
            if seller_price <= 200: return gender_data.get("0-200", 0.0)
            elif seller_price <= 300: return gender_data.get("200-300", 0.0)
            elif seller_price <= 400: return gender_data.get("300-400", 0.0)
            elif seller_price <= 500: return gender_data.get("400-500", 0.0)
            elif seller_price <= 800: return gender_data.get("500-800", 0.0)
            else: return gender_data.get("800+", 0.0)
        else: 
            if seller_price <= 300: return gender_data.get("0-300", 0.0)
            elif seller_price <= 500: return gender_data.get("300-500", 0.0)
            elif seller_price <= 1000: return gender_data.get("500-1000", 0.0)
            elif seller_price <= 2000: return gender_data.get("1000-2000", 0.0)
            else: return gender_data.get("2000+", 0.0)
            
    except Exception:
        return 0.0

def calculate_myntra_new_fixed_fee(brand, taxable_value_for_slab):
    base_fee = 0.0 
    
    if taxable_value_for_slab <= 500:
        base_fee = 50.0
    elif taxable_value_for_slab <= 1000:
        base_fee = 80.0
    elif taxable_value_for_slab <= 2000:
        base_fee = 145.0
    else: 
        base_fee = 175.0
    
    gst_on_fee = base_fee * 0.18
    final_fee = base_fee + gst_on_fee
            
    return final_fee 

def calculate_myntra_new_royalty(brand, sale_price, apply_kuchipoo_royalty_flag):
    royalty_rate = 0.0
    
    if brand == "YK":
        royalty_rate = 0.01 
    elif brand == "YK Disney":
        royalty_rate = 0.07 
    elif brand == "YK Marvel":
        royalty_rate = 0.07 
    elif brand == "KUCHIPOO" and apply_kuchipoo_royalty_flag == 'Yes':
        royalty_rate = 0.10 
        
    return sale_price * royalty_rate

def calculate_myntra_yk_fixed_fee(brand, taxable_value_for_slab):
    if brand not in ["YK", "YK Disney", "YK Marvel"]:
        return 0.0 

    base_fee = 0.0
    if taxable_value_for_slab <= 1000:
        base_fee = 27.0
    else: 
        base_fee = 45.0
    
    gst_on_fee = base_fee * 0.18
    final_fee = base_fee + gst_on_fee
            
    return final_fee

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
    if sale_price <= 500: return rates.get("0-500", 0.0)
    else: return rates.get("500+", 0.0)

def calculate_taxable_amount_value(customer_paid_amount):
    if customer_paid_amount >= 2500:
        tax_rate = 0.12
        divisor = 1.12
    else:
        tax_rate = 0.05
        divisor = 1.05
    taxable_amount = customer_paid_amount / divisor
    return taxable_amount, tax_rate

def perform_calculations(mrp, discount, 
                           product_cost, platform,
                           myntra_new_brand=None, myntra_new_category=None, myntra_new_gender=None,
                           apply_kuchipoo_royalty='No',
                           weight_in_kg=0.0, shipping_zone=None, jiomart_category=None, jiomart_benefit_rate=0.0,
                           meesho_charge_rate=0.0, wrong_defective_price=None,
                           apply_royalty='No', marketing_fee_rate=0.0):
    
    gt_charge = 0.0 
    yk_fixed_fee = 0.0 
    royalty_fee = 0.0
    marketing_fee_base = 0.0 
    marketing_fee_gst = 0.0 # GST on Marketing
    final_commission = 0.0
    commission_rate = 0.0
    
    jiomart_comm_fee_base = 0.0
    jiomart_fixed_fee_base = 0.0
    jiomart_shipping_fee_base = 0.0
    jiomart_total_fee_base = 0.0
    jiomart_benefit_amount = 0.0 
    jiomart_final_applicable_fee_base = 0.0
    jiomart_gst_on_fees = 0.0
    total_platform_deduction = 0.0
    
    total_fixed_charge = 0.0 
    GST_RATE_FEES = 0.18 

    if platform == 'Meesho':
        if wrong_defective_price is not None and wrong_defective_price > 0:
            customer_paid_amount = wrong_defective_price
        else:
            customer_paid_amount = mrp
            
        sale_price = customer_paid_amount
        discount = mrp - sale_price 

    else:
        sale_price = mrp - discount 
        
        if sale_price < 0:
            return (sale_price, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -99999999.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0) 

        customer_paid_amount = sale_price 

    # --- COMMON TAX CALCULATION ---
    taxable_amount_value, invoice_tax_rate = calculate_taxable_amount_value(customer_paid_amount)
    tax_amount = customer_paid_amount - taxable_amount_value
    tds = taxable_amount_value * 0.001
    tcs = tax_amount * 0.10 
    # --- 

    # --- PLATFORM SPECIFIC FEES ---
    if platform == 'Meesho':
        commission_rate = meesho_charge_rate
        commission_base = customer_paid_amount * commission_rate
        commission_tax = commission_base * GST_RATE_FEES
        final_commission = commission_base + commission_tax
        gt_charge = 0.0
        yk_fixed_fee = 0.0
        marketing_fee_base = 0.0
        royalty_fee = customer_paid_amount * 0.10 if apply_royalty == 'Yes' else 0.0 
        total_fixed_charge = 0.0

    elif platform == 'Myntra':
        
        gt_charge = calculate_myntra_new_fixed_fee(myntra_new_brand, taxable_amount_value) 
        
        yk_fixed_fee = calculate_myntra_yk_fixed_fee(myntra_new_brand, taxable_amount_value) 

        total_fixed_charge = gt_charge + yk_fixed_fee 
        
        # Commission is usually on Net Selling Price (Price - Base Fixed Fee)
        # Using approximated approach: CPA - GT Charge for base
        seller_price = customer_paid_amount - gt_charge 
        
        commission_rate = get_myntra_new_commission_rate(myntra_new_brand, myntra_new_category, myntra_new_gender, seller_price) 
            
        commission_base = seller_price * commission_rate
        commission_tax = commission_base * GST_RATE_FEES
        final_commission = commission_base + commission_tax
        
        royalty_fee = calculate_myntra_new_royalty(myntra_new_brand, customer_paid_amount, apply_kuchipoo_royalty) 
        
        # --- Myntra Marketing Fee + GST ---
        if myntra_new_brand == "KUCHIPOO":
            marketing_fee_base = customer_paid_amount * 0.05
        elif myntra_new_brand in ["YK", "YK Disney", "YK Marvel"]:
            marketing_fee_base = customer_paid_amount * 0.04
        else:
            marketing_fee_base = 0.0
            
        marketing_fee_gst = marketing_fee_base * 0.18 # GST on Marketing
        
        sale_price = seller_price # Internal override for checking
            
    elif platform == 'FirstCry':
        commission_rate = 0.42
        final_commission = customer_paid_amount * commission_rate 
        gt_charge = 0.0
        marketing_fee_base = 0.0
        total_fixed_charge = 0.0
        royalty_fee = customer_paid_amount * 0.10 if apply_royalty == 'Yes' else 0.0 

    elif platform == 'Ajio':
        commission_rate = 0.20
        commission_base = customer_paid_amount * commission_rate 
        commission_tax = commission_base * 0.18
        final_commission = commission_base + commission_tax
        scm_base = 95.0
        scm_tax = scm_base * 0.18
        gt_charge = scm_base + scm_tax
        marketing_fee_base = 0.0
        total_fixed_charge = gt_charge
        royalty_fee = customer_paid_amount * 0.10 if apply_royalty == 'Yes' else 0.0 

    elif platform == 'Snapdeal':
        commission_rate = 0.24
        commission_base = round(customer_paid_amount * commission_rate)
        commission_tax = round(commission_base * GST_RATE_FEES)
        final_commission = commission_base + commission_tax
        
        ro_base = round(customer_paid_amount * 0.08)
        ro_tax = round(ro_base * 0.14)
        gt_charge = ro_base + ro_tax
            
        marketing_fee_base = 0.0
        total_fixed_charge = gt_charge
        royalty_fee = customer_paid_amount * 0.10 if apply_royalty == 'Yes' else 0.0 

    elif platform == 'Jiomart':
        
        commission_rate = get_jiomart_commission_rate(jiomart_category, customer_paid_amount) if jiomart_category else 0.0 
        jiomart_comm_fee_base = customer_paid_amount * commission_rate 
        jiomart_fixed_fee_base = calculate_jiomart_fixed_fee_base(customer_paid_amount) 
        jiomart_shipping_fee_base = calculate_jiomart_shipping_fee_base(weight_in_kg, shipping_zone) if shipping_zone and weight_in_kg > 0 else 0.0
        
        jiomart_total_fee_base = jiomart_comm_fee_base + jiomart_fixed_fee_base + jiomart_shipping_fee_base
        
        jiomart_benefit_amount = -(customer_paid_amount * jiomart_benefit_rate) 
        
        jiomart_final_applicable_fee_base = jiomart_total_fee_base + jiomart_benefit_amount
            
        jiomart_gst_on_fees = jiomart_final_applicable_fee_base * GST_RATE_FEES
            
        total_platform_deduction = jiomart_final_applicable_fee_base + jiomart_gst_on_fees
        
        final_commission = jiomart_comm_fee_base 
        total_fixed_charge = jiomart_fixed_fee_base + jiomart_shipping_fee_base
        gt_charge = total_fixed_charge 
        
        royalty_fee = customer_paid_amount * 0.10 if apply_royalty == 'Yes' else 0.0 

    # --- 4. Total Deductions & Settlement (Paid by Platform) ---
    
    if platform == 'Jiomart':
        total_deductions = total_platform_deduction 
    elif platform == 'Myntra':
         # --- (UPDATED) REMOVED Marketing Fee from Platform Deductions ---
         # Marketing Fee is now treated as an External Expense (Paid separately by user)
         total_deductions = final_commission + gt_charge + yk_fixed_fee 
    elif platform == 'Meesho':
        total_deductions = final_commission 
    else: 
        total_deductions = final_commission + marketing_fee_base + gt_charge
        
    settled_amount = customer_paid_amount - total_deductions - tds - tcs
    
    # --- 5. Net Profit (Actual Cash in Hand) ---
    # Deduct Royalty AND Marketing Fee HERE because you pay it separately from the settlement
    net_profit = settled_amount - product_cost - royalty_fee - marketing_fee_base - marketing_fee_gst

    return (sale_price, gt_charge, customer_paid_amount, royalty_fee,
            marketing_fee_base, marketing_fee_gst, # Return GST too
            final_commission, 
            commission_rate, settled_amount, taxable_amount_value,
            net_profit, tds, tcs, invoice_tax_rate, 
            jiomart_fixed_fee_base, jiomart_shipping_fee_base,
            jiomart_benefit_amount, 
            jiomart_total_fee_base, 
            jiomart_final_applicable_fee_base, 
            jiomart_gst_on_fees, 
            yk_fixed_fee 
            )

def find_discount_for_target_profit(mrp, target_profit, product_cost, platform,
                                    myntra_new_brand=None, myntra_new_category=None, myntra_new_gender=None,
                                    apply_kuchipoo_royalty='No',
                                    weight_in_kg=0.0, shipping_zone=None, jiomart_category=None, jiomart_benefit_rate=0.0,
                                    meesho_charge_rate=0.0, wrong_defective_price=None, 
                                    apply_royalty='No'):

    def get_net_profit(disc, wdp=None):
        results = perform_calculations(mrp, disc, product_cost, platform,
                                       myntra_new_brand, myntra_new_category, myntra_new_gender,
                                       apply_kuchipoo_royalty,
                                       weight_in_kg, shipping_zone, jiomart_category, jiomart_benefit_rate,
                                       meesho_charge_rate, wdp,
                                       apply_royalty, 0.0) 
        
        if results is None: return -9999.0
        # Return Net Profit (which now accounts for Royalty deduction)
        return results[10]

    # --- Optimizing Search Step ---
    step_size = 5.0

    if platform == 'Meesho':
        max_profit = get_net_profit(0.0, mrp) 
        if max_profit < target_profit:
            return None, max_profit, 0.0 
            
        required_wdp = mrp
        while required_wdp >= 0:
            current_profit = get_net_profit(0.0, required_wdp) 
            if current_profit < target_profit:
                # Revert one step to stay above target
                final_wdp = required_wdp + step_size
                target_wdp = min(final_wdp, mrp) 
                
                discount_amount = mrp - target_wdp 
                discount_percent = (discount_amount / mrp) * 100 if mrp > 0 else 0.0
                final_profit = get_net_profit(0.0, target_wdp)
                return discount_amount, final_profit, discount_percent 
            required_wdp -= step_size
            
        final_profit = get_net_profit(0.0, 0.0)
        return mrp, final_profit, 100.0 

    # For other platforms
    initial_profit = get_net_profit(0.0) 
    if initial_profit < target_profit:
        return None, initial_profit, 0.0 

    required_discount = 0.0
    while required_discount <= mrp:
        current_profit = get_net_profit(required_discount)
        if current_profit < target_profit:
            final_discount = max(0.0, required_discount - step_size)
            final_profit = get_net_profit(final_discount)
            discount_percent = (final_discount / mrp) * 100
            return final_discount, final_profit, discount_percent
        required_discount += step_size

    final_profit = get_net_profit(mrp)
    return mrp, final_profit, 100.0


# --- Helper function for bulk processing ---
def run_bulk_processing(df, bulk_platform, mode, target_margin=0.0, meesho_charge=0.0, jio_benefit=0.0):
    
    results = []
    cols = df.columns
    
    sku_col_name = None
    if 'seller_sku_code' in cols: sku_col_name = 'seller_sku_code'
    elif 'sku_code' in cols: sku_col_name = 'sku_code'
    
    mrp_col_name = None
    if 'product_mrp' in cols: mrp_col_name = 'product_mrp'
    elif 'mrp' in cols: mrp_col_name = 'mrp'
    elif 'product_mrp_' in cols: mrp_col_name = 'product_mrp_' 
    
    cost_col_name = None
    if 'product_cost' in cols: cost_col_name = 'product_cost'
    elif 'cost_price' in cols: cost_col_name = 'cost_price'

    selling_price_col_name = None
    if 'selling_price' in cols: selling_price_col_name = 'selling_price'

    required_cols_check = [sku_col_name, mrp_col_name, cost_col_name]
    if mode == 'Check With Selling Price': 
        if not selling_price_col_name:
            st.error("File missing required column: 'selling_price' is needed for 'Check With Selling Price' mode.")
            return pd.DataFrame()
        required_cols_check.append(selling_price_col_name)

    if not all(required_cols_check):
        st.error(f"File missing required columns. Need SKU, MRP, and Cost. Check template downloads.")
        return pd.DataFrame()

    platform_col_name = None
    if bulk_platform == 'Consolidated':
        if 'platform' in cols:
            platform_col_name = 'platform'
        else:
            st.error("Consolidated mode requires a 'platform' column in your file.")
            return pd.DataFrame()

    brand_col = 'myntra_brand' if 'myntra_brand' in cols else 'brand' if 'brand' in cols else None
    cat_col = 'myntra_article_type' if 'myntra_article_type' in cols else 'article_type' if 'article_type' in cols else None
    gen_col = 'myntra_gender' if 'myntra_gender' in cols else 'gender' if 'gender' in cols else None
    
    jio_cat_col = 'jiomart_category' if 'jiomart_category' in cols else 'category' if 'category' in cols else None
    weight_col = 'product_weight_kg' if 'product_weight_kg' in cols else 'product_weight' if 'product_weight' in cols else None
    zone_col = 'shipping_zone' if 'shipping_zone' in cols else None

    output_rows = []

    for row in df.itertuples():
        try:
            sku = str(getattr(row, sku_col_name))
            mrp = float(getattr(row, mrp_col_name))
            cost = float(getattr(row, cost_col_name))

            if mrp <= 0 or cost <= 0: continue 

            current_platform = getattr(row, platform_col_name) if bulk_platform == 'Consolidated' else bulk_platform
            current_platform = str(current_platform).strip()

            myntra_brand = getattr(row, brand_col) if current_platform == 'Myntra' and brand_col and hasattr(row, brand_col) else None
            myntra_cat = getattr(row, cat_col) if current_platform == 'Myntra' and cat_col and hasattr(row, cat_col) else None
            myntra_gen = getattr(row, gen_col) if current_platform == 'Myntra' and gen_col and hasattr(row, gen_col) else None
            
            jio_cat = getattr(row, jio_cat_col) if current_platform == 'Jiomart' and jio_cat_col and hasattr(row, jio_cat_col) else None
            jio_zone = getattr(row, zone_col) if current_platform == 'Jiomart' and zone_col and hasattr(row, zone_col) else 'National' 
            jio_weight = 0.5 
            if current_platform == 'Jiomart' and weight_col and hasattr(row, weight_col):
                try:
                    weight_val = float(getattr(row, weight_col))
                    if weight_col == 'product_weight': jio_weight = weight_val / 1000.0
                    else: jio_weight = weight_val
                except: jio_weight = 0.5 
            
            apply_royalty = 'No'
            apply_kuchipoo_royalty = 'No'
            
            if current_platform == 'Myntra':
                is_myntra_royalty_sku = sku.startswith("DKUC") or sku.startswith("MKUC")
                if myntra_brand == 'KUCHIPOO' and is_myntra_royalty_sku:
                    apply_kuchipoo_royalty = 'Yes'
            else:
                is_other_portal_royalty_sku = ("DKUC" in sku) or ("MKUC" in sku)
                if is_other_portal_royalty_sku:
                    apply_royalty = 'Yes'
            
            output_data = {
                "SKU": sku,
                "MRP": mrp,
                "Cost_Price": cost,
            }
            if bulk_platform == 'Consolidated':
                output_data["Platform"] = current_platform

            if mode == 'Check With Selling Price':
                selling_price = float(getattr(row, selling_price_col_name))
                discount_amount = mrp - selling_price
                wdp = selling_price 
                
                (sale_price, gt_charge, customer_paid_amount, royalty_fee,
                 marketing_fee_base, marketing_fee_gst, final_commission,
                 commission_rate, settled_amount, taxable_amount_value,
                 net_profit, tds, tcs, invoice_tax_rate, jiomart_fixed_fee_base, jiomart_shipping_fee_base,
                 jiomart_benefit_amount, jiomart_total_fee_base, jiomart_final_applicable_fee_base, jiomart_gst_on_fees,
                 yk_fixed_fee 
                ) = perform_calculations(
                    mrp, discount_amount, cost, current_platform,
                    myntra_brand, myntra_cat, myntra_gen, apply_kuchipoo_royalty,
                    jio_weight, jio_zone, jio_cat, jio_benefit,
                    meesho_charge, wdp if current_platform == 'Meesho' else None,
                    apply_royalty, 0.0
                )
                
                output_data.update({
                    "Selling_Price": selling_price,
                    "Bank_Settlement_Amount": settled_amount,
                    "Royalty_You_Pay": royalty_fee,
                    "Marketing_Fee_You_Pay": marketing_fee_base + marketing_fee_gst,
                    "Net_Profit_In_Hand": net_profit
                })

            else: 
                # Check With Cost Price (Target Margin)
                discount_amount, final_profit, discount_percent = find_discount_for_target_profit(
                    mrp, target_margin, cost, current_platform,
                    myntra_brand, myntra_cat, myntra_gen, apply_kuchipoo_royalty,
                    jio_weight, jio_zone, jio_cat, jio_benefit,
                    meesho_charge, None,
                    apply_royalty
                )
                
                selling_price_req = (mrp - discount_amount) if discount_amount is not None else "N/A"
                bank_settlement_amt = "N/A"
                marketing_total_pay = "N/A"

                if discount_amount is not None:
                    wdp_calc = (mrp - discount_amount)
                    
                    # Re-run calc to get breakdown
                    (sale_price, gt_charge, customer_paid_amount, royalty_fee,
                     marketing_fee_base, marketing_fee_gst, final_commission,
                     commission_rate, settled_amount, taxable_amount_value,
                     net_profit, tds, tcs, invoice_tax_rate, jiomart_fixed_fee_base, jiomart_shipping_fee_base,
                     jiomart_benefit_amount, jiomart_total_fee_base, jiomart_final_applicable_fee_base, jiomart_gst_on_fees,
                     yk_fixed_fee 
                    ) = perform_calculations(
                        mrp, discount_amount, cost, current_platform,
                        myntra_brand, myntra_cat, myntra_gen, apply_kuchipoo_royalty,
                        jio_weight, jio_zone, jio_cat, jio_benefit,
                        meesho_charge, wdp_calc if current_platform == 'Meesho' else None,
                        apply_royalty, 0.0
                    )
                    bank_settlement_amt = settled_amount
                    marketing_total_pay = marketing_fee_base + marketing_fee_gst

                output_data.update({
                    "Target_Margin": target_margin,
                    "Required_Selling_Price": selling_price_req,
                    "Bank_Settlement_Amount": bank_settlement_amt,
                    "Marketing_Fee_You_Pay": marketing_total_pay,
                    "Projected_Net_Profit": final_profit if final_profit is not None else "N/A"
                })

            output_rows.append(output_data)

        except Exception as e:
            continue
            
    return pd.DataFrame(output_rows)


@st.cache_data
def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

# ==============================================================================
# --- MAIN APP STRUCTURE ---
# ==============================================================================

st.title("🛍️ " + FULL_TITLE)
st.markdown("###### **1. Select Mode**")
main_mode = st.radio("Select Mode", ("Single Product Calculation", "Bulk Calculation"), horizontal=True, label_visibility="collapsed")

st.markdown("###### **2. Upload SKU File (CSV or XLSX)**")

sku_col_1, sku_col_2 = st.columns([3, 1])

with sku_col_1:
    sku_file = st.file_uploader("Upload your platform-specific or consolidated SKU file:", type=['csv', 'xlsx'])

with sku_col_2:
    if 'sku_df' in st.session_state:
        def clear_sku_data():
            st.session_state.pop('sku_df', None)
            st.session_state.pop('sku_message', None)
            st.session_state.pop('sku_select_key', None)
            
            keys_to_clear = [
                'myntra_brand_v3', 'myntra_cat_v3', 'myntra_gen_v3',
                'new_mrp', 'style_id_display', 'single_cost',
                'jiomart_category_selector', 'single_weight', 'single_zone'
            ]
            for key in keys_to_clear:
                if key in st.session_state:
                    del st.session_state[key]

        st.button("Clear SKU Data", on_click=clear_sku_data, use_container_width=True)

if sku_file is not None and 'sku_df' not in st.session_state:
    try:
        if sku_file.name.endswith('.xlsx'):
            df = pd.read_excel(sku_file, dtype=str, engine='openpyxl')
        else:
            df = pd.read_csv(sku_file, encoding='utf-8-sig', dtype=str)
        
        df.columns = [str(col).strip().lower().replace(' ', '_') for col in df.columns]
        st.session_state.sku_df = df
        st.success(f"Successfully loaded {len(df)} SKUs.")
    except Exception as e:
        st.error(f"Error loading SKU file: {e}")

# --- Templates (Same as before) ---
st.markdown("**Download Templates (CSV):**")
with st.expander("Show Templates"):
    col1, col2 = st.columns(2)
    with col1:
        myntra_template_csv = "seller_sku_code,product_mrp,product_cost,brand,article_type,gender,style_id,style_name\nDKUC-TEST-001,1999,500,KUCHIPOO,Tshirts,Boys,123456,Test Style\n"
        st.download_button("Myntra Template", data=myntra_template_csv, file_name="template_target_myntra.csv", mime="text/csv")
    with col2:
        consolidated_template_csv = "platform,seller_sku_code,product_mrp,product_cost,myntra_brand,myntra_article_type,myntra_gender,jiomart_category,product_weight_kg,shipping_zone,style_id,style_name\nMyntra,DKUC-MYN-001,1999,500,KUCHIPOO,Tshirts,Boys,,,,123456,Test Myntra\n"
        st.download_button("Consolidated Template", data=consolidated_template_csv, file_name="template_target_consolidated.csv", mime="text/csv")

st.divider()

if main_mode == "Single Product Calculation":
    
    if st.session_state.password_correct: 

        st.markdown("###### **3. Select Calculation Mode**")
        single_calc_mode = st.radio(
            "Select Calculation Mode:", 
            ('Check With Selling Price', 'Check With Cost Price'),
            index=0, label_visibility="collapsed", horizontal=True
        )
        st.markdown("---")


        platform_selector = st.radio(
            "Select Platform:",
            ('Myntra', 'FirstCry', 'Ajio', 'Jiomart', 'Meesho', 'Snapdeal'),
            index=0, horizontal=True,
            key="platform_selector_key" 
        )

        def lookup_sku():
            sku = st.session_state.get('sku_select_key', '').strip() 
            if not sku or sku == "Select SKU...": return

            if 'sku_df' in st.session_state:
                sku_df = st.session_state.sku_df
                cols = sku_df.columns
                sku_col_name = 'seller_sku_code' if 'seller_sku_code' in cols else 'sku_code'
                mrp_col_name = 'product_mrp' if 'product_mrp' in cols else 'mrp'
                cost_col_name = 'product_cost' if 'product_cost' in cols else 'cost_price'
                
                result = sku_df[sku_df[sku_col_name].astype(str).str.lower() == sku.lower()]
                
                if not result.empty:
                    row = result.iloc[0]
                    try: st.session_state.new_mrp = float(row[mrp_col_name])
                    except: pass
                    try: st.session_state.single_cost = float(row[cost_col_name])
                    except: pass

                    if platform_selector == 'Myntra':
                        brand_col = 'myntra_brand' if 'myntra_brand' in cols else 'brand' 
                        cat_col = 'myntra_article_type' if 'myntra_article_type' in cols else 'article_type'
                        gen_col = 'myntra_gender' if 'myntra_gender' in cols else 'gender'
                        if brand_col in row: st.session_state.myntra_brand_v3 = row[brand_col]
                        if cat_col in row: st.session_state.myntra_cat_v3 = row[cat_col]
                        if gen_col in row: st.session_state.myntra_gen_v3 = row[gen_col]

        if 'sku_df' in st.session_state:
            sku_df = st.session_state.sku_df 
            cols = sku_df.columns
            sku_col_name = 'seller_sku_code' if 'seller_sku_code' in cols else 'sku_code'
            
            if sku_col_name:
                sku_options = ["Select SKU..."] + sorted(st.session_state.sku_df[sku_col_name].dropna().unique().tolist())
                st.selectbox("**Fetch by SKU:**", options=sku_options, key="sku_select_key", on_change=lookup_sku)

        st.markdown("###### **4. Configuration Settings**")

        myntra_new_brand = None
        myntra_new_category = None
        myntra_new_gender = None
        jiomart_category = None
        jiomart_benefit_rate = 0.0
        weight_in_kg = 0.0
        shipping_zone = None
        meesho_charge_rate = 0.0
        apply_royalty = 'No' 

        if platform_selector == 'Myntra':
            col_brand, col_cat, col_gen = st.columns(3)
            brand_options = list(MYNTRA_COMMISSION_DATA.keys())
            myntra_new_brand = col_brand.selectbox("Select Brand:", brand_options, key="myntra_brand_v3")
            
            try:
                category_options = list(MYNTRA_COMMISSION_DATA[myntra_new_brand].keys())
                myntra_new_category = col_cat.selectbox("Select Category:", category_options, key="myntra_cat_v3")
            except KeyError:
                category_options = []
                myntra_new_category = col_cat.selectbox("Select Category:", category_options, index=0, key="myntra_cat_v3")
            
            try:
                gender_options = list(MYNTRA_COMMISSION_DATA[myntra_new_brand][myntra_new_category].keys())
                myntra_new_gender = col_gen.selectbox("Select Gender:", gender_options, key="myntra_gen_v3")
            except KeyError:
                 gender_options = []
                 myntra_new_gender = col_gen.selectbox("Select Gender:", gender_options, index=0, key="myntra_gen_v3")


        elif platform_selector == 'Jiomart':
            col_jio_cat, col_jio_benefit = st.columns(2)
            jiomart_category_options = ["Select Category"] + sorted(list(JIOMART_COMMISSION_RATES.keys()))
            selected_jiomart_category = col_jio_cat.selectbox("Product Category:", jiomart_category_options, index=0)
            jiomart_category = None if selected_jiomart_category == "Select Category" else selected_jiomart_category
            jiomart_benefit_rate = col_jio_benefit.number_input("Benefit Rate (%)", value=1.0) / 100.0
            
            col_weight, col_zone = st.columns(2)
            weight_in_kg = col_weight.number_input("Product Weight (KG)", value=0.5)
            shipping_zone = col_zone.selectbox("Shipping Zone:", ('Local', 'Regional', 'National'))

        elif platform_selector == 'Meesho':
            meesho_charge_percent = st.number_input("Meesho Platform Charge (%)", value=5.0) / 100.0
            meesho_charge_rate = meesho_charge_percent
            
        col_cost, col_target = st.columns(2)
        product_cost = col_cost.number_input("Product Cost (₹)", min_value=0.0, value=1000.0, key="single_cost")
        
        target_label = "Target Net Profit (₹)"
        product_margin_target_rs = col_target.number_input(target_label, min_value=0.0, value=200.0, key="single_target", help="Net Profit you want in hand AFTER paying Royalty")
        
        st.divider()

        col_mrp_in, col_price_in = st.columns(2)
        new_mrp = col_mrp_in.number_input("Product MRP (₹)", min_value=1.0, value=2500.0, key="new_mrp")

        new_discount = 0.0
        wrong_defective_price = None

        if platform_selector == 'Meesho':
            if single_calc_mode != 'Check With Cost Price':
                wrong_defective_price = col_price_in.number_input("Selling Price (WDP) (₹)", value=min(new_mrp, 2000.0))
        else:
            if single_calc_mode == 'Check With Selling Price':
                new_discount = col_price_in.number_input("Discount Amount (₹)", value=500.0)

        st.divider()

        if new_mrp > 0 and product_cost > 0:
            
            apply_kuchipoo_royalty = 'No' 
            apply_royalty = 'No' 
            
            if 'sku_df' in st.session_state:
                selected_sku = st.session_state.get('sku_select_key', '').strip()
                if platform_selector == 'Myntra':
                    is_myntra_royalty_sku = selected_sku and (selected_sku.startswith("DKUC") or selected_sku.startswith("MKUC"))
                    if myntra_new_brand == 'KUCHIPOO' and is_myntra_royalty_sku:
                        apply_kuchipoo_royalty = 'Yes'
                        st.success(f"Royalty Active: 10% (SKU: {selected_sku})")
                else:
                    is_other_portal_royalty_sku = selected_sku and (("DKUC" in selected_sku) or ("MKUC" in selected_sku))
                    if is_other_portal_royalty_sku:
                        apply_royalty = 'Yes'
                        st.success(f"Royalty Active: 10% (SKU: {selected_sku})")

            # --- PERFORM CALCULATION ---
            if single_calc_mode == 'Check With Cost Price':
                calculated_discount, initial_max_profit, calculated_discount_percent = find_discount_for_target_profit(
                    new_mrp, product_margin_target_rs, product_cost, platform_selector,
                    myntra_new_brand, myntra_new_category, myntra_new_gender, apply_kuchipoo_royalty, 
                    weight_in_kg, shipping_zone, jiomart_category, jiomart_benefit_rate,
                    meesho_charge_rate, None, apply_royalty
                )
                
                if calculated_discount is None:
                    st.error(f"Cannot achieve Target Profit. Max possible profit at MRP is ₹ {initial_max_profit:,.2f}.")
                    st.stop()
                    
                new_discount = calculated_discount
                if platform_selector == 'Meesho':
                    wrong_defective_price = new_mrp - calculated_discount

            # Final Detailed Run
            (sale_price, gt_charge, customer_paid_amount, royalty_fee,
             marketing_fee_base, marketing_fee_gst, final_commission,
             commission_rate, settled_amount, taxable_amount_value,
             net_profit, tds, tcs, invoice_tax_rate, jiomart_fixed_fee_base, jiomart_shipping_fee_base,
             jiomart_benefit_amount, jiomart_total_fee_base, jiomart_final_applicable_fee_base, jiomart_gst_on_fees,
             yk_fixed_fee 
             ) = perform_calculations(
                 new_mrp, new_discount, product_cost, platform_selector,
                 myntra_new_brand, myntra_new_category, myntra_new_gender, apply_kuchipoo_royalty, 
                 weight_in_kg, shipping_zone, jiomart_category, jiomart_benefit_rate,
                 meesho_charge_rate, wrong_defective_price,
                 apply_royalty, 0.0 
             )

            col_left, col_right = st.columns(2)

            with col_left:
                st.markdown("### 1. Invoice & Sales")
                st.metric("Selling Price", f"₹ {sale_price:,.2f}")
                st.metric("Discount", f"₹ {new_discount:,.2f}")
                
                st.markdown("### 2. Platform Deductions")
                c1, c2 = st.columns(2)
                c1.metric("Commission (+GST)", f"₹ {final_commission:,.2f}")
                c2.metric("Fixed/Logistics (+GST)", f"₹ {gt_charge + yk_fixed_fee:,.2f}")
                
                # if platform_selector == 'Myntra':
                #    c3, c4 = st.columns(2)
                #    c3.metric("Marketing Base", f"₹ {marketing_fee_base:,.2f}")
                #    c4.metric("Marketing GST (18%)", f"₹ {marketing_fee_gst:,.2f}")

                total_deductions_display = final_commission + gt_charge + yk_fixed_fee 
                st.info(f"Total Platform Deductions: ₹ {total_deductions_display:,.2f}")

            with col_right:
                st.markdown("### 3. Settlement & Profit")
                
                st.metric("🏦 Bank Settlement (From Platform)", f"₹ {settled_amount:,.2f}", 
                          help="This amount will come to your bank account from Myntra/Platform.")
                
                st.markdown("---")
                st.write("**Your Expenses after Settlement:**")
                ex1, ex2 = st.columns(2)
                ex1.metric("Product Cost", f"₹ {product_cost:,.2f}")
                ex2.metric("Royalty (You Pay)", f"₹ {royalty_fee:,.2f}", delta="Pay Externally", delta_color="inverse")
                
                if platform_selector == 'Myntra':
                    ex3, ex4 = st.columns(2)
                    ex3.metric("Marketing (You Pay)", f"₹ {marketing_fee_base:,.2f}", delta="Pay Externally", delta_color="inverse")
                    ex4.metric("Mrkt GST (18%)", f"₹ {marketing_fee_gst:,.2f}", delta="Pay Externally", delta_color="inverse")

                st.markdown("---")
                st.metric("💰 NET PROFIT (In Hand)", f"₹ {net_profit:,.2f}", delta=f"Target: ₹ {product_margin_target_rs:,.2f}")

    else: 
        st.warning("Locked.")
        if st.text_input("Password", type="password") == "4255":
            st.session_state.password_correct = True
            st.rerun()

elif main_mode == "Bulk Calculation":
    
    st.markdown("###### **3. Configure Bulk Calculation**")
    
    col1_bulk, col2_bulk = st.columns(2)
    
    with col1_bulk:
        bulk_platform = st.selectbox(
            "Select Platform:",
            ('Consolidated', 'Myntra', 'FirstCry', 'Ajio', 'Jiomart', 'Meesho', 'Snapdeal'),
            index=0, 
            key="bulk_platform_selector"
        )
    
    with col2_bulk:
        bulk_calc_mode = st.radio(
            "Select Calculation Mode", 
            ('Check With Selling Price', 'Check With Cost Price'),
            index=0, 
            horizontal=True,
            key="bulk_calc_mode_selector"
        )

    st.markdown("---")
    st.markdown("###### **4. Set Calculation Parameters**")

    # --- Global Inputs for Bulk ---
    bulk_target_margin = 0.0
    bulk_meesho_charge_rate = 0.05 
    bulk_jiomart_benefit_rate = 0.0

    if bulk_calc_mode == 'Check With Selling Price':
        pass 
    else: 
        bulk_target_margin = st.number_input("Target Margin Amount (₹) (per SKU)", min_value=0.0, value=100.0, step=10.0)

    if bulk_platform == 'Jiomart' or bulk_platform == 'Consolidated':
        bulk_jiomart_benefit_rate = st.number_input("Default Jiomart Benefit Rate (%)", value=1.0) / 100.0

    st.divider()

    if st.button("Run Bulk Calculation", use_container_width=True, type="primary"):
        if 'sku_df' not in st.session_state:
            st.error("Please upload an SKU file first.")
        else:
            with st.spinner("Processing..."):
                df_results = run_bulk_processing(
                    st.session_state.sku_df,
                    bulk_platform,
                    bulk_calc_mode,
                    target_margin=bulk_target_margin,
                    meesho_charge=bulk_meesho_charge_rate,
                    jio_benefit=bulk_jiomart_benefit_rate
                )
            
            if not df_results.empty:
                st.markdown("###### **5. Calculation Results**")
                st.dataframe(df_results.style.format(precision=2))
                csv_data = convert_df_to_csv(df_results)
                st.download_button(
                    label="Download Results as CSV",
                    data=csv_data,
                    file_name=f"bulk_results.csv",
                    mime="text/csv",
                    use_container_width=True
                )


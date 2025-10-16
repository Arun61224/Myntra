import pandas as pd
import streamlit as st
import numpy as np

# Set page config for wide layout and minimum gaps, using the specified full title
FULL_TITLE = "Vardhman Wool Store E.com Calculator" 
st.set_page_config(layout="wide", page_title=FULL_TITLE, page_icon="🛍️")

# --- Custom CSS for Compactness (Scroll Reduction and Narrow Layout) ---
st.markdown("""
<style>
    /* 1. Force a Maximum Width on the main content block and center it */
    .block-container {
        /* VERTICAL SQUEEZE: Reduced from 1rem to 0.5rem */
        padding-top: 1.25rem; 
        padding-bottom: 0.5rem; 
        padding-left: 1rem;
        padding-right: 1rem;
        
        /* FIX: Max-Width set to 1200px to ensure title fits and prevents jagged edges */
        max-width: 1840px; 
        
        /* Set margin to 'auto' for centering */
        margin-left: auto;
        margin-right: auto;
    }
    
    /* 2. Standard Compactness Rules (from original code) */
    
    /* 🔥 FIX: Increased margin-top to push headings/sections down (Text Niche Karna) */
    h1, h2, h3, h4, h5, h6 {
        margin-top: 0.5rem; /* Increased to 0.5rem for more top spacing */
        margin-bottom: 0.25rem;
    }
    
    /* FIX FOR TITLE (h1): Font size reduced to fit in one line */
    h1 {
        font-size: 2.25rem;
        line-height: 1.1; 
        /* Added more top margin for title */
        margin-top: 1.0rem; 
    }

    /* VERTICAL SQUEEZE: Reduce vertical spacing around st.divider() */
    hr {
        margin: 0.5rem 0 !important;
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

# --- CALCULATION LOGIC FUNCTIONS ---

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

def perform_calculations(mrp, discount, apply_royalty, marketing_fee_rate, product_cost, platform):
    """Performs all sequential calculations for profit analysis based on platform."""
    sale_price = mrp - discount
    if sale_price < 0:
        # Return negative profit if sale price is invalid, handles edge case in search
        return (sale_price, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, -99999999.0, 0.0, 0.0, 0.0)
    
    # --- INITIAL VALUES ---
    gt_charge = 0.0
    royalty_fee = 0.0
    marketing_fee_base = 0.0
    final_commission = 0.0
    commission_rate = 0.0 
    customer_paid_amount = sale_price 
    
    # --- PLATFORM SPECIFIC LOGIC ---
    if platform == 'Myntra':
        
        gt_charge = calculate_myntra_gt_charges(sale_price)
        customer_paid_amount = sale_price - gt_charge # CPA = Sale Price - GT
        
        commission_rate = get_myntra_commission_rate(customer_paid_amount)
        commission_amount_base = customer_paid_amount * commission_rate
        
        # Royalty Logic
        if apply_royalty == 'Yes':
            royalty_fee = customer_paid_amount * 0.10
        else:
            royalty_fee = 0.0
            
        # Marketing Fee Logic (Uses the rate passed from the new selector)
        marketing_fee_base = customer_paid_amount * marketing_fee_rate
            
        # Final Commission (with 18% tax)
        commission_tax = commission_amount_base * 0.18
        final_commission = commission_amount_base + commission_tax
        
    elif platform == 'FirstCry': 
        
        # FirstCry Logic: 42% Flat Deduction on Selling Price + Royalty (on Sale Price)
        commission_rate = 0.42 # Flat combined deduction rate for display
        
        # Commission (42% of Sale Price)
        final_commission = sale_price * commission_rate
        
        # Royalty Fee (10% of Sale Price)
        if apply_royalty == 'Yes':
            royalty_fee = sale_price * 0.10
        else:
            royalty_fee = 0.0 # Ensure royalty_fee is defined
        
        # GT Charge & Marketing are zero
        gt_charge = 0.0 
        marketing_fee_base = 0.0 
        
        customer_paid_amount = sale_price # CPA = Sale Price 
        marketing_fee_rate = 0.0 # Force 0 for FC display
        
    elif platform == 'Ajio': # New Ajio Logic implemented here
        
        # 1. Commission (20% on Sale Price + 18% GST)
        commission_rate = 0.20
        commission_base = sale_price * commission_rate
        commission_tax = commission_base * 0.18
        final_commission = commission_base + commission_tax
        
        # 2. SCM Charges (Fixed Fee: 95 + 18% GST) - Displayed as gt_charge
        scm_base = 95.0
        scm_tax = scm_base * 0.18
        gt_charge = scm_base + scm_tax 
        
        # CPA calculation
        customer_paid_amount = sale_price # Invoice Value = Sale Price 
        
        # 3. Royalty Fee (10% on Sale Price)
        if apply_royalty == 'Yes':
            royalty_fee = sale_price * 0.10
        else:
            royalty_fee = 0.0
            
        marketing_fee_base = 0.0 # No separate marketing fee
        marketing_fee_rate = 0.0 # Force 0 for Ajio display
        
    # --- COMMON TAX AND FINAL SETTLEMENT LOGIC ---
    
    # Taxable Amount Value (for GST)
    taxable_amount_value, invoice_tax_rate = calculate_taxable_amount_value(sale_price) 
    
    # Calculate Tax base amounts based on the total CPA (Sale Price)
    tax_amount = customer_paid_amount - taxable_amount_value
    tcs = tax_amount * 0.10 # TCS calculation remains 10% on Tax Amount as requested previously
    tds = taxable_amount_value * 0.001 
    
    # Final Payment (Settled Amount)
    # Final Settled Amount is calculated by reducing all charges, including TDS and TCS (as requested).
    settled_amount = customer_paid_amount - final_commission - royalty_fee - marketing_fee_base - tds + tcs
    
    # Net Profit
    net_profit = settled_amount - product_cost
    
    return (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
            marketing_fee_base, marketing_fee_rate, final_commission, 
            commission_rate, settled_amount, taxable_amount_value, 
            net_profit, tds, tcs, invoice_tax_rate)

# --- NEW FUNCTION: Find Discount for Target Profit ---
def find_discount_for_target_profit(mrp, target_profit, apply_royalty, marketing_fee_rate, product_cost, platform):
    """Finds the maximum discount allowed (in 1.0 steps) to achieve at least the target profit."""
    
    # Calculate max possible profit (at 0 discount)
    (_, _, _, _, _, _, _, _, _, _, initial_profit, _, _, _) = perform_calculations(mrp, 0.0, apply_royalty, marketing_fee_rate, product_cost, platform)

    if initial_profit < target_profit:
        # Target profit is unachievable even with zero discount
        return None, initial_profit, 0.0 # required_discount, max_profit, max_discount_percent
    
    # Binary search/Iteration setup
    discount_step = 1.0 # Step size for finding the discount
    required_discount = 0.0
    
    # Iteratively increase discount until profit drops below target
    while required_discount <= mrp:
        # The relationship is inverse: more discount -> less profit.
        (_, _, _, _, _, _, _, _, _, _, current_profit, _, _, _) = perform_calculations(mrp, required_discount, apply_royalty, marketing_fee_rate, product_cost, platform)
        
        if current_profit < target_profit:
            # We crossed the target. The best discount is the previous step.
            # Use the previous discount to calculate final metrics
            final_discount = max(0.0, required_discount - discount_step)
            # Re-calculate with the final discount for accurate output
            (_, _, _, _, _, _, _, _, settled_amount, _, final_profit, _, _, _) = perform_calculations(mrp, final_discount, apply_royalty, marketing_fee_rate, product_cost, platform)
            
            discount_percent = (final_discount / mrp) * 100
            return final_discount, final_profit, discount_percent
        
        required_discount += discount_step

    # Fallback for full MRP discount case (should only happen if profit is still > target at full discount)
    (_, _, _, _, _, _, _, _, settled_amount, _, final_profit, _, _, _) = perform_calculations(mrp, mrp, apply_royalty, marketing_fee_rate, product_cost, platform)
    discount_percent = 100.0
    return mrp, final_profit, discount_percent


# --- 2. STREAMLIT APP STRUCTURE ---

st.title("🛍️ " + FULL_TITLE)
st.markdown("###### **1. Input and Configuration**")

# --- PLATFORM SELECTOR ---
platform_selector = st.radio(
    "Select Platform:",
    ('Myntra', 'FirstCry', 'Ajio'), # Options updated here
    index=0, 
    horizontal=True
)

# --- CONFIGURATION (UPDATED LAYOUT AND MARKETING FEE SELECTOR) ---
st.markdown("##### **Configuration Settings**")

# Row 1: Calculation Mode, Royalty, Marketing Fee - 3 Columns
col_mode, col_royalty, col_marketing = st.columns(3)

with col_mode:
    # Calculation Mode Selector
    calculation_mode = st.radio(
        "Calculation Mode:",
        ('Profit Calculation', 'Target Discount'),
        index=0, 
        label_visibility="visible"
    )

with col_royalty:
    # Royalty Fee Radio Button 
    royalty_base = 'CPA' if platform_selector == 'Myntra' else 'Sale Price'
    royalty_label = f"Royalty Fee (10% of {royalty_base})?"
    
    # Royalty Fee is applicable to all
    apply_royalty = st.radio(
        royalty_label,
        ('Yes', 'No'),
        index=0, 
        horizontal=True,
        label_visibility="visible"
    )

with col_marketing:
    # Marketing Fee Selectbox (Replaced Radio)
    marketing_options = ['0%', '4%', '5%']
    # Set default for Myntra to 4%, others to 0%
    default_index = marketing_options.index('4%') if platform_selector == 'Myntra' else marketing_options.index('0%')
    
    selected_marketing_fee_str = st.selectbox(
        "Marketing Fee Rate:", 
        marketing_options,
        index=default_index,
        help="Rate applied to CPA (Customer Paid Amount) on Myntra.",
        key="marketing_fee_selector"
    )
    # Convert selected string to a float rate (0.00, 0.04, 0.05)
    marketing_fee_rate = float(selected_marketing_fee_str.strip('%')) / 100.0


# Row 2: Product Cost, Target Profit - 2 Columns
col_cost, col_target = st.columns(2)

with col_cost:
    # Product Cost Input
    product_cost = st.number_input(
        "Product Cost (₹)",
        min_value=0.0,
        value=1000.0,
        step=10.0,
        label_visibility="visible"
    )
    
with col_target:
    # Target Margin Input (Used in both modes)
    product_margin_target_rs = st.number_input(
        "Target Net Profit (₹)",
        min_value=0.0,
        value=200.0,
        step=10.0,
        label_visibility="visible"
    )
    # Removed extra spacer as layout is cleaner now


st.divider() 

# --- INPUT FIELDS (Main Body) ---
col_mrp_in, col_discount_in = st.columns(2)

new_mrp = col_mrp_in.number_input(
    "Product MRP (₹)",
    min_value=1.0,
    value=2500.0,
    step=100.0,
    key="new_mrp",
    label_visibility="visible"
) 

# Conditional Discount Input based on Calculation Mode
if calculation_mode == 'Profit Calculation':
    new_discount = col_discount_in.number_input(
        "Discount Amt (₹)",
        min_value=0.0,
        max_value=new_mrp,
        value=500.0,
        step=10.0,
        key="new_discount_manual",
        label_visibility="visible"
    )
else:
    # In Target Discount Finder mode, we don't need a manual discount input
    col_discount_in.info(f"Targeting a Net Profit of ₹ {product_margin_target_rs:,.2f}...")
    new_discount = 0.0 # Placeholder, will be calculated later

st.divider() 

if new_mrp > 0 and product_cost > 0:
    try:
        
        calculated_discount = 0.0
        final_profit = 0.0
        
        # --- MODE 1: Target Discount Finder ---
        if calculation_mode == 'Target Discount':
            
            # Find the required discount to meet the target profit
            target_profit = product_margin_target_rs
            
            # NOTE: Passed marketing_fee_rate (float) instead of apply_marketing_fee (string)
            calculated_discount, initial_max_profit, calculated_discount_percent = find_discount_for_target_profit(
                new_mrp, target_profit, apply_royalty, marketing_fee_rate, product_cost, platform_selector
            )

            if calculated_discount is None:
                # Target unachievable
                st.error(f"Cannot achieve the Target Profit of ₹ {target_profit:,.2f}. The maximum possible Net Profit at 0% discount is ₹ {initial_max_profit:,.2f}.")
                st.stop()
            
            # Use the calculated discount for the main calculation
            new_discount = calculated_discount
            
        # --- MODE 2: Profit Calculation (Direct) ---
        
        # Perform calculations using the actual or calculated discount
        # NOTE: Passed marketing_fee_rate (float) instead of apply_marketing_fee (string)
        (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
         marketing_fee_base, current_marketing_fee_rate, final_commission, 
         commission_rate, settled_amount, taxable_amount_value, 
         net_profit, tds, tcs, invoice_tax_rate) = perform_calculations(new_mrp, new_discount, apply_royalty, marketing_fee_rate, product_cost, platform_selector)
        
        # Calculate Margin Difference for display
        target_profit = product_margin_target_rs
        delta_value = net_profit - target_profit
        
        current_margin_percent = (net_profit / product_cost) * 100 if product_cost > 0 else 0.0

        delta_label = f"vs Target: ₹ {delta_value:,.2f}"
        delta_color = "normal" if net_profit >= target_profit else "inverse"
            
        # --- DISPLAY RESULTS ---
        
        # Section 2: Sales and Revenue (3 columns)
        st.markdown("###### **2. Sales and Revenue**")
        col_mrp_out, col_discount_out, col_sale = st.columns(3)
        
        # Display MRP in the results section too
        col_mrp_out.metric(label="Product MRP (₹)", value=f"₹ {new_mrp:,.2f}", delta_color="off")

        if calculation_mode == 'Target Discount':
            # Display calculated discount in the main area
            discount_percent = (new_discount / new_mrp) * 100 if new_mrp > 0 else 0.0
            col_discount_out.metric(
                label="Required Discount", 
                value=f"₹ {new_discount:,.2f}",
                delta=f"{discount_percent:,.2f}% of MRP",
                delta_color="off"
            )
        else:
              # Display manual discount as entered
            discount_percent = (new_discount / new_mrp) * 100 if new_mrp > 0 else 0.0
            col_discount_out.metric(
                label="Discount Amount", 
                value=f"₹ {new_discount:,.2f}",
                delta=f"{discount_percent:,.2f}% of MRP",
                delta_color="off"
            )
            
        col_sale.metric(label="Sale Price (MRP - Discount)", value=f"₹ {sale_price:,.2f}")
        
        st.divider()
        
        col_gt, col_customer = st.columns(2)
        
        # GT Charge/Fixed Fee display logic
        if platform_selector == 'Myntra':
            col_gt.metric(
                label="GT Charge (Deducted from Sale Price)", 
                value=f"₹ {gt_charge:,.2f}",
                delta="Myntra Only",
                delta_color="off"
            )
        elif platform_selector == 'FirstCry': 
              col_gt.metric(
                label="Fixed Charges", 
                value=f"₹ {gt_charge:,.2f}", # This will be 0.00
                delta_color="off"
            )
        else: # Ajio (New) display
              col_gt.metric(
                label="SCM Charges (₹95 + 18% GST) - Not Deducted in Settlement Payout", 
                value=f"₹ {gt_charge:,.2f}", 
                delta_color="off"
            )
            
        col_customer.metric(label="**Invoice Value (CPA)**", value=f"₹ {customer_paid_amount:,.2f}") # CPA = Sale Price for Ajio/FC, Sale Price - GT for Myntra

        st.divider() 
        
        # Section 3: Deductions (Charges) - 3 COLUMNS, 2 ROWS
        st.markdown("###### **3. Deductions (Charges)**")
        
        # Row 1 (3 columns): Commission/Deduction, Marketing/Other, Royalty
        col1_r1, col2_r1, col3_r1 = st.columns(3)
        
        if platform_selector == 'Myntra':
            col1_r1.metric(
                label=f"Commission ({commission_rate*100:.0f}%+Tax)",
                value=f"₹ {final_commission:,.2f}",
            )
            # Display Marketing Fee based on the actual rate used
            col2_r1.metric(
                label=f"Marketing Fee ({marketing_fee_rate*100:.0f}%)",
                value=f"₹ {marketing_fee_base:,.2f}",
            )
        elif platform_selector == 'FirstCry': 
              col1_r1.metric(
                label="**Flat Deduction (42% on Sale Price)**",
                value=f"₹ {final_commission:,.2f}",
            )
              col2_r1.metric(
                label="Marketing/Other Fees", 
                value="₹ 0.00",
                delta_color="off"
            )
        else: # Ajio (New) display
              commission_rate_ajio = 0.20 # Use 20% for Ajio display
              col1_r1.metric(
                label=f"Commission ({commission_rate_ajio*100:.0f}% on Sale Price + 18% Tax)",
                value=f"₹ {final_commission:,.2f}",
            )
              col2_r1.metric(
                label="Marketing/Other Fees", 
                value="₹ 0.00",
                delta_color="off"
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
        # TDS display update to ensure positive sign
        col2_r2.metric(
            label="TDS (0.1%)",
            value=f"₹ {abs(tds):,.2f}"
        )
        # TCS display update to ensure positive sign
        col3_r2.metric(
            label="TCS (10% on Tax Amt)",
            value=f"₹ {abs(tcs):,.2f}"
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
    st.info("Please enter a valid MRP and Product Cost to start the calculation.")

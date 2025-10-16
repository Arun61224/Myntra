# ... (Calculation Logic Functions remain unchanged)
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

# --- CONFIGURATION (MOVED FROM SIDEBAR) ---
st.markdown("##### **Configuration Settings**")
col_config_1, col_config_2 = st.columns(2)

# Column 1: Mode, Royalty, Marketing
with col_config_1:
    # Calculation Mode Selector
    calculation_mode = st.radio(
        "Calculation Mode:",
        ('Profit Calculation (for given Discount)', 'Target Discount Finder (for given Profit)'),
        index=0, 
        label_visibility="visible"
    )
    
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

    # Marketing Fee Radio Button 
    apply_marketing_fee_default = 'Yes (4%)' if platform_selector == 'Myntra' else 'No (0%)'
    apply_marketing_fee = st.radio(
        "Marketing Fee (Myntra 4% of CPA)?", 
        ('Yes (4%)', 'No (0%)'),
        index=0 if apply_marketing_fee_default.startswith('Yes') else 1,
        horizontal=True,
        label_visibility="visible"
    )

# Column 2: Product Cost, Target Profit
with col_config_2:
    # Product Cost Input
    product_cost = st.number_input(
        "Product Cost (₹)",
        min_value=0.0,
        value=1000.0,
        step=10.0,
        label_visibility="visible"
    )
    
    # Target Margin Input (Used in both modes)
    product_margin_target_rs = st.number_input(
        "Target Net Profit (₹)",
        min_value=0.0,
        value=200.0,
        step=10.0,
        label_visibility="visible"
    )
    # Added vertical spacer to align inputs better
    st.markdown("<div style='height: 4.5rem;'></div>", unsafe_allow_html=True) 

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
) # <--- यह ब्रैकेट पहले बंद नहीं हो रहा था, अब बंद हो गया है।

# Conditional Discount Input based on Calculation Mode
if calculation_mode == 'Profit Calculation (for given Discount)':
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
        if calculation_mode == 'Target Discount Finder (for given Profit)':
            
            # Find the required discount to meet the target profit
            target_profit = product_margin_target_rs
            
            calculated_discount, initial_max_profit, calculated_discount_percent = find_discount_for_target_profit(
                new_mrp, target_profit, apply_royalty, apply_marketing_fee, product_cost, platform_selector
            )

            if calculated_discount is None:
                # Target unachievable
                st.error(f"Cannot achieve the Target Profit of ₹ {target_profit:,.2f}. The maximum possible Net Profit at 0% discount is ₹ {initial_max_profit:,.2f}.")
                st.stop()
            
            # Use the calculated discount for the main calculation
            new_discount = calculated_discount
            
        # --- MODE 2: Profit Calculation (Direct) ---
        
        # Perform calculations using the actual or calculated discount
        (sale_price, gt_charge, customer_paid_amount, royalty_fee, 
         marketing_fee_base, marketing_fee_rate, final_commission, 
         commission_rate, settled_amount, taxable_amount_value, 
         net_profit, tds, tcs, invoice_tax_rate) = perform_calculations(new_mrp, new_discount, apply_royalty, apply_marketing_fee, product_cost, platform_selector)
        
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

        if calculation_mode == 'Target Discount Finder (for given Profit)':
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
            # Display Marketing Fee based on the selected rate
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

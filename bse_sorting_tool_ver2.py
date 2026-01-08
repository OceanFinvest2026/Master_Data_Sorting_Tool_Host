import streamlit as st
import pandas as pd
import io

# Set page configuration
st.set_page_config(
    page_title="BSE Master Data Sorting Tool",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)
# Custom CSS for Dark Theme and Aesthetics
st.caption(f"Streamlit version: {st.__version__}")
st.markdown("""
    <style>
    /* Global Reset & Dark Theme */
    body {
        color: #ffffff;
        background-color: #0e1117;
    }
    .stApp {
        background-color: #0e1117;
    }
    
    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #161b22 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.2);
    }
    
    /* Headers & Text High Contrast */
    h1, h2, h3, h4, h5, h6 {
        color: #ffffff !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 600;
    }
    p, label, span, div {
        color: #e0e0e0;
    }
    
    /* DataFrames & Tables */
    /* Target the container */
    .stDataFrame {
        background-color: #161b22 !important;
        border: 1px solid rgba(255, 255, 255, 0.3);
        border-radius: 8px;
    }
    
    /* Buttons (Green Action) */
    .stButton > button {
        background-color: #2e7d32 !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1b5e20 !important;
        border-color: #ffffff !important;
        transform: translateY(-2px);
    }

    /* Generic button fallback (covers different Streamlit DOM structures) */
    .stApp :where(button, input[type="button"], input[type="submit"]) {
        background-color: #2e7d32 !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px !important;
        padding: 0.4rem 1rem !important;
        font-weight: 600 !important;
    }
    .stApp :where(button, input[type="button"], input[type="submit"]):hover {
        background-color: #1b5e20 !important;
    }
    
    /* Download Buttons (Blue Action) */
    .stDownloadButton > button,
    .stApp :where(a[data-testid="stDownloadButton"], div[data-testid="stDownloadButton"]) > button {
        background-color: #1565c0 !important;
        color: white !important;
        border: 1px solid rgba(255, 255, 255, 0.3) !important;
        border-radius: 8px;
        width: 100%;
        transition: all 0.3s ease;
    }
    .stDownloadButton > button:hover,
    .stApp :where(a[data-testid="stDownloadButton"], div[data-testid="stDownloadButton"]) > button:hover {
        background-color: #0d47a1 !important;
        border-color: #ffffff !important;
    }

    /* Metrics */
    div[data-testid="stMetricValue"] {
        color: #4fc3f7 !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #cfd8dc !important;
    }
    
    /* File Uploader - Explicit Darkening */
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #161b22 !important;
        border: 1px dashed rgba(255, 255, 255, 0.4) !important;
        border-radius: 10px;
    }
    div[data-testid="stFileUploader"] {
        background-color: transparent !important;
    }
    
    /* "Drag and drop file here" and "Limit 200MB..." text */
    div[data-testid="stFileUploaderDropzone"] div {
        color: #ffffff !important;
    }
    div[data-testid="stFileUploaderDropzone"] small {
        color: #ffffff !important;
    }

    /* "Browse files" Button Text — Dark background with white text */
    div[data-testid="stFileUploaderDropzone"] button,
    .stApp input[type="file"] + label,
    .stApp input[type="file"] {
        color: #ffffff !important;
        background-color: #161b22 !important; /* same dark background as app */
        border: 1px solid rgba(255,255,255,0.12) !important;
        font-weight: 600 !important;
        padding: 0.4rem 0.9rem !important;
        border-radius: 8px !important;
    }
    div[data-testid="stFileUploaderDropzone"] button:hover {
        background-color: #1f2933 !important;
    }

    /* DataFrame/Table styling for dark theme */
    .stDataFrame, .stDataFrame > div {
        background-color: #161b22 !important;
        color: #ffffff !important;
        border-radius: 8px;
    }
    .stDataFrame table {
        background-color: transparent !important;
        color: #ffffff !important;
        border-collapse: collapse !important;
    }
    .stDataFrame thead th {
        color: #ffffff !important;
        border-bottom: 1px solid rgba(255,255,255,0.12) !important;
        background-color: #161b22 !important;
    }
    .stDataFrame tbody td {
        color: #ffffff !important;
        border: 1px solid rgba(255,255,255,0.06) !important;
        padding: 6px 8px !important;
    }
    .stDataFrame tbody tr:nth-child(odd) td {
        background-color: rgba(255,255,255,0.02) !important;
    }
    
    /* Mobile Responsiveness */
    @media (max-width: 768px) {
        .stButton > button {
            width: 100%;
            margin-bottom: 0.5rem;
        }
        .stDownloadButton > button {
            width: 100%;
        }
        .css-1r6slb0, .stDataFrame, .stAlert, div[data-testid="stFileUploaderDropzone"] {
            padding: 10px;
        }
        h1 {
            font-size: 1.8rem !important;
        }
    }
    </style>
""", unsafe_allow_html=True)

# Application Header - Keeping it very close to original as requested
st.title("📊 BSE Master Data Sorting Tool (Ver 2)")
st.markdown("---")

# Sidebar for Configuration
st.sidebar.header("Configuration")
uploaded_file = st.sidebar.file_uploader("Upload Master Data CSV", type=['csv'])

# Processing Function
def process_data(df):
    results = {}
    
    # Standardize column names for easier access (optional, but good for robustness)
    # keeping original names for output, using stripped upper for logic
    df.columns = [c.strip() for c in df.columns]
    
    # 1. Deduplication
    total_raw_rows = len(df)
    df_unique = df.drop_duplicates(keep='first')
    unique_rows = len(df_unique)
    
    results['master_data'] = df_unique
    
    # Initialize containers
    categories = {
        "Direct_Payout": [],
        "Direct_Reinvestment": [],
        "Regular_Payout": [],
        "Regular_Reinvestment": [],
        "Inseparable": [] # Kept for consistency
    }
    
    # Logic Iteration
    # Converting to dictionaries for faster iteration than iterrows
    rows = df_unique.to_dict('records')
    
    for row in rows:
        scheme_plan = str(row.get("Scheme Plan", "")).strip().upper()
        scheme_name = str(row.get("Scheme Name", "")).strip().upper()
        
        category = None
        comment = ""
        
        is_regular = scheme_plan in ["NORMAL", "REGULAR"]
        is_direct = scheme_plan == "DIRECT"
        
        # 1. Primary Keyword Check
        if "GROWTH" in scheme_name:
             pass
        elif "PAYOUT" in scheme_name or "IDCW" in scheme_name:
            if is_regular: category = "Regular_Payout"
            elif is_direct: category = "Direct_Payout"
        elif "REINVESTMENT" in scheme_name:
            if is_regular: category = "Regular_Reinvestment"
            elif is_direct: category = "Direct_Reinvestment"
            
        # 2. Secondary Check (Monthly Payout Keywords)
        if not category:
            payout_keywords = ["MONTHLY", "MONTHLY PAYMENT", "MONTHLY PAY", "MONTHLY PAYOUT"]
            if any(k in scheme_name for k in payout_keywords):
                if is_regular: category = "Regular_Payout"
                elif is_direct: category = "Direct_Payout"
        
        # 3. Final Fallback (Aggressive Catch-all from first_sort.py)
        if not category and (is_regular or is_direct):
            if 'REINVESTMENT' in scheme_name:
                category = "Regular_Reinvestment" if is_regular else "Direct_Reinvestment"
            elif 'IDCW' in scheme_name:
                category = "Regular_Payout" if is_regular else "Direct_Payout"
            
        if category:
            categories[category].append(row)
        else:
            categories['Inseparable'].append(row)

    # Helper function to check Y filters
    def check_filters(row_data):
        # Returns True if Purchase Allowed = Y AND Redemption Allowed = Y
        p_allowed = str(row_data.get("Purchase Allowed", "")).strip().upper() == 'Y'
        r_allowed = str(row_data.get("Redemption Allowed", "")).strip().upper() == 'Y'
        return p_allowed and r_allowed

    # Convert lists back to DataFrames AND Apply Filter
    final_output = {}
    
    # 1. Direct_payout_purchase_redemption_y.csv
    direct_payout_raw = categories["Direct_Payout"]
    filtered_dp = [r for r in direct_payout_raw if check_filters(r)]
    final_output["Direct_payout_purchase_redemption_y"] = pd.DataFrame(filtered_dp) if filtered_dp else pd.DataFrame(columns=df.columns)

    # 2. Direct_reinvestment_purchase_redemption_y.csv
    direct_reinv_raw = categories["Direct_Reinvestment"]
    filtered_dr = [r for r in direct_reinv_raw if check_filters(r)]
    final_output["Direct_reinvestment_purchase_redemption_y"] = pd.DataFrame(filtered_dr) if filtered_dr else pd.DataFrame(columns=df.columns)

    # 3. Regular_payout_purchase_redemption_y.csv
    regular_payout_raw = categories["Regular_Payout"]
    filtered_rp = [r for r in regular_payout_raw if check_filters(r)]
    final_output["Regular_payout_purchase_redemption_y"] = pd.DataFrame(filtered_rp) if filtered_rp else pd.DataFrame(columns=df.columns)

    # 4. rEGULAR_REINVESTMENT_PURCHASE_REDEMPTION_y.csv
    regular_reinv_raw = categories["Regular_Reinvestment"]
    filtered_rr = [r for r in regular_reinv_raw if check_filters(r)]
    final_output["rEGULAR_REINVESTMENT_PURCHASE_REDEMPTION_y"] = pd.DataFrame(filtered_rr) if filtered_rr else pd.DataFrame(columns=df.columns)

    return final_output, results['master_data'], total_raw_rows, unique_rows, len(categories['Inseparable'])

# Main Action
if uploaded_file is None:
    # Try looking for local master_data.csv
    try:
        local_df = pd.read_csv("master_data.csv", encoding='utf-8-sig')
        st.info("Loaded 'master_data.csv' from local directory. You can also upload a file in the sidebar.")
        df = local_df
        file_ready = True
    except FileNotFoundError:
        st.warning("No 'master_data.csv' found locally. Please upload a file.")
        df = None
        file_ready = False
else:
    df = pd.read_csv(uploaded_file, encoding='utf-8-sig')
    file_ready = True

if file_ready and df is not None:
    st.subheader("Data Preview")
    st.dataframe(df.head(), use_container_width=True)
    
    if st.button("Process Data", type="primary"):
        with st.spinner("Processing..."):
            try:
                filtered_results, master_cleaned, total, unique, inseparable_count = process_data(df)
                
                # Metrics - Keeping the 3-column layout same as original
                st.markdown("### Processing Summary")
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Input Rows", total)
                c2.metric("Unique Rows", unique)
                c3.metric("Inseparable Rows (Excluded)", inseparable_count)
                
                st.success("Processing Complete!")
                
                # Separate Result Groups
                st.markdown("### Filtered Lists")
                
                # Helper to create download button
                def make_download_btn(label, data, filename):
                    csv = data.to_csv(index=False).encode('utf-8')
                    st.download_button(
                        label=f"📥 {label} ({len(data)})",
                        data=csv,
                        file_name=filename,
                        mime='text/csv'
                    )

                col1, col2 = st.columns(2)
                
                with col1:
                    make_download_btn("Direct Payout (Pur=Y, Red=Y)", filtered_results['Direct_payout_purchase_redemption_y'], "Direct_payout_purchase_redemption_y.csv")
                    make_download_btn("Direct Reinvestment (Pur=Y, Red=Y)", filtered_results['Direct_reinvestment_purchase_redemption_y'], "Direct_reinvestment_purchase_redemption_y.csv")
                    make_download_btn("Master Data Cleaned", master_cleaned, "mASTER_DATA_CLEANED_CSV.csv")

                with col2:
                    make_download_btn("Regular Payout (Pur=Y, Red=Y)", filtered_results['Regular_payout_purchase_redemption_y'], "Regular_payout_purchase_redemption_y.csv")
                    make_download_btn("Regular Reinvestment (Pur=Y, Red=Y)", filtered_results['rEGULAR_REINVESTMENT_PURCHASE_REDEMPTION_y'], "rEGULAR_REINVESTMENT_PURCHASE_REDEMPTION_y.csv")

            except Exception as e:
                st.error(f"An error occurred during processing: {e}")
                st.exception(e)

else:
    st.info("Awaiting input data...")

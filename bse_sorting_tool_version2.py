import streamlit as st
import pandas as pd
import io

# Set page configuration
st.set_page_config(
    page_title="BSE Master Data Sorting Tool V2",
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

# Application Header
st.title("📊 BSE Master Data Sorting Tool V2")
st.markdown("---")

# Sidebar for Configuration
st.sidebar.header("Configuration")
uploaded_file = st.sidebar.file_uploader("Upload Master Data CSV", type=['csv'])

# Processing Function
def process_data(df):
    results = {}
    
    # Standardize column names for easier access (optional, but good for robustness)
    df.columns = [c.strip() for c in df.columns]
    
    # 1. Deduplication
    total_raw_rows = len(df)
    df_unique = df.drop_duplicates(keep='first')
    unique_rows = len(df_unique)
    
    results['master_data'] = df_unique
    
    # Initialize containers
    categories = {
        "Direct_Growth": [],
        "Direct_Payout": [],
        "Direct_Reinvestment": [],
        "Regular_Growth": [],
        "Regular_Payout": [],
        "Regular_Reinvestment": [],
        "Inseparable": []
    }
    
    # Logic Iteration
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
            if is_regular: category = "Regular_Growth"
            elif is_direct: category = "Direct_Growth"
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
        
        # 3. Final Fallback
        if not category and (is_regular or is_direct):
            if 'REINVESTMENT' in scheme_name:
                category = "Regular_Reinvestment" if is_regular else "Direct_Reinvestment"
            elif 'IDCW' in scheme_name:
                category = "Regular_Payout" if is_regular else "Direct_Payout"
            else:
                category = "Regular_Growth" if is_regular else "Direct_Growth"
                comment = "Classified as Growth via fallback logic."

        # 4. Handle completely unknown Plans
        if not category:
            comment = f"Unknown Scheme Plan: {scheme_plan}" if not comment else comment

        if category:
            categories[category].append(row)
        else:
            row_copy = row.copy()
            row_copy['Comment'] = comment
            categories['Inseparable'].append(row_copy)

    # Convert lists back to DataFrames
    for cat, data in categories.items():
        if data:
            results[cat] = pd.DataFrame(data)
        else:
            results[cat] = pd.DataFrame(columns=df.columns)

    # New Filtered Categories based on user request
    def filter_y_both(df_cat):
        if df_cat.empty:
            return df_cat
        mask = (df_cat["Purchase Allowed"].astype(str).str.strip().str.upper() == 'Y') & \
               (df_cat["Redemption Allowed"].astype(str).str.strip().str.upper() == 'Y')
        return df_cat[mask]

    results['Direct_Payout_Y'] = filter_y_both(results['Direct_Payout'])
    results['Direct_Reinvestment_Y'] = filter_y_both(results['Direct_Reinvestment'])
    results['Regular_Payout_Y'] = filter_y_both(results['Regular_Payout'])
    results['Regular_Reinvestment_Y'] = filter_y_both(results['Regular_Reinvestment'])

    return results, total_raw_rows, unique_rows

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
                results, total, unique = process_data(df)
                
                # Metrics
                st.markdown("### Processing Summary")
                c1, c2, c3 = st.columns(3)
                c1.metric("Total Input Rows", total)
                c2.metric("Unique Rows", unique)
                c3.metric("Inseparable Rows", len(results['Inseparable']))
                
                st.success("Processing Complete!")
                
                # Separate Result Groups
                st.markdown("### Export Files")
                
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
                    st.markdown("#### Main Categories")
                    make_download_btn("Direct Growth", results['Direct_Growth'], "Direct_Growth.csv")
                    make_download_btn("Direct Payout", results['Direct_Payout'], "Direct_Payout.csv")
                    make_download_btn("Direct Reinvestment", results['Direct_Reinvestment'], "Direct_Reinvestment.csv")
                    make_download_btn("Regular Growth", results['Regular_Growth'], "Regular_Growth.csv")
                    make_download_btn("Regular Payout", results['Regular_Payout'], "Regular_Payout.csv")
                    make_download_btn("Regular Reinvestment", results['Regular_Reinvestment'], "Regular_Reinvestment.csv")
                    
                    if not results['Inseparable'].empty:
                         st.error(f"Inseparable Data Found: {len(results['Inseparable'])} rows")
                    make_download_btn("Inseparable", results['Inseparable'], "Inseparable.csv")

                with col2:
                    st.markdown("#### Filtered Lists")
                    # 1. Direct_payout_purchase_redemption_y.csv
                    make_download_btn("Direct Payout (P&R=Y)", results['Direct_Payout_Y'], "Direct_payout_purchase_redemption_y.csv")
                    # 2. Direct_reinvestment_purchase_redemption_y.csv
                    make_download_btn("Direct Reinvestment (P&R=Y)", results['Direct_Reinvestment_Y'], "Direct_reinvestment_purchase_redemption_y.csv")
                    # 3. Regular_payout_purchase_redemption_y.csv
                    make_download_btn("Regular Payout (P&R=Y)", results['Regular_Payout_Y'], "Regular_payout_purchase_redemption_y.csv")
                    # 4. rEGULAR_REINVESTMENT_PURCHASE_REDEMPTION_y.csv
                    make_download_btn("Regular Reinvestment (P&R=Y)", results['Regular_Reinvestment_Y'], "Regular_reinvestment_purchase_redemption_y.csv")
                    # 5. MASTER_DATA_CLEANED_CSV
                    make_download_btn("Master Data (Cleaned)", results['master_data'], "master_data_cleaned.csv")
                
            except Exception as e:
                st.error(f"An error occurred during processing: {e}")
                st.exception(e)

else:
    st.info("Awaiting input data...")

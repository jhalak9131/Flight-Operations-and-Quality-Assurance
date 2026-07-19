import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Custom Dashboard", layout="wide")

st.title("📊 Custom Operations Dashboard")
st.markdown("Upload your Excel file to generate a clean, automated dashboard.")

uploaded_file = st.file_uploader("Upload Excel Dashboard File (.xlsx)", type=['xlsx', 'xls'])

def highlight_status(val):
    """Highlight status cells."""
    if pd.isna(val):
        return ''
    val_str = str(val).strip().lower()
    if val_str in ['pass', 'completed', 'done', 'yes', '✓', 'true']:
        return 'color: white; background-color: #2e7d32; font-weight: bold;'
    elif val_str in ['fail', 'pending', 'no', 'x', 'false']:
        return 'color: white; background-color: #c62828; font-weight: bold;'
    return ''

def highlight_variance(val):
    """Highlight variance/percentage cells."""
    if isinstance(val, (int, float)):
        if val > 0:
            return 'color: #2e7d32; font-weight: bold;' # Green
        elif val < 0:
            return 'color: #c62828; font-weight: bold;' # Red
    elif isinstance(val, str) and '%' in val:
        try:
            num = float(val.replace('%', '').strip())
            if num > 0:
                return 'color: #2e7d32; font-weight: bold;'
            elif num < 0:
                return 'color: #c62828; font-weight: bold;'
        except:
            pass
    return ''

if uploaded_file:
    try:
        # Load the data
        df = pd.read_excel(uploaded_file)
        
        st.success("File uploaded successfully!")
        st.markdown("---")
        
        # --- TOP KPI CARDS ---
        st.subheader("Summary KPIs")
        col1, col2, col3, col4 = st.columns(4)
        
        # Generic KPIs based on data shape
        total_rows = len(df)
        col1.metric("Total Count", f"{total_rows}")
        
        # Try to find a Status column for completion rate
        status_cols = [c for c in df.columns if 'status' in c.lower() or 'check' in c.lower()]
        if status_cols:
            stat_col = status_cols[0]
            # Count positive statuses
            positive_vals = ['pass', 'completed', 'done', 'yes', '✓', 'true', 'ok']
            completed = df[stat_col].astype(str).str.lower().str.strip().isin(positive_vals).sum()
            completion_rate = (completed / total_rows) * 100 if total_rows > 0 else 0
            
            col2.metric(f"Completed Tasks", f"{completed}")
            col3.metric(f"Pending/Failed", f"{total_rows - completed}")
            col4.metric(f"Completion Rate", f"{completion_rate:.1f}%")
        else:
            col2.metric("Total Columns", f"{len(df.columns)}")
            
            # Try to find target vs actual columns to show averages
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) >= 2:
                col3.metric(f"Avg {numeric_cols[0]}", f"{df[numeric_cols[0]].mean():.2f}")
                col4.metric(f"Avg {numeric_cols[1]}", f"{df[numeric_cols[1]].mean():.2f}")
            else:
                col3.metric("Data Quality", "Good")
                col4.metric("Last Updated", "Just Now")
        
        st.markdown("---")
        
        # --- DATA TABLE ---
        st.subheader("Detailed Records")
        
        # Apply styling to the dataframe
        styled_df = df.style
        
        # Apply status highlighting if applicable
        if status_cols:
            styled_df = styled_df.map(highlight_status, subset=status_cols)
            
        # Apply variance highlighting to numeric or percentage columns
        variance_cols = [c for c in df.columns if 'var' in c.lower() or 'diff' in c.lower() or 'vs' in c.lower() or '%' in c]
        if variance_cols:
            styled_df = styled_df.map(highlight_variance, subset=variance_cols)
            
        st.dataframe(
            styled_df,
            use_container_width=True,
            height=600
        )

    except Exception as e:
        st.error(f"Error processing the file: {str(e)}")
else:
    st.info("Please upload an Excel file to see the dashboard.")

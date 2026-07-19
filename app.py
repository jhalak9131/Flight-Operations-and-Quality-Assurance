import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from data_processor import process_and_merge, rule_based_analysis
from ml_model import run_anomaly_detection

st.set_page_config(page_title="FOQA Dashboard", layout="wide")

st.title("FOQA Flight Data Analysis Dashboard")
st.markdown("Upload FDR Excel files (GP1, GP2, GP9, GP16) to automatically detect anomalies, temperature exceedances, and monitor pilot performance.")

# Offline Note
st.info("System is running in Offline Mode. All models and logic are executed locally without internet dependencies.")

uploaded_files = st.file_uploader("Upload Excel Files (.xlsx)", accept_multiple_files=True, type=['xlsx'])

if uploaded_files:
    # Convert uploaded files into a dict mapping filename to BytesIO
    files_dict = {f.name: f for f in uploaded_files}
    
    with st.spinner("Processing data offline..."):
        # Process and merge
        merged_df, individual_dfs = process_and_merge(files_dict)
        
        if merged_df is not None:
            # Run Rule-based logic
            df_analyzed, rb_results = rule_based_analysis(merged_df)
            
            # Run ML logic
            df_final = run_anomaly_detection(df_analyzed)
            
            # Clean up empty strings globally to prevent Arrow and Plotly crashes
            df_final.replace(r'^\s*$', np.nan, regex=True, inplace=True)
            
            st.success("Data processed successfully!")
            
            # Dashboard KPIs
            st.header("Flight Summary & KPIs")
            col1, col2, col3, col4 = st.columns(4)
            
            col1.metric("Rows Analyzed", f"{len(df_final):,}")
            col2.metric("Active Phase Rows (Nf1 > 10)", f"{df_final['Active'].sum():,}")
            
            tgt_exceedances = rb_results.get('TGT_Exceedance_Count', 0)
            col3.metric("TGT Exceedances (>620°C)", tgt_exceedances, delta_color="inverse")
            
            life_insight = rb_results.get('Life_Consumption', 'Normal')
            col4.metric("Life Consumption", life_insight)
            
            st.markdown("---")
            
            # Display Stats Table
            st.subheader("Engine Stability Statistics")
            st.markdown("Calculated across the entire column (including idle phases where Nf1/Ng1 ≈ -0.4)")
            
            stats_dict = rb_results.get('Stats', {})
            if stats_dict:
                # Restructure stats dict to display as dataframe
                stats_df_data = {}
                for param in ['Nf1', 'Ng1', 'T451', 'TGT452']:
                    if f'{param}_Mean' in stats_dict:
                        stats_df_data[param] = {
                            "Mean": round(stats_dict[f'{param}_Mean'], 2),
                            "Std (Stability)": round(stats_dict[f'{param}_Std'], 2),
                            "Count (Valid Rows)": stats_dict[f'{param}_Count']
                        }
                if stats_df_data:
                    st.table(pd.DataFrame(stats_df_data).T)
            
            st.markdown("---")
            
            # System Warnings
            warnings = rb_results.get('System_Warnings', [])
            if warnings:
                st.error(f"Critical System Warnings Detected: {', '.join(warnings)}")
            else:
                st.success("No Critical System Warnings Detected.")
            
            # Limits Report Table
            st.header("Component Limits Exceedance Report")
            limits_data = rb_results.get('Limits_Report', [])
            if limits_data:
                limits_df = pd.DataFrame(limits_data)
                
                # Apply styling to highlight FAIL status
                def highlight_status(val):
                    color = '#ff4b4b' if val == 'FAIL' else '#00cc96'
                    return f'color: white; background-color: {color}'
                    
                st.dataframe(limits_df.style.map(highlight_status, subset=['Status']), use_container_width=True)
            else:
                st.info("No limit parameters found in uploaded data.")
            
            st.markdown("---")
            
            # Visualizations
            st.header("Trend Analysis")
            
            # TGT and Ng1 over Time
            if 'Time' in df_final.columns and 'TGT452' in df_final.columns and 'Ng1' in df_final.columns:
                fig = px.line(df_final, x=df_final.index, y=['TGT452', 'Ng1'], title="TGT & Ng1 over Time")
                fig.add_hline(y=620, line_dash="dash", line_color="red", annotation_text="TGT Limit (620°C)")
                st.plotly_chart(fig, use_container_width=True)
                
            # Plotly ML Anomalies
            if 'Anomaly_ML' in df_final.columns and df_final['Anomaly_ML'].any():
                st.subheader("Machine Learning Anomalies")
                st.markdown("The Isolation Forest model detected unusual deviations in engine behavior during the following periods.")
                anomalies_df = df_final[df_final['Anomaly_ML']]
                
                fig2 = px.scatter(df_final, x=df_final.index, y='TGT452', color='Anomaly_ML',
                                  color_discrete_map={True: 'red', False: 'blue'},
                                  title="Detected Anomalies in TGT")
                st.plotly_chart(fig2, use_container_width=True)
                
                st.dataframe(anomalies_df[['Time', 'Nf1', 'Ng1', 'T451', 'TGT452']])
                
            # Rule Based Anomalies Data
            if df_final['Anomaly_RuleBased'].any():
                st.subheader("TGT Exceedance Data (Rule-Based)")
                st.dataframe(df_final[df_final['Anomaly_RuleBased']][['Time', 'Nf1', 'Ng1', 'T451', 'TGT452']])
                
            # Raw Data Expander with Per-Row Component Logic
            st.header("Row-by-Row Exceedance Analysis")
            st.markdown("This interactive table adds a new column (`Exceedance_Details`) to your Excel data, automatically analyzing which components failed for each specific row.")
            
            # Show only the most relevant columns first
            display_cols = ['Time', 'Exceedance_Details', 'Anomaly_RuleBased', 'Anomaly_ML']
            other_cols = [c for c in df_final.columns if c not in display_cols]
            
            # Fix Arrow serialization issues by replacing space strings with NaN
            df_to_display = df_final[display_cols + other_cols].copy()
            df_to_display.replace(r'^\s*$', np.nan, regex=True, inplace=True)
            
            st.dataframe(df_to_display, use_container_width=True)
            
            # Provide Download button for the analyzed Excel file
            @st.cache_data
            def convert_df_to_csv(df):
                return df.to_csv(index=False).encode('utf-8')
                
            csv = convert_df_to_csv(df_final)
            st.download_button(
                label="📥 Download Analyzed Excel Data (with Status Columns)",
                data=csv,
                file_name="FOQA_Analyzed_FDR.csv",
                mime="text/csv",
            )
        else:
            st.warning("Could not process the uploaded files. Please ensure you upload valid GP files containing FDR headers.")
else:
    st.info("Please upload one or more FDR Excel files to begin analysis.")

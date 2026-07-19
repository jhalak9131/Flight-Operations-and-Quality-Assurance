import pandas as pd
import numpy as np

def identify_group(df):
    """Identify which GP group the dataframe belongs to based on columns."""
    cols = set(df.columns)
    if 'TGT452' in cols or 'Nf1' in cols:
        return 'GP1'
    elif 'RADALT' in cols or 'PP_LAT' in cols:
        return 'GP2'
    elif 'MGBPR#1' in cols or 'FIRE1' in cols:
        return 'GP9'
    elif 'PWRLOSS' in cols or 'OEIQLMT' in cols:
        return 'GP16'
    return 'UNKNOWN'

def process_and_merge(files):
    """
    Takes a dictionary of {filename: file_buffer}
    Returns a single merged dataframe and a dictionary of individual DataFrames.
    """
    dataframes = {}
    
    # Read each uploaded file
    for filename, file_buffer in files.items():
        try:
            df = pd.read_excel(file_buffer)
            
            # Check for and remove units/sub-header row (commonly has NaN in Time column at index 0)
            if 'Time' in df.columns and not df.empty and pd.isna(df['Time'].iloc[0]):
                df = df.iloc[1:].reset_index(drop=True)
                
            # Forward fill the time column if it has NaNs (common in these logs)
            if 'Time' in df.columns:
                df['Time'] = df['Time'].ffill()
                
            group = identify_group(df)
            if group != 'UNKNOWN':
                dataframes[group] = df
        except Exception as e:
            print(f"Error reading {filename}: {e}")
            continue

    if not dataframes:
        return None, dataframes

    # Try to merge on 'Time' if multiple groups exist
    merged_df = None
    if 'GP1' in dataframes:
        merged_df = dataframes['GP1'].copy()
        
    for gp in ['GP2', 'GP9', 'GP16']:
        if gp in dataframes:
            if merged_df is None:
                merged_df = dataframes[gp].copy()
            else:
                # Merge on Time if available
                if 'Time' in merged_df.columns and 'Time' in dataframes[gp].columns:
                    # Drop duplicate columns except Time before merging
                    cols_to_use = dataframes[gp].columns.difference(merged_df.columns).tolist()
                    cols_to_use.append('Time')
                    # Drop duplicates in time to avoid exploding join
                    df_to_join = dataframes[gp][cols_to_use].drop_duplicates(subset=['Time'])
                    merged_df = pd.merge(merged_df, df_to_join, on='Time', how='left')

    return merged_df, dataframes

def rule_based_analysis(df):
    """
    Applies transparent logic from the Correlation Matrix:
    - Active Phase: Nf1 > 10
    - Life Consumption High: Sustained TGT > 620
    """
    results = {}
    
    if df is None or df.empty:
        return results

    df = df.copy()
    
    # Convert relevant columns to numeric, forcing errors to NaN
    for col in ['Nf1', 'Nf2', 'Ng1', 'Ng2', 'T451', 'TGT452']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')

    # Identify Active Phase
    if 'Nf1' in df.columns:
        df['Active'] = df['Nf1'] > 10
    else:
        df['Active'] = False

    active_df = df[df['Active']]
    
    # Temperature Exceedance (TGT > 620)
    if 'TGT452' in active_df.columns:
        exceedances = active_df[active_df['TGT452'] > 620]
        results['TGT_Exceedance_Count'] = len(exceedances)
        results['Max_TGT'] = active_df['TGT452'].max()
    else:
        results['TGT_Exceedance_Count'] = 0
        results['Max_TGT'] = None

    # Calculate Means, Stds & Counts for the ENTIRE column (including idle phases ≈ -0.4)
    stats = {}
    for col in ['Nf1', 'Ng1', 'T451', 'TGT452']:
        if col in df.columns:
            stats[f'{col}_Mean'] = df[col].mean()
            stats[f'{col}_Std'] = df[col].std()
            stats[f'{col}_Count'] = df[col].count()
            
    # Life Consumption Insight
    life_consumption = "Normal"
    if 'TGT452' in df.columns:
        mean_tgt = stats.get('TGT452_Mean', 0)
        idle_count = (df['Nf1'] < 0).sum() if 'Nf1' in df.columns else 0
        
        if results['TGT_Exceedance_Count'] > 5 and mean_tgt > 500:
            life_consumption = "Very High (Highest average TGT + high power)"
        elif results['TGT_Exceedance_Count'] > 0:
            life_consumption = "High (Sustained TGT > 620°C)"
        elif idle_count > (len(df) * 0.4): # More than 40% idle
            life_consumption = "Low (Long idle periods ≈ -0.4)"
            
    results['Life_Consumption'] = life_consumption
            
    results['Stats'] = stats
    
    # System Warnings (GP9 & GP16)
    warnings = []
    warning_cols = ['FIRE1', 'FIRE2', 'VNEWARN', 'PWRLOSS']
    for wc in warning_cols:
        if wc in df.columns:
            # Check if warning triggered (assuming 1/True or non-zero means warning)
            # converting to numeric
            temp_s = pd.to_numeric(df[wc], errors='coerce').fillna(0)
            if (temp_s > 0).any():
                warnings.append(wc)
                
    results['System_Warnings'] = warnings
    # Add detailed exceedance column to the dataframe
    def get_exceedance_details(row):
        details = []
        try:
            if 'TGT452' in row and pd.notna(row['TGT452']) and float(row['TGT452']) > 620:
                details.append(f"TGT Exceed ({row['TGT452']})")
        except (ValueError, TypeError):
            pass
            
        try:
            if 'Nf1' in row and pd.notna(row['Nf1']) and float(row['Nf1']) > 110: # Example limit
                details.append(f"Nf1 Overspeed ({row['Nf1']})")
        except (ValueError, TypeError):
            pass
        
        for wc in warning_cols:
            if wc in row and pd.notna(row[wc]):
                try:
                    if float(row[wc]) > 0:
                        details.append(f"Warning: {wc}")
                except (ValueError, TypeError):
                    pass
                
        return " | ".join(details) if details else "Normal"
        
    df['Exceedance_Details'] = df.apply(get_exceedance_details, axis=1)
    
    # Mark rows that have exceedances for the dataframe
    if 'TGT452' in df.columns:
        df['Anomaly_RuleBased'] = (df['TGT452'] > 620) & df['Active']
    else:
        df['Anomaly_RuleBased'] = False
        
    # Generate Limits Report Table
    limits_report = []
    
    # Define limits (Parameter: Limit)
    limits_config = {
        'TGT452': 620.0,
        'Nf1': 110.0,
        'Ng1': 100.0,
    }
    
    for param, limit in limits_config.items():
        if param in active_df.columns:
            max_val = active_df[param].max()
            exceedances = len(active_df[active_df[param] > limit])
            status = "FAIL" if exceedances > 0 else "PASS"
            limits_report.append({
                "Parameter": param,
                "Limit": limit,
                "Max Value": round(max_val, 2) if pd.notna(max_val) else "-",
                "Exceedances": exceedances,
                "Status": status
            })
            
    results['Limits_Report'] = limits_report

    return df, results

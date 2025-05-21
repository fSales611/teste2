import pandas as pd
import numpy as np

def process_data(df):
    """
    Process the input dataframe for analysis
    - Handle missing values
    - Detect column types
    - Convert date columns to datetime
    
    Args:
        df (pd.DataFrame): The input dataframe
        
    Returns:
        pd.DataFrame: Processed dataframe
    """
    # Create a copy to avoid modifying the original
    processed_df = df.copy()
    
    # Get column types
    numeric_cols = processed_df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = processed_df.select_dtypes(include=['object']).columns.tolist()
    
    # Try to convert potential date columns to datetime
    for col in categorical_cols:
        try:
            # Check if column has date-like strings
            if processed_df[col].astype(str).str.match(r'^\d{4}-\d{2}-\d{2}').any() or \
               processed_df[col].astype(str).str.match(r'^\d{2}/\d{2}/\d{4}').any() or \
               processed_df[col].astype(str).str.match(r'^\d{2}-\d{2}-\d{4}').any():
                processed_df[col] = pd.to_datetime(processed_df[col], errors='coerce')
        except:
            pass
    
    # Handle missing values
    for col in processed_df.columns:
        if col in numeric_cols:
            # Fill numeric missing values with median
            if processed_df[col].isna().any():
                median_val = processed_df[col].median()
                processed_df[col] = processed_df[col].fillna(median_val)
        else:
            # Fill non-numeric missing values with mode or "Unknown"
            if processed_df[col].isna().any():
                if not processed_df[col].dropna().empty:
                    mode_val = processed_df[col].mode()[0]
                    processed_df[col] = processed_df[col].fillna(mode_val)
                else:
                    processed_df[col] = processed_df[col].fillna("Unknown")
    
    return processed_df

def get_summary_stats(df):
    """
    Generate summary statistics for dataframe
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        pd.DataFrame: Summary statistics
    """
    # Initialize list to store summary stats
    summary_data = []
    
    # Get numeric and categorical columns
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    
    # Numeric column statistics
    for col in numeric_cols:
        summary_data.append({
            'Column': col,
            'Type': 'Numeric',
            'Count': df[col].count(),
            'Missing': df[col].isna().sum(),
            'Mean': round(df[col].mean(), 2) if not pd.isna(df[col].mean()) else None,
            'Median': round(df[col].median(), 2) if not pd.isna(df[col].median()) else None,
            'Min': round(df[col].min(), 2) if not pd.isna(df[col].min()) else None,
            'Max': round(df[col].max(), 2) if not pd.isna(df[col].max()) else None,
            'StdDev': round(df[col].std(), 2) if not pd.isna(df[col].std()) else None
        })
    
    # Categorical column statistics
    for col in categorical_cols:
        unique_values = df[col].nunique()
        most_common = df[col].value_counts().index[0] if not df[col].value_counts().empty else "None"
        summary_data.append({
            'Column': col,
            'Type': 'Categorical' if not pd.api.types.is_datetime64_dtype(df[col]) else 'DateTime',
            'Count': df[col].count(),
            'Missing': df[col].isna().sum(),
            'Unique Values': unique_values,
            'Most Common': str(most_common)[:20] + ('...' if len(str(most_common)) > 20 else ''),
            'Mean': None,
            'Median': None,
            'Min': None,
            'Max': None,
            'StdDev': None
        })
    
    return pd.DataFrame(summary_data)

def filter_data(df, column, values):
    """
    Filter dataframe by column values
    
    Args:
        df (pd.DataFrame): Input dataframe
        column (str): Column to filter on
        values (list): List of values to keep
        
    Returns:
        pd.DataFrame: Filtered dataframe
    """
    return df[df[column].isin(values)]

def detect_data_types(df):
    """
    Detect and categorize data types in the DataFrame
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        dict: Dictionary of column types
    """
    column_types = {
        'numeric': [],
        'categorical': [],
        'datetime': [],
        'text': [],
        'boolean': []
    }
    
    for col in df.columns:
        # Check for datetime
        if pd.api.types.is_datetime64_dtype(df[col]):
            column_types['datetime'].append(col)
        
        # Check for numeric
        elif pd.api.types.is_numeric_dtype(df[col]):
            # Check if it's potentially a boolean column
            if df[col].nunique() <= 2 and set(df[col].dropna().unique()).issubset({0, 1, True, False}):
                column_types['boolean'].append(col)
            else:
                column_types['numeric'].append(col)
        
        # Check categorical vs text
        elif pd.api.types.is_object_dtype(df[col]):
            # If most values are unique and strings are long, likely text
            if df[col].nunique() > df.shape[0] * 0.5 or df[col].str.len().mean() > 50:
                column_types['text'].append(col)
            else:
                column_types['categorical'].append(col)
        
        # Default to categorical for other types
        else:
            column_types['categorical'].append(col)
    
    return column_types
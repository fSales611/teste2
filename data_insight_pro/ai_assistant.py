import pandas as pd
import numpy as np
import json
import re
import plotly.express as px
import plotly.graph_objects as go

def query_data_with_ai(query, df):
    """
    Analyze data and answer user queries using rule-based methods
    
    Args:
        query (str): User's question about the data
        df (pd.DataFrame): The dataset
        
    Returns:
        tuple: (response text, chart if generated or None)
    """
    # Create a data profile
    data_profile = create_data_profile(df)
    
    # Convert query to lowercase for easier matching
    query_lower = query.lower()
    
    # Get column types
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime']).columns.tolist()
    
    # Initialize response and visualization
    response = ""
    visualization = None
    
    # Handle summary requests
    if any(word in query_lower for word in ["summarize", "summary", "overview", "describe"]):
        response = f"## Data Summary\n\n"
        response += f"The dataset contains {df.shape[0]} rows and {df.shape[1]} columns.\n\n"
        
        # Add column information
        response += "### Column Information\n\n"
        for col in df.columns:
            if col in numeric_cols:
                response += f"- **{col}**: Numeric column with values from {df[col].min()} to {df[col].max()}, "
                response += f"average: {df[col].mean():.2f}, median: {df[col].median():.2f}\n"
            elif col in datetime_cols:
                response += f"- **{col}**: Date/time column ranging from {df[col].min()} to {df[col].max()}\n"
            else:
                unique_count = df[col].nunique()
                response += f"- **{col}**: Categorical column with {unique_count} unique values\n"
        
        # Create a summary visualization
        if len(numeric_cols) >= 2:
            # Create a scatter matrix of numeric columns
            fig = px.scatter_matrix(
                df,
                dimensions=numeric_cols[:4],  # Use first 4 numeric columns or fewer
                title="Relationships Between Numeric Variables"
            )
            visualization = fig
        
    # Handle statistical questions
    elif any(word in query_lower for word in ["average", "mean", "median", "maximum", "minimum", "correlation", "correlate"]):
        if "average" in query_lower or "mean" in query_lower:
            # Find the column being asked about
            target_col = None
            for col in df.columns:
                if col.lower() in query_lower:
                    target_col = col
                    break
            
            if target_col and target_col in numeric_cols:
                mean_val = df[target_col].mean()
                response = f"## Average Analysis\n\n"
                response += f"The average of **{target_col}** is **{mean_val:.2f}**.\n\n"
                
                # Create a histogram with mean line
                fig = px.histogram(
                    df, 
                    x=target_col,
                    title=f"Distribution of {target_col} with Mean"
                )
                fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                             annotation_text=f"Mean: {mean_val:.2f}", 
                             annotation_position="top right")
                visualization = fig
            else:
                response = "I couldn't identify which numeric column you want to find the average for. Please specify a numeric column name."
                
        elif "median" in query_lower:
            # Find the column being asked about
            target_col = None
            for col in df.columns:
                if col.lower() in query_lower:
                    target_col = col
                    break
            
            if target_col and target_col in numeric_cols:
                median_val = df[target_col].median()
                response = f"## Median Analysis\n\n"
                response += f"The median of **{target_col}** is **{median_val:.2f}**.\n\n"
                
                # Create a histogram with median line
                fig = px.histogram(
                    df, 
                    x=target_col,
                    title=f"Distribution of {target_col} with Median"
                )
                fig.add_vline(x=median_val, line_dash="dash", line_color="green", 
                             annotation_text=f"Median: {median_val:.2f}", 
                             annotation_position="top right")
                visualization = fig
            else:
                response = "I couldn't identify which numeric column you want to find the median for. Please specify a numeric column name."
                
        elif "maximum" in query_lower or "max" in query_lower:
            # Find the column being asked about
            target_col = None
            for col in df.columns:
                if col.lower() in query_lower:
                    target_col = col
                    break
            
            if target_col and target_col in numeric_cols:
                max_val = df[target_col].max()
                max_row = df.loc[df[target_col].idxmax()]
                
                response = f"## Maximum Analysis\n\n"
                response += f"The maximum value of **{target_col}** is **{max_val:.2f}**.\n\n"
                response += f"This occurs in a row with the following values:\n\n"
                
                for col, val in max_row.items():
                    if isinstance(val, (int, float)):
                        response += f"- **{col}**: {val:.2f}\n"
                    else:
                        response += f"- **{col}**: {val}\n"
                
                # Create a histogram highlighting max
                fig = px.histogram(
                    df, 
                    x=target_col,
                    title=f"Distribution of {target_col} with Maximum Highlighted"
                )
                fig.add_vline(x=max_val, line_dash="dash", line_color="red", 
                             annotation_text=f"Max: {max_val:.2f}", 
                             annotation_position="top right")
                visualization = fig
            else:
                response = "I couldn't identify which numeric column you want to find the maximum for. Please specify a numeric column name."
                
        elif "minimum" in query_lower or "min" in query_lower:
            # Find the column being asked about
            target_col = None
            for col in df.columns:
                if col.lower() in query_lower:
                    target_col = col
                    break
            
            if target_col and target_col in numeric_cols:
                min_val = df[target_col].min()
                min_row = df.loc[df[target_col].idxmin()]
                
                response = f"## Minimum Analysis\n\n"
                response += f"The minimum value of **{target_col}** is **{min_val:.2f}**.\n\n"
                response += f"This occurs in a row with the following values:\n\n"
                
                for col, val in min_row.items():
                    if isinstance(val, (int, float)):
                        response += f"- **{col}**: {val:.2f}\n"
                    else:
                        response += f"- **{col}**: {val}\n"
                
                # Create a histogram highlighting min
                fig = px.histogram(
                    df, 
                    x=target_col,
                    title=f"Distribution of {target_col} with Minimum Highlighted"
                )
                fig.add_vline(x=min_val, line_dash="dash", line_color="blue", 
                             annotation_text=f"Min: {min_val:.2f}", 
                             annotation_position="top right")
                visualization = fig
            else:
                response = "I couldn't identify which numeric column you want to find the minimum for. Please specify a numeric column name."
                
        elif "correlation" in query_lower or "correlate" in query_lower:
            if len(numeric_cols) >= 2:
                # Create a correlation matrix
                corr_matrix = df[numeric_cols].corr()
                
                # Find the highest correlation
                highest_corr = 0
                col1_highest = ""
                col2_highest = ""
                
                for col1 in corr_matrix.columns:
                    for col2 in corr_matrix.columns:
                        if col1 != col2 and abs(corr_matrix.loc[col1, col2]) > highest_corr:
                            highest_corr = abs(corr_matrix.loc[col1, col2])
                            col1_highest = col1
                            col2_highest = col2
                
                response = f"## Correlation Analysis\n\n"
                response += f"The strongest correlation is between **{col1_highest}** and **{col2_highest}** "
                response += f"with a correlation coefficient of **{corr_matrix.loc[col1_highest, col2_highest]:.3f}**.\n\n"
                
                # Create a heatmap
                fig = px.imshow(
                    corr_matrix, 
                    text_auto=True, 
                    color_continuous_scale='RdBu_r',
                    title="Correlation Matrix of Numeric Variables"
                )
                visualization = fig
                
                # Also add a scatter plot for the highest correlation
                fig2 = px.scatter(
                    df,
                    x=col1_highest,
                    y=col2_highest,
                    trendline="ols",
                    title=f"Scatter Plot of {col1_highest} vs {col2_highest}"
                )
                visualization = fig2  # Override with scatter plot
            else:
                response = "The dataset doesn't have enough numeric columns to perform correlation analysis."
    
    # Handle distribution questions
    elif any(word in query_lower for word in ["distribution", "histogram", "spread", "range"]):
        # Find the column being asked about
        target_col = None
        for col in df.columns:
            if col.lower() in query_lower:
                target_col = col
                break
        
        if target_col:
            if target_col in numeric_cols:
                response = f"## Distribution Analysis for {target_col}\n\n"
                response += f"Statistics for **{target_col}**:\n"
                response += f"- Mean: {df[target_col].mean():.2f}\n"
                response += f"- Median: {df[target_col].median():.2f}\n"
                response += f"- Standard Deviation: {df[target_col].std():.2f}\n"
                response += f"- Minimum: {df[target_col].min():.2f}\n"
                response += f"- Maximum: {df[target_col].max():.2f}\n"
                
                # Create a histogram
                fig = px.histogram(
                    df,
                    x=target_col,
                    title=f"Distribution of {target_col}",
                    marginal="box"  # adds a box plot on the margin
                )
                visualization = fig
            elif target_col in categorical_cols:
                value_counts = df[target_col].value_counts()
                
                response = f"## Distribution Analysis for {target_col}\n\n"
                response += f"**{target_col}** is a categorical variable with {len(value_counts)} unique values.\n\n"
                response += "Most common values:\n"
                
                for value, count in value_counts.head(5).items():
                    response += f"- {value}: {count} occurrences ({count/len(df)*100:.1f}%)\n"
                
                # Create a bar chart
                fig = px.bar(
                    value_counts.reset_index(),
                    x="index",
                    y=target_col,
                    title=f"Distribution of {target_col}",
                    labels={"index": target_col, target_col: "Count"}
                )
                visualization = fig
        else:
            response = "I couldn't identify which column you want to analyze. Please specify a column name."
    
    # Handle comparison questions
    elif any(word in query_lower for word in ["compare", "comparison", "difference", "versus", "vs"]):
        # Try to identify two columns to compare
        columns_to_compare = []
        
        for col in df.columns:
            if col.lower() in query_lower:
                columns_to_compare.append(col)
                
        if len(columns_to_compare) >= 2:
            col1 = columns_to_compare[0]
            col2 = columns_to_compare[1]
            
            response = f"## Comparison: {col1} vs {col2}\n\n"
            
            # If both are numeric
            if col1 in numeric_cols and col2 in numeric_cols:
                response += f"Statistical comparison:\n\n"
                response += f"**{col1}**:\n"
                response += f"- Mean: {df[col1].mean():.2f}\n"
                response += f"- Median: {df[col1].median():.2f}\n"
                response += f"- Min: {df[col1].min():.2f}\n"
                response += f"- Max: {df[col1].max():.2f}\n\n"
                
                response += f"**{col2}**:\n"
                response += f"- Mean: {df[col2].mean():.2f}\n"
                response += f"- Median: {df[col2].median():.2f}\n"
                response += f"- Min: {df[col2].min():.2f}\n"
                response += f"- Max: {df[col2].max():.2f}\n\n"
                
                # Calculate correlation
                correlation = df[col1].corr(df[col2])
                response += f"The correlation between {col1} and {col2} is {correlation:.3f}.\n"
                
                # Create a scatter plot
                fig = px.scatter(
                    df,
                    x=col1,
                    y=col2,
                    trendline="ols",
                    title=f"Scatter Plot: {col1} vs {col2}"
                )
                visualization = fig
            
            # If one is categorical and one is numeric
            elif (col1 in categorical_cols and col2 in numeric_cols) or (col1 in numeric_cols and col2 in categorical_cols):
                cat_col = col1 if col1 in categorical_cols else col2
                num_col = col2 if col1 in categorical_cols else col1
                
                response += f"Comparing numeric variable **{num_col}** across different categories of **{cat_col}**.\n\n"
                
                # Calculate statistics by group
                group_stats = df.groupby(cat_col)[num_col].agg(['mean', 'median', 'min', 'max']).reset_index()
                
                # Format for display
                for _, row in group_stats.iterrows():
                    response += f"**{row[cat_col]}**:\n"
                    response += f"- Mean: {row['mean']:.2f}\n"
                    response += f"- Median: {row['median']:.2f}\n"
                    response += f"- Min: {row['min']:.2f}\n"
                    response += f"- Max: {row['max']:.2f}\n\n"
                
                # Create a box plot
                fig = px.box(
                    df,
                    x=cat_col,
                    y=num_col,
                    title=f"Box Plot: {num_col} by {cat_col}"
                )
                visualization = fig
            
            # If both are categorical
            elif col1 in categorical_cols and col2 in categorical_cols:
                response += f"Comparing categorical variables **{col1}** and **{col2}**.\n\n"
                
                # Create a contingency table
                contingency = pd.crosstab(df[col1], df[col2])
                
                response += "Contingency table (showing how many times each combination occurs):\n\n"
                response += contingency.to_markdown() + "\n\n"
                
                # Create a heatmap
                fig = px.imshow(
                    contingency,
                    title=f"Heatmap: {col1} vs {col2}",
                    labels=dict(x=col2, y=col1, color="Count")
                )
                visualization = fig
        else:
            response = "I couldn't identify which columns you want to compare. Please specify both column names."
    
    # Handle trend questions (for time series)
    elif any(word in query_lower for word in ["trend", "time", "over time", "change", "evolution"]):
        # Check if we have datetime columns
        time_col = None
        for col in datetime_cols:
            time_col = col
            break
            
        # If no explicit datetime column, look for anything that might be a date
        if not time_col:
            for col in df.columns:
                if any(date_word in col.lower() for date_word in ["date", "time", "year", "month", "day"]):
                    time_col = col
                    break
        
        if time_col:
            # Find a numeric column to analyze over time
            target_col = None
            for col in numeric_cols:
                if col.lower() in query_lower:
                    target_col = col
                    break
                    
            # If no specific column mentioned, use the first numeric column
            if not target_col and numeric_cols:
                target_col = numeric_cols[0]
                
            if target_col:
                # Ensure time_col is sorted
                if time_col in datetime_cols:
                    df_sorted = df.sort_values(by=time_col)
                else:
                    df_sorted = df.sort_values(by=time_col)
                
                response = f"## Trend Analysis: {target_col} over {time_col}\n\n"
                response += f"Analyzing how **{target_col}** changes over **{time_col}**.\n\n"
                
                # Calculate basic change statistics
                first_val = df_sorted[target_col].iloc[0]
                last_val = df_sorted[target_col].iloc[-1]
                pct_change = ((last_val - first_val) / first_val) * 100 if first_val != 0 else float('inf')
                
                response += f"- Value at start: {first_val:.2f}\n"
                response += f"- Value at end: {last_val:.2f}\n"
                response += f"- Change: {last_val - first_val:.2f}\n"
                response += f"- Percent change: {pct_change:.1f}%\n\n"
                
                # Create a line chart
                fig = px.line(
                    df_sorted,
                    x=time_col,
                    y=target_col,
                    title=f"Trend of {target_col} over {time_col}"
                )
                visualization = fig
            else:
                response = "I couldn't identify which value you want to track over time. Please specify a numeric column name."
        else:
            response = "I couldn't find a suitable time or date column in the data to analyze trends."
    
    # Handle general questions or unrecognized queries
    else:
        response = f"## Data Analysis\n\n"
        response += f"Based on the dataset with {df.shape[0]} rows and {df.shape[1]} columns, here's what I can tell you:\n\n"
        
        # Add basic dataset statistics
        numeric_summary = df[numeric_cols].describe().T[['mean', 'min', 'max']] if numeric_cols else pd.DataFrame()
        
        if not numeric_summary.empty:
            response += "### Numeric Columns Overview\n\n"
            for col in numeric_summary.index:
                response += f"- **{col}**: ranges from {numeric_summary.loc[col, 'min']:.2f} to {numeric_summary.loc[col, 'max']:.2f}, "
                response += f"with an average of {numeric_summary.loc[col, 'mean']:.2f}\n"
        
        if categorical_cols:
            response += "\n### Categorical Columns Overview\n\n"
            for col in categorical_cols[:5]:  # Limit to first 5 categorical columns
                value_counts = df[col].value_counts()
                top_value = value_counts.index[0] if not value_counts.empty else "N/A"
                response += f"- **{col}**: has {df[col].nunique()} unique values, most common is '{top_value}' "
                response += f"({value_counts.iloc[0]} occurrences)\n"
        
        response += "\n### Suggested Analysis\n\n"
        response += "You can ask more specific questions about the data such as:\n"
        response += "- Summarize the dataset\n"
        response += "- What is the average of [column name]?\n"
        response += "- Show the distribution of [column name]\n"
        response += "- Compare [column1] and [column2]\n"
        response += "- Show trends over time\n"
        
        # Create a general visualization depending on the data structure
        if len(numeric_cols) >= 2:
            # Create a correlation heatmap
            corr_matrix = df[numeric_cols].corr()
            fig = px.imshow(
                corr_matrix,
                title="Correlation Matrix of Numeric Variables"
            )
            visualization = fig
        elif numeric_cols:
            # Create a histogram of the first numeric column
            fig = px.histogram(
                df,
                x=numeric_cols[0],
                title=f"Distribution of {numeric_cols[0]}"
            )
            visualization = fig
        elif categorical_cols:
            # Create a bar chart of the first categorical column
            value_counts = df[categorical_cols[0]].value_counts().reset_index()
            fig = px.bar(
                value_counts,
                x="index",
                y=categorical_cols[0],
                title=f"Distribution of {categorical_cols[0]}",
                labels={"index": categorical_cols[0], categorical_cols[0]: "Count"}
            )
            visualization = fig
    
    return response, visualization

def create_data_profile(df):
    """
    Create a profile of the dataset for the AI to understand its structure
    
    Args:
        df (pd.DataFrame): The dataset
        
    Returns:
        str: A text description of the dataset
    """
    # Basic information
    basic_info = f"Dataset with {df.shape[0]} rows and {df.shape[1]} columns."
    
    # Column information
    column_info = []
    for col in df.columns:
        data_type = str(df[col].dtype)
        missing = df[col].isna().sum()
        missing_pct = (missing / len(df)) * 100
        
        if pd.api.types.is_numeric_dtype(df[col]):
            if df[col].nunique() <= 5:
                # Likely a categorical variable stored as numeric
                info = f"'{col}' ({data_type}): Categorical numeric with {df[col].nunique()} unique values. "
                info += f"Missing: {missing} rows ({missing_pct:.1f}%)."
            else:
                # Regular numeric variable
                info = f"'{col}' ({data_type}): Numeric with range [{df[col].min()}, {df[col].max()}]. "
                info += f"Mean: {df[col].mean():.2f}, Median: {df[col].median():.2f}. "
                info += f"Missing: {missing} rows ({missing_pct:.1f}%)."
        elif pd.api.types.is_datetime64_dtype(df[col]):
            # Datetime variable
            info = f"'{col}' ({data_type}): Datetime ranging from {df[col].min()} to {df[col].max()}. "
            info += f"Missing: {missing} rows ({missing_pct:.1f}%)."
        else:
            # Categorical/text variable
            unique_count = df[col].nunique()
            if unique_count <= 10:
                values = ", ".join([f"'{x}'" for x in df[col].dropna().unique()[:5]])
                info = f"'{col}' ({data_type}): Categorical with {unique_count} unique values. "
                info += f"Examples: {values}... "
                info += f"Missing: {missing} rows ({missing_pct:.1f}%)."
            else:
                info = f"'{col}' ({data_type}): Text/categorical with {unique_count} unique values. "
                info += f"Missing: {missing} rows ({missing_pct:.1f}%)."
        
        column_info.append(info)
    
    # Combine all information
    column_details = "\n".join(column_info)
    
    # Potential relationships
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    relationship_info = ""
    
    if len(numeric_cols) >= 2:
        # Compute correlation for top 5 numeric column pairs
        correlations = []
        for i in range(len(numeric_cols)):
            for j in range(i+1, len(numeric_cols)):
                col1 = numeric_cols[i]
                col2 = numeric_cols[j]
                corr = df[col1].corr(df[col2])
                if not np.isnan(corr):
                    correlations.append((col1, col2, abs(corr)))
        
        # Sort by correlation strength and take top 5
        correlations.sort(key=lambda x: x[2], reverse=True)
        top_correlations = correlations[:5]
        
        if top_correlations:
            relationship_info = "Notable relationships:\n"
            for col1, col2, corr in top_correlations:
                relationship_info += f"- '{col1}' and '{col2}' have correlation of {corr:.2f}\n"
    
    # Combine everything
    data_profile = f"{basic_info}\n\nColumn details:\n{column_details}\n\n{relationship_info}"
    
    return data_profile

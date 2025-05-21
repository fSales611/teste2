import pandas as pd
import base64
import io
import json
from plotly.io import to_image, to_html

def get_table_download_link(df, format_type="csv", link_text="Download data"):
    """
    Generate a link to download the dataframe as a file
    
    Args:
        df (pd.DataFrame): Dataframe to download
        format_type (str): Format to download ("csv" or "excel")
        link_text (str): Text to display for the link
        
    Returns:
        str: HTML link for downloading
    """
    if format_type.lower() == "csv":
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="data_export.csv">{link_text}</a>'
    elif format_type.lower() == "excel":
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
            writer.save()
        b64 = base64.b64encode(buffer.getvalue()).decode()
        href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="data_export.xlsx">{link_text}</a>'
    else:
        href = "Unsupported format"
    
    return href

def get_chart_download_link(fig, format_type="png", link_text="Download chart"):
    """
    Generate a link to download a Plotly chart
    
    Args:
        fig (plotly.graph_objects.Figure): Plotly figure to download
        format_type (str): Format to download ("png" or "html")
        link_text (str): Text to display for the link
        
    Returns:
        str: HTML link for downloading
    """
    if format_type.lower() == "png":
        img_bytes = to_image(fig, format="png")
        b64 = base64.b64encode(img_bytes).decode()
        href = f'<a href="data:image/png;base64,{b64}" download="chart.png">{link_text}</a>'
    elif format_type.lower() == "html":
        html_str = to_html(fig, include_plotlyjs="cdn")
        b64 = base64.b64encode(html_str.encode()).decode()
        href = f'<a href="data:text/html;base64,{b64}" download="chart.html">{link_text}</a>'
    else:
        href = "Unsupported format"
    
    return href

def format_large_number(num):
    """
    Format large numbers with suffixes like K, M, B
    
    Args:
        num (float): Number to format
        
    Returns:
        str: Formatted number string
    """
    suffixes = ['', 'K', 'M', 'B', 'T']
    magnitude = 0
    
    while abs(num) >= 1000 and magnitude < len(suffixes)-1:
        magnitude += 1
        num /= 1000.0
    
    return f"{num:.1f}{suffixes[magnitude]}"

def is_valid_json(json_str):
    """
    Check if a string is valid JSON
    
    Args:
        json_str (str): String to check
        
    Returns:
        bool: True if valid JSON, False otherwise
    """
    try:
        json.loads(json_str)
        return True
    except:
        return False
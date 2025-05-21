import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np

def get_visualization_options(df):
    """
    Get appropriate visualization options based on dataframe structure
    
    Args:
        df (pd.DataFrame): Input dataframe
        
    Returns:
        dict: Dictionary of visualization options
    """
    # Get column types
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(exclude=[np.number]).columns.tolist()
    datetime_cols = df.select_dtypes(include=['datetime']).columns.tolist()
    
    # Define visualization options
    visualization_options = {}
    
    # Only add visualization types that make sense for the data
    
    # Scatter Plot (needs at least 2 numeric columns)
    if len(numeric_cols) >= 2:
        visualization_options['scatter_plot'] = {
            'x': numeric_cols,
            'y': numeric_cols,
            'color': ['None'] + categorical_cols + numeric_cols,
            'size': ['None'] + numeric_cols,
            'hover_data': {'type': 'multiselect', 'options': df.columns.tolist()},
            'trendline': {'type': 'checkbox', 'default': False}
        }
    
    # Line Chart (needs at least 1 numeric column and preferably a datetime)
    if len(numeric_cols) >= 1:
        x_options = datetime_cols + numeric_cols + categorical_cols
        visualization_options['line_chart'] = {
            'x': x_options,
            'y': numeric_cols,
            'color': ['None'] + categorical_cols,
            'line_group': ['None'] + categorical_cols,
            'hover_data': {'type': 'multiselect', 'options': df.columns.tolist()}
        }
    
    # Bar Chart (works with various combinations)
    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        visualization_options['bar_chart'] = {
            'x': categorical_cols + numeric_cols,
            'y': numeric_cols + categorical_cols,
            'color': ['None'] + categorical_cols,
            'barmode': ['group', 'stack', 'relative'],
            'hover_data': {'type': 'multiselect', 'options': df.columns.tolist()}
        }
    
    # Histogram (needs at least 1 numeric column)
    if len(numeric_cols) >= 1:
        visualization_options['histogram'] = {
            'x': numeric_cols + categorical_cols,
            'color': ['None'] + categorical_cols,
            'nbins': {'type': 'slider', 'min': 5, 'max': 100, 'default': 20},
            'histnorm': ['', 'percent', 'probability', 'density', 'probability density']
        }
    
    # Box Plot (needs at least 1 numeric column)
    if len(numeric_cols) >= 1:
        visualization_options['box_plot'] = {
            'x': ['None'] + categorical_cols,
            'y': numeric_cols,
            'color': ['None'] + categorical_cols,
            'notched': {'type': 'checkbox', 'default': False},
            'hover_data': {'type': 'multiselect', 'options': df.columns.tolist()}
        }
    
    # Pie Chart (needs at least 1 categorical and 1 numeric column)
    if len(categorical_cols) >= 1 and len(numeric_cols) >= 1:
        visualization_options['pie_chart'] = {
            'names': categorical_cols,
            'values': numeric_cols,
            'hole': {'type': 'slider', 'min': 0, 'max': 0.8, 'default': 0},
            'hover_data': {'type': 'multiselect', 'options': df.columns.tolist()}
        }
    
    # Heatmap (needs at least 2 categorical/datetime columns and 1 numeric column)
    if (len(categorical_cols) + len(datetime_cols) >= 2) and len(numeric_cols) >= 1:
        visualization_options['heatmap'] = {
            'x': categorical_cols + datetime_cols,
            'y': categorical_cols + datetime_cols,
            'z': numeric_cols,
            'colorscale': ['Viridis', 'Plasma', 'Inferno', 'Magma', 'Cividis', 'Blues', 'Reds', 'Greens']
        }
    
    # Bubble Chart (needs at least 3 numeric columns)
    if len(numeric_cols) >= 3:
        visualization_options['bubble_chart'] = {
            'x': numeric_cols,
            'y': numeric_cols,
            'size': numeric_cols,
            'color': ['None'] + categorical_cols + numeric_cols,
            'hover_data': {'type': 'multiselect', 'options': df.columns.tolist()}
        }
    
    # Scatter Matrix (needs at least 3 numeric columns)
    if len(numeric_cols) >= 3:
        visualization_options['scatter_matrix'] = {
            'dimensions': {'type': 'multiselect', 'options': numeric_cols},
            'color': ['None'] + categorical_cols,
            'hover_data': {'type': 'multiselect', 'options': df.columns.tolist()}
        }
    
    return visualization_options

def create_visualization(df, chart_type, params, title=None, width=800, height=500):
    """
    Create a visualization based on chart type and parameters
    
    Args:
        df (pd.DataFrame): Input dataframe
        chart_type (str): Type of chart to create
        params (dict): Parameters for the chart
        title (str): Chart title
        width (int): Chart width
        height (int): Chart height
        
    Returns:
        plotly.graph_objects.Figure: Plotly figure object
    """
    fig = None
    
    # Scatter Plot
    if chart_type == 'scatter_plot':
        fig = px.scatter(
            df,
            x=params.get('x'),
            y=params.get('y'),
            color=None if params.get('color') == 'None' else params.get('color'),
            size=None if params.get('size') == 'None' else params.get('size'),
            hover_data=params.get('hover_data', []),
            title=title,
            width=width,
            height=height
        )
        
        if params.get('trendline'):
            fig.update_traces(mode='markers')
            # Add trendline
            x = df[params.get('x')].values
            y = df[params.get('y')].values
            
            # Filter out NaN values
            mask = ~np.isnan(x) & ~np.isnan(y)
            x = x[mask]
            y = y[mask]
            
            if len(x) > 1 and len(y) > 1:
                z = np.polyfit(x, y, 1)
                p = np.poly1d(z)
                
                fig.add_trace(
                    go.Scatter(
                        x=x,
                        y=p(x),
                        mode='lines',
                        name='Trendline',
                        line=dict(color='red', dash='dash')
                    )
                )
    
    # Line Chart
    elif chart_type == 'line_chart':
        fig = px.line(
            df,
            x=params.get('x'),
            y=params.get('y'),
            color=None if params.get('color') == 'None' else params.get('color'),
            line_group=None if params.get('line_group') == 'None' else params.get('line_group'),
            hover_data=params.get('hover_data', []),
            title=title,
            width=width,
            height=height
        )
    
    # Bar Chart
    elif chart_type == 'bar_chart':
        fig = px.bar(
            df,
            x=params.get('x'),
            y=params.get('y'),
            color=None if params.get('color') == 'None' else params.get('color'),
            barmode=params.get('barmode', 'group'),
            hover_data=params.get('hover_data', []),
            title=title,
            width=width,
            height=height
        )
    
    # Histogram
    elif chart_type == 'histogram':
        fig = px.histogram(
            df,
            x=params.get('x'),
            color=None if params.get('color') == 'None' else params.get('color'),
            nbins=params.get('nbins', 20),
            histnorm=params.get('histnorm', ''),
            title=title,
            width=width,
            height=height
        )
    
    # Box Plot
    elif chart_type == 'box_plot':
        fig = px.box(
            df,
            x=None if params.get('x') == 'None' else params.get('x'),
            y=params.get('y'),
            color=None if params.get('color') == 'None' else params.get('color'),
            notched=params.get('notched', False),
            hover_data=params.get('hover_data', []),
            title=title,
            width=width,
            height=height
        )
    
    # Pie Chart
    elif chart_type == 'pie_chart':
        fig = px.pie(
            df,
            names=params.get('names'),
            values=params.get('values'),
            hole=params.get('hole', 0),
            hover_data=params.get('hover_data', []),
            title=title,
            width=width,
            height=height
        )
    
    # Heatmap
    elif chart_type == 'heatmap':
        # Pivot data for heatmap
        heatmap_data = df.pivot_table(
            values=params.get('z'),
            index=params.get('y'),
            columns=params.get('x'),
            aggfunc='mean'
        )
        
        fig = px.imshow(
            heatmap_data,
            color_continuous_scale=params.get('colorscale', 'Viridis'),
            title=title,
            width=width,
            height=height
        )
    
    # Bubble Chart
    elif chart_type == 'bubble_chart':
        fig = px.scatter(
            df,
            x=params.get('x'),
            y=params.get('y'),
            size=params.get('size'),
            color=None if params.get('color') == 'None' else params.get('color'),
            hover_data=params.get('hover_data', []),
            title=title,
            width=width,
            height=height
        )
    
    # Scatter Matrix
    elif chart_type == 'scatter_matrix':
        dimensions = params.get('dimensions', [])
        if len(dimensions) > 1:
            fig = px.scatter_matrix(
                df,
                dimensions=dimensions,
                color=None if params.get('color') == 'None' else params.get('color'),
                hover_data=params.get('hover_data', []),
                title=title,
                width=width,
                height=height
            )
    
    # Add layout improvements
    if fig:
        fig.update_layout(
            title={
                'text': title,
                'y': 0.95,
                'x': 0.5,
                'xanchor': 'center',
                'yanchor': 'top'
            },
            margin=dict(l=50, r=50, t=80, b=50),
            template='plotly_white'
        )
    
    return fig
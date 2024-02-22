import plotly.express as px
import pandas as pd
import random

def get_chart_data():
    # Generate random chart data for demonstration
    data = {'x': range(10), 'y': [random.randint(1, 10) for _ in range(10)]}
    df = pd.DataFrame(data)
    
    # Create a scatter plot
    fig = px.scatter(df, x='x', y='y', title='Dynamic Chart')

    # Convert the Plotly figure to JSON for rendering in the template
    chart_data = fig.to_json()
    print(chart_data)

    return chart_data

import plotly.express as px
import pandas as pd

def generate_issued_chart(df):
    # Generate Issued ATOM chart
    fig = px.line(df, x='Month', y=['Inflow Issued ATOM (new)', 'Issued ATOM (old)'],
                labels={'value': 'Value', 'variable': 'Category'},
                title='Issued ATOM',
                template='plotly_white')

    # Convert the Plotly figure to JSON for rendering in the template
    chart_data = fig.to_json()
    return chart_data


def generate_cumm_issued_chart(df):
    # Generate Cumulatively Issued ATOM
    fig = px.line(df, x='Month', y=['Total Cumulatively Issued ATOM (new)', 'Cumulatively Issued ATOM (old)'],
                labels={'value': 'Value', 'variable': 'Category'},
                title='Cumulatively Issued ATOM',
                template='plotly_white',
                line_dash_sequence=['solid', 'dot'])

    # Convert the Plotly figure to JSON for rendering in the template
    chart_data = fig.to_json()
    return chart_data
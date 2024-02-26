import streamlit as st
import pandas as pd
import plotly.express as px
from app.charts.chart_data import generate_issued_chart, generate_cumm_issued_chart

def calculate_outflow_security_subsidy(month, security_subsidy_termination, current_security_subsidy, security_subsidy_decay, distrbution_module_pct_to_community_pool):
    if month > security_subsidy_termination:
        return 0
    else:
        return current_security_subsidy * pow((1 - security_subsidy_decay / 100), month) * (1 - distrbution_module_pct_to_community_pool / 100)

def calculate_outflow_distribution_community_pool(month, security_subsidy_termination, current_security_subsidy, security_subsidy_decay, distrbution_module_pct_to_community_pool):
    if month > security_subsidy_termination:
        return 0
    else:
        return current_security_subsidy * pow((1 - security_subsidy_decay / 100), month) * (distrbution_module_pct_to_community_pool / 100)

def calculate_inflow_issued_atom_new(month, time_until_steady_state_issuance, issuance, issuance_reduction_amount, steady_state_issuance):
    if month >= time_until_steady_state_issuance:
        return steady_state_issuance
    else:
        return ((issuance - 200000) * pow((1 - issuance_reduction_amount / 100), month) + 200000)

def calculate_total_treasury_pool_balance(outflow_distribution_community_pool, outflow_security_subsidy, inflow_issued_atom_new):
    total_outflow = outflow_distribution_community_pool + outflow_security_subsidy
    total_treasury_pool_balance = inflow_issued_atom_new - total_outflow
    return total_treasury_pool_balance

def calculate_total_atom_supply(total_atom_supply, inflow_issued_atom_new):
    total_atom_supply += inflow_issued_atom_new
    return total_atom_supply

def calculate_old_regime(total_atom_supply_old, issued_atom_old, cumulatively_issued_atom_old, current_security_subsidy_rate):
    total_atom_supply_old += issued_atom_old
    issued_atom_old = total_atom_supply_old * current_security_subsidy_rate / 100 / 12
    cumulatively_issued_atom_old += issued_atom_old
    return total_atom_supply_old, issued_atom_old, cumulatively_issued_atom_old

def populate_table(timeline_length, current_total_atom_supply, current_community_pool_balance, current_security_subsidy_rate, current_security_subsidy, security_subsidy_decay, security_subsidy_termination, issuance, issuance_reduction_amount, steady_state_issuance, time_until_steady_state_issuance, distrbution_module_pct_to_community_pool):
    # Initialize lists to store data
    data = []
    columns = ["Month", "Outflow Security Subsidy", "Outflow Distribution to Community Pool",
               "Inflow Issued ATOM (new)", "Total Treasury Pool Balance",
               "Current Community Pool Balance", "Total Cumulatively Issued ATOM (new)",
               "Total ATOM Supply", "Total ATOM Supply (old)", "Issued ATOM (old)",
               "Cumulatively Issued ATOM (old)"]

    # Call the functions
    total_treasury_pool_balance = 0
    current_total_comm_pool = current_community_pool_balance
    total_cumulatively_issued_atom_new = 0
    total_atom_supply = current_total_atom_supply
    total_atom_supply_old = current_total_atom_supply
    issued_atom_old = 0
    cumulatively_issued_atom_old = issued_atom_old

    for month in range(timeline_length + 1):
        outflow_security_subsidy = calculate_outflow_security_subsidy(month, security_subsidy_termination,
                                                                      current_security_subsidy, security_subsidy_decay,
                                                                      distrbution_module_pct_to_community_pool)
        outflow_distribution_community_pool = calculate_outflow_distribution_community_pool(month,
                                                                                              security_subsidy_termination,
                                                                                              current_security_subsidy,
                                                                                              security_subsidy_decay,
                                                                                              distrbution_module_pct_to_community_pool)
        inflow_issued_atom_new = calculate_inflow_issued_atom_new(month, time_until_steady_state_issuance, issuance,
                                                                  issuance_reduction_amount, steady_state_issuance)
        total_treasury_pool_balance += calculate_total_treasury_pool_balance(
            outflow_distribution_community_pool, outflow_security_subsidy, inflow_issued_atom_new)
        current_total_comm_pool += outflow_distribution_community_pool
        total_cumulatively_issued_atom_new += inflow_issued_atom_new
        total_atom_supply = calculate_total_atom_supply(total_atom_supply, inflow_issued_atom_new)
        total_atom_supply_old, issued_atom_old, cumulatively_issued_atom_old = calculate_old_regime(
            total_atom_supply_old, issued_atom_old, cumulatively_issued_atom_old, current_security_subsidy_rate)

        # Append data for the current month to the list
        data.append([month, outflow_security_subsidy, outflow_distribution_community_pool, inflow_issued_atom_new,
                     total_treasury_pool_balance, current_total_comm_pool, total_cumulatively_issued_atom_new,
                     total_atom_supply, total_atom_supply_old, issued_atom_old, cumulatively_issued_atom_old])

    # Create a DataFrame from the lists
    df = pd.DataFrame(data, columns=columns)

    return df


def main():
    st.title("ATOM Issuance Model")
    
    current_total_atom_supply = st.slider("Current Total Atom Supply", min_value=0, max_value=1000000000, value=300000000)
    current_community_pool_balance = st.slider("Current Community Pool Balance", min_value=0, max_value=10000000, value=1140000)
    current_security_subsidy_rate = st.slider("Current Security Subsidy Rate", min_value=0.0, max_value=20.0, value=13.5)  # Adjust the range as needed
    current_security_subsidy = (current_total_atom_supply * (current_security_subsidy_rate / 100)) / 12
    security_subsidy_decay = st.slider("Security Subsidy Decay", min_value=0.0, max_value=100.0, value=10.0)  # Adjust the range as needed
    security_subsidy_termination = st.slider("Security Subsidy Termination", min_value=0, max_value=120, value=36)
    issuance = st.slider("Issuance", min_value=0, max_value=100000000, value=10000000)
    issuance_reduction_epoch_rate = st.slider("Issuance Reduction Epoch Rate", min_value=0, max_value=10, value=1)
    issuance_reduction_amount = st.slider("Issuance Reduction Amount", min_value=0.0, max_value=20.0, value=12.0)  # Adjust the range as needed
    steady_state_issuance = st.slider("Steady-State Issuance", min_value=0, max_value=1000000, value=300000)
    time_until_steady_state_issuance = st.slider("Time Until Steady State Issuance", min_value=0, max_value=100, value=36)
    distrbution_module_pct_to_community_pool = st.slider("Distribution Module % to Community Pool", min_value=0.0, max_value=20.0, value=5.0)
    timeline_length = st.slider("Timeline Length", min_value=1, max_value=100, value=60)

    # Call the function to populate the table
    df = populate_table(timeline_length, current_total_atom_supply, current_community_pool_balance,
                        current_security_subsidy_rate, current_security_subsidy, security_subsidy_decay,
                        security_subsidy_termination, issuance, issuance_reduction_amount, steady_state_issuance,
                        time_until_steady_state_issuance, distrbution_module_pct_to_community_pool)

    # Display the DataFrame
    st.dataframe(df)


    # Display the line chart using st.line_chart
    st.plotly_chart(px.line(df, x='Month', y=['Inflow Issued ATOM (new)', 'Issued ATOM (old)'],
                labels={'value': 'Value', 'variable': 'Category'},
                title='Issued ATOM',
                template='plotly_white'))
    
    st.plotly_chart(px.line(df, x='Month', y=['Total Cumulatively Issued ATOM (new)', 'Cumulatively Issued ATOM (old)'],
                labels={'value': 'Value', 'variable': 'Category'},
                title='Cumulatively Issued ATOM',
                template='plotly_white',
                line_dash_sequence=['solid', 'dot']))



if __name__ == "__main__":
    main()

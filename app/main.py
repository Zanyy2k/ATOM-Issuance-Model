from flask import Flask, render_template, request
from charts.chart_data import generate_issued_chart, generate_cumm_issued_chart
import pandas as pd

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', data=None)


# Outflow - Security Subsidy
def calculate_outflow_security_subsidy(month, security_subsidy_termination, current_security_subsidy, security_subsidy_decay, distrbution_module_pct_to_community_pool):
    if month > security_subsidy_termination : 
        return 0
    else: 
        return(current_security_subsidy * pow((1-security_subsidy_decay/100),month)*(1-distrbution_module_pct_to_community_pool/100))
    

# Outflow - Distribution to Community Pool
def calculate_outflow_distribution_community_pool(month, security_subsidy_termination, current_security_subsidy, security_subsidy_decay, distrbution_module_pct_to_community_pool):
    if month > security_subsidy_termination : 
        return 0
    else: 
        return(current_security_subsidy * pow((1-security_subsidy_decay/100),month)*(distrbution_module_pct_to_community_pool/100))


# Inflow - Issued ATOM (new)
def calculate_inflow_issued_atom_new(month, time_until_steady_state_issuance, issuance, issuance_reduction_amount, steady_state_issuance):
    if month >= time_until_steady_state_issuance : 
        return steady_state_issuance
    else: 
        return((issuance-200000) * pow((1-issuance_reduction_amount/100),month)+200000)


# Total pool Balance
def calculate_total_treasury_pool_balance(outflow_distribution_community_pool, outflow_security_subsidy, inflow_issued_atom_new):
    total_outflow = outflow_distribution_community_pool + outflow_security_subsidy
    total_treasury_pool_balance = inflow_issued_atom_new - total_outflow
    return total_treasury_pool_balance


# Total ATOM supply
def calculate_total_atom_supply(total_atom_supply,inflow_issued_atom_new ):
    total_atom_supply += inflow_issued_atom_new
    return total_atom_supply


# Old_Regime 
def calculate_old_regime(total_atom_supply_old, issued_atom_old, cumulatively_issued_atom_old, current_security_subsidy_rate):
    total_atom_supply_old += issued_atom_old
    issued_atom_old = total_atom_supply_old*current_security_subsidy_rate/100/12
    cumulatively_issued_atom_old += issued_atom_old
    return (total_atom_supply_old, issued_atom_old, cumulatively_issued_atom_old)


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
        outflow_security_subsidy = calculate_outflow_security_subsidy(month, security_subsidy_termination, current_security_subsidy, security_subsidy_decay, distrbution_module_pct_to_community_pool)
        outflow_distribution_community_pool = calculate_outflow_distribution_community_pool(month, security_subsidy_termination, current_security_subsidy, security_subsidy_decay, distrbution_module_pct_to_community_pool)
        inflow_issued_atom_new = calculate_inflow_issued_atom_new(month, time_until_steady_state_issuance, issuance, issuance_reduction_amount, steady_state_issuance)
        total_treasury_pool_balance += calculate_total_treasury_pool_balance(outflow_distribution_community_pool, outflow_security_subsidy, inflow_issued_atom_new)
        current_total_comm_pool += outflow_distribution_community_pool
        total_cumulatively_issued_atom_new += inflow_issued_atom_new
        total_atom_supply = calculate_total_atom_supply(total_atom_supply,inflow_issued_atom_new)
        total_atom_supply_old,issued_atom_old, cumulatively_issued_atom_old = calculate_old_regime(total_atom_supply_old, issued_atom_old, cumulatively_issued_atom_old, current_security_subsidy_rate)

        # print(month, outflow_security_subsidy, outflow_distribution_community_pool, inflow_issued_atom_new, total_treasury_pool_balance, current_total_comm_pool, total_cumulatively_issued_atom_new, total_atom_supply, total_atom_supply_old,issued_atom_old, cumulatively_issued_atom_old)

        # Append data for the current month to the list
        data.append([month, outflow_security_subsidy, outflow_distribution_community_pool, inflow_issued_atom_new,
                    total_treasury_pool_balance, current_total_comm_pool, total_cumulatively_issued_atom_new,
                    total_atom_supply, total_atom_supply_old, issued_atom_old, cumulatively_issued_atom_old])

    # Create a DataFrame from the lists
    df = pd.DataFrame(data, columns=columns)

    # Transpose the DataFrame
    df_transposed = df.transpose()

    # return the transposed DataFrame
    return(df, df_transposed)


@app.route('/populate', methods=['POST'])
def populate():
    current_total_atom_supply = float(request.form['current_total_atom_supply'])
    current_community_pool_balance = float(request.form['current_community_pool_balance'])
    current_security_subsidy_rate = float(request.form['current_security_subsidy_rate'])
    current_security_subsidy = (current_total_atom_supply * (current_security_subsidy_rate/100))/12
    security_subsidy_decay = float(request.form['security_subsidy_decay'])
    security_subsidy_termination = int(request.form['security_subsidy_termination'])
    issuance = float(request.form['issuance'])
    issuance_reduction_epoch_rate = int(request.form['issuance_reduction_epoch_rate'])
    issuance_reduction_amount = float(request.form['issuance_reduction_amount'])
    steady_state_issuance = float(request.form['steady_state_issuance'])
    time_until_steady_state_issuance = int(request.form['time_until_steady_state_issuance'])
    distrbution_module_pct_to_community_pool = float(request.form['distrbution_module_pct_to_community_pool'])
    timeline_length = int(request.form['timeline_length'])


    setting_inputs = {
            'Current Total Atom Supply': current_total_atom_supply,
            'Current Community Pool Balance': current_community_pool_balance,
            'Current Security Subsidy Rate': current_security_subsidy_rate,
            'Current Security Subsidy': current_security_subsidy,
            'Security Subsidy Decay': security_subsidy_decay,
            'Security Subsidy Termination': security_subsidy_termination,
            'Issuance': issuance,
            'Issuance Reduction Epoch Rate': issuance_reduction_epoch_rate,
            'Issuance Reduction Amount': issuance_reduction_amount,
            'Steady-State Issuance': steady_state_issuance,
            'Time Until Steady State Issuance': time_until_steady_state_issuance,
            'Distribution Module % to Community Pool': distrbution_module_pct_to_community_pool,
            'Timeline Length': timeline_length
        }

    df, data_table = populate_table(timeline_length, current_total_atom_supply, current_community_pool_balance, current_security_subsidy_rate, current_security_subsidy, security_subsidy_decay, security_subsidy_termination, issuance, issuance_reduction_amount, steady_state_issuance, time_until_steady_state_issuance, distrbution_module_pct_to_community_pool)

    chart1 = generate_issued_chart(df)

    chart2 = generate_cumm_issued_chart(df)

    return render_template('index.html', setting_inputs = setting_inputs, data_table= data_table.to_html(), chart1=chart1, chart2=chart2 )



if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request
from charts.chart_data import get_chart_data

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html', data=None)


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

    return render_template('index.html', setting_inputs = setting_inputs)
    

if __name__ == '__main__':
    app.run(debug=True)

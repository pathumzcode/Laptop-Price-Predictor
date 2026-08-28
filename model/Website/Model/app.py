from flask import Flask, render_template, request
import hashlib
import os
import pickle
from pathlib import Path
import pandas as pd

app = Flask(__name__)
EUR_TO_USD = 1.17
ALLOWED_VALUES = {
    'ram': {'2', '4', '6', '8', '12', '16', '24', '32', '64'},
    'weight': {'0.92', '1.5', '2.0', '2.5', '3.0', '4.0'},
    'company': {'acer', 'apple', 'asus', 'dell', 'hp', 'lenovo', 'msi', 'other', 'toshiba'},
    'typename': {'2in1convertible', 'gaming', 'netbook', 'notebook', 'ultrabook', 'workstation'},
    'opsys': {'linux', 'mac', 'other', 'windows'},
    'cpuname': {'amd', 'intelcorei3', 'intelcorei5', 'intelcorei7', 'other'},
    'gpuname': {'amd', 'intel', 'nvidia'},
}

def prediction(lst, ram, weight, company, typename, opsys, cpu, gpu, touchscreen, ips):
    filename = Path(__file__).with_name('predictor_normalized.pickle')
    expected_hash = os.environ.get('MODEL_SHA256')
    if expected_hash:
        actual_hash = hashlib.sha256(filename.read_bytes()).hexdigest()
        if actual_hash.lower() != expected_hash.lower():
            raise RuntimeError('The model integrity check failed.')

    with open(filename, 'rb') as file:
        model = pickle.load(file)

    form_values = {
        'Ram_GB': float(ram),
        'Weight_KG': float(weight),
        'Company': {
            'acer': 'Acer', 'apple': 'Apple', 'asus': 'Asus',
            'dell': 'Dell', 'hp': 'HP', 'lenovo': 'Lenovo',
            'msi': 'MSI', 'toshiba': 'Toshiba', 'other': 'Other',
        }[company],
        'TypeName': {
            '2in1convertible': '2 in 1 Convertible', 'gaming': 'Gaming',
            'netbook': 'Netbook', 'notebook': 'Notebook',
            'ultrabook': 'Ultrabook', 'workstation': 'Workstation',
        }[typename],
        'OpSys': {'windows': 'Windows', 'mac': 'Mac', 'linux': 'Linux', 'other': 'Other'}[opsys],
        'CPU': {
            'intelcorei3': 'Intel Core i3', 'intelcorei5': 'Intel Core i5',
            'intelcorei7': 'Intel Core i7', 'amd': 'AMD', 'other': 'Other',
        }[cpu],
        'GPU': {'intel': 'Intel', 'amd': 'AMD', 'nvidia': 'Nvidia'}[gpu],
        'Touchscreen': 'Yes' if touchscreen else 'No',
        'IPS': 'Yes' if ips else 'No',
    }
    return model.predict(pd.DataFrame([form_values]))[0]

@app.route('/', methods =['POST', 'GET'])
def index():
    pred_value = 0
    error = None
    if request.method == 'POST':
        values = {field: request.form.get(field) for field in ALLOWED_VALUES}
        invalid_fields = [
            field for field, allowed in ALLOWED_VALUES.items()
            if values[field] not in allowed
        ]

        if invalid_fields:
            error = 'Please select a valid value for every laptop field.'
        else:
            touchscreen = bool(request.form.getlist('touchscreen'))
            ips = bool(request.form.getlist('ips'))
            try:
                predicted_eur = float(prediction(
                    [], values['ram'], values['weight'], values['company'],
                    values['typename'], values['opsys'], values['cpuname'],
                    values['gpuname'], touchscreen, ips
                ))
                pred_value = round(predicted_eur * EUR_TO_USD, 2)
            except (OSError, RuntimeError, TypeError, ValueError):
                app.logger.exception('Laptop price prediction failed')
                error = 'Unable to calculate the estimate right now.'

    return render_template('index.html', pred_value=pred_value, error=error)

if __name__ == '__main__':
    app.run(debug=False)
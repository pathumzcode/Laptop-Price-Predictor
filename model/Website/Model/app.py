from flask import Flask, render_template, request
import hashlib
import os
import pickle
from pathlib import Path
import numpy as np

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
    filename = Path(__file__).with_name('predictor.pickle')
    expected_hash = os.environ.get('MODEL_SHA256')
    if expected_hash:
        actual_hash = hashlib.sha256(filename.read_bytes()).hexdigest()
        if actual_hash.lower() != expected_hash.lower():
            raise RuntimeError('The model integrity check failed.')

    with open(filename, 'rb') as file:
        model = pickle.load(file)

    features = list(model.feature_names_in_)
    values = np.zeros((1, len(features)))

    def set_feature(prefix, value):
        value = str(value).lower().replace(' ', '')
        for position, feature in enumerate(features):
            normalized = feature.lower().replace(' ', '')
            if normalized.startswith(prefix.lower()) and value in normalized:
                values[0, position] = 1
                return

    set_feature('Company_', company)
    set_feature('TypeName_', typename)
    set_feature('OpSys_', 'Other' if opsys == 'other' else opsys)
    set_feature('Cpu_', cpu.replace('intelcore', 'Intel Core '))
    set_feature('Gpu_', gpu)
    set_feature('Ram_', f'{ram}GB')
    set_feature('Weight_', f'{weight}kg')

    if touchscreen:
        set_feature('Touchscreen_', 'Yes')
    if ips:
        set_feature('IPS_', 'Yes')

    return model.predict(values)[0]

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
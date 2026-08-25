from flask import Flask, render_template, request
import pickle
from pathlib import Path
import numpy as np

app = Flask(__name__)
EUR_TO_USD = 1.17

def prediction(lst, ram, weight, company, typename, opsys, cpu, gpu, touchscreen, ips):
    filename = Path(__file__).with_name('predictor.pickle')
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
    if request.method == 'POST':
        # Handle POST request here
        ram = request.form.get('ram')
        weight = request.form.get('weight')
        company = request.form.get('company')
        typename = request.form.get('typename')
        opsys = request.form.get('opsys')
        cpu = request.form.get('cpuname')
        gpu = request.form.get('gpuname')
        touchscreen = request.form.getlist('touchscreen')
        ips = request.form.getlist('ips')

        print(f"RAM: {ram}, Weight: {weight}, Company: {company}, Type Name: {typename}, OS: {opsys}, CPU: {cpu}, GPU: {gpu}, Touchscreen: {touchscreen}, IPS: {ips}")  

        feature_list = []
        feature_list.append(int(ram))
        feature_list.append(float(weight))
        feature_list.append(len(touchscreen))
        feature_list.append(len(ips))

        company_list = ['acer', 'apple', 'asus', 'dell', 'hp', 'lenovo', 'msi', 'other', 'toshiba']
        typename_list = ['2in1convertible', 'gaming', 'netbook', 'notebook', 'ultrabook', 'workstation']
        opsys_list = ['linux', 'mac','others', 'windows']
        cpu_list = ['amd', 'intelcorei3', 'intelcorei5', 'intelcorei7','other']
        gpu_list = ['amd','intel','nvidia']

        def traverse(list, value):
            for item in list:
                if item == value:
                    feature_list.append(1)
                else:
                    feature_list.append(0)
        
        traverse(company_list, company)
        traverse(typename_list, typename)
        traverse(opsys_list, opsys)
        traverse(cpu_list, cpu)
        traverse(gpu_list, gpu)

        print(f"Feature List: {feature_list}")  # Print the feature list for debugging

        predicted_eur = float(prediction(
            feature_list, ram, weight, company, typename, opsys, cpu, gpu,
            touchscreen, ips
        ))
        pred_value = round(predicted_eur * EUR_TO_USD, 2)
        print(f"Predicted Value (EUR): {predicted_eur:.2f}")
        print(f"Predicted Value (USD): {pred_value:.2f}")

    return render_template('index.html', pred_value=pred_value)

if __name__ == '__main__':
    app.run(debug=True)
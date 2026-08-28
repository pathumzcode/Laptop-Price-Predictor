# Laptop Price Predictor

A machine learning web application that estimates a laptop's price from its hardware and software configuration.

The project includes a Jupyter notebook for exploring and training the model and a Flask application for making predictions through a browser. The current saved model is a `RandomForestRegressor` trained on the laptop price dataset and reports approximately 76.4% accuracy in the notebook.

## Features

- Predicts an estimated laptop price from a simple web form.
- Uses RAM, weight, manufacturer, laptop type, operating system, CPU, GPU, touchscreen support, and IPS display support.
- Displays the estimate in US dollars.
- Includes the training dataset, model-building notebook, and serialized model.

## Project Structure

```text
model/
|-- data set/
|   `-- laptop_price.csv
|-- model building.ipynb
|-- predictor.pickle
|-- train_normalized_model.py
|-- normalized_model_training.ipynb
`-- Website/
	`-- Model/
		|-- app.py
		|-- predictor_normalized.pickle
		|-- templates/
		`-- static/
```

## Requirements

- Python 3.9 or newer
- Flask
- NumPy
- scikit-learn
- Jupyter Notebook (only needed to rerun the training notebook)

## Run the Web App

From the repository root on Windows PowerShell:

```powershell
cd model\Website\Model
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r ..\..\..\requirements.txt
python app.py
```

Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in a browser.

On Windows Command Prompt, activate the environment with:

```bat
.venv\Scripts\activate
```

The application loads `predictor_normalized.pickle` from the same directory as `app.py`. Keep the model file in that location when moving or deploying the web app.

For a production deployment, set `MODEL_SHA256` to the SHA-256 hash of the trusted model file and use a production WSGI server instead of Flask's built-in server:

```powershell
$env:MODEL_SHA256 = (Get-FileHash .\predictor_normalized.pickle -Algorithm SHA256).Hash
python -m pip install waitress
waitress-serve --listen=127.0.0.1:5000 app:app
```

Never enable Flask debug mode on a public server.

## Train or Inspect the Model

The notebook is located at [model/model building.ipynb](model/model%20building.ipynb). To open it with Jupyter:

```powershell
cd model
python -m pip install jupyter pandas matplotlib seaborn scikit-learn
jupyter notebook "model building.ipynb"
```

The original notebook reads `data set/laptop_price.csv`, prepares categorical features, compares regression models, and saves the original `predictor.pickle`. The normalized training script and notebook convert raw dataset values to the same categories used by the web form, normalize RAM and weight, evaluate the model, and save `predictor_normalized.pickle` directly into `model/Website/Model/`.

## Input Categories

The web form supports the following values:

- RAM: 2, 4, 6, 8, 12, 16, 24, 32, or 64 GB
- Weight: under 1 kg, 1-1.9 kg, 2-2.4 kg, 2.5-2.9 kg, 3-3.9 kg, or 4 kg and above
- Companies: Acer, Apple, Asus, Dell, HP, Lenovo, MSI, Toshiba, or Other
- Types: 2 in 1 Convertible, Gaming, Net Book, Note Book, Ultra Book, or Workstation
- Operating systems: Windows, Mac, Linux, or Other
- CPUs: Intel Core i3, Intel Core i5, Intel Core i7, AMD, or Other
- GPUs: Intel, AMD, or Nvidia
- Optional display features: touchscreen and IPS

## Limitations

- The prediction is an estimate, not a guaranteed market or resale price.
- The model is trained on the included dataset and may not reflect current prices.
- The application uses a fixed EUR-to-USD conversion rate of `1.17`; update `EUR_TO_USD` in `model/Website/Model/app.py` when a different rate is required.
- The serialized model was created with scikit-learn. Use a compatible scikit-learn version when loading or retraining it.

## License

See [LICENSE](LICENSE) for the project license.
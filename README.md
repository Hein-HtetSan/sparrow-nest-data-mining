# Sparrow Nest Data Mining

## Contributors

- Hein Htet San

## Supervisor

- Prof. Hsu Myat Mo

## Institution

- University of Computer Studies, Yangon

## Introduction

This project analyzes 657 Eurasian Tree Sparrow building records from China. It combines descriptive statistics, association rules, clustering, classification and regression, then tests the selected predictive models on unseen spatial groups.

## Live Applications

| Application | Link |
|---|---|
| Presentation website | [Open SparrowScope](https://sites-project.heinhtetsan33455.workers.dev) |
| Streamlit model lab | [Test the models](https://sparrow-nest-data-mining.streamlit.app) |
| Project book | [PDF](documentation/Eurasian_Tree_Sparrow_Data_Mining_Project.pdf) · [Word](documentation/Eurasian_Tree_Sparrow_Data_Mining_Project.docx) |
| Hosted presentation | [Download PPTX](https://sites-project.heinhtetsan33455.workers.dev/downloads/Sparrow_Cluster_Profiles.pptx) |
| GitHub repository | [View source](https://github.com/Hein-HtetSan/sparrow-nest-data-mining) |

## Project Overview

One dataset row represents one building. Seven building and environmental variables are used:

- Building height and width
- Altitude and average noise
- Temperature, precipitation and wind

The classification target is `Lower` for 1–4 nests and `Higher` for 5 or more nests. Regression predicts the exact `NestCount`.

In the simulator, the displayed record number is only the building's position in the interface. `Building#` and `ID` identify the observed building and survey site; neither identifier is used as a model feature.

## Notebook Workflow

1. [`notebook/main.ipynb`](notebook/main.ipynb) loads, validates and splits the data by spatial `ID` into 501 training and 156 holdout records.
2. [`notebook/association.ipynb`](notebook/association.ipynb) mines Apriori and FP-Growth rules from training-data tertiles.
3. [`notebook/clustering.ipynb`](notebook/clustering.ipynb) compares K-means and hierarchical clustering and exports five K-means profiles.
4. [`notebook/classification.ipynb`](notebook/classification.ipynb) compares classifiers with group-aware cross-validation.
5. [`notebook/regression.ipynb`](notebook/regression.ipynb) compares regressors with mean and median baselines.
6. [`notebook/final_eval.ipynb`](notebook/final_eval.ipynb) fits the selected Decision Trees and evaluates them once on the spatial holdout.

## Cluster Characteristic Profiles

| Cluster | Characteristic profile | Records | Mean nests |
|---:|---|---:|---:|
| 0 | Moderate-altitude, noisy sites | 125 | 5.31 |
| 1 | Warm, wet, low-altitude sites | 76 | 13.58 |
| 2 | High-altitude, dry, wide buildings | 156 | 3.78 |
| 3 | Highest-altitude, cool, low-wind sites | 93 | 2.86 |
| 4 | Very tall buildings | 51 | 5.65 |

`NestCount` was excluded from K-means and compared only after cluster formation. The selected K-means solution has a silhouette score of 0.267, so the profiles overlap and should be interpreted descriptively.

## Model Evaluation

| Task | Selected model | Cross-validation criterion | Spatial holdout result |
|---|---|---|---|
| Classification | Decision Tree | Highest mean F1: 0.630 | ROC-AUC: 0.505 |
| Regression | Decision Tree | Lowest mean MAE: 2.824 | MAE: 4.095 |

The holdout regression tree performed worse than the mean baseline MAE of 3.190. The deployed tools demonstrate the notebook pipeline; they are not operational ecological predictors.

## Project Structure

```text
sparrow-nest-data-mining/
├── api/                         Local simulation API
├── dataset/                     Source data and notes
├── models/                      Saved Decision Tree models and metadata
├── notebook/                    Six analysis notebooks
├── outputs/                     Tables, plots and predictions
├── presentation/                Editable cluster-profile PowerPoint
├── sparrow-scope/               Presentation website
├── streamlit_app.py             Streamlit model lab
├── requirements.txt             Python dependencies
└── README.md
```

## PowerPoint

Download the editable presentation: [`presentation/Sparrow_Cluster_Profiles.pptx`](presentation/Sparrow_Cluster_Profiles.pptx).

## Local Setup

### 1. Clone the repository

```bash
git clone https://github.com/Hein-HtetSan/sparrow-nest-data-mining.git
cd sparrow-nest-data-mining
```

### 2. Create and activate a Python environment

macOS or Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows PowerShell:

```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
```

### 3. Install the Python packages

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Run the Streamlit model lab

```bash
streamlit run streamlit_app.py
```

Open `http://localhost:8501`.

### 5. Run the local simulation API

```bash
python api/main.py
```

The API runs at `http://localhost:8000` and supports the simulation inside the presentation website.

### 6. Run the presentation website

Node.js 22.13 or newer is required.

```bash
cd sparrow-scope
npm install
npm run dev
```

Open the local URL printed by Vite.

## Deployment

### Streamlit Community Cloud

1. Push the repository to GitHub.
2. Sign in to [Streamlit Community Cloud](https://share.streamlit.io/).
3. Select **Create app** and choose this repository.
4. Set the branch to `main` and the entry point to `streamlit_app.py`.
5. Deploy the app.

Deployed URL: [https://sparrow-nest-data-mining.streamlit.app](https://sparrow-nest-data-mining.streamlit.app)

### Cloudflare Workers

```bash
cd sparrow-scope
npm install
npm run build
npx wrangler login
npx wrangler deploy --config dist/server/wrangler.json
```

Deployed URL: [https://sites-project.heinhtetsan33455.workers.dev](https://sites-project.heinhtetsan33455.workers.dev)

## Main Outputs

- Cluster profile tables and PCA visualization
- Apriori and FP-Growth association rules
- Group-aware classification and regression comparisons
- Final holdout predictions and evaluation figures
- Saved models used by the Streamlit app and local simulation API

## Limitations

- The records come from China only.
- Nest count does not measure breeding success.
- Cluster boundaries overlap.
- Predictive performance did not transfer reliably to held-out spatial groups.

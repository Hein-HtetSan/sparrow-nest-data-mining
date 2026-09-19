# Eurasian Tree Sparrow Data Mining

This project analyzes 657 Eurasian Tree Sparrow building records from China. It combines descriptive statistics, association-rule mining, clustering, classification and regression. The final evaluation uses a spatial holdout split by survey ID.

## Live applications

- Presentation website: [SparrowScope](https://sites-project.heinhtetsan33455.workers.dev)
- Streamlit model lab: deployment in progress

## PowerPoint

The editable cluster-profile presentation is available at [`presentation/Sparrow_Cluster_Profiles.pptx`](presentation/Sparrow_Cluster_Profiles.pptx).

## Project workflow

1. `notebook/main.ipynb` audits the data, defines the seven features and creates the group-aware train/holdout split.
2. `notebook/association.ipynb` mines Apriori and FP-Growth rules from training-tertile categories.
3. `notebook/clustering.ipynb` compares K-means and hierarchical clustering and exports the five K-means profiles.
4. `notebook/classification.ipynb` compares five classification approaches using grouped cross-validation.
5. `notebook/regression.ipynb` compares learned regressors with mean and median baselines.
6. `notebook/final_eval.ipynb` evaluates the selected Decision Trees on 156 held-out spatial records.

## Cluster profiles

| Cluster | Characteristic profile | Training records | Mean nests |
|---:|---|---:|---:|
| 0 | Moderate-altitude, noisy sites | 125 | 5.31 |
| 1 | Warm, wet, low-altitude sites | 76 | 13.58 |
| 2 | High-altitude, dry, wide buildings | 156 | 3.78 |
| 3 | Highest-altitude, cool, low-wind sites | 93 | 2.86 |
| 4 | Very tall buildings | 51 | 5.65 |

NestCount was excluded from K-means and compared only after cluster formation. The selected K-means solution has a silhouette score of 0.267, so the groups overlap and should be interpreted as descriptive profiles.

## Run the Streamlit app locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Run the presentation website locally

```bash
cd sparrow-scope
npm install
npm run dev
```

The model lab is educational. On the spatial holdout, classification ROC-AUC was 0.505 and the regression Decision Tree performed worse than the mean baseline.

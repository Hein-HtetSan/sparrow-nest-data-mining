from pathlib import Path

import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.dummy import DummyRegressor
from sklearn.ensemble import RandomForestClassifier, RandomForestRegressor
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.naive_bayes import GaussianNB
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier, DecisionTreeRegressor


ROOT = Path(__file__).resolve().parent
FEATURES = ["BuildingHeight", "BuildingWidth", "Altitude", "AveNoise", "temp", "prec", "win"]
LABELS = dict(zip(FEATURES, ["Building height", "Building width", "Altitude", "Average noise", "Temperature", "Precipitation", "Wind"]))
NAMES = {0: "Moderate-altitude, noisy sites", 1: "Warm, wet, low-altitude sites", 2: "High-altitude, dry, wide buildings", 3: "Highest-altitude, cool, low-wind sites", 4: "Very tall buildings"}
DESCRIPTIONS = {
    0: "Lower buildings, moderate altitude, highest average noise and above-average precipitation.",
    1: "Lowest altitude, warmest and wettest conditions, with relatively tall and narrow buildings.",
    2: "Lowest and widest buildings, high altitude, driest conditions and slightly higher wind.",
    3: "Highest altitude, coolest temperature and lowest wind, with relatively low buildings.",
    4: "Tallest buildings by a large margin, with otherwise moderate environmental conditions.",
}


@st.cache_resource
def load_project():
    data = pd.read_csv(ROOT / "outputs/sparrow_model_data.csv", dtype={"ID": str})
    train = data.loc[data["Split"] == "train"].copy()
    scaler = StandardScaler().fit(train[FEATURES])
    clusters = KMeans(n_clusters=5, random_state=42, n_init=20).fit(scaler.transform(train[FEATURES]))
    y_class = (train["NestCount"] > 4).astype(int)
    classifiers = {
        "Decision Tree": DecisionTreeClassifier(max_depth=3, min_samples_leaf=10, random_state=42).fit(train[FEATURES], y_class),
        "Random Forest": RandomForestClassifier(n_estimators=200, max_depth=5, min_samples_leaf=5, random_state=42).fit(train[FEATURES], y_class),
        "Logistic Regression": make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(train[FEATURES], y_class),
        "Gaussian Naive Bayes": GaussianNB().fit(train[FEATURES], y_class),
    }
    regressors = {
        "Decision Tree": DecisionTreeRegressor(max_depth=3, min_samples_leaf=10, random_state=42).fit(train[FEATURES], train["NestCount"]),
        "Random Forest": RandomForestRegressor(n_estimators=200, max_depth=5, min_samples_leaf=5, random_state=42).fit(train[FEATURES], train["NestCount"]),
        "Linear Regression": make_pipeline(StandardScaler(), LinearRegression()).fit(train[FEATURES], train["NestCount"]),
        "Mean baseline": DummyRegressor(strategy="mean").fit(train[FEATURES], train["NestCount"]),
        "Median baseline": DummyRegressor(strategy="median").fit(train[FEATURES], train["NestCount"]),
    }
    return data, train, scaler, clusters, classifiers, regressors


def input_record(data, train, key):
    source = st.radio("Input source", ["Observed dataset record", "Custom values"], horizontal=True, key=f"source-{key}")
    if source == "Observed dataset record":
        position = st.selectbox(
            "Observed building record",
            range(len(data)),
            format_func=lambda index: f"Record {index + 1} · {data.iloc[index]['Building#']} · Site ID {data.iloc[index]['ID']} · {data.iloc[index]['Split']}",
            key=f"record-{key}",
        )
        sample = data.iloc[position]
        st.caption("The record number is only its position in this app. Each record is one observed building; Building# and Site ID are identifiers and are not model features.")
    else:
        sample = data.iloc[0]
        st.caption("Custom values create a hypothetical building, so no observed NestCount is available for comparison.")
    ranges = train[FEATURES].agg(["min", "median", "max"])
    values = {}
    columns = st.columns(4)
    for index, feature in enumerate(FEATURES):
        default = float(sample[feature]) if source == "Observed dataset record" else float(ranges.at["median", feature])
        values[feature] = columns[index % 4].number_input(LABELS[feature], min_value=float(ranges.at["min", feature]), max_value=float(ranges.at["max", feature]), value=default, disabled=source == "Observed dataset record", key=f"{key}-{feature}")
    return pd.DataFrame([values], columns=FEATURES), sample, source


data, train, scaler, clusters, classifiers, regressors = load_project()
profiles = pd.read_csv(ROOT / "outputs/cluster_profiles.csv").set_index("Cluster")
nest_profiles = pd.read_csv(ROOT / "outputs/cluster_nest_profiles.csv").set_index("Cluster")
rules = pd.read_csv(ROOT / "outputs/positive_nest_rules.csv")
classification_scores = pd.read_csv(ROOT / "outputs/classification_cv_results.csv").set_index("Model")
regression_scores = pd.read_csv(ROOT / "outputs/regression_cv_results.csv").set_index("Model")

st.set_page_config(page_title="Sparrow Data Mining Simulator", page_icon="🐦", layout="wide")
st.title("Sparrow Data Mining Simulator")
st.caption("Explore association rules, cluster profiles, and predictions from the submitted notebook outputs.")

association_tab, clustering_tab, prediction_tab, dataset_tab = st.tabs(["Association Rules", "Clustering", "Prediction Testing", "Dataset Explorer"])

with association_tab:
    st.subheader("Choose a condition to discover its nest-count associations")
    feature = st.selectbox("Building or environmental feature", FEATURES, format_func=LABELS.get)
    level = st.segmented_control("Category", ["Low", "Medium", "High"], default="Low")
    condition = f"{feature}={level}"
    matches = rules[rules["antecedents"].str.contains(condition, regex=False)].sort_values("lift", ascending=False)
    st.caption(f"Rules whose starting conditions include **{LABELS[feature]} = {level}**.")
    st.metric("Matching rules", len(matches))
    if matches.empty:
        st.info("No shortlisted positive rule contains this condition. Try another category.")
    else:
        strongest = matches.iloc[0]
        st.subheader(f"Strongest result: {strongest.antecedents} → {strongest.consequents.replace('NestCountGroup=', '')}")
        a, b, c = st.columns(3)
        a.metric("Support", f"{strongest.support:.1%}", help="Share of all training records containing the full rule")
        b.metric("Confidence", f"{strongest.confidence:.1%}", help="Share of matching conditions with this nest-count outcome")
        c.metric("Lift", f"{strongest.lift:.2f}×", help="Strength compared with the outcome occurring by chance")
        st.progress(min(float(strongest.confidence), 1.0), text=f"{strongest.confidence:.1%} confidence")
        st.info("These conditions occur together in the training data. Association does not prove causation.")
        with st.expander("All matching rules and technical values"):
            st.dataframe(matches[["antecedents", "consequents", "support", "confidence", "lift"]], hide_index=True, width="stretch")

with clustering_tab:
    st.subheader("Explore the five building and environmental profiles")
    selected = st.selectbox("Cluster profile", list(NAMES), format_func=lambda cluster: f"Cluster {cluster}: {NAMES[cluster]}")
    row = profiles.loc[selected]
    outcome = nest_profiles.loc[selected]
    st.write(DESCRIPTIONS[selected])
    a, b, c, d = st.columns(4)
    a.metric("Training records", f"{int(row.Records)} ({row.Records / len(train):.1%})")
    b.metric("Mean nests", f"{outcome.MeanNestCount:.2f}")
    c.metric("Median nests", f"{outcome.MedianNestCount:.0f}")
    d.metric("Higher-count share", f"{outcome.HigherCountFraction:.1%}")
    comparison = pd.DataFrame({"Cluster mean": row[FEATURES].astype(float), "Training mean": train[FEATURES].mean()})
    comparison.index = [LABELS[name] for name in comparison.index]
    st.bar_chart(comparison)
    with st.expander("Exact cluster means"):
        st.dataframe(comparison.style.format("{:.2f}"), width="stretch")
    st.info("NestCount was excluded from clustering and added afterward for interpretation. Silhouette 0.267 means the profiles overlap.")

with prediction_tab:
    st.subheader("Test different models on the same record")
    task = st.segmented_control("Prediction task", ["Classification", "Regression"], default="Classification")
    available = classifiers if task == "Classification" else regressors
    model_name = st.selectbox("Model", list(available), key="prediction-model")
    row, sample, source = input_record(data, train, "prediction")
    if st.button("Run selected model", type="primary", use_container_width=True):
        model = available[model_name]
        prediction = model.predict(row)[0]
        actual = int(sample.NestCount) if source == "Observed dataset record" else None
        if task == "Classification":
            probability = float(model.predict_proba(row)[0, 1]) if hasattr(model, "predict_proba") else None
            a, b, c = st.columns(3)
            a.metric("Predicted class", "Higher (5+)" if int(prediction) else "Lower (1–4)")
            b.metric("Higher probability", f"{probability:.1%}" if probability is not None else "Not available")
            c.metric("Actual class", ("Higher (5+)" if actual > 4 else "Lower (1–4)") if actual is not None else "N/A")
            score = classification_scores.loc[model_name]
            st.caption(f"Notebook cross-validation: F1 {score.f1_mean:.3f} · Accuracy {score.accuracy_mean:.3f} · ROC-AUC {score.roc_auc_mean:.3f}")
        else:
            estimate = max(0.0, float(prediction))
            a, b, c = st.columns(3)
            a.metric("Estimated nests", f"{estimate:.2f}")
            b.metric("Actual nests", actual if actual is not None else "N/A")
            c.metric("Absolute error", f"{abs(estimate - actual):.2f}" if actual is not None else "N/A")
            score = regression_scores.loc[model_name]
            st.caption(f"Notebook cross-validation: MAE {score.MAE_mean:.3f} · RMSE {score.RMSE_mean:.3f} · R² {score.R2_mean:.3f}")
        cluster = int(clusters.predict(scaler.transform(row))[0])
        st.success(f"This record also belongs to Cluster {cluster}: {NAMES[cluster]}.")
        st.warning("Final spatial holdout performance was weak. Use this simulator to inspect model behavior, not for operational prediction.")
    with st.expander("Compare notebook model scores"):
        columns = ["accuracy_mean", "precision_mean", "recall_mean", "f1_mean", "roc_auc_mean"] if task == "Classification" else ["MAE_mean", "RMSE_mean", "R2_mean"]
        scores = classification_scores if task == "Classification" else regression_scores
        st.dataframe(scores[columns].style.format("{:.3f}"), width="stretch")

with dataset_tab:
    st.subheader("Browse the dataset used by the notebooks")
    split = st.segmented_control("Records", ["All", "Train", "Holdout"], default="All")
    shown = data if split == "All" else data[data["Split"].str.lower() == split.lower()]
    a, b, c, d = st.columns(4)
    a.metric("Records", len(shown))
    b.metric("Spatial IDs", shown["ID"].nunique())
    c.metric("Median nests", f"{shown.NestCount.median():.0f}")
    d.metric("Maximum nests", int(shown.NestCount.max()))
    st.dataframe(shown, hide_index=True, width="stretch", height=430)

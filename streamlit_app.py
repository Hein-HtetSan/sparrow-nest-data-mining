from pathlib import Path

import joblib
import pandas as pd
import streamlit as st
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


ROOT = Path(__file__).resolve().parent
FEATURES = ["BuildingHeight", "BuildingWidth", "Altitude", "AveNoise", "temp", "prec", "win"]
NAMES = {
    0: "Moderate-altitude, noisy sites",
    1: "Warm, wet, low-altitude sites",
    2: "High-altitude, dry, wide buildings",
    3: "Highest-altitude, cool, low-wind sites",
    4: "Very tall buildings",
}
DESCRIPTIONS = {
    0: "Lower buildings, moderate altitude, highest average noise and above-average precipitation.",
    1: "Lowest altitude, warmest and wettest conditions, with relatively tall and narrow buildings.",
    2: "Lowest and widest buildings, high altitude, driest conditions and slightly higher wind.",
    3: "Highest altitude, coolest temperature and lowest wind, with relatively low buildings.",
    4: "Tallest buildings by a large margin, with otherwise moderate environmental conditions.",
}


@st.cache_resource
def load_models():
    data = pd.read_csv(ROOT / "outputs/sparrow_model_data.csv", dtype={"ID": str})
    train = data.loc[data["Split"] == "train"].copy()
    scaler = StandardScaler().fit(train[FEATURES])
    clusters = KMeans(n_clusters=5, random_state=42, n_init=20).fit(scaler.transform(train[FEATURES]))
    classifier = joblib.load(ROOT / "models/classification_tree.joblib")
    regressor = joblib.load(ROOT / "models/regression_tree.joblib")
    return data, train, scaler, clusters, classifier, regressor


data, train, scaler, clusters, classifier, regressor = load_models()
profiles = pd.read_csv(ROOT / "outputs/cluster_profiles.csv").set_index("Cluster")
nest_profiles = pd.read_csv(ROOT / "outputs/cluster_nest_profiles.csv").set_index("Cluster")
ranges = train[FEATURES].agg(["min", "median", "max"])

st.set_page_config(page_title="Sparrow Cluster Lab", page_icon="🐦", layout="wide")
st.title("Sparrow Cluster and Prediction Lab")
st.caption("Uses the notebook's 501 training records, K-means k=5, and saved Decision Trees.")

profile_tab, test_tab = st.tabs(["Cluster profiles", "Test one record"])

with profile_tab:
    st.subheader("Cluster-characteristic profiles")
    selected = st.selectbox(
        "Cluster",
        list(NAMES),
        format_func=lambda cluster: f"Cluster {cluster}: {NAMES[cluster]}",
    )
    row = profiles.loc[selected]
    outcome = nest_profiles.loc[selected]
    a, b, c, d = st.columns(4)
    a.metric("Training records", f"{int(row.Records)} ({row.Records / len(train):.1%})")
    b.metric("Mean nests", f"{outcome.MeanNestCount:.2f}")
    c.metric("Median nests", f"{outcome.MedianNestCount:.0f}")
    d.metric("Higher-count share", f"{outcome.HigherCountFraction:.1%}")
    st.write(DESCRIPTIONS[selected])
    comparison = pd.DataFrame({
        "Cluster mean": row[FEATURES].astype(float),
        "Training mean": train[FEATURES].mean(),
    })
    st.dataframe(comparison.style.format("{:.2f}"), width="stretch")
    relative = ((row[FEATURES].astype(float) - train[FEATURES].mean()) / train[FEATURES].std()).rename("Standard deviations from training mean")
    st.bar_chart(relative)
    st.info("NestCount was excluded from clustering. The nest statistics above were calculated afterward for interpretation. Silhouette 0.267 indicates overlapping clusters.")

with test_tab:
    mode = st.radio("Input source", ["Dataset row", "Edited values"], horizontal=True)
    source = st.number_input("Dataset row", 1, len(data), 1) - 1
    sample = data.iloc[int(source)]
    values = {}
    columns = st.columns(4)
    for index, feature in enumerate(FEATURES):
        default = float(sample[feature]) if mode == "Dataset row" else float(ranges.at["median", feature])
        values[feature] = columns[index % 4].number_input(
            feature,
            min_value=float(ranges.at["min", feature]),
            max_value=float(ranges.at["max", feature]),
            value=default,
        )

    if st.button("Run notebook models", type="primary"):
        row = pd.DataFrame([values], columns=FEATURES)
        cluster = int(clusters.predict(scaler.transform(row))[0])
        predicted_class = int(classifier.predict(row)[0])
        probability = float(classifier.predict_proba(row)[0, 1])
        count = max(0.0, float(regressor.predict(row)[0]))

        st.subheader(f"Cluster {cluster}: {NAMES[cluster]}")
        st.write(DESCRIPTIONS[cluster])
        a, b, c, d = st.columns(4)
        a.metric("Estimated nests", f"{count:.2f}")
        b.metric("Predicted class", "Higher (5+)" if predicted_class else "Lower (1–4)")
        c.metric("Model probability", f"{probability:.1%}")
        d.metric("Actual nests", int(sample.NestCount) if mode == "Dataset row" else "N/A")
        st.warning("The final holdout ROC-AUC was 0.505, and regression MAE was worse than the mean baseline. Treat these results as an educational demonstration.")

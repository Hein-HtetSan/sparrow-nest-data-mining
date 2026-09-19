from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, sys

import joblib
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ["BuildingHeight", "BuildingWidth", "Altitude", "AveNoise", "temp", "prec", "win"]
classification = joblib.load(ROOT / "models/classification_tree.joblib")
regression = joblib.load(ROOT / "models/regression_tree.joblib")
data = pd.read_csv(ROOT / "outputs/sparrow_model_data.csv")
train = data.query("Split == 'train'")
scaled = StandardScaler().fit_transform(train[FEATURES])
clusters = KMeans(n_clusters=5, random_state=42, n_init=20).fit(scaled)
scaler = StandardScaler().fit(train[FEATURES])
rules = pd.read_csv(ROOT / "outputs/positive_nest_rules.csv").head(20)
cluster_profiles = pd.read_csv(ROOT / "outputs/cluster_profiles.csv").set_index("Cluster")
CLUSTER_NAMES = {
    0: "Moderate-altitude, noisy sites",
    1: "Warm, wet, low-altitude sites",
    2: "High-altitude, dry, wide buildings",
    3: "Highest-altitude, cool, low-wind sites",
    4: "Very tall buildings",
}
CLUSTER_CHARACTERISTICS = {
    0: "Lower buildings, moderate altitude, highest average noise and above-average precipitation",
    1: "Lowest altitude, warmest and wettest conditions, with relatively tall and narrow buildings",
    2: "Lowest and widest buildings, high altitude, driest conditions and slightly higher wind",
    3: "Highest altitude, coolest temperature and lowest wind, with relatively low buildings",
    4: "Tallest buildings by a large margin, with otherwise moderate environmental conditions",
}

class Handler(BaseHTTPRequestHandler):
    def do_OPTIONS(self): self.send_response(204); self.cors(); self.end_headers()
    def do_POST(self):
        try:
            size = int(self.headers.get("Content-Length", 0))
            body = json.loads(self.rfile.read(size))
            if body.get("mode") == "simulation":
                position = body.get("position")
                sample = data.sample(1) if position is None else data.iloc[[max(0, min(int(position), len(data) - 1))]]
                row = pd.DataFrame([body.get("values", sample.iloc[0][FEATURES].to_dict())], columns=FEATURES).astype(float)
                actual = None if body.get("values") is not None else int(sample.iloc[0].NestCount)
                cls = int(classification.predict(row)[0]); count = max(0, float(regression.predict(row)[0]))
                labels = {}
                for f in FEATURES:
                    q1, q2 = train[f].quantile([1/3, 2/3]); labels[f] = "Low" if row.iloc[0][f] <= q1 else "Medium" if row.iloc[0][f] <= q2 else "High"
                matched = [r for _, r in rules.iterrows() if all(labels.get(item.split('=')[0]) == item.split('=')[1] for item in str(r.antecedents).split(' AND '))]
                cluster = int(clusters.predict(scaler.transform(row))[0])
                result = {"position": int(sample.index[0]), "totalRecords": len(data), "building": str(sample.iloc[0]["Building#"]), "id": str(sample.iloc[0].ID), "split": str(sample.iloc[0].Split), "record": {f: round(float(row.iloc[0][f]), 2) for f in FEATURES}, "actualNestCount": actual, "edited": body.get("values") is not None, "bestModels": {"classifier": "Decision Tree", "class": "Higher (5+)" if cls else "Lower (1–4)", "probability": round(float(classification.predict_proba(row)[0][1]), 3), "regressor": "Decision Tree", "estimatedCount": round(count, 2)}, "cluster": cluster, "clusterProfile": {"name": CLUSTER_NAMES[cluster], "characteristics": CLUSTER_CHARACTERISTICS[cluster], "records": int(cluster_profiles.at[cluster, "Records"])}, "associationRules": [{"rule": f"{r.antecedents} → {r.consequents}", "confidence": round(float(r.confidence), 3), "lift": round(float(r.lift), 3)} for r in matched[:3]]}
                self.reply(200, result); return
            row = pd.DataFrame([{f: float(body[f]) for f in FEATURES}])
            mode = body.get("mode", "prediction")
            if mode == "prediction":
                cls = int(classification.predict(row)[0]); count = max(0, float(regression.predict(row)[0]))
                result = {"class": "Higher (5+)" if cls else "Lower (1–4)", "count": round(count, 2)}
                if hasattr(classification, "predict_proba"): result["probability"] = round(float(classification.predict_proba(row)[0][1]), 3)
            elif mode == "clustering":
                result = {"cluster": int(clusters.predict(scaler.transform(row))[0]), "note": "K-means k=5 using all seven standardized features"}
            else:
                labels = {}
                for f in FEATURES:
                    q1, q2 = train[f].quantile([1/3, 2/3]); labels[f] = "Low" if row.at[0,f] <= q1 else "Medium" if row.at[0,f] <= q2 else "High"
                matched = [r for _, r in rules.iterrows() if all(labels.get(item.split('=')[0]) == item.split('=')[1] for item in str(r.antecedents).split(' AND '))]
                result = {"matches": [{"rule": f"{r.antecedents} → {r.consequents}", "confidence": round(float(r.confidence), 3), "lift": round(float(r.lift), 3)} for r in matched[:3]]}
            self.reply(200, result)
        except Exception as exc: self.reply(400, {"error": str(exc)})
    def cors(self): self.send_header("Access-Control-Allow-Origin", "http://localhost:3000"); self.send_header("Access-Control-Allow-Headers", "Content-Type")
    def reply(self, status, data):
        payload=json.dumps(data).encode(); self.send_response(status); self.cors(); self.send_header("Content-Type","application/json"); self.send_header("Content-Length",str(len(payload))); self.end_headers(); self.wfile.write(payload)

if __name__ == "__main__":
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"SparrowScope model API: http://localhost:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()

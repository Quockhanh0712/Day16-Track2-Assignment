import os
import time
import json
import numpy as np
import pandas as pd
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score, accuracy_score, f1_score, precision_score, recall_score

def run_benchmark():
    print("=== STARTING LIGHTGBM BENCHMARK ===")
    
    # 1. Load data
    print("1. Loading Credit Card Fraud Detection dataset...")
    start_time = time.time()
    csv_path = "creditcard.csv"
    if not os.path.exists(csv_path):
        # Look for the file in current directory or prompt
        raise FileNotFoundError(f"Could not find {csv_path}. Please make sure you downloaded and unzipped the creditcardfraud dataset in this directory.")
        
    df = pd.read_csv(csv_path)
    load_time = time.time() - start_time
    print(f"   Loaded {len(df)} rows in {load_time:.4f} seconds.")
    
    # 2. Preprocess data
    X = df.drop(columns=["Class"])
    y = df["Class"]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # 3. Train LightGBM Model
    print("2. Training LightGBM model...")
    train_data = lgb.Dataset(X_train, label=y_train)
    test_data = lgb.Dataset(X_test, label=y_test, reference=train_data)
    
    params = {
        "objective": "binary",
        "metric": "auc",
        "boosting_type": "gbdt",
        "n_jobs": -1,  # Use all available CPU cores
        "random_state": 42,
        "verbose": -1
    }
    
    start_train = time.time()
    bst = lgb.train(
        params,
        train_data,
        num_boost_round=100,
        valid_sets=[test_data],
        callbacks=[lgb.log_evaluation(period=10)]
    )
    train_time = time.time() - start_train
    print(f"   Model training completed in {train_time:.4f} seconds.")
    
    # 4. Evaluate Model
    print("3. Evaluating model...")
    y_pred_prob = bst.predict(X_test)
    y_pred = (y_pred_prob > 0.5).astype(int)
    
    auc = roc_auc_score(y_test, y_pred_prob)
    accuracy = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred)
    recall = recall_score(y_test, y_pred)
    
    print(f"   AUC-ROC:   {auc:.6f}")
    print(f"   Accuracy:  {accuracy:.6f}")
    print(f"   F1-Score:  {f1:.6f}")
    print(f"   Precision: {precision:.6f}")
    print(f"   Recall:    {recall:.6f}")
    
    # 5. Benchmark Inference Latency & Throughput
    print("4. Benchmarking inference latency & throughput...")
    
    # Inference latency (1 row) - average over 1000 iterations
    single_row = X_test.iloc[[0]]
    latencies = []
    for _ in range(1000):
        t0 = time.time()
        bst.predict(single_row)
        latencies.append(time.time() - t0)
    avg_latency_ms = np.mean(latencies) * 1000
    
    # Inference throughput (1000 rows) - average over 100 iterations
    batch_rows = X_test.iloc[:1000]
    throughput_times = []
    for _ in range(100):
        t0 = time.time()
        bst.predict(batch_rows)
        throughput_times.append(time.time() - t0)
    avg_throughput_time = np.mean(throughput_times)
    throughput_per_sec = 1000 / avg_throughput_time if avg_throughput_time > 0 else 0
    
    print(f"   Inference latency (1 row): {avg_latency_ms:.4f} ms")
    print(f"   Inference throughput (1000 rows): {throughput_per_sec:.2f} rows/sec")
    
    # 6. Save results to JSON
    results = {
        "load_time_seconds": round(load_time, 4),
        "training_time_seconds": round(train_time, 4),
        "auc_roc": round(auc, 6),
        "accuracy": round(accuracy, 6),
        "f1_score": round(f1, 6),
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "inference_latency_1_row_ms": round(avg_latency_ms, 4),
        "inference_throughput_1000_rows_per_sec": round(throughput_per_sec, 2)
    }
    
    output_path = "benchmark_result.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=4)
    print(f"\nResults successfully saved to {output_path}!")

if __name__ == "__main__":
    run_benchmark()

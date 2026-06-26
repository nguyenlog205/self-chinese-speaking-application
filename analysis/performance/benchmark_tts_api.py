#!/usr/bin/env python3
"""
Benchmark TTS API endpoint /tts/synthesize/
Measures latency, throughput, generates statistics and saves results.

Output:
    - results/tts_latency.csv
    - results/tts_speaker_latency.csv
    - results/tts_bitrate_latency.csv
    - results/tts_report.txt (detailed summary)
    - results/plots/tts_latency_comparison.png
"""

import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime

# ==================== CONFIG ====================
API_BASE = "http://localhost:8000"
N_REQUESTS = 10

TEST_CASES = [
    {"name": "short_1char", "text": "你"},
    {"name": "short_2char", "text": "你好"},
    {"name": "medium_5char", "text": "你好世界"},
    {"name": "medium_10char", "text": "今天是星期一"},
    {"name": "long_20char", "text": "学好中文需要每天练习"},
    {"name": "long_50char", "text": "学习中文需要不断练习，每天坚持才会进步"},
]

SPEAKERS = ["Vivian", "Serena", "Uncle_Fu", "Dylan", "Eric"]
BITRATES = ["128k", "192k", "320k"]

# ==================== SETUP ====================
Path("results").mkdir(exist_ok=True)
Path("results/plots").mkdir(exist_ok=True)

# ==================== FUNCTIONS ====================

def benchmark_tts_single(text, speaker="Vivian", bitrate="192k"):
    start = time.perf_counter()
    try:
        response = requests.get(
            f"{API_BASE}/tts/synthesize/",
            params={"text": text, "speaker": speaker, "bitrate": bitrate},
            timeout=60
        )
        latency = (time.perf_counter() - start) * 1000
        return {
            "latency_ms": latency,
            "status": response.status_code,
            "size_bytes": len(response.content) if response.status_code == 200 else 0,
            "success": response.status_code == 200
        }
    except Exception as e:
        return {
            "latency_ms": 0,
            "status": 500,
            "size_bytes": 0,
            "success": False,
            "error": str(e)
        }


def run_benchmark(text, speaker="Vivian", bitrate="192k", n=10):
    rows = []
    print(f"  Testing: '{text[:20]}...' | {speaker} | {bitrate}")
    for i in range(n):
        result = benchmark_tts_single(text, speaker, bitrate)
        rows.append({
            "text": text,
            "text_len": len(text),
            "speaker": speaker,
            "bitrate": bitrate,
            "latency_ms": result["latency_ms"],
            "success": result["success"],
            "size_bytes": result["size_bytes"]
        })
        print(f"    [{i+1}/{n}] {result['latency_ms']:.0f}ms")
    return pd.DataFrame(rows)


def write_report(filename, content):
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(content)


# ==================== MAIN ====================

def main():
    print("=" * 70)
    print("TTS API BENCHMARK")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)

    # Check backend
    try:
        requests.get(f"{API_BASE}/docs", timeout=3)
    except:
        print("ERROR: Backend not running. Please start with: python -m src.main")
        return

    all_dfs = []

    # 1. By text length
    print("\n[1] Benchmark by text length...")
    for case in TEST_CASES:
        df = run_benchmark(case["text"], n=N_REQUESTS)
        df["test_case"] = case["name"]
        all_dfs.append(df)

    df_text = pd.concat(all_dfs, ignore_index=True)
    df_text.to_csv("results/tts_latency.csv", index=False)
    print(f"\nSaved: results/tts_latency.csv")

    # 2. By speaker
    print("\n[2] Benchmark by speaker...")
    speaker_dfs = []
    for sp in SPEAKERS:
        df = run_benchmark("你好世界", speaker=sp, n=5)
        df["speaker"] = sp
        speaker_dfs.append(df)
    df_speakers = pd.concat(speaker_dfs, ignore_index=True)
    df_speakers.to_csv("results/tts_speaker_latency.csv", index=False)
    print(f"Saved: results/tts_speaker_latency.csv")

    # 3. By bitrate
    print("\n[3] Benchmark by bitrate...")
    bitrate_dfs = []
    for br in BITRATES:
        df = run_benchmark("你好世界", bitrate=br, n=5)
        df["bitrate"] = br
        bitrate_dfs.append(df)
    df_bitrates = pd.concat(bitrate_dfs, ignore_index=True)
    df_bitrates.to_csv("results/tts_bitrate_latency.csv", index=False)
    print(f"Saved: results/tts_bitrate_latency.csv")

    # ==================== GENERATE REPORT ====================
    print("\n[4] Generating detailed report...")

    report_lines = []
    report_lines.append("=" * 70)
    report_lines.append("TTS API BENCHMARK REPORT")
    report_lines.append(f"Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 70)
    report_lines.append("")

    # Overall stats
    successful = df_text[df_text["success"]]
    total_requests = len(df_text)
    success_rate = len(successful) / total_requests * 100 if total_requests > 0 else 0
    total_time = successful["latency_ms"].sum() / 1000 if len(successful) > 0 else 0
    throughput = len(successful) / total_time if total_time > 0 else 0

    report_lines.append("GENERAL STATISTICS")
    report_lines.append("-" * 40)
    report_lines.append(f"  Total requests: {total_requests}")
    report_lines.append(f"  Successful: {len(successful)}")
    report_lines.append(f"  Success rate: {success_rate:.2f}%")
    report_lines.append(f"  Throughput: {throughput:.2f} req/s")
    report_lines.append("")

    # Text length summary
    report_lines.append("BY TEXT LENGTH (latency in ms)")
    report_lines.append("-" * 40)
    summary = df_text.groupby("test_case")["latency_ms"].agg(["mean", "std", "min", "max"]).round(0)
    report_lines.append(summary.to_string())
    report_lines.append("")

    # Percentiles
    report_lines.append("PERCENTILES BY TEXT LENGTH (ms)")
    report_lines.append("-" * 40)
    percentiles = [50, 75, 90, 95, 99]
    p_stats = df_text.groupby("test_case")["latency_ms"].quantile([p/100 for p in percentiles]).unstack()
    p_stats.columns = [f"P{p}" for p in percentiles]
    report_lines.append(p_stats.round(0).to_string())
    report_lines.append("")

    # Speaker summary
    report_lines.append("BY SPEAKER (latency in ms)")
    report_lines.append("-" * 40)
    speaker_summary = df_speakers.groupby("speaker")["latency_ms"].agg(["mean", "std"]).round(0)
    report_lines.append(speaker_summary.to_string())
    report_lines.append("")

    # Bitrate summary
    report_lines.append("BY BITRATE (latency in ms)")
    report_lines.append("-" * 40)
    bitrate_summary = df_bitrates.groupby("bitrate")["latency_ms"].agg(["mean", "std"]).round(0)
    report_lines.append(bitrate_summary.to_string())
    report_lines.append("")

    # Combined statistics
    report_lines.append("COMBINED STATISTICS")
    report_lines.append("-" * 40)
    combined_stats = df_text["latency_ms"].describe().round(0)
    report_lines.append(combined_stats.to_string())
    report_lines.append("")

    # Final
    report_lines.append("=" * 70)
    report_lines.append("END OF REPORT")
    report_lines.append("=" * 70)

    report_content = "\n".join(report_lines)
    write_report("results/tts_report.txt", report_content)
    print("Saved: results/tts_report.txt")

    # ==================== GENERATE PLOT ====================
    print("\n[5] Generating plot...")
    sns.set_style("whitegrid")
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df_text, x="test_case", y="latency_ms")
    plt.title("TTS Latency by Text Length")
    plt.xlabel("Test Case")
    plt.ylabel("Latency (ms)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("results/plots/tts_latency_comparison.png", dpi=150, bbox_inches="tight")
    print("Saved: results/plots/tts_latency_comparison.png")
    plt.close()

    # ==================== PRINT REPORT TO CONSOLE ====================
    print("\n" + "=" * 70)
    print("REPORT SUMMARY (see results/tts_report.txt for full details)")
    print("=" * 70)
    print(f"Success rate: {success_rate:.2f}%")
    print(f"Throughput: {throughput:.2f} req/s")
    print(f"Mean latency (all): {df_text['latency_ms'].mean():.0f} ms")
    print(f"P95 latency (all): {df_text['latency_ms'].quantile(0.95):.0f} ms")
    print("=" * 70)

    print("\nDONE. All results saved in 'results/'")
    print("  - results/tts_latency.csv")
    print("  - results/tts_speaker_latency.csv")
    print("  - results/tts_bitrate_latency.csv")
    print("  - results/tts_report.txt")
    print("  - results/plots/tts_latency_comparison.png")

if __name__ == "__main__":
    main()

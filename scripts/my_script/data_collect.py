import json
import pandas as pd
import os

INPUT_PATH = "../../json/1core/gaze_ipcp_l1/"   
OUTPUT_CSV = "../../results/gaze_ipcp_l1_analysis.csv"


def extract_from_file(json_path, prefetcher_name):
    """Extract relevant statistics from a single ChampSim JSON file."""
    with open(json_path, "r") as f:
        data = json.load(f)

    records = []

    for sim in data:
        trace = sim.get("traces", ["unknown"])[0]
        workload = os.path.basename(trace)

        roi = sim.get("roi", {})
        core = roi.get("cores", [{}])[0]

        l1d = roi.get("cpu0_L1D", {})
        l2c = roi.get("cpu0_L2C", {})
        llc = roi.get("LLC", {})

        record = {
            "Workload": workload,
            "Prefetcher": prefetcher_name,
            "Cycles": core.get("cycles", 0),
            "mshr_full": l1d.get("mshr full", 0),
            "prefetch_requested": l1d.get("prefetch requested", 0),
            "prefetch_issued": l1d.get("prefetch issued", 0),
            "l1D_prefetch_useful": l1d.get("prefetch useful", 0),
            "l1D_prefetch_useless": l1d.get("prefetch useless", 0),
            "l1D_prefetch_late": l1d.get("prefetch late", 0),
            "l2_prefetch_useful": l2c.get("pf_useful_at_l2_from_l1", 0),
            "l2_prefetch_useless": l2c.get("pf_useless_at_l2_from_l1", 0),
            "llc_load_miss": (
                llc.get("LOAD", {}).get("miss", [0])[0]
                if isinstance(llc.get("LOAD", {}).get("miss", [0]), list)
                else llc.get("LOAD", {}).get("miss", 0)
            ),
            "PQ_FULL": l1d.get("cache queues", {}).get("PQ_FULL", 0),
            "PQ_MERGED": l1d.get("cache queues", {}).get("PQ_MERGED", 0),
        }

        records.append(record)

    return records


def main():
    prefetcher_name = os.path.basename(INPUT_PATH.rstrip("/"))
    print(f"Detected Prefetcher: {prefetcher_name}")

    all_records = []

    if os.path.isdir(INPUT_PATH):
        json_files = [f for f in os.listdir(INPUT_PATH) if f.endswith(".json")]
        print(f"Found {len(json_files)} JSON files in {INPUT_PATH}")
        for fname in json_files:
            fpath = os.path.join(INPUT_PATH, fname)
            print(f"Processing {fname}")
            all_records.extend(extract_from_file(fpath, prefetcher_name))
    else:
        print(f"Processing single file: {INPUT_PATH}")
        all_records.extend(extract_from_file(INPUT_PATH, prefetcher_name))

    df = pd.DataFrame(all_records)
    os.makedirs(os.path.dirname(OUTPUT_CSV), exist_ok=True)
    if os.path.exists(OUTPUT_CSV):
        df.to_csv(OUTPUT_CSV, mode='a', header=False, index=False)
        print(f"\nData added successfully: {OUTPUT_CSV}")
    else:
        df.to_csv(OUTPUT_CSV, index=False)
        print(f"\nCSV created successfully: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()

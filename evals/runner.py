import json
import requests
import time

ENDPOINT = "http://127.0.0.1:8000/triage"

def run_eval():
    with open("evals/cases.json", "r", encoding="utf-8") as f:
        cases = json.load(f)

    total = len(cases)
    matched_category = 0
    failures = []

    print(f"Running evaluation against {total} test cases...\n")

    for case in cases:
        payload = {"text": case["input"]}
        start_time = time.time()
        try:
            res = requests.post(ENDPOINT, json=payload, timeout=35)
            elapsed_ms = int((time.time() - start_time) * 1000)

            if res.status_code != 200:
                failures.append({
                    "id": case["id"],
                    "input": case["input"],
                    "error": f"HTTP {res.status_code}: {res.text}"
                })
                print(f"[FAIL] Case {case['id']}: Status {res.status_code}")
                continue

            data = res.json()
            actual_cat = data.get("category")
            expected_cat = case["expected_category"]

            if actual_cat == expected_cat:
                matched_category += 1
                print(f"[PASS] Case {case['id']} [{elapsed_ms}ms] -> Expected: '{expected_cat}', Got: '{actual_cat}' (Confidence: {data.get('confidence')})")
            else:
                failures.append({
                    "id": case["id"],
                    "input": case["input"],
                    "expected": expected_cat,
                    "actual": actual_cat,
                    "reason": data.get("reason")
                })
                print(f"[MISMATCH] Case {case['id']} [{elapsed_ms}ms] -> Expected: '{expected_cat}', Got: '{actual_cat}'")

        except Exception as e:
            failures.append({"id": case["id"], "input": case["input"], "error": str(e)})
            print(f"[ERROR] Case {case['id']}: Exception {e}")

    accuracy = (matched_category / total) * 100
    print("\n" + "=" * 45)
    print(f"EVAL SUMMARY: {matched_category}/{total} matched ({accuracy:.1f}% accuracy)")
    print("=" * 45)
    if failures:
        print("\nMismatches / Failures:")
        print(json.dumps(failures, indent=2))

if __name__ == "__main__":
    run_eval()

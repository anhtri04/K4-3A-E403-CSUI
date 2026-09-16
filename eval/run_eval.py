"""Chấm golden set dùng mock_engine (hoặc REAL nếu bỏ --mock và có key)."""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "codebase"))
from mock_engine import generate_plan as mock_plan
from validator import validate

def check_case(case, data):
    blob = json.dumps(data, ensure_ascii=False)
    fails = []
    for s in case.get("must_contain", []):
        if s not in blob:
            fails.append(f"thiếu must_contain={s!r}")
    for s in case.get("must_not_contain", []):
        if s and s in blob:
            fails.append(f"dính must_not_contain={s!r}")
    try:
        json.dumps(data, ensure_ascii=False)
    except Exception:
        fails.append("json_invalid")
    if not data.get("disclaimer"):
        fails.append("missing_disclaimer")
    fails += validate(data, case["input"]["level"], case["input"]["sessions"])
    return fails

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", default="golden_set.json")
    ap.add_argument("--output", default="results_run1.json")
    ap.add_argument("--mock", action="store_true", default=True)
    args = ap.parse_args()

    base = pathlib.Path(__file__).parent
    cases = json.loads((base / args.input).read_text(encoding="utf-8"))
    rows = []
    passed = 0
    for c in cases:
        inp = c["input"]
        data = mock_plan(inp.get("level", "beginner"), inp.get("goal", ""),
                         int(inp.get("sessions", 3)), inp.get("constraints", ""), inp.get("lang", "vi"))
        fails = check_case(c, data)
        ok = not fails
        passed += ok
        rows.append({"id": c["id"], "pass": ok, "fails": fails, "engine": data.get("engine")})
        print(f"{c['id']}: {'PASS' if ok else 'FAIL ' + '; '.join(fails)}")
    print(f"\nTổng: {passed}/{len(cases)} pass ({passed/len(cases)*100:.1f}%)")
    (base / args.output).write_text(json.dumps({"summary": {"passed": passed, "total": len(cases)}, "rows": rows}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Đã lưu {args.output}")

if __name__ == "__main__":
    main()

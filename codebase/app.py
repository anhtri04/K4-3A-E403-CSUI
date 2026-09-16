"""CLI chính: python app.py plan --level beginner --goal "..." --sessions 3 [--mock]"""
import argparse
import datetime
import json
import os
import pathlib

from prompt import SYSTEM_PROMPT, build_user_prompt
from mock_engine import generate_plan as mock_plan

def run_real_or_mock(level, goal, sessions, constraints, lang, force_mock):
    from validator import validate
    if force_mock or not os.getenv("OPENAI_API_KEY"):
        print("[MOCK] Không dùng API thật (thiếu key hoặc --mock). Dùng mock_engine rule-based.")
        data = mock_plan(level, goal, sessions, constraints, lang)
    else:
        from ai_client import call_real_ai
        user = build_user_prompt(level, goal, sessions, constraints, lang)
        try:
            print(f"[REAL] Gọi model={os.getenv('MODEL_NAME', 'gpt-4o-mini')} ...")
            data = call_real_ai(SYSTEM_PROMPT, user)
        except Exception as e:
            print(f"[MOCK] REAL thất bại ({e}) → retry 1 lần ...")
            try:
                data = call_real_ai(SYSTEM_PROMPT, user)
            except Exception as e2:
                print(f"[MOCK] Retry thất bại ({e2}) → fallback mock.")
                data = mock_plan(level, goal, sessions, constraints, lang)
    errs = validate(data, level, sessions)
    if errs:
        print(f"[WARN] validator: {errs}")
    return data

def cmd_plan(args):
    data = run_real_or_mock(args.level, args.goal, args.sessions, args.constraints, args.lang, args.mock)
    outdir = pathlib.Path(__file__).parent / "outputs"
    outdir.mkdir(exist_ok=True)
    tag = "mock" if data.get("mock") else "real"
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = outdir / f"plan_{ts}_{tag}.json"
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n=== GIÁO ÁN TUẦN (engine={data.get('engine')}) ===")
    for d in data.get("weekly_plan", []):
        print(f"- {d['day']}: {d['focus']} | {d['duration_min']}p | RPE {d['intensity_rpe']} | {d.get('notes','')}")
    print("\nAn toàn:")
    for s in data.get("safety_notes", []):
        print(f"  • {s}")
    print(f"\nĐộng viên: {data.get('motivation')}")
    print(f"\nDisclaimer: {data.get('disclaimer')}")
    print(f"\nĐã lưu: {path}")

def cmd_demo(_args):
    for lvl, goal, ses in [("beginner", "chạy 5km trong 30 phút", 3),
                           ("intermediate", "chạy 10km bền hơn", 4),
                           ("beginner", "mới tập, đau gối nhẹ", 3)]:
        print(f"\n######## DEMO: {lvl} | {goal} | {ses} buổi ########")
        data = run_real_or_mock(lvl, goal, ses, "", "vi", force_mock=not os.getenv("OPENAI_API_KEY"))
        print(f"=> engine={data.get('engine')}")

def main():
    p = argparse.ArgumentParser(prog="stamina-coach")
    sub = p.add_subparsers(dest="cmd", required=True)
    pp = sub.add_parser("plan")
    pp.add_argument("--level", default="beginner", choices=["beginner", "intermediate", "advanced"])
    pp.add_argument("--goal", required=True)
    pp.add_argument("--sessions", type=int, default=3)
    pp.add_argument("--constraints", default="")
    pp.add_argument("--lang", default="vi")
    pp.add_argument("--mock", action="store_true")
    pp.set_defaults(func=cmd_plan)
    pd = sub.add_parser("demo")
    pd.set_defaults(func=cmd_demo)
    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()

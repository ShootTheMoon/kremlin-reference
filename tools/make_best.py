# -*- coding: utf-8 -*-
"""뷰별 대표 1장을 _best/ 로 모은다 (모델링 투입용).

  python tools/make_best.py <best_dir>            # dry-run
  python tools/make_best.py <best_dir> --apply

_best/<건물폴더>/<뷰이름>.jpg 로 복사한다. 파일명이 곧 방향이라 블렌더에서 바로 걸 수 있다.
정사 평면도(_plans/*.svg)와 실측 도면(0_실측도면/)도 같이 넣는다.
"""
import os, sys, json, glob, shutil, io, html

REF  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BEST = os.path.join(REF, "_best")
VIEWS = ["1_Top","2_Left45","3_Front","4_Right45","5_Left","6_Right","7_Back","8_Bottom"]

def find(fol, fn):
    for sub in sorted(os.listdir(os.path.join(REF, fol))):
        p = os.path.join(REF, fol, sub, fn)
        if os.path.exists(p): return p
    p = os.path.join(REF, fol, fn)
    return p if os.path.exists(p) else None

def main():
    src_dir = sys.argv[1]; apply_ = "--apply" in sys.argv
    plan, miss = [], []
    for jf in sorted(glob.glob(os.path.join(src_dir, "*.json"))):
        fol = os.path.splitext(os.path.basename(jf))[0]
        if not os.path.isdir(os.path.join(REF, fol)):
            print("!! 건물 폴더 없음:", fol); continue
        for view, e in json.load(open(jf, encoding="utf-8")).items():
            fn = e.get("f") if isinstance(e, dict) else e
            if not fn:
                miss.append((fol, view, (e or {}).get("why",""))); continue
            s = find(fol, fn)
            if not s: print("!! 파일 없음:", fol, fn); continue
            ext = os.path.splitext(fn)[1].lower()
            plan.append((s, os.path.join(BEST, fol, view + ext), fol, view, fn))
    # 실측 도면 + 정사 평면도
    extra = []
    for fol in sorted(f for f in os.listdir(REF) if f[0].isdigit()):
        dd = os.path.join(REF, fol, "0_실측도면")
        if os.path.isdir(dd):
            for f in sorted(os.listdir(dd)):
                if f.lower().endswith((".jpg",".png")):
                    extra.append((os.path.join(dd,f), os.path.join(BEST,fol,"0_도면_"+f), fol, "0_실측도면", f))
        for v in ("1_Top","8_Bottom"):
            sv = os.path.join(REF, fol, v, "plan.svg")
            if os.path.exists(sv):
                extra.append((sv, os.path.join(BEST,fol,v+"_plan.svg"), fol, v, "plan.svg"))
    print("사진 %d장 + 도면·평면도 %d장 = %d개 파일" % (len(plan), len(extra), len(plan)+len(extra)))
    if miss:
        print("\n채울 수 없는 칸 %d개:" % len(miss))
        for f, v, w in miss: print("   %-24s %-11s %s" % (f[:24], v, w[:60]))
    print()
    for s, d, fol, view, fn in plan:
        print("  %-24s %-11s <- %s" % (fol[:24], view, fn))
    if apply_:
        for s, d, *_ in plan + extra:
            os.makedirs(os.path.dirname(d), exist_ok=True); shutil.copy2(s, d)
        # 색인
        rows = []
        for fol in sorted(f for f in os.listdir(BEST) if os.path.isdir(os.path.join(BEST, f))):
            fs = sorted(os.listdir(os.path.join(BEST, fol)))
            rows.append("<h2>%s <span class='n'>(%d)</span></h2><div class='row'>%s</div>" % (
                html.escape(fol), len(fs),
                "".join("<figure><a href='%s/%s' target='_blank'>%s</a><figcaption>%s</figcaption></figure>" % (
                    html.escape(fol), html.escape(f),
                    ("<img src='%s/%s' loading='lazy'>" % (html.escape(fol), html.escape(f))),
                    html.escape(os.path.splitext(f)[0])) for f in fs)))
        io.open(os.path.join(BEST, "index.html"), "w", encoding="utf-8").write(
            "<!doctype html><meta charset='utf-8'><title>크렘린 — 뷰별 대표 1장</title>"
            "<style>body{font-family:system-ui,'Malgun Gothic',sans-serif;margin:0;background:#1b1b1e;color:#e8e8ea}"
            "h1{padding:18px 24px 6px;margin:0;font-size:20px}"
            "h2{margin:30px 0 4px;padding:0 24px;font-size:17px;border-top:1px solid #333;padding-top:20px}"
            ".n{color:#7a7a84;font-weight:400}"
            ".row{display:flex;flex-wrap:wrap;gap:10px;padding:0 24px 8px}"
            "figure{margin:0;width:200px}figure img{width:200px;height:150px;object-fit:contain;background:#000;border-radius:3px}"
            "figcaption{font-size:12px;color:#c8c8d0;padding-top:3px;text-align:center}</style>"
            "<h1>크렘린 — 뷰별 대표 1장 <span class='n'>(모델링 투입용)</span></h1>" + "".join(rows))
        print("\n_best/ 생성 완료 + index.html")
    else:
        print("\n(dry-run) 실제 복사하려면 --apply")

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""모델별 배경제거 결과 중 채택본을 골라 _best_ai/ 로 확정한다.

  python tools/assemble_ai.py <pick_dir> [--apply]

pick_dir 의 *.json 은 [{"fol":..,"view":..,"best":"u2net|bria-rmbg|birefnet-general|none","why":..}] 형식.
best=="none" 인 것은 복사하지 않고 REJECTED.md 에 사유와 함께 남긴다.
"""
import os, sys, json, glob, shutil, io, html
import numpy as np
from PIL import Image

REF = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REF, "_best_ai")
MODELS = ["u2net", "bria-rmbg", "birefnet-general"]

def main():
    pd = sys.argv[1]; apply_ = "--apply" in sys.argv
    picks = []
    for jf in sorted(glob.glob(os.path.join(pd, "*.json"))):
        picks += json.load(open(jf, encoding="utf-8"))
    seen = set(); rows = []; rej = []
    for e in picks:
        k = (e["fol"], e["view"])
        if k in seen: print("!! 중복 판정:", k); continue
        seen.add(k)
        m = e.get("best")
        if m == "none" or not m:
            rej.append((e["fol"], e["view"], e.get("why",""))); continue
        if m not in MODELS: print("!! 알 수 없는 모델:", k, m); continue
        src = os.path.join(REF, "_ai_"+m, e["fol"], e["view"]+".png")
        if not os.path.exists(src): print("!! 파일 없음:", src); continue
        rows.append((src, os.path.join(OUT, e["fol"], e["view"]+".png"), e["fol"], e["view"], m, e.get("why","")))
    print("채택 %d / 반려 %d / 판정 총 %d" % (len(rows), len(rej), len(picks)))
    from collections import Counter
    print("모델별 채택:", dict(Counter(r[4] for r in rows)))
    if rej:
        print("\n반려:")
        for f, v, w in rej: print("   %-24s %-16s %s" % (f[:24], v, w[:60]))
    if not apply_:
        print("\n(dry-run) --apply 로 확정")
        return
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    for src, dst, fol, view, m, why in rows:
        os.makedirs(os.path.dirname(dst), exist_ok=True); shutil.copy2(src, dst)
    # 반려 기록
    lines = ["# AI 입력에서 제외된 컷", "",
             "배경 제거 3종(u2net / bria-rmbg / birefnet-general)을 다 돌렸지만",
             "대상 건물을 분리하지 못한 것들이다. `_best/` 의 원본 사진은 그대로 있으니",
             "수동 마스킹하거나, 모델링 레퍼런스로만 써라.", "",
             "| 건물 | 뷰 | 사유 |", "|---|---|---|"]
    for f, v, w in rej: lines.append("| %s | `%s` | %s |" % (f, v, w))
    io.open(os.path.join(OUT, "REJECTED.md"), "w", encoding="utf-8").write("\n".join(lines) + "\n")
    # 색인
    body = []
    for fol in sorted(f for f in os.listdir(OUT) if os.path.isdir(os.path.join(OUT, f))):
        fs = sorted(os.listdir(os.path.join(OUT, fol)))
        body.append("<h2>%s <span class='n'>(%d)</span></h2><div class='row'>%s</div>" % (
            html.escape(fol), len(fs),
            "".join("<figure><a href='%s/%s' target='_blank'><img src='%s/%s' loading='lazy'></a>"
                    "<figcaption>%s</figcaption></figure>" % (
                        html.escape(fol), html.escape(x), html.escape(fol), html.escape(x),
                        html.escape(os.path.splitext(x)[0])) for x in fs)))
    io.open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write(
        "<!doctype html><meta charset='utf-8'><title>크렘린 — AI 3D 생성 입력</title>"
        "<style>body{font-family:system-ui,'Malgun Gothic',sans-serif;margin:0;background:#1b1b1e;color:#e8e8ea}"
        "h1{padding:18px 24px 6px;margin:0;font-size:20px}"
        "h2{margin:30px 0 4px;padding:0 24px 0;font-size:17px;border-top:1px solid #333;padding-top:20px}"
        ".n{color:#7a7a84;font-weight:400}.row{display:flex;flex-wrap:wrap;gap:10px;padding:0 24px 8px}"
        "figure{margin:0;width:190px}"
        "figure img{width:190px;height:190px;object-fit:contain;border-radius:3px;"
        "background:repeating-conic-gradient(#2a2a2e 0% 25%,#232327 0% 50%) 50%/16px 16px}"
        "figcaption{font-size:12px;color:#c8c8d0;padding-top:3px;text-align:center}</style>"
        "<h1>크렘린 — AI 3D 생성 입력 <span class='n'>(배경 제거 · 정사각 · 투명 PNG)</span></h1>" + "".join(body))
    print("\n_best_ai/ 확정 %d장 + REJECTED.md + index.html" % len(rows))

if __name__ == "__main__":
    main()

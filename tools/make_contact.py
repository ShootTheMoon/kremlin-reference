# -*- coding: utf-8 -*-
"""_contact/*.html 컨택트 시트를 현재 폴더 구조대로 다시 만든다.

  python tools/make_contact.py
"""
import os, io, html, collections

REF = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(REF, "_contact")
ORDER = ["0_실측도면","1_Top","2_Left45","3_Front","4_Right45","5_Left","6_Right","7_Back","8_Bottom",
         "_unsorted","_indoor","_detail","_pano","_other","_notphoto","_mirror"]
LABEL = {"1_Top":"Top","2_Left45":"Left 45°","3_Front":"Front","4_Right45":"Right 45°",
         "5_Left":"Left","6_Right":"Right","7_Back":"Back","8_Bottom":"Bottom",
         "0_실측도면":"★ 실측도면 (1:1 트레이싱 가능)","_unsorted":"미분류","_indoor":"실내(모델링 무관)",
         "_detail":"부분 접사","_pano":"원경/파노라마","_other":"다른 건물",
         "_notphoto":"판화·도면","_mirror":"좌우반전 — 트레이싱 금지"}
NOTE  = {"8_Bottom":"건물 밑면은 촬영 불가 — 정사 평면도로 대체"}
CSS = """<style>body{font-family:system-ui,'Malgun Gothic',sans-serif;margin:0;background:#1b1b1e;color:#e8e8ea}
h1{padding:18px 24px 6px;margin:0;font-size:20px}
h2{margin:34px 0 4px;padding:0 24px;font-size:17px;border-top:1px solid #333;padding-top:22px}
.sub{padding:0 24px;color:#9a9aa2;font-size:12.5px;margin-bottom:10px}
.view{padding:6px 24px 2px;color:#c8c8d0;font-size:13px;font-weight:600}
.view .n{color:#7a7a84;font-weight:400}
.row{display:flex;flex-wrap:wrap;gap:6px;padding:0 24px 8px}
.row img{height:118px;border-radius:3px;background:#000;object-fit:cover}
.row a{line-height:0}
.empty{padding:0 24px 8px;color:#6a6a72;font-size:12px;font-style:italic}
.plan{height:150px!important;background:#fff!important;object-fit:contain!important;padding:4px}
</style>"""

def scan(fol):
    d = os.path.join(REF, fol); got = collections.OrderedDict()
    if not os.path.isdir(d): return got
    subs = [s for s in os.listdir(d) if os.path.isdir(os.path.join(d, s))]
    for s in ORDER + sorted(x for x in subs if x not in ORDER):
        if s not in subs: continue
        fs = sorted(f for f in os.listdir(os.path.join(d, s))
                    if f.lower().endswith((".jpg",".jpeg",".png",".svg")))
        if fs or s in NOTE: got[s] = fs
    loose = sorted(f for f in os.listdir(d)
                   if os.path.isfile(os.path.join(d, f))
                   and f.lower().endswith((".jpg",".jpeg",".png",".svg")))
    if loose: got["(폴더 직하)"] = loose
    return got

def block(fol, got):
    o = []
    for s, fs in got.items():
        o.append("<div class='view'>%s <span class='n'>(%d)</span></div>"
                 % (html.escape(LABEL.get(s, s)), len(fs)))
        if not fs:
            o.append("<div class='empty'>%s</div>" % html.escape(NOTE.get(s, "없음")))
            continue
        o.append("<div class='row'>")
        for f in fs:
            rel = "../%s/%s/%s" % (fol, s, f) if s != "(폴더 직하)" else "../%s/%s" % (fol, f)
            cls = " class='plan'" if f.lower().endswith(".svg") else ""
            o.append("<a href='%s' target='_blank'><img%s src='%s' loading='lazy'></a>"
                     % (html.escape(rel), cls, html.escape(rel)))
        o.append("</div>")
    return "".join(o)

def main():
    os.makedirs(OUT, exist_ok=True)
    fols = sorted(f for f in os.listdir(REF)
                  if os.path.isdir(os.path.join(REF, f)) and not f.startswith("_"))
    idx = ["<!doctype html><meta charset='utf-8'><title>크렘린 레퍼런스 — 전체 컨택트 시트</title>", CSS,
           "<h1>크렘린 레퍼런스 — 전체 컨택트 시트</h1>"]
    for fol in fols:
        got = scan(fol); n = sum(len(v) for v in got.values())
        idx += ["<h2><a href='%s.html' style='color:inherit'>%s</a> <span class='n'>(%d)</span></h2>"
                % (html.escape(fol), html.escape(fol), n), block(fol, got)]
        one = ["<!doctype html><meta charset='utf-8'><title>크렘린 레퍼런스 — %s</title>" % html.escape(fol),
               CSS, "<h1>%s <span class='n'>(%d)</span></h1>" % (html.escape(fol), n),
               "<div class='sub'><a href='index.html' style='color:#8ab'>← 전체</a></div>", block(fol, got)]
        io.open(os.path.join(OUT, fol + ".html"), "w", encoding="utf-8").write("\n".join(one))
    io.open(os.path.join(OUT, "index.html"), "w", encoding="utf-8").write("\n".join(idx))
    print("컨택트 시트 %d개 + index 생성" % len(fols))

if __name__ == "__main__":
    main()

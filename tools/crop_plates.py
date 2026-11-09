# -*- coding: utf-8 -*-
"""실측 도판에서 요소별 입면·평면·단면을 잘라내 _best/ 에 넣는다.

  python tools/crop_plates.py [--apply]

각 조각 아래에 그 도판의 스케일바를 붙여서, 조각 하나만 봐도 치수를 잴 수 있게 한다.
좌표는 도판 폭·높이에 대한 비율 (x0, y0, x1, y1).
"""
import os, sys
from PIL import Image

REF  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC  = os.path.join(REF, "00_소련1953_실측도면")
BEST = os.path.join(REF, "_best")

# 도판: (파일, 회전각, 스케일바 박스)
PLATES = {
 "tab01": ("tab01_p025.jpg",   0, (0.21, 0.095, 0.54, 0.165)),
 "tab05": ("tab05_p033.jpg", -90, (0.05, 0.375, 0.62, 0.425)),   # 평면용 + 남측입면용 둘 다 포함
 "tab08": ("tab08_p039.jpg",   0, (0.23, 0.430, 0.46, 0.530)),
 "tab12": ("tab12_p047.jpg",   0, (0.03, 0.395, 0.25, 0.475)),
}
# 조각별 스케일바 override (도판마다 축척이 여러 개다 — 입면용/평면용/상세용이 따로 있다)
BARS = {
 "tab05_plan":  (0.060, 0.380, 0.215, 0.420),   # 0 5 10 20 м  (평면용)
 "tab05_porch": (0.425, 0.400, 0.615, 0.442),   # 0 1 2 3 4 5 м (현관 상세용)
 "tab05_fac":   (0.355, 0.850, 0.615, 0.890),   # 0..10..20 м  (남측입면용)
 "tab05_ark":   (0.845, 0.300, 0.955, 0.345),   # 0 100 см     (아케이드 상세용)
}
# (도판, 건물폴더, 출력이름, 박스, 스케일바키(없으면 도판 기본))
CROPS = [
 # --- Табл. 1 ---
 ("tab01","12_스파스카야_탑","3_Front_도면_정면입면",      (0.70,0.045,1.00,0.58)),
 ("tab01","11_성벽_여장",   "0_도면_성벽단면",            (0.83,0.760,1.00,0.92)),
 ("tab01","11_성벽_여장",   "0_도면_크렘린배치평면",       (0.15,0.390,0.80,0.89)),
 # --- Табл. 5 (우스펜스키, -90 회전 필요) ---
 ("tab05","01_우스펜스키_대성당","5_Left_도면_남측입면",    (0.050,0.255,0.52,0.885), "tab05_fac"),
 ("tab05","01_우스펜스키_대성당","3_Front_도면_서측현관",   (0.35,0.015,0.66,0.398), "tab05_porch"),
 ("tab05","01_우스펜스키_대성당","8_Bottom_도면_평면",      (0.02,0.02,0.27,0.375), "tab05_plan"),
 ("tab05","01_우스펜스키_대성당","0_도면_종단면",           (0.525,0.19,0.98,0.885), "tab05_fac"),
 ("tab05","01_우스펜스키_대성당","0_도면_아케이드열주대상세",(0.76,0.015,0.99,0.295), "tab05_ark"),
 # --- Табл. 8 ---
 ("tab08","04_이반대제_종탑","3_Front_도면_서측입면",       (0.01,0.12,0.31,0.89)),
 ("tab08","04_이반대제_종탑","8_Bottom_도면_평면",          (0.28,0.685,0.45,0.89)),
 ("tab08","02_아르한겔스키_대성당","3_Front_도면_서측입면",  (0.61,0.515,1.00,0.89)),
 ("tab08","02_아르한겔스키_대성당","0_도면_종단면",          (0.39,0.470,0.64,0.69)),
 ("tab08","02_아르한겔스키_대성당","8_Bottom_도면_평면",     (0.41,0.680,0.63,0.89)),
 ("tab08","03_블라고베셴스키_대성당","5_Left_도면_남측입면",  (0.37,0.115,0.77,0.45)),
 ("tab08","03_블라고베셴스키_대성당","0_도면_종단면",         (0.22,0.085,0.43,0.31)),
 ("tab08","03_블라고베셴스키_대성당","8_Bottom_도면_1층평면", (0.73,0.220,0.96,0.43)),
 # --- Табл. 12 ---
 ("tab12","07_테렘궁","3_Front_도면_주입면",               (0.31,0.080,0.92,0.40)),
 ("tab12","07_테렘궁","6_Right_도면_측면입면_단면",         (0.03,0.080,0.31,0.41)),
 ("tab12","07_테렘궁","8_Bottom_도면_거주층평면",           (0.41,0.370,0.99,0.49)),
 ("tab12","06_파세트궁","3_Front_도면_주입면",              (0.57,0.460,0.99,0.72)),
 ("tab12","06_파세트궁","8_Bottom_도면_평면",               (0.35,0.690,0.61,0.87)),
 ("tab12","06_파세트궁","0_도면_단면",                      (0.59,0.700,0.99,0.87)),
 ("tab12","06_파세트궁","0_도면_17세기도상_파사드상세",      (0.35,0.430,0.59,0.63)),
 ("tab12","05_대크렘린궁","0_도면_궁전복합체배치평면",        (0.01,0.470,0.37,0.88)),
 ("tab12","07_테렘궁","0_도면_궁전복합체배치평면",            (0.01,0.470,0.37,0.88)),
]

def load(key):
    fn, rot, sb = PLATES[key]
    im = Image.open(os.path.join(SRC, fn)).convert("RGB")
    if rot: im = im.rotate(rot, expand=True)
    w, h = im.size
    bar = im.crop((int(sb[0]*w), int(sb[1]*h), int(sb[2]*w), int(sb[3]*h)))
    return im, bar

def barcrop(im, key):
    w, h = im.size; b = BARS[key]
    return im.crop((int(b[0]*w), int(b[1]*h), int(b[2]*w), int(b[3]*h)))

def main():
    apply_ = "--apply" in sys.argv
    cache = {}
    for row in CROPS:
        key, fol, name, box = row[:4]
        bkey = row[4] if len(row) > 4 else None
        if key not in cache: cache[key] = load(key)
        im, bar = cache[key]
        if bkey: bar = barcrop(im, bkey)
        w, h = im.size
        c = im.crop((int(box[0]*w), int(box[1]*h), int(box[2]*w), int(box[3]*h)))
        # 스케일바를 조각 폭에 맞춰 아래에 붙인다
        bw = min(c.width, int(bar.width * 1.0))
        b2 = bar.resize((bw, int(bar.height * bw / bar.width)), Image.LANCZOS)
        out = Image.new("RGB", (c.width, c.height + b2.height + 14), "white")
        out.paste(c, (0, 0)); out.paste(b2, (8, c.height + 10))
        d = os.path.join(BEST, fol, name + ".jpg")
        print("%-26s %-30s %dx%d" % (fol[:26], name, out.width, out.height))
        if apply_:
            os.makedirs(os.path.dirname(d), exist_ok=True)
            out.save(d, "JPEG", quality=92, subsampling=0)
    print("\n%d개 %s" % (len(CROPS), "생성 완료" if apply_ else "(dry-run) --apply 로 실행"))

if __name__ == "__main__":
    main()

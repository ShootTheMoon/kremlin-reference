# -*- coding: utf-8 -*-
"""_best/ 사진을 AI 3D 생성기 입력용으로 가공해 _best_ai/ 에 넣는다.

  python tools/make_ai_inputs.py [--model isnet-general-use] [--size 2048]

처리: 배경 제거(rembg) -> 피사체 바운딩박스로 크롭 -> 여백 8% -> 정사각 패딩 -> 투명 PNG.
도면(0_도면_*, *_도면_*)과 SVG 는 건너뛴다 — AI 에 넣으면 종이 질감 덩어리가 나온다.
"""
import os, sys, io
import numpy as np
from PIL import Image, ImageOps

REF  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BEST = os.path.join(REF, "_best")
def arg(flag, default):
    return sys.argv[sys.argv.index(flag)+1] if flag in sys.argv else default

OUT  = os.path.join(REF, arg("--out", "_best_ai"))

SIZE  = int(arg("--size", 2048))
MODEL = arg("--model", "u2net")
MARGIN = 0.08

def is_photo(fn):
    if not fn.lower().endswith((".jpg", ".jpeg", ".png")): return False
    if "도면" in fn: return False
    return True

def keep_main_blob(im, min_ratio=0.06):
    """작은 섬(사람·가로등·조각)을 떼어낸다. 가장 큰 덩어리의 min_ratio 미만은 삭제."""
    import cv2
    a = np.array(im.split()[-1])
    m = (a > 8).astype(np.uint8)
    n, lab, stats, _ = cv2.connectedComponentsWithStats(m, 8)
    if n <= 2: return im
    areas = stats[1:, cv2.CC_STAT_AREA]
    keep = 1 + np.where(areas >= areas.max() * min_ratio)[0]
    mask = np.isin(lab, keep)
    a2 = np.where(mask, a, 0).astype(np.uint8)
    out = im.copy(); out.putalpha(Image.fromarray(a2))
    return out

def square_pad(im, size, margin):
    """알파 바운딩박스로 자르고 여백 준 정사각 캔버스에 올린다."""
    a = np.array(im.split()[-1])
    ys, xs = np.where(a > 8)
    if len(xs) == 0: return None
    x0, x1, y0, y1 = xs.min(), xs.max()+1, ys.min(), ys.max()+1
    im = im.crop((int(x0), int(y0), int(x1), int(y1)))
    side = int(max(im.width, im.height) * (1 + 2*margin))
    canvas = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    canvas.paste(im, ((side-im.width)//2, (side-im.height)//2), im)
    return canvas.resize((size, size), Image.LANCZOS)

def main():
    from rembg import new_session, remove
    sess = new_session(MODEL)
    n = skip = fail = 0
    for fol in sorted(f for f in os.listdir(BEST) if os.path.isdir(os.path.join(BEST, f))):
        for fn in sorted(os.listdir(os.path.join(BEST, fol))):
            if not is_photo(fn): skip += 1; continue
            src = os.path.join(BEST, fol, fn)
            dst = os.path.join(OUT, fol, os.path.splitext(fn)[0] + ".png")
            im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
            cut = remove(im, session=sess, post_process_mask=True)
            cut = keep_main_blob(cut)
            sq = square_pad(cut, SIZE, MARGIN)
            if sq is None:
                print("  !! 피사체 못 찾음:", fol, fn); fail += 1; continue
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            sq.save(dst, "PNG", optimize=True)
            cov = (np.array(sq.split()[-1]) > 8).mean()
            print("  %-24s %-28s 알파점유 %4.1f%%" % (fol[:24], os.path.basename(dst), cov*100))
            n += 1
    print("\n%d장 생성 / 도면·SVG %d건 제외 / 실패 %d" % (n, skip, fail))

if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
ref/ 사진을 건물별 8뷰 폴더로 배정한다 (좌표 트랙).

  python tools/sort_views.py            # dry-run, 제안만 출력
  python tools/sort_views.py --apply    # 실제 이동
  python tools/sort_views.py --audit    # 이미 분류된 것과의 불일치만

핵심 공식
  front_azimuth = 공칭_정면_나침반방위 - yaw        <- yaw 를 빼야 한다
  az  = atan2(x_cam - x_bldg, y_cam - y_bldg)       (0=북, 시계방향)
  rel = ((az - front) + 180) mod 360 - 180
  |rel|<22.5 Front / 22.5~67.5 Right45 / 67.5~112.5 Right / 그밖 Back / 음수쪽은 Left

이미 손으로 분류된 76장에 대해 100% 재현되는 것을 확인했다 (yaw 미보정 시 43%).
"""
import os, sys, math, io, shutil, collections

REF   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LAT0, LON0   = 55.7516212, 37.6181220          # 크렘린 relation 1360641 중심
M_LAT, M_LON = 111337.3, 62772.1               # φ=55.7516° 에서의 m/deg

# xy: 앵커 기준 m (README) | nom: 정면의 공칭 나침반 방위 | yaw: README | plan: 평면 치수 | h: 높이
BLDG = {
 "01_우스펜스키_대성당":    dict(xy=( -66.58,  -76.79), nom=270, yaw=16, plan=(43.10, 28.62), h=49.0),
 "02_아르한겔스키_대성당":  dict(xy=( -20.42, -160.23), nom=270, yaw= 7, plan=(34.71, 30.00), h=47.5),
 "03_블라고베셴스키_대성당":dict(xy=( -77.74, -179.25), nom=270, yaw=14, plan=(23.21, 26.59), h=37.0),
 "04_이반대제_종탑":        dict(xy=(   5.65, -100.19), nom=270, yaw=19, plan=(14.88, 14.63), h=81.0),
 "05_대크렘린궁":           dict(xy=(-150.82, -153.96), nom=180, yaw=14, plan=(176.44,145.23),h=47.0),
 # 06/07 은 OSM relation 7679578 / node 2368886164 에서 새로 확보 (2026-08-19)
 # ⚠ 06: relation 7679578 을 멀티폴리곤으로 조립한 값(닫힌 링 1개, 면적 992.7 m2,
 #    OBB 39.90 x 31.47 @ 13.7deg = 주 블록 34.9 x 27.27 + 북서 부속 11.3 x 4.2).
 #    front=76 은 장축 방위 76.3deg 로 기하 확인됨. 그러나 이 폴더 사진 14장 중 9장은
 #    좌표가 건물에서 1.5 m(=피사체 좌표)이고 나머지 5장도 지오태그가 서로 모순이라
 #    표본이 사실상 없다 -> trust=False, 육안 우선.
 "06_파세트궁":             dict(xy=( -91.73, -122.37), nom= 90, yaw=14, plan=(39.90, 31.47), h=21.0, trust=False),
 "07_테렘궁":               dict(xy=(-156.58, -115.51), nom=180, yaw=14, plan=(60.00, 30.00), h=32.0),
 "08_상원궁":               dict(xy=(  27.04,  178.20), nom=180, yaw=47, plan=(137.41,138.72),h=27.0),
 "09_아르세날":             dict(xy=(-115.95,  222.90), nom=180, yaw=69, plan=(306.93, 87.24),h=24.0),
 "10_오루제이나야_팔라타":  dict(xy=(-293.65, -225.33), nom=180, yaw=54, plan=(90.88, 34.91), h=22.0),
 # 11 성벽은 2.2 km 라 '정면'이 없다 -> 8뷰 분류 대상 아님
 "12_스파스카야_탑":        dict(xy=( 204.77,  100.55), nom= 90, yaw=47, plan=(25.59, 18.03), h=71.0),
}
BINS = [(-22.5, 22.5, "3_Front"), (22.5, 67.5, "4_Right45"), (67.5, 112.5, "6_Right"),
        (-67.5, -22.5, "2_Left45"), (-112.5, -67.5, "5_Left")]
VIEWS = ["1_Top","2_Left45","3_Front","4_Right45","5_Left","6_Right","7_Back","8_Bottom"]
# 육안 판정으로 반려된 것 — 방위는 맞아도 뷰 레퍼런스로 못 쓰므로 좌표 트랙이 건드리지 않는다
REJECT = {"_indoor","_pano","_other","_detail","_notphoto","_mirror"}

def front_az(b):        return (b["nom"] - b["yaw"]) % 360
def to_xy(lat, lon):    return ((lon-LON0)*M_LON, (lat-LAT0)*M_LAT)

def radius(b):
    """유효 촬영 반경. 탑처럼 높은 것은 멀리서도 면이 잡히므로 높이에 비례시킨다."""
    return max(80.0, min(400.0, max(max(b["plan"])*2.5, b["h"]*4.0)))

def load():
    rd = lambda p: io.open(os.path.join(REF,p), encoding="utf-8-sig").read().splitlines()
    cam = {}
    for ln in rd("_camera_coords.tsv")[1:]:
        f = ln.split("\t")
        if len(f) >= 4 and f[3] == "camera":
            cam.setdefault(f[0], (float(f[1]), float(f[2])))
    src = {}
    for ln in rd("SOURCES.txt"):
        f = ln.split("\t")
        if len(f) >= 2: src[f[0]] = f[1]
    cur = {}
    for fol in BLDG:
        d = os.path.join(REF, fol)
        if not os.path.isdir(d): continue
        for sub in sorted(os.listdir(d)):
            sd = os.path.join(d, sub)
            if os.path.isdir(sd):
                for fn in sorted(os.listdir(sd)):
                    if fn.lower().endswith((".jpg",".jpeg",".png")):
                        cur[fol+"/"+fn] = sub
    return cam, src, cur

def classify(fol, fn, cam, src):
    """-> (view, rel, dist) | (None, 사유, None)"""
    b = BLDG[fol]
    title = src.get(fol+"/"+fn)                    # SOURCES 는 뷰 폴더 이전 경로 기준
    if not title:            return None, "SOURCES에 없음", None
    if title not in cam:     return None, "촬영좌표 없음", None
    cx, cy = to_xy(*cam[title])
    dx, dy = cx-b["xy"][0], cy-b["xy"][1]
    dist   = math.hypot(dx, dy)
    if dist < 12.0:          return None, "좌표무효(피사체좌표, %.0fm)" % dist, dist
    if dist > radius(b):     return None, "원경(%.0fm > %.0fm)" % (dist, radius(b)), dist
    az  = math.degrees(math.atan2(dx, dy)) % 360
    rel = ((az - front_az(b)) + 180) % 360 - 180
    for lo, hi, name in BINS:
        if lo <= rel < hi:   return name, rel, dist
    return "7_Back", rel, dist

def main():
    apply_ = "--apply" in sys.argv
    audit  = "--audit" in sys.argv
    cam, src, cur = load()
    stat, moves, skips = collections.Counter(), [], collections.Counter()
    for key, sub in sorted(cur.items()):
        fol, fn = key.split("/")
        if not BLDG[fol].get("trust", True):
            stat["좌표불신(육안우선)"] += 1
            continue
        if sub in REJECT:
            stat["반려(육안)"] += 1
            continue
        view, info, dist = classify(fol, fn, cam, src)
        if view is None:
            skips[str(info).split("(")[0]] += 1
            stat["좌표불가"] += 1
            continue
        stat["판정"] += 1
        if view != sub:
            moves.append((fol, fn, sub, view, info, dist))
            stat["불일치"] += 1
    print("판정 %d장 / 좌표불가 %d장 / 불일치 %d장 / 육안반려 %d장 / 좌표불신 %d장"
          % (stat["판정"], stat["좌표불가"], stat["불일치"], stat["반려(육안)"], stat["좌표불신(육안우선)"]))
    for k, v in skips.most_common(): print("   좌표불가 사유: %-14s %d" % (k, v))
    if moves:
        print("\n%-24s %-8s %-11s -> %-11s rel   dist" % ("건물","파일","현재","제안"))
        for fol, fn, sub, view, rel, dist in moves:
            print("%-24s %-8s %-11s -> %-11s %+5.0f %5.0fm" % (fol[:22], fn, sub, view, rel, dist))
    if apply_:
        for fol, fn, sub, view, rel, dist in moves:
            s = os.path.join(REF, fol, sub, fn); d = os.path.join(REF, fol, view, fn)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            if os.path.exists(d):
                print("  건너뜀(중복):", d); continue
            shutil.move(s, d)
        print("\n%d장 이동 완료." % len(moves))
    elif not audit:
        print("\n(dry-run) 실제 이동하려면 --apply")

if __name__ == "__main__":
    main()

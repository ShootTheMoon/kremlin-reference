# -*- coding: utf-8 -*-
"""
육안 판정 결과(verdicts/*.json)를 실제 폴더 구조에 반영한다.

  python tools/apply_verdicts.py <verdicts_dir>            # dry-run
  python tools/apply_verdicts.py <verdicts_dir> --apply

verdicts/<건물폴더>.json 은 [{"f":"07.jpg","view":"4_Right45","confidence":"high","why":"..."}] 형식.
view 는 8뷰 이름이거나 반려 버킷(_indoor/_pano/_other/_detail/_notphoto/_mirror/_unsorted).
low confidence 는 기본으로 건너뛴다(--include-low 로 포함).
"""
import os, sys, json, glob, shutil, collections

REF = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VIEWS   = {"1_Top","2_Left45","3_Front","4_Right45","5_Left","6_Right","7_Back","8_Bottom"}
BUCKETS = {"_indoor","_pano","_other","_detail","_notphoto","_mirror","_unsorted"}

def find_current(fol, fn):
    d = os.path.join(REF, fol)
    for sub in sorted(os.listdir(d)):
        if os.path.isdir(os.path.join(d, sub)) and os.path.exists(os.path.join(d, sub, fn)):
            return sub
    return None

def main():
    vdir  = sys.argv[1]
    apply_= "--apply" in sys.argv
    low   = "--include-low" in sys.argv
    stat  = collections.Counter(); plan = []
    for jf in sorted(glob.glob(os.path.join(vdir, "*.json"))):
        fol = os.path.splitext(os.path.basename(jf))[0]
        if not os.path.isdir(os.path.join(REF, fol)):
            print("!! 건물 폴더 없음:", fol); continue
        for e in json.load(open(jf, encoding="utf-8")):
            fn, view = e["f"], e["view"]
            if view == "8_Bottom":
                print("!! 8_Bottom 배정 거부:", fol, fn); stat["거부"] += 1; continue
            if view not in VIEWS and view not in BUCKETS:
                print("!! 알 수 없는 view:", fol, fn, view); stat["거부"] += 1; continue
            if e.get("confidence") == "low" and not low:
                stat["low건너뜀"] += 1; continue
            cur = find_current(fol, fn)
            if cur is None:
                print("!! 파일 없음:", fol, fn); stat["없음"] += 1; continue
            if cur == view: stat["변화없음"] += 1; continue
            plan.append((fol, fn, cur, view, e.get("confidence",""), e.get("why","")))
            stat["이동"] += 1
    print("이동 %d / 변화없음 %d / low건너뜀 %d / 거부 %d / 없음 %d"
          % (stat["이동"], stat["변화없음"], stat["low건너뜀"], stat["거부"], stat["없음"]))
    dest = collections.Counter(p[3] for p in plan)
    print("\n목적지별:", dict(dest.most_common()))
    print()
    for fol, fn, cur, view, conf, why in plan:
        print("%-24s %-16s %-11s -> %-11s [%s] %s" % (fol[:22], fn, cur, view, conf, why[:56]))
    if apply_:
        for fol, fn, cur, view, conf, why in plan:
            s = os.path.join(REF, fol, cur, fn); d = os.path.join(REF, fol, view, fn)
            os.makedirs(os.path.dirname(d), exist_ok=True)
            if os.path.exists(d): print("  건너뜀(중복):", d); continue
            shutil.move(s, d)
        # 빈 폴더 정리
        for fol in {p[0] for p in plan}:
            for sub in os.listdir(os.path.join(REF, fol)):
                sd = os.path.join(REF, fol, sub)
                if os.path.isdir(sd) and not os.listdir(sd): os.rmdir(sd)
        print("\n%d장 이동 완료." % len(plan))
    else:
        print("\n(dry-run) 실제 이동하려면 --apply")

if __name__ == "__main__":
    main()

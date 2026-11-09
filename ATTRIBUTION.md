# 출처 표시

## 실측 도면

**С.П. Бартенев, 『Московский Кремль в старину и теперь』 книга 1**
М.: Издание Министерства Императорского Двора, 1912. 퍼블릭 도메인.
스캔 제공: ЦУНБ им. Н.А. Некрасова 전자열람실 — <https://electro.nekrasovka.ru/books/705>
페이지 이미지 API `/api/books/705/pages/{N}/img/original`, 약 2900×4000 (300 dpi).
파일명 `pNNN.jpg` 의 NNN 은 **원본 PDF 페이지 번호**다.

**『Русское зодчество. Выпуск 2. Памятники архитектуры XV—XVI веков: Чертежи и фотографии』**
М.: Госстройиздат, 1953. 전 94쪽, 도판 34장(Табл.1–34).
스캔 제공: ЦУНБ им. Н.А. Некрасова 전자열람실.
수록한 8장은 Табл. 1 · 4 · 5 · 8 · 12 · 13 · 14 · 15 다.
파일명 `tabNN_pNNN.jpg` = 도판번호 + 원본 PDF 페이지.
**저작권 상태 미확정** — `README.md` 의 「라이선스」 참조.

## 지리 데이터

**© OpenStreetMap 기여자** — <https://www.openstreetmap.org/copyright>
ODbL 1.0 으로 배포된다. `plans/` 의 SVG 와
`docs/MEASUREMENTS.md` 의 위치·평면 치수·yaw 는 아래 OSM 객체에서 유도했다.

| 객체 | 용도 |
|---|---|
| `relation/1360641` | 크렘린 castle 폴리곤 (1,204 점 · 둘레 2,570.6 m) — **앵커의 기준** |
| `relation/17256358` | 성벽 멀티폴리곤 (멤버 1,043) |
| 탑·성당 relation 각각 | `docs/MEASUREMENTS.md` 표의 `rel` 열에 ID 가 있다 |

> 성벽을 way 4개로 보면 안 된다. 그 4개를 합쳐도 2.4 m 다.
> 크렘린의 탑과 성당은 대부분 **way 가 아니라 relation** 이라,
> way 만 파싱하면 탑 20기가 전부 누락된다.

## 사진

**Wikimedia Commons** 큐레이션 카테고리에서 받은 **542장**(파생본 2건 포함 544행)이다.
파일별 원본 제목과 라이선스는 `docs/SOURCES.txt` 에 있고, 경로는 사진 팩을
레포 루트에 풀었을 때와 1:1 로 대응한다.

```
01_우스펜스키_대성당/1_Top/01.jpg<TAB>File:2019-07-26-Moscow-3116-Assumption Cathedral.jpg<TAB>[CC BY-SA 4.0]
```

`SOURCES.txt` 끝에는 **미수집 후보 180건**이 주석으로 남아 있다. 2차 수집
목록만 만들고 실제로 받지 않은 것이라 로컬 파일이 없다. 사진을 보충할 때
쓰면 된다.

배포되는 544행의 라이선스 분포 — CC BY-SA 4.0 (201) · CC BY-SA 3.0 (109) · CC BY-SA 2.0 (47) · CC BY 4.0 (45) ·
CC0 (44) · CC BY 2.0 (43) · CC BY 3.0 (31) · Public domain (21) ·
CC BY-SA 2.5 (2) · CC BY-SA 3.0 de (1).

> ⚠ **`SOURCES.txt` 에는 저작자명이 없다.** 수집 당시 파일 제목과
> 라이선스만 기록했다. CC BY / CC BY-SA 는 저작자 표시가 의무이므로,
> 사진을 재배포하거나 텍스처로 구워 배포할 때는
> `https://commons.wikimedia.org/wiki/<File: 제목>` 에서 저작자를
> 확인해 표시해야 한다. 파일 제목이 그 링크 역할을 한다.

**카메라 좌표** — `docs/camera_coords.tsv` 는 Commons API 의
`prop=coordinates&coprop=type` 에서 `type="camera"` 인 항목만 뽑은 것이다.
전체 사진의 27~50% 만 이 좌표를 갖고 있어서, 나머지는 눈으로 분류했다.
EXIF 는 쓸 수 없었다(`GPSImgDirection` 이 수백 장 중 2장에만 있었다).

## 이 레포의 창작물

`plans/` · `docs/MEASUREMENTS.md` · `docs/VIEWS.md` · `docs/PROMPTS.md` ·
`docs/HUNYUAN_PROMPT_RESEARCH.md` · `tools/` · 각 `INDEX.md` 는
**CC BY 4.0** 이다 (`LICENSE-ASSETS`).

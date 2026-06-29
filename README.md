# 간다GO — 서울 출장마사지·홈타이 생활권 안내 사이트

서울 전역 방문 관리(출장마사지·홈타이)를 **생활권 편집지도** 구조로 안내하는 정적 사이트입니다.
상호: **간다GO** · 예약전화: **0508-202-4719**

## 구조

- 정적 HTML 사이트 — 어느 호스팅(GitHub Pages, Netlify, 일반 웹서버)에서든 그대로 서빙 가능
- `build.py` + `content/` 패키지에서 페이지를 생성하는 빌드 방식
- 생성물(각 디렉터리의 `index.html`, `sitemap.xml`, `robots.txt`)도 저장소에 포함
- 루트(`/`)는 서울 메인, 기존 노원 콘텐츠는 `/nowon-gu/` 이하로 유지

```
build.py              # 빌드 (레이아웃·글자수 검사·공통 스키마·sitemap/이미지 sitemap)
content/
  site.py             # 상호·전화·BASE_URL·텔레그램·권위 링크·서울 메뉴(NAV)
  seoul/              # 서울 생활권 편집지도
    data.py           # 권역9·구25·생활권25·역세권37·행정동118·이용7·확인8·정책5 데이터
    render.py         # 본문 작성기(Who/How/Why·체크리스트·개인정보·불법서비스·FAQ·작성자)
    pages.py          # 권역·구·생활권·역세권·행정동·이용·확인·정책·문의 페이지 생성
    main.py           # 서울 메인(허브)
  areas.py            # (노원) 노원구 허브 + 대표 동 5개
  stations.py         # (노원) 역 13개
  themes.py / info.py / magazine.py / about.py   # (노원) 보조 콘텐츠
assets/               # CSS, 모바일 내비 JS, 대표 이미지(cover-*.png)
```

## URL 규칙 (루트 기준, `/seoul/` 미사용)

| 유형 | URL |
|---|---|
| 서울 메인 | `/` |
| 권역 | `/area/<slug>/` |
| 구 | `/<gu>/` (예: `/gangnam-gu/`) |
| 생활권 | `/life/<slug>/` |
| 역세권 | `/station/<slug>/` |
| 대표 행정동 | `/<gu>/<dong>/` |
| 이용 장소 | `/use/<slug>/` |
| 예약 전 확인 | `/check/<slug>/` |
| 운영 기준 | `/policy/<slug>/` · 문의 `/contact/` |

## 빌드

```bash
python3 build.py
```

빌드 시 페이지별 본문 글자수와 색인 여부 리포트가 출력됩니다.

## SEO 운영 원칙 (빌드/데이터에 반영)

- 본문 **2,000자 미만 페이지는 자동 `noindex`** 처리되고 sitemap에서 제외 (행정동 단계적 색인)
- 색인 페이지는 **2,000~2,500자 고유 본문** — 지역명만 바꾼 중복 본문 금지
- 출구별/노선별 역 페이지 없음, 번호동은 대표동으로 통합
- 모든 페이지: `WebPage`·`BreadcrumbList`·`Organization` + (해당 시) `FAQPage` JSON-LD
- 모든 주요 페이지: **Who/How/Why**, **작성자·검수자(E-E-A-T)**, **예약 전 체크리스트**,
  **개인정보 처리 기준**, **불법·선정적 서비스 불가 안내**
- 매장 없는 방문형이므로 `LocalBusiness`/`Review`/`AggregateRating` 미사용, 허위 후기·가짜 평점 없음
- 대표 이미지 + `og:image`/schema image + 이미지 sitemap, alt 는 키워드 반복 없이 자연스럽게
- 상위노출 보장 표현 사용 안 함

## 콘텐츠 추가 방법

- 구/생활권/역세권/행정동: `content/seoul/data.py` 의 해당 표에 항목 추가 → 빌드 시 페이지·메뉴·스키마 자동 생성
- 행정동 슬러그: `ROMAJA` 에 한글동명→슬러그 매핑 추가, 고유 설명은 `DONG_NOTES`
- 대표 이미지 디자인 변경: 카테고리별 `assets/cover-*.png` 교체

## 배포 전 해야 할 일

1. `content/site.py`의 `BASE_URL`을 실제 도메인으로 변경
2. `python3 build.py` 재실행 (canonical·sitemap·robots.txt에 반영됨)
3. Google Search Console에 `sitemap.xml` 제출

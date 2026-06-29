# 사이트 공통 설정
# 배포 도메인 확정 후 BASE_URL 을 실제 도메인으로 변경하세요.
BASE_URL = "https://www.seoul-ganda.example.com"

BRAND = "간다GO"             # 사이트 브랜드 = 상호
COMPANY = "간다GO"            # 상호(사업자명)
SERVICE_AREA = "서울특별시 전역"
PHONE = "0508-202-4719"
PHONE_DISPLAY = "0508-202-4719"

# 외부 문의 채널 — 텔레그램
TELEGRAM_MAKE = "https://t.me/googleseolab"      # 웹사이트 제작문의
TELEGRAM_PARTNER = "https://t.me/googleseolab"   # 제휴문의

# 권위 있는 외부 참고 링크 — 내부링크 보강 및 신뢰 신호용(E-E-A-T)
AUTHORITY_LINKS = [
    ("서울특별시 공식 홈페이지", "https://www.seoul.go.kr/"),
    ("서울교통공사 노선 안내", "https://www.seoulmetro.co.kr/"),
    ("국가법령정보센터", "https://www.law.go.kr/"),
]

# 상단 메뉴 — 서울 생활권 편집지도 구조.
# 메뉴명에는 "출장마사지"를 반복하지 않고 지역·생활권·장소명만 노출한다.
from .seoul.data import AREAS, DISTRICTS, LIFE_AREAS, STATIONS, USE_CASES, CHECKS, POLICIES

# 권역 순서대로 25개 구(노원 포함)
_GU_ORDER = []
for _a in AREAS:
    for _s in _a["districts"]:
        if _s not in _GU_ORDER:
            _GU_ORDER.append(_s)

_GU_NAME = {**{k: v["name"] for k, v in DISTRICTS.items()}, "nowon-gu": "노원구"}

_areas_sub = [("권역 전체", "/#areas")] + [(_a["name"], f"/area/{_a['slug']}/") for _a in AREAS]
_gu_sub = [(_GU_NAME[_s], f"/{_s}/") for _s in _GU_ORDER]
_life_sub = [(_l["name"], _l.get("link") or f"/life/{_l['slug']}/") for _l in LIFE_AREAS]
_station_sub = [(_s["name"], _s.get("link") or f"/station/{_s['slug']}/") for _s in STATIONS]
_use_sub = [(_u["name"], f"/use/{_u['slug']}/") for _u in USE_CASES]
_check_sub = [(_c["name"], f"/check/{_c['slug']}/") for _c in CHECKS]
_policy_sub = [(_p["name"], f"/policy/{_p['slug']}/") for _p in POLICIES] + [("문의하기", "/contact/")]

NAV = [
    ("서울 홈", "/", []),
    ("권역 안내", "/#areas", _areas_sub),
    ("구별 안내", "/#districts", _gu_sub),
    ("생활권", "/#life", _life_sub),
    ("지하철역", "/#life", _station_sub),
    ("이용 장소", "/#use", _use_sub),
    ("예약 전 확인", "/#check", _check_sub),
    ("운영 기준", "/#policy", _policy_sub),
    ("노원구", "/nowon-gu/", []),
]

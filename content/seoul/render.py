# -*- coding: utf-8 -*-
"""서울 페이지 본문 작성기.

data.py 의 구조화된 사실을 엮어 페이지마다 다른 2,000~2,500자 본문을 만든다.
지역명만 바꾼 중복 본문을 피하기 위해 각 엔티티의 고유 note·생활권·역·행정동·
이용 장소 구성을 본문 전반에 녹인다. 공통 컴플라이언스 블록(개인정보·불법 서비스
불가·Who/How/Why·작성자)은 모든 주요 페이지 하단에 둔다.
"""
import html as _html
import json

from .data import (AUTHOR, CHECKS, DISTRICTS, LIFE_AREAS, NOWON_URL, POLICIES,
                   REVIEWER, ROMAJA, STATIONS, USE_CASES)

# ── URL 헬퍼 ─────────────────────────────────────────────
def gu_url(slug):
    return f"/{slug}/"

def gu_name(slug):
    if slug == "nowon-gu":
        return "노원구"
    return DISTRICTS[slug]["name"]

def area_url(slug):
    return f"/area/{slug}/"

def life_url(slug):
    return f"/life/{slug}/"

def station_url(slug):
    return f"/station/{slug}/"

def use_url(slug):
    return f"/use/{slug}/"

def check_url(slug):
    return f"/check/{slug}/"

def policy_url(slug):
    return f"/policy/{slug}/"

def dong_url(gu_slug, dong_name):
    return f"/{gu_slug}/{ROMAJA[dong_name]}/"

# 이름 → 슬러그 역참조
_LIFE_BY_NAME = {l["name"]: l for l in LIFE_AREAS}
_STATION_BY_NAME = {s["name"]: s for s in STATIONS}


def _life_link(name):
    l = _LIFE_BY_NAME.get(name)
    if l:
        return f'<a href="{life_url(l["slug"])}">{name}</a>'
    return name


def _station_link(name):
    s = _STATION_BY_NAME.get(name)
    if s:
        return f'<a href="{station_url(s["slug"])}">{name}</a>'
    return name


def _join_links(linker, names):
    return ", ".join(linker(n) for n in names)


# ── 이용 장소 기준 문구 (area_type 별로 다르게) ──────────
_PLACE_TEXT = {
    "business": "업무지구 비중이 높아 평일 저녁과 늦은 시간 오피스텔·업무용 빌딩 방문 문의가 많습니다. 업무용 건물은 야간 출입이 제한되는 경우가 있어 공동현관과 엘리베이터 출입 방식, 방문 가능 시간대를 미리 확인해 주세요. 자택 방문은 정확한 도로명 주소와 조용한 공간 확보가, 호텔·숙소 방문은 객실 외부인 출입 정책 확인이 우선입니다.",
    "residential": "주거 생활권이 넓어 자택과 대단지 아파트 방문 비중이 높습니다. 공동현관 비밀번호와 동·호수, 엘리베이터 동선을 미리 확인하면 방문이 원활합니다. 오피스텔이나 숙소를 이용하실 때는 관리 규정과 객실 출입 가능 여부를 함께 확인해 주세요. 차량 이동이 필요한 외곽 위치는 예약 전 이동 기준을 안내받는 것이 좋습니다.",
    "hotel-area": "호텔과 숙소가 밀집해 객실 방문 문의가 많습니다. 숙소마다 외부인 객실 출입 정책이 달라 예약 전 프런트 경유 여부와 객실 출입 가능 여부를 반드시 확인해야 합니다. 자택·오피스텔 방문은 공동현관 출입 방식과 정확한 호수를, 게스트하우스·공유숙소는 공용 공간 여부를 확인해 주세요.",
    "downtown": "도심 업무지구와 상권, 호텔이 함께 있어 자택·오피스텔·숙소 방문이 고르게 들어옵니다. 도심 빌딩과 호텔은 출입 절차가 까다로운 편이라 건물 출입 방식과 방문 가능 시간대를 미리 확인하는 것이 좋습니다. 자택 방문은 정확한 도로명 주소와 동·호수 확인이 기본입니다.",
    "university": "대학가 원룸·오피스텔과 1인 가구 주거가 많아 늦은 시간 방문 문의가 잦습니다. 원룸 건물은 공동현관 출입 방식이 제각각이라 비밀번호나 출입 방법을 미리 확인해 주세요. 자택 방문은 정확한 호수와 조용한 공간 확보가, 숙소 방문은 객실 출입 가능 여부 확인이 중요합니다.",
    "mixed": "주거지와 상권, 업무·숙박이 함께 있어 자택·오피스텔·호텔 방문 문의가 고르게 들어옵니다. 위치에 따라 확인할 내용이 달라지므로, 자택은 도로명 주소와 공동현관 출입 방식, 오피스텔은 관리 규정, 호텔·숙소는 객실 출입 가능 여부를 각각 확인해 주세요.",
}


# ── area_type 별 방문 환경 특징 (엔티티명 결합) ──────────
_CHAR_TEXT = {
    "business": "은 업무지구 비중이 높아 평일 저녁과 야간에 오피스텔·업무용 빌딩 방문 문의가 몰립니다. 업무용 건물은 야간에 출입이 제한되거나 안내 데스크를 거쳐야 하는 경우가 있어, 방문 가능 시간대와 엘리베이터 출입 방식을 예약 전에 확인해 두면 도착 후 대기 없이 진행됩니다. 주말에는 인근 주거지·숙소 수요로 흐름이 바뀝니다.",
    "residential": "은 대단지 아파트와 빌라, 주거용 오피스텔이 넓게 자리한 주거 생활권입니다. 가정 방문이 많아 공동현관 비밀번호, 동·호수, 엘리베이터 동선을 미리 정리해 두면 방문이 매끄럽습니다. 낮 시간대 가족 단위 문의와 저녁 시간대 1인 가구 문의가 함께 들어오는 편이라 시간대별 예약 여유를 두는 것이 좋습니다.",
    "hotel-area": "은 호텔·게스트하우스·공유숙소가 밀집해 객실 방문 문의가 많은 지역입니다. 숙소마다 외부인 객실 출입 정책이 달라, 프런트 경유 여부와 객실 출입 가능 여부를 예약 전에 확인하는 것이 가장 중요합니다. 늦은 시간 문의가 잦은 만큼 야간 출입 제한과 연락 가능 여부도 함께 확인해 두면 좋습니다.",
    "downtown": "은 도심 업무지구와 상권, 호텔이 한곳에 모여 자택·오피스텔·숙소 방문이 고르게 들어옵니다. 도심 빌딩과 호텔은 출입 절차가 까다로운 편이라, 건물 출입 방식과 방문 가능 시간대를 미리 확인하면 도착 후 지체 없이 진행됩니다. 평일 업무 수요와 주말 관광·숙박 수요가 번갈아 나타납니다.",
    "university": "은 대학가 원룸·오피스텔과 1인 가구 주거가 밀집해 늦은 시간 방문 문의가 잦습니다. 원룸 건물은 공동현관 출입 방식이 제각각이라 비밀번호나 출입 방법을 미리 확인해 두는 편이 좋습니다. 학기 중과 방학, 평일과 주말에 따라 생활 리듬과 예약 흐름이 눈에 띄게 달라지는 지역입니다.",
    "mixed": "은 주거지와 상권, 업무·숙박 시설이 한 생활권 안에 섞여 있어 자택·오피스텔·호텔 방문 문의가 고르게 들어옵니다. 위치에 따라 확인할 내용이 달라지므로, 자신이 머무는 곳이 어떤 유형의 건물인지 먼저 확인하면 예약 전 준비가 분명해집니다. 평일과 주말의 수요 흐름도 위치마다 다릅니다.",
}


def character_block(name, area_type):
    return (f'<section><h2>{name} 방문 환경 특징</h2>'
            f'<p>{name}{_CHAR_TEXT.get(area_type, _CHAR_TEXT["mixed"])}</p></section>')


# ── 공통 블록 ────────────────────────────────────────────
def checklist_block(area_type="mixed"):
    extra = {
        "business": "<li>업무용 빌딩의 야간 출입 가능 시간대를 확인했나요?</li>",
        "residential": "<li>대단지 아파트 동·호수와 공동현관 비밀번호를 확인했나요?</li>",
        "hotel-area": "<li>호텔·숙소의 외부인 객실 출입 정책을 확인했나요?</li>",
        "downtown": "<li>도심 빌딩·호텔의 출입 절차와 방문 시간을 확인했나요?</li>",
        "university": "<li>원룸·오피스텔 공동현관 출입 방식을 확인했나요?</li>",
        "mixed": "<li>방문 장소가 자택·오피스텔·숙소 중 어디인지 확인했나요?</li>",
    }.get(area_type, "")
    return f"""<section>
<h2>예약 전 체크리스트</h2>
<ul class="checklist">
<li>방문 주소를 도로명 기준으로 정확히 확인했나요?</li>
<li>공동현관 또는 건물 출입 방식이 있나요?</li>
{extra}
<li>호텔·오피스텔 이용 시 관리 규정을 확인했나요?</li>
<li>주차나 차량 이동이 필요한 위치인가요?</li>
<li>예약 가능 시간대를 확인했나요?</li>
<li><a href="{check_url('privacy')}">개인정보 처리 기준</a>을 확인했나요?</li>
<li><a href="{check_url('service-policy')}">불법·선정적 서비스 불가 안내</a>를 확인했나요?</li>
</ul>
</section>"""


def privacy_block():
    return f"""<section>
<h2>개인정보 처리 기준</h2>
<p>예약 정보는 예약 확인과 연락에 필요한 최소 범위만 사용하며, 그 외의 목적으로는 사용하지 않습니다. 상담과 예약이 끝난 뒤에는 보관을 최소화하고, 제3자에게 제공하지 않습니다. 자세한 처리 기준은 <a href="{policy_url('privacy')}">개인정보 처리방침</a>과 <a href="{check_url('privacy')}">예약 전 개인정보 처리 기준</a>에서 확인하실 수 있습니다.</p>
</section>"""


def illegal_block():
    return f"""<section>
<h2>불법·선정적 서비스 불가 안내</h2>
<p>이 사이트는 불법이거나 선정적인 서비스를 제공하거나 안내하지 않습니다. 건전한 방문 관리만 안내하며, 무리하거나 불법적인 요청에는 어떤 경우에도 응하지 않습니다. 관련 기준은 <a href="{policy_url('no-illegal')}">불법·선정적 서비스 불가 안내</a>에서 확인하실 수 있습니다.</p>
</section>"""


def who_how_why():
    return """<section>
<h2>Who, How, Why</h2>
<p><strong>Who.</strong> 이 페이지는 서울 지역 방문형 관리 서비스 안내 콘텐츠 담당자가 작성하고 운영 책임자가 검수합니다.</p>
<p><strong>How.</strong> 서울시 행정구역, 주요 생활권, 지하철역, 이용 장소별 예약 전 확인사항을 기준으로 구성했습니다.</p>
<p><strong>Why.</strong> 서울에서 방문형 서비스를 찾는 사용자가 자신의 지역과 이용 장소를 안전하게 확인할 수 있도록 돕기 위해 작성했습니다.</p>
</section>"""


def byline_block():
    return f"""<section class="byline">
<h2>작성·검수 정보</h2>
<p><strong>작성자</strong> {AUTHOR} · <strong>검수자</strong> {REVIEWER}</p>
<p>이 콘텐츠는 서울 행정구역, 생활권, 주요 지하철역, 이용 장소별 예약 전 확인사항을 기준으로 작성하며, 행정동 변경·생활권 변화·지하철역 정보 변화와 사용자 문의 흐름, 콘텐츠 품질 점검 결과를 반영해 수정합니다. 자세한 기준은 <a href="{policy_url('authors')}">작성자·검수자 안내</a>에서 확인할 수 있습니다.</p>
</section>"""


def faq_block(faqs):
    rows = "".join(
        f'<div class="faq-item"><h3>{q}</h3><p>{a}</p></div>' for q, a in faqs
    )
    return f'<section id="faq"><h2>자주 묻는 질문</h2>{rows}</section>'


def faq_jsonld(faqs):
    data = {
        "@context": "https://schema.org",
        "@type": "FAQPage",
        "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}}
            for q, a in faqs
        ],
    }
    return ('<script type="application/ld+json">\n'
            + json.dumps(data, ensure_ascii=False) + "\n</script>\n")


# 지역 공통 FAQ (지역명 삽입 + 1개 지역화)
def region_faqs(region, local_q=None, local_a=None):
    base = [
        (f"{region}도 방문이 가능한가요?",
         "실제 방문 주소와 가까운 생활권, 예약 가능 시간, 이동 기준을 확인한 뒤 안내합니다. 정확한 가능 여부는 예약 시 위치를 기준으로 확인합니다."),
        ("호텔이나 숙소에서도 이용할 수 있나요?",
         "숙소마다 외부인 객실 출입 정책이 다르므로 예약 전 프런트 경유 여부와 객실 출입 가능 여부를 먼저 확인해야 합니다."),
        ("오피스텔은 어떤 점을 확인해야 하나요?",
         "공동현관, 엘리베이터 출입 카드, 관리 규정, 방문 가능 시간대를 미리 확인해 주세요."),
        ("불법·선정적 서비스도 가능한가요?",
         "불법·선정적 서비스는 제공하거나 안내하지 않습니다. 건전한 방문 관리만 안내합니다."),
    ]
    if local_q and local_a:
        base.insert(1, (local_q, local_a))
    return base


def related_block(title, links):
    """links: [(label, href), ...]"""
    items = "".join(f'<li><a href="{href}">{label}</a></li>' for label, href in links)
    return f'<section><h2>{title}</h2><ul class="card-grid">{items}</ul></section>'

# -*- coding: utf-8 -*-
"""서울 출장마사지 메인 페이지 — 생활권 편집지도 허브."""
from ..site import PHONE, PHONE_DISPLAY
from . import render as R
from .data import AREAS, DISTRICTS, LIFE_AREAS, USE_CASES

# 25개 구(노원 포함) — 권역 순서대로
_GU_ORDER = []
for _a in AREAS:
    for _s in _a["districts"]:
        if _s not in _GU_ORDER:
            _GU_ORDER.append(_s)


def _area_cards():
    out = []
    for a in AREAS:
        gus = "·".join(R.gu_name(s) for s in a["districts"])
        out.append(
            f'<li><a href="{R.area_url(a["slug"])}"><strong>{a["name"]}</strong>'
            f'<span>{gus}</span></a></li>'
        )
    return "".join(out)


def _gu_cards():
    return "".join(
        f'<li><a href="{R.gu_url(s)}">{R.gu_name(s)}</a></li>' for s in _GU_ORDER
    )


def _life_cards():
    out = []
    for l in LIFE_AREAS:
        href = l.get("link") or R.life_url(l["slug"])
        out.append(f'<li><a href="{href}">{l["name"]}</a></li>')
    return "".join(out)


def _use_cards():
    return "".join(
        f'<li><a href="{R.use_url(u["slug"])}">{u["name"]}</a></li>' for u in USE_CASES
    )


_HERO = f"""<section class="hero">
  <div class="hero-inner">
    <p class="hero-badge">서울 생활권 편집지도 · 25개 구 안내</p>
    <h1>서울 출장마사지<br>생활권별 방문 가능 지역 안내</h1>
    <p class="hero-lead">강남, 잠실, 홍대, 여의도, 성수, 용산, 목동, 마곡 등 서울 주요 생활권과<br>자택·호텔·오피스텔 이용 전 확인사항을 안내합니다.</p>
    <div class="hero-actions">
      <a class="hero-btn primary" href="tel:{PHONE}">📞 {PHONE_DISPLAY}</a>
      <a class="hero-btn" href="#areas">권역 안내 보기</a>
    </div>
    <ul class="hero-stats">
      <li><strong>9개</strong><span>생활권 권역</span></li>
      <li><strong>25개</strong><span>자치구 안내</span></li>
      <li><strong>20+</strong><span>핵심 생활권</span></li>
      <li><strong>37개</strong><span>역세권 안내</span></li>
    </ul>
  </div>
</section>
"""

_BODY = f"""
<section id="intro">
<h2>서울 출장마사지는 구 이름만으로 판단하기 어렵습니다</h2>
<p>서울은 25개 구와 수백 개 행정동이 촘촘하게 연결된 도시입니다. 같은 구 안에서도 생활권 성격이 다르고, 같은 역세권이라도 자택·호텔·오피스텔·업무지구에 따라 이용 전 확인사항이 달라집니다. 예를 들어 강남구는 강남역·역삼, 삼성·선릉, 청담·압구정처럼 업무지구와 오피스텔이 많은 지역이 있고, 송파구는 잠실, 문정, 가락처럼 주거지와 상권이 함께 있는 생활권이 있습니다. 이 사이트는 서울 지역을 구, 생활권, 지하철역, 이용 장소 기준으로 나누어, 자신의 위치와 이용 장소를 안전하게 확인할 수 있도록 안내합니다.</p>
</section>

<section id="areas">
<h2>서울 권역별로 빠르게 찾기</h2>
<p>서울을 생활권 단위로 묶은 아홉 개 권역입니다. 각 권역 페이지에서 포함 구와 대표 생활권, 가까운 역, 이용 장소 기준을 확인할 수 있습니다.</p>
<ul class="card-grid area-cards">{_area_cards()}</ul>
</section>

<section id="districts">
<h2>서울 25개 구 안내</h2>
<p>서울 25개 자치구를 모두 안내합니다. 각 구 페이지에서 대표 생활권 2~4곳, 가까운 역, 대표 행정동, 이용 장소별 예약 전 확인사항을 동마다 다른 내용으로 설명합니다.</p>
<ul class="card-grid">{_gu_cards()}</ul>
</section>

<section id="life">
<h2>서울 주요 생활권 안내</h2>
<p>업무지구, 숙소·상권, 주거, 대학가, 도심 등 성격이 다른 핵심 생활권입니다. 행정구역만으로 드러나지 않는 생활 리듬을 생활권 단위로 확인할 수 있습니다.</p>
<ul class="card-grid">{_life_cards()}</ul>
</section>

<section id="use">
<h2>이용 장소에 따라 확인할 내용이 다릅니다</h2>
<p>같은 지역이라도 자택, 호텔·숙소, 오피스텔, 업무지구, 역세권에 따라 출입 방식과 확인할 내용이 달라집니다. 이용 장소별 안내에서 장소에 맞는 기준을 확인하세요.</p>
<ul class="card-grid">{_use_cards()}</ul>
</section>

<section id="check">
<h2>예약 전 확인해야 할 내용</h2>
<ul class="checklist">
<li>방문 주소를 도로명 기준으로 정확히 확인했나요?</li>
<li>공동현관 또는 건물 출입 방식이 있나요?</li>
<li>호텔·숙소 이용 가능 여부를 확인했나요?</li>
<li>오피스텔 관리 규정이 있나요?</li>
<li>주차나 차량 이동이 필요한 위치인가요?</li>
<li>예약 가능 시간대를 확인했나요?</li>
<li><a href="{R.check_url('privacy')}">개인정보 처리 기준</a>을 확인했나요?</li>
<li><a href="{R.check_url('service-policy')}">불법·선정적 서비스 불가 안내</a>를 확인했나요?</li>
</ul>
</section>

<section id="policy">
<h2>서울 지역 페이지 운영 기준</h2>
<p>이 사이트는 불법·선정적 서비스를 안내하지 않습니다. 허위 후기, 가짜 평점, 과장된 가격 문구를 사용하지 않으며, 실제 오프라인 매장이 없는 방문형 서비스이므로 매장 기반 정보도 사용하지 않습니다. 개인정보는 예약 확인과 연락에 필요한 최소 범위만 사용합니다. 모든 지역 페이지는 지역명만 바꾸지 않고 생활권, 가까운 역, 이용 장소, 예약 전 확인사항을 다르게 구성합니다. 운영 원칙은 <a href="{R.policy_url('service-standard')}">서비스 이용 기준</a>·<a href="{R.policy_url('no-illegal')}">불법·선정적 서비스 불가 안내</a>·<a href="{R.policy_url('content-standard')}">콘텐츠 작성 기준</a>에서 확인할 수 있습니다.</p>
</section>

{R.faq_block(R.region_faqs('서울 전역', '강남·잠실·홍대 같은 주요 지역도 가능한가요?', '주요 생활권과 역세권은 각 구·생활권·역세권 페이지에서 안내합니다. 정확한 가능 여부는 예약 시 도로명 주소를 기준으로 확인합니다.'))}
{R.who_how_why()}
{R.byline_block()}
<section id="contact" class="cta">
<h2>예약문의</h2>
<p>방문 위치(도로명 주소)와 희망 시간을 알려주시면 가능 여부를 바로 확인해 드립니다.</p>
<a class="cta-phone" href="tel:{PHONE}">{PHONE_DISPLAY}</a>
</section>
"""

PAGE = {
    "path": "",
    "title": "서울 출장마사지 | 강남·잠실·홍대·여의도·성수 홈타이 지역 안내",
    "desc": "서울 출장마사지·홈타이 예약 전 강남, 잠실, 홍대, 여의도, 성수 등 주요 생활권과 자택·호텔·오피스텔 이용 기준을 안내합니다.",
    "h1": "서울 출장마사지 · 생활권별 방문 가능 지역 안내",
    "body": _BODY,
    "extra_head": R.faq_jsonld(R.region_faqs('서울 전역', '강남·잠실·홍대 같은 주요 지역도 가능한가요?', '주요 생활권과 역세권은 각 구·생활권·역세권 페이지에서 안내합니다. 정확한 가능 여부는 예약 시 도로명 주소를 기준으로 확인합니다.')),
    "breadcrumb": [],
    "hero": _HERO,
    "image": "/assets/cover-main.png",
    "image_alt": "서울 생활권 방문 안내 이미지",
}

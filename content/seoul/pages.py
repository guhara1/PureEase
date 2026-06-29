# -*- coding: utf-8 -*-
"""서울 페이지 생성 — 메인·권역·구·생활권·역세권·행정동·이용 장소·예약 전 확인·운영 기준.

각 페이지는 data.py 의 고유 사실을 엮어 2,000~2,500자 본문으로 조립한다.
2,000자 미만 행정동 페이지는 build.py 가 자동으로 noindex 처리한다(단계적 색인).
"""
from . import render as R
from .data import (AREAS, CHECKS, DISTRICTS, DONG_NOTES, LIFE_AREAS, NOWON_URL,
                   POLICIES, STATIONS, USE_CASES)

_AREA_BY_SLUG = {a["slug"]: a for a in AREAS}


def _clip(s, n=80):
    return s if len(s) <= n else s[: n - 1].rstrip() + "…"


def _cta():
    from ..site import PHONE, PHONE_DISPLAY
    return (f'<section class="cta"><h2>예약문의</h2>'
            f'<p>방문 위치(도로명 주소)와 희망 시간을 알려주시면 가능 여부를 바로 확인해 드립니다.</p>'
            f'<a class="cta-phone" href="tel:{PHONE}">{PHONE_DISPLAY}</a></section>')


# ── 구 상세 페이지 ───────────────────────────────────────
def _district_page(slug, d):
    name = d["name"]
    area = _AREA_BY_SLUG[d["area"]]
    area_name = area["name"]
    life_links = R._join_links(R._life_link, d["life_areas"])
    station_links = R._join_links(R._station_link, d["stations"])
    nearby_links = ", ".join(
        f'<a href="{R.gu_url(s)}">{R.gu_name(s)}</a>' for s in d["nearby"]
    )
    dong_links = ", ".join(
        f'<a href="{R.dong_url(slug, dn)}">{dn}</a>' for dn in d["dongs"]
    )

    body = f"""
<p class="lead">{name}는 {area_name}에 속한 자치구입니다. {d['note']}</p>

<section>
<h2>{name} 지역 개요</h2>
<p>{name}는 {d['focus']} 생활권으로 이해하면 자신의 위치에 맞는 정보를 찾기 쉽습니다. 같은 {name} 안에서도 업무지구와 주거지, 숙소 인접 지역의 이용 기준이 달라 구 이름만으로 방문 환경을 판단하기는 어렵습니다. 이 페이지는 {name}를 생활권, 가까운 지하철역, 이용 장소 기준으로 나누어 예약 전에 확인할 내용을 정리했습니다. {area_name}의 전체 흐름은 <a href="{R.area_url(area['slug'])}">{area_name} 안내</a>에서 함께 볼 수 있습니다.</p>
</section>

<section>
<h2>대표 생활권</h2>
<p>{name}의 대표 생활권은 {life_links}입니다. 생활권마다 주거·업무·숙소 비중이 달라 방문 시간대와 출입 방식, 확인할 내용이 조금씩 다릅니다. 자신이 머무는 위치가 어느 생활권에 가까운지 먼저 확인하면, 예약 전에 무엇을 준비해야 하는지 분명해집니다.</p>
</section>

<section>
<h2>가까운 지하철역과 인접 지역</h2>
<p>{name}에서 가까운 주요 역은 {station_links}입니다. 역세권은 출구 번호가 아니라 실제 도로명 주소를 기준으로 안내하며, 환승역도 노선과 무관하게 위치로 확인합니다. 인접 자치구로는 {nearby_links}가 있어 생활권이 자연스럽게 이어집니다. {name}의 대표 행정동으로는 {dong_links} 등을 안내합니다.</p>
</section>

<section>
<h2>이용 장소별 안내</h2>
<p>{R._PLACE_TEXT[d['area_type']]}</p>
<p>이용 장소별 자세한 기준은 <a href="{R.use_url('home')}">자택</a>, <a href="{R.use_url('hotel')}">호텔·숙소</a>, <a href="{R.use_url('officetel')}">오피스텔</a>, <a href="{R.use_url('business-district')}">업무지구</a>, <a href="{R.use_url('station-area')}">역세권</a> 이용 안내에서 확인할 수 있습니다.</p>
</section>

{R.checklist_block(d['area_type'])}
{R.privacy_block()}
{R.illegal_block()}
{R.faq_block(R.region_faqs(name, '예약 가능 시간은 어떻게 확인하나요?', '위치와 요일·시간대에 따라 달라집니다. 저녁과 주말은 문의가 몰릴 수 있어 여유 있게 예약하시기를 권합니다.'))}
{R.who_how_why()}
{R.byline_block()}
{R.related_block(name + ' 관련 지역 보기', [(area_name + ' 안내', R.area_url(area['slug']))] + [(R.gu_name(s), R.gu_url(s)) for s in d['nearby']] + [(ln, R.life_url(R._LIFE_BY_NAME[ln]['slug'])) for ln in d['life_areas'] if ln in R._LIFE_BY_NAME])}
{_cta()}
"""
    desc = _clip(f"{name} 출장마사지·홈타이 안내입니다. {', '.join(d['life_areas'][:3])} 생활권과 가까운 역, 이용 장소별 예약 전 확인사항을 정리했습니다.")
    return {
        "path": f"{slug}/",
        "title": f"{name} 출장마사지·홈타이 | 생활권별 방문 예약 안내",
        "desc": desc,
        "h1": f"{name} 출장마사지 · 생활권별 예약 안내",
        "body": body,
        "extra_head": R.faq_jsonld(R.region_faqs(name, '예약 가능 시간은 어떻게 확인하나요?', '위치와 요일·시간대에 따라 달라집니다. 저녁과 주말은 문의가 몰릴 수 있어 여유 있게 예약하시기를 권합니다.')),
        "breadcrumb": [(area_name, R.area_url(area['slug'])), (name, "")],
    }


# ── 권역 페이지 ──────────────────────────────────────────
def _area_page(a):
    slug, name = a["slug"], a["name"]
    gu_links = "".join(
        f'<li><a href="{R.gu_url(s)}">{R.gu_name(s)}</a></li>' for s in a["districts"]
    )
    # 권역에 속한 구들의 대표 생활권/역 모으기
    life_all, st_all = [], []
    for s in a["districts"]:
        if s in DISTRICTS:
            life_all += DISTRICTS[s]["life_areas"][:2]
            st_all += DISTRICTS[s]["stations"][:2]
    life_links = R._join_links(R._life_link, list(dict.fromkeys(life_all))[:6])
    station_links = R._join_links(R._station_link, list(dict.fromkeys(st_all))[:6])

    body = f"""
<p class="lead">{a['headline']}. {a['note']}</p>

<section>
<h2>{name} 개요</h2>
<p>{name}은 서울을 생활권 단위로 나눴을 때 묶이는 권역입니다. {a['note']} 같은 권역이라도 구와 생활권마다 업무지구·주거지·숙소 비중이 달라, 방문 전에 확인할 내용이 조금씩 다릅니다. 이 페이지는 {name}에 속한 구와 대표 생활권, 가까운 역, 이용 장소 기준을 한눈에 볼 수 있도록 정리했습니다.</p>
</section>

<section>
<h2>포함 구</h2>
<ul class="card-grid">{gu_links}</ul>
<p>각 구 페이지에서 대표 생활권, 가까운 지하철역, 대표 행정동, 이용 장소별 예약 전 확인사항을 자세히 확인할 수 있습니다.</p>
</section>

<section>
<h2>대표 생활권과 지하철역</h2>
<p>{name}의 대표 생활권은 {life_links} 등이며, 가까운 주요 역으로는 {station_links} 등이 있습니다. 역세권은 출구가 아니라 실제 도로명 주소를 기준으로 안내하고, 환승역도 노선과 무관하게 위치로 확인합니다.</p>
</section>

<section>
<h2>이용 장소별 안내</h2>
<p>권역 안에서도 자택, 호텔·숙소, 오피스텔, 업무지구에 따라 확인할 내용이 다릅니다. <a href="{R.use_url('home')}">자택</a>·<a href="{R.use_url('hotel')}">호텔·숙소</a>·<a href="{R.use_url('officetel')}">오피스텔</a>·<a href="{R.use_url('business-district')}">업무지구</a> 이용 안내에서 장소별 기준을 확인하고, 예약 전에는 <a href="{R.check_url('address')}">방문 주소</a>와 <a href="{R.check_url('building-access')}">건물 출입 방식</a>을 점검해 주세요.</p>
</section>

{R.checklist_block()}
{R.privacy_block()}
{R.illegal_block()}
{R.faq_block(R.region_faqs(name))}
{R.who_how_why()}
{R.byline_block()}
{R.related_block(name + ' 관련 지역 보기', [(R.gu_name(s), R.gu_url(s)) for s in a['districts']])}
{_cta()}
"""
    desc = _clip(f"{name} 출장마사지 지역 안내입니다. {'·'.join(R.gu_name(s) for s in a['districts'][:3])} 생활권과 가까운 역, 이용 장소별 확인사항을 정리했습니다.")
    return {
        "path": f"area/{slug}/",
        "title": f"{name} 출장마사지 지역 안내 | 구·생활권·역세권",
        "desc": desc,
        "h1": f"{name} 출장마사지 지역 안내",
        "body": body,
        "extra_head": R.faq_jsonld(R.region_faqs(name)),
        "breadcrumb": [("권역 안내", "/#areas"), (name, "")],
    }


# ── 생활권 페이지 ────────────────────────────────────────
def _life_page(l):
    slug, name = l["slug"], l["name"]
    if l.get("link"):
        return None  # 노원·상계 등은 기존 노원 페이지로 연결만, 별도 생성 안 함
    gu_links = ", ".join(
        f'<a href="{R.gu_url(g)}">{g}</a>' if g in [v["name"] for v in []] else g
        for g in l["districts"]
    )
    # 구 이름 → 슬러그
    name2slug = {v["name"]: k for k, v in DISTRICTS.items()}
    gu_links = ", ".join(
        (f'<a href="{R.gu_url(name2slug[g])}">{g}</a>' if g in name2slug else g)
        for g in l["districts"]
    )
    station_links = R._join_links(R._station_link, l["stations"])

    body = f"""
<p class="lead">{name} 생활권 안내입니다. {l['note']}</p>

<section>
<h2>{name} 생활권 개요</h2>
<p>{name}은 {l['group']} 성격이 강한 생활권입니다. {l['note']} 행정구역만으로는 드러나지 않는 생활 리듬을 생활권 단위로 보면, 방문 전에 무엇을 준비해야 하는지 더 분명해집니다. 이 페이지는 {name}의 포함 지역과 가까운 역, 이용 장소 기준을 정리했습니다.</p>
</section>

<section>
<h2>포함 행정구역과 가까운 역</h2>
<p>{name}은 {gu_links} 일대를 포함하며, 가까운 주요 역은 {station_links}입니다. 역세권은 출구 번호가 아니라 도로명 주소를 기준으로 안내하고, 환승역도 노선과 무관하게 위치로 확인합니다.</p>
</section>

<section>
<h2>이용 장소별 안내</h2>
<p>{R._PLACE_TEXT[l['area_type']]}</p>
<p>장소별 기준은 <a href="{R.use_url('home')}">자택</a>·<a href="{R.use_url('hotel')}">호텔·숙소</a>·<a href="{R.use_url('officetel')}">오피스텔</a> 이용 안내에서, 예약 전 확인은 <a href="{R.check_url('address')}">방문 주소</a>·<a href="{R.check_url('building-access')}">건물 출입 방식</a>에서 확인할 수 있습니다.</p>
</section>

{R.character_block(name, l['area_type'])}
{R.checklist_block(l['area_type'])}
{R.privacy_block()}
{R.illegal_block()}
{R.faq_block(R.region_faqs(name))}
{R.who_how_why()}
{R.byline_block()}
{R.related_block(name + ' 관련 지역 보기', [(g, R.gu_url(name2slug[g])) for g in l['districts'] if g in name2slug] + [(st + ' 역세권', R.station_url(R._STATION_BY_NAME[st]['slug'])) for st in l['stations'] if st in R._STATION_BY_NAME] + [('자택 이용', R.use_url('home')), ('호텔·숙소 이용', R.use_url('hotel'))])}
{_cta()}
"""
    desc = _clip(f"{name} 출장마사지 생활권 안내입니다. 포함 지역과 가까운 역, 이용 장소별 예약 전 확인사항을 정리했습니다.")
    return {
        "path": f"life/{slug}/",
        "title": f"{name} 출장마사지 생활권 안내",
        "desc": desc,
        "h1": f"{name} 출장마사지 생활권 안내",
        "body": body,
        "extra_head": R.faq_jsonld(R.region_faqs(name)),
        "breadcrumb": [(name, "")],
    }


# ── 역세권 페이지 ────────────────────────────────────────
def _station_page(s):
    slug, name = s["slug"], s["name"]
    if s.get("link"):
        return None  # 노원역 등 기존 노원 사이트로 연결만
    name2slug = {v["name"]: k for k, v in DISTRICTS.items()}
    gu = s["district"]
    gu_link = f'<a href="{R.gu_url(name2slug[gu])}">{gu}</a>' if gu in name2slug else gu
    life_link = R._life_link(s["life"])

    body = f"""
<p class="lead">{name}({s['lines']}) 인근 방문 예약 안내입니다. {s['note']}</p>

<section>
<h2>{name} 역세권 개요</h2>
<p>{name}은 {gu_link}에 속한 역으로 {s['life']} 생활권과 가깝습니다. {s['note']} 역세권 안내는 특정 출구가 아니라 역 주변 생활권 전체를 기준으로 합니다. 정확한 방문 위치는 예약 시 도로명 주소로 확인합니다.</p>
</section>

<section>
<h2>출구별·노선별 페이지를 만들지 않는 이유</h2>
<p>{name} 1번출구, 2번출구처럼 출구별로 페이지를 나누거나, 환승역을 노선별로 쪼개면 같은 생활권을 두고 비슷한 내용이 반복됩니다. 이용자에게도 어느 페이지를 봐야 할지 혼란스럽습니다. 그래서 {name}은 하나의 역세권 페이지로 운영하고, 방문 가능 여부는 출구나 노선이 아니라 실제 도로명 주소와 예약 시간으로 판단합니다.</p>
</section>

<section>
<h2>가까운 생활권과 이용 장소</h2>
<p>{name} 인근 생활권으로는 {life_link}가 있습니다. 역세권 주변은 주거·오피스텔·숙소가 섞여 있어 위치에 따라 확인할 내용이 다릅니다. <a href="{R.use_url('station-area')}">역세권 이용</a>·<a href="{R.use_url('hotel')}">호텔·숙소</a>·<a href="{R.use_url('officetel')}">오피스텔</a> 이용 안내에서 장소별 기준을 확인하세요.</p>
</section>

{R.character_block(name + ' 주변', 'mixed')}
{R.checklist_block('mixed')}
{R.privacy_block()}
{R.illegal_block()}
{R.faq_block(R.region_faqs(name + ' 인근'))}
{R.who_how_why()}
{R.byline_block()}
{R.related_block(name + ' 관련 지역 보기', ([(gu, R.gu_url(name2slug[gu]))] if gu in name2slug else []) + ([(s['life'] + ' 생활권', R.life_url(R._LIFE_BY_NAME[s['life']]['slug']))] if s['life'] in R._LIFE_BY_NAME else []) + [('역세권 이용', R.use_url('station-area')), ('호텔·숙소 이용', R.use_url('hotel'))])}
{_cta()}
"""
    desc = _clip(f"{name} 출장마사지 역세권 안내입니다. 가까운 생활권과 이용 장소, 예약 전 확인사항을 정리했습니다.")
    return {
        "path": f"station/{slug}/",
        "title": f"{name} 출장마사지 | 역세권 예약 안내",
        "desc": desc,
        "h1": f"{name} 출장마사지 · 역세권 예약 안내",
        "body": body,
        "extra_head": R.faq_jsonld(R.region_faqs(name + ' 인근')),
        "breadcrumb": [(name, "")],
    }


# ── 대표 행정동 페이지 ───────────────────────────────────
def _dong_pages():
    pages = []
    name2slug = {v["name"]: k for k, v in DISTRICTS.items()}
    for gu_slug, d in DISTRICTS.items():
        gu = d["name"]
        life0 = d["life_areas"][0]
        st = d["stations"][:2]
        for dong in d["dongs"]:
            station_links = R._join_links(R._station_link, st)
            life_link = R._life_link(life0)
            other_dongs = ", ".join(
                f'<a href="{R.dong_url(gu_slug, x)}">{x}</a>' for x in d["dongs"] if x != dong
            )
            body = f"""
<p class="lead">{dong} 방문 예약 안내입니다. {DONG_NOTES.get(dong, gu + ' 생활권에 속한 동입니다.')}</p>

<section>
<h2>{dong} 위치와 상위 구</h2>
<p>{dong}은 {gu}에 속한 동으로, <a href="{R.gu_url(gu_slug)}">{gu}</a> 생활권의 일부입니다. {DONG_NOTES.get(dong, '')} {gu} 전체 흐름은 {d['note']} 이런 특성을 알면 {dong} 인근에서 방문 전에 무엇을 준비해야 하는지 정리하기 쉽습니다.</p>
</section>

<section>
<h2>가까운 생활권과 지하철역</h2>
<p>{dong}에서 가까운 생활권은 {life_link}이고, 가까운 주요 역은 {station_links}입니다. 정확한 방문 위치는 예약 시 도로명 주소와 동·호수로 확인합니다. {gu}의 다른 대표 행정동으로는 {other_dongs} 등이 있습니다.</p>
</section>

<section>
<h2>{dong} 방문 환경</h2>
<p>{DONG_NOTES.get(dong, '')} {dong}{R._CHAR_TEXT.get(d['area_type'], R._CHAR_TEXT['mixed'])}</p>
</section>

<section>
<h2>이용 장소별 안내</h2>
<p>{R._PLACE_TEXT[d['area_type']]}</p>
<p>장소별 기준은 <a href="{R.use_url('home')}">자택</a>·<a href="{R.use_url('officetel')}">오피스텔</a>·<a href="{R.use_url('hotel')}">호텔·숙소</a> 이용 안내에서 확인할 수 있습니다.</p>
</section>

{R.checklist_block(d['area_type'])}
{R.privacy_block()}
{R.illegal_block()}
{R.faq_block(R.region_faqs(dong))}
{R.who_how_why()}
{R.byline_block()}
{_cta()}
"""
            desc = _clip(f"{gu} {dong} 출장마사지·홈타이 안내입니다. 가까운 생활권과 역, 이용 장소별 예약 전 확인사항을 정리했습니다.")
            pages.append({
                "path": f"{gu_slug}/{R.slug_for(dong)}/",
                "title": f"{dong} 출장마사지 | {gu} 방문 예약 안내",
                "desc": desc,
                "h1": f"{dong} 출장마사지 · {gu} 방문 안내",
                "body": body,
                "extra_head": R.faq_jsonld(R.region_faqs(dong)),
                "breadcrumb": [(gu, R.gu_url(gu_slug)), (dong, "")],
                # 고유 설명(DONG_NOTES)이 있는 동만 색인. 나머지는 생성·링크만 하고
                # 중복 본문 위험을 피하기 위해 noindex(단계적 색인, 지시서 23항).
                "noindex": dong not in DONG_NOTES,
            })
    return pages


# ── 이용 장소 / 예약 전 확인 / 운영 기준 ─────────────────
def _points_body(item, kind):
    points = "".join(f"<li>{p}</li>" for p in item["points"]) if item.get("points") else ""
    extra_links = (f'<a href="{R.check_url("address")}">방문 주소</a>·'
                   f'<a href="{R.check_url("building-access")}">건물 출입 방식</a>·'
                   f'<a href="{R.check_url("time")}">예약 가능 시간</a>')
    return f"""
<p class="lead">{item['lead']}</p>

<section>
<h2>{item['name']} 안내</h2>
<p>{item['lead']} 서울은 구와 생활권마다 건물 형태와 출입 방식이 달라, 같은 항목이라도 위치에 따라 확인할 내용이 조금씩 달라집니다. 자신의 위치와 이용 장소를 먼저 확인하면 예약이 한결 원활해집니다.</p>
</section>

<section>
<h2>확인할 내용</h2>
<ul class="checklist">{points}</ul>
</section>

<section>
<h2>지역·생활권별 차이</h2>
<p>업무지구는 야간 출입 제한이, 주거지는 공동현관 출입 방식이, 호텔·숙소는 객실 출입 정책이 가장 중요한 확인 항목입니다. 같은 서울이라도 강남·여의도 같은 업무지구, 목동·노원 같은 주거 생활권, 명동·홍대 같은 숙소 밀집지는 확인할 내용이 서로 다릅니다. 권역별 흐름은 <a href="/#areas">권역 안내</a>에서, 구별 안내는 <a href="/#districts">구별 안내</a>에서 확인할 수 있습니다.</p>
</section>

<section>
<h2>예약 흐름 속에서 확인하는 방법</h2>
<p>이 항목은 예약을 확정하기 전 단계에서 함께 확인하는 것이 가장 확실합니다. 먼저 방문 위치를 도로명 주소로 정하고, 건물 유형(자택·오피스텔·호텔·업무지구)을 확인한 뒤, 출입 방식과 예약 가능 시간을 맞춰 보면 도착 후 대기나 혼선을 줄일 수 있습니다. 위치나 시간이 바뀔 때는 가능한 한 빨리 알려주시면 다음 안내가 빨라집니다. 자세한 절차는 <a href="{R.check_url('time')}">예약 가능 시간</a>과 <a href="{R.check_url('change-policy')}">예약 변경 기준</a>에서 확인할 수 있습니다.</p>
</section>

{R.privacy_block()}
{R.illegal_block()}
{R.faq_block(R.region_faqs('이 경우', item['name'] + '은 어떻게 확인하나요?', item['lead']))}
{R.who_how_why()}
{R.byline_block()}
<section><h2>관련 안내</h2><p>예약 전 확인은 {extra_links}에서, 이용 장소별 기준은 <a href="{R.use_url('home')}">자택</a>·<a href="{R.use_url('hotel')}">호텔·숙소</a>·<a href="{R.use_url('officetel')}">오피스텔</a> 안내에서 함께 확인하세요.</p></section>
{_cta()}
"""


def _use_pages():
    out = []
    for u in USE_CASES:
        body = _points_body(u, "use")
        out.append({
            "path": f"use/{u['slug']}/",
            "title": f"{u['h1']} | 서울 출장마사지",
            "desc": _clip(f"{u['name']} 안내입니다. {u['lead']}"),
            "h1": u["h1"],
            "body": body,
            "extra_head": R.faq_jsonld(R.region_faqs('이 경우', u['name'] + '은 어떻게 확인하나요?', u['lead'])),
            "breadcrumb": [("이용 장소", "/#use"), (u["name"], "")],
        })
    return out


def _check_pages():
    out = []
    for c in CHECKS:
        body = _points_body(c, "check")
        out.append({
            "path": f"check/{c['slug']}/",
            "title": f"{c['h1']}",
            "desc": _clip(f"{c['name']} 안내입니다. {c['lead']}"),
            "h1": c["h1"],
            "body": body,
            "extra_head": R.faq_jsonld(R.region_faqs('이 경우', c['name'] + '은 어떻게 확인하나요?', c['lead'])),
            "breadcrumb": [("예약 전 확인", "/#check"), (c["name"], "")],
        })
    return out


def _policy_pages():
    out = []
    for p in POLICIES:
        body = f"""
<p class="lead">{p['lead']}</p>

<section>
<h2>{p['name']}</h2>
<p>{p['lead']} 이 사이트는 서울 지역 방문형 관리 서비스를 안내하며, 실제 오프라인 매장이 없는 방문형 서비스이므로 매장 기반 정보나 허위 후기, 가짜 평점을 사용하지 않습니다. 모든 안내는 실제 행정구역·생활권·역세권·이용 장소 정보를 기준으로 작성합니다.</p>
</section>

<section>
<h2>운영 원칙</h2>
<p>지역명만 바꾼 중복 본문을 만들지 않고, 생활권·가까운 역·이용 장소·예약 전 확인사항을 지역마다 다르게 구성합니다. 개인정보는 예약 확인과 연락에 필요한 최소 범위만 사용하며, 불법·선정적 서비스는 제공하거나 안내하지 않습니다. 상위노출을 보장한다는 표현은 사용하지 않습니다.</p>
</section>

<section>
<h2>콘텐츠 작성과 업데이트 기준</h2>
<p>모든 지역 안내는 서울시 행정구역, 대표 생활권, 주요 지하철역, 이용 장소별 예약 전 확인사항을 기준으로 작성합니다. 작성자는 서울 지역 안내 콘텐츠 담당자, 검수자는 콘텐츠 품질 검수 담당자이며, 행정동 변경·생활권 변화·지하철역 정보 변화와 사용자 문의 흐름, 품질 점검 결과를 반영해 내용을 수정합니다. 실제 오프라인 매장이 없는 방문형 서비스이므로 매장 기반 구조화 데이터나 허위 후기, 가짜 평점은 사용하지 않으며, 페이지에 보이지 않는 정보를 구조화 데이터로 넣지 않습니다.</p>
</section>

<section>
<h2>이용자 보호</h2>
<p>예약 정보는 예약 확인과 연락 목적으로만 사용하고, 상담·예약이 끝난 뒤에는 보관을 최소화합니다. 불법·선정적 서비스나 무리한 요청에는 어떤 경우에도 응하지 않으며, 관련 법령과 위생·안전 기준을 따릅니다. 이용 중 궁금한 점은 운영 기준 페이지와 예약 전 확인 페이지에서 확인할 수 있으며, 추가 문의는 <a href="/contact/">문의하기</a>를 통해 예약전화 또는 텔레그램으로 연락하실 수 있습니다. 운영 기준은 사용자 문의 흐름과 품질 점검 결과에 따라 주기적으로 보완합니다.</p>
</section>

<section>
<h2>개인정보 보호 세부 기준</h2>
<p>수집하는 정보는 예약 확인과 방문 안내에 필요한 연락처, 방문 위치, 희망 시간 정도로 한정합니다. 이 정보는 예약 진행과 연락 외의 목적으로 사용하지 않고, 제3자에게 제공하거나 광고 목적으로 활용하지 않습니다. 상담이나 예약이 끝난 뒤에는 보관 기간을 최소화하며, 이용자가 요청하면 보유한 정보의 처리 현황을 안내합니다. 서울 전역 어느 지역에서 문의하시더라도 동일한 기준이 적용되며, 구체적인 처리 항목과 절차는 <a href="{R.policy_url('privacy')}">개인정보 처리방침</a>에서 확인할 수 있습니다.</p>
</section>

{R.privacy_block()}
{R.illegal_block()}
{R.who_how_why()}
{R.byline_block()}
<section><h2>운영 기준 바로가기</h2><ul class="card-grid">{''.join(f'<li><a href="{R.policy_url(x["slug"])}">{x["name"]}</a></li>' for x in POLICIES if x["slug"] != p["slug"])}</ul></section>
{_cta()}
"""
        out.append({
            "path": f"policy/{p['slug']}/",
            "title": f"{p['h1']} | 서울 출장마사지",
            "desc": _clip(f"{p['name']} 안내입니다. {p['lead']}"),
            "h1": p["h1"],
            "body": body,
            "breadcrumb": [("운영 기준", "/#policy"), (p["name"], "")],
        })
    return out


# ── 문의하기 ─────────────────────────────────────────────
def _contact_page():
    from ..site import PHONE, PHONE_DISPLAY, TELEGRAM_MAKE, TELEGRAM_PARTNER
    body = f"""
<p class="lead">서울 전역 방문 예약과 상담은 전화로 가장 빠르게 진행됩니다. 방문 위치(도로명 주소)와 희망 시간을 알려주시면 가능 여부를 바로 확인해 드립니다.</p>

<section>
<h2>예약·상담 문의</h2>
<p>예약 문의는 연중무휴 24시간 받습니다. 정확한 방문 위치와 희망 시간, 이용 장소(자택·호텔·숙소·오피스텔)를 알려주시면 가능 여부와 준비 사항을 안내해 드립니다. 저녁 시간대와 주말은 문의가 몰릴 수 있어 여유 있게 연락 주시는 것이 좋습니다.</p>
<p><a class="cta-phone" href="tel:{PHONE}">{PHONE_DISPLAY}</a></p>
</section>

<section>
<h2>웹사이트 제작·제휴 문의</h2>
<p>웹사이트 제작 문의와 제휴 문의는 텔레그램으로 받습니다. 아래 버튼으로 연결됩니다.</p>
<p><a href="{TELEGRAM_MAKE}" target="_blank" rel="noopener nofollow">웹사이트 제작문의 ↗</a> · <a href="{TELEGRAM_PARTNER}" target="_blank" rel="noopener nofollow">제휴문의 ↗</a></p>
</section>

<section>
<h2>문의 전 확인하면 좋은 내용</h2>
<ul class="checklist">
<li>방문 주소를 도로명 기준으로 확인했나요?</li>
<li>건물 출입 방식(공동현관·엘리베이터·프런트)을 확인했나요?</li>
<li>이용 장소가 자택·호텔·오피스텔 중 어디인가요?</li>
<li>희망 시간대와 연락 가능 여부를 확인했나요?</li>
</ul>
<p>자세한 항목은 <a href="{R.check_url('address')}">방문 주소 확인</a>·<a href="{R.check_url('building-access')}">건물 출입 방식</a>·<a href="{R.check_url('time')}">예약 가능 시간</a>에서 확인할 수 있습니다.</p>
</section>

{R.privacy_block()}
{R.illegal_block()}
{R.who_how_why()}
{R.byline_block()}
"""
    return {
        "path": "contact/",
        "title": "문의하기 | 서울 출장마사지 간다GO",
        "desc": "서울 전역 방문 예약·상담과 웹사이트 제작·제휴 문의 안내입니다. 예약전화와 텔레그램으로 연결됩니다.",
        "h1": "문의하기",
        "body": body,
        "breadcrumb": [("문의하기", "")],
    }


# ── 전체 PAGES 조립 ──────────────────────────────────────
def build_pages():
    pages = []
    for a in AREAS:
        pages.append(_area_page(a))
    for slug, d in DISTRICTS.items():
        pages.append(_district_page(slug, d))
    for l in LIFE_AREAS:
        pg = _life_page(l)
        if pg:
            pages.append(pg)
    for s in STATIONS:
        pg = _station_page(s)
        if pg:
            pages.append(pg)
    pages += _dong_pages()
    pages += _use_pages()
    pages += _check_pages()
    pages += _policy_pages()
    pages.append(_contact_page())
    _attach_images(pages)
    return pages


def _attach_images(pages):
    """경로 유형별 대표 이미지(og + schema + 본문)와 자연스러운 alt 를 부여한다."""
    import re as _re
    for p in pages:
        path = p["path"]
        if path.startswith("area/"):
            img = "cover-area"
        elif path.startswith("life/"):
            img = "cover-life"
        elif path.startswith("station/"):
            img = "cover-station"
        elif path.startswith("use/"):
            img = "cover-use"
        elif path.startswith("check/"):
            img = "cover-check"
        elif path.startswith("policy/"):
            img = "cover-policy"
        elif path == "contact/":
            img = "cover-main"
        elif path.count("/") == 2:   # 행정동
            img = "cover-dong"
        else:                         # 구
            img = "cover-district"
        # alt 은 "출장마사지" 반복 없이 자연스럽게 구성
        label = _re.sub(r"출장마사지", "", p["h1"])
        label = _re.sub(r"\s*·\s*", " ", label)
        label = _re.sub(r"\s+", " ", label).strip()
        suffix = " 이미지" if label.endswith("안내") else " 안내 이미지"
        p["image"] = f"/assets/{img}.png"
        p["image_alt"] = f"{label}{suffix}"


PAGES = build_pages()

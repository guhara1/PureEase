#!/usr/bin/env python3
"""노원 블랙 마사지 — 정적 사이트 빌드 스크립트.

content/ 패키지의 페이지 정의를 읽어 정적 HTML을 생성한다.

규칙(자동 적용):
  - 본문 텍스트 2,000자 미만 페이지는 robots noindex 처리
  - sitemap.xml 에는 index 허용 페이지만 포함
  - 지역+역+테마 조합 경로는 생성 자체가 불가능한 구조
"""
import html
import json
import os
import re
import shutil
import sys
from datetime import date

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from content import PAGES
from content.site import (AUTHORITY_LINKS, BASE_URL, BRAND, COMPANY, NAV,
                          PHONE, PHONE_DISPLAY, TELEGRAM_MAKE,
                          TELEGRAM_PARTNER)

ROOT = os.path.dirname(os.path.abspath(__file__))
MIN_INDEX_CHARS = 2000
# 모든 페이지에 공통으로 노출하는 대표 이미지(사용자가 교체). 메인은 히어로 옆에 표시.
HERO_IMAGE = "/assets/hero.jpg"


def text_length(body_html: str) -> int:
    """태그를 제거한 본문 글자수(공백 포함, 연속 공백은 1자).
    공통 요금 블록은 페이지 고유 본문이 아니므로 측정에서 제외한다."""
    text = re.sub(r'<section class="pricing">.*?</section>', " ", body_html, flags=re.S)
    text = re.sub(r"<[^>]+>", " ", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return len(text)


def render_nav(current_path: str) -> str:
    items = []
    for label, href, children in NAV:
        active = " is-active" if href == "/" + current_path else ""
        if children:
            sub = "".join(
                f'<li><a href="{c_href}">{c_label}</a></li>'
                for c_label, c_href in children
            )
            items.append(
                f'<li class="nav-item has-sub{active}">'
                f'<a href="{href}">{label}</a>'
                f'<ul class="sub-menu">{sub}</ul></li>'
            )
        else:
            items.append(
                f'<li class="nav-item{active}"><a href="{href}">{label}</a></li>'
            )
    return "".join(items)


def render_breadcrumb(crumbs) -> str:
    if not crumbs:
        return ""
    parts = ['<nav class="breadcrumb" aria-label="현재 위치"><ol>']
    parts.append('<li><a href="/">홈</a></li>')
    for label, href in crumbs:
        if href:
            parts.append(f'<li><a href="{href}">{label}</a></li>')
        else:
            parts.append(f"<li><span>{label}</span></li>")
    parts.append("</ol></nav>")
    return "".join(parts)


def inject_toc(body: str):
    """본문 섹션(h2)에 id를 보장하고 좌측 목차 데이터를 만든다."""
    items = []
    counter = [0]

    def repl(m):
        attrs, title = m.group(1), m.group(2)
        idm = re.search(r'id="([^"]+)"', attrs)
        if idm:
            sid = idm.group(1)
            opening = f"<section{attrs}>"
        else:
            counter[0] += 1
            sid = f"sec-{counter[0]}"
            opening = f'<section id="{sid}"{attrs}>'
        label = re.sub(r"<[^>]+>", "", title).strip()
        items.append((sid, label))
        return f"{opening}<h2>{title}</h2>"

    body = re.sub(r"<section([^>]*)>\s*<h2>(.*?)</h2>", repl, body, flags=re.S)
    return body, items


def render_toc(items) -> str:
    if len(items) < 3:
        return ""
    links = "".join(
        f'<li><a href="#{sid}">{label}</a></li>' for sid, label in items
    )
    return (
        '<aside class="page-toc"><nav aria-label="페이지 목차">'
        '<p class="toc-title">목차</p>'
        f"<ul>{links}</ul></nav></aside>"
    )


def build_schema(page: dict, canonical: str, crumbs) -> str:
    """모든 페이지 공통 구조화 데이터(JSON-LD)를 생성한다.

    - Organization / WebSite / WebPage / BreadcrumbList 를 @graph 로 묶는다.
    - 오프라인 매장이 없는 방문형 서비스이므로 LocalBusiness 계열은 쓰지 않는다.
    - 실제 후기 데이터가 없으므로 Review·AggregateRating 도 쓰지 않는다.
    """
    base = BASE_URL.rstrip("/")
    og_image = base + (page.get("image") or "/assets/og-image.png")

    org = {
        "@type": "Organization",
        "@id": f"{base}/#organization",
        "name": COMPANY,
        "alternateName": BRAND,
        "url": f"{base}/",
        "image": og_image,
        "logo": {
            "@type": "ImageObject",
            "url": f"{base}/assets/icon-512.png",
            "width": 512,
            "height": 512,
        },
        "telephone": PHONE,
        "areaServed": {"@type": "City", "name": "서울특별시"},
        "contactPoint": {
            "@type": "ContactPoint",
            "telephone": PHONE,
            "contactType": "reservations",
            "areaServed": "KR",
            "availableLanguage": ["ko"],
        },
        "sameAs": [TELEGRAM_MAKE],
    }

    website = {
        "@type": "WebSite",
        "@id": f"{base}/#website",
        "name": BRAND,
        "url": f"{base}/",
        "inLanguage": "ko-KR",
        "publisher": {"@id": f"{base}/#organization"},
    }

    webpage = {
        "@type": "WebPage",
        "@id": canonical + "#webpage",
        "url": canonical,
        "name": page["title"],
        "description": page["desc"],
        "inLanguage": "ko-KR",
        "isPartOf": {"@id": f"{base}/#website"},
        "about": {"@id": f"{base}/#organization"},
        "primaryImageOfPage": {
            "@type": "ImageObject",
            "url": og_image,
            "width": 1200,
            "height": 630,
        },
    }

    graph = [org, website, webpage]

    # BreadcrumbList — 홈 + 페이지 breadcrumb
    items = [{"name": "홈", "item": f"{base}/"}]
    for label, href in (crumbs or []):
        url = base + href if href else canonical
        items.append({"name": re.sub(r"<[^>]+>", "", label).strip(), "item": url})
    if len(items) > 1:
        webpage["breadcrumb"] = {"@id": canonical + "#breadcrumb"}
        graph.append({
            "@type": "BreadcrumbList",
            "@id": canonical + "#breadcrumb",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": i + 1,
                    "name": it["name"],
                    "item": it["item"],
                }
                for i, it in enumerate(items)
            ],
        })

    data = {"@context": "https://schema.org", "@graph": graph}
    return (
        '<script type="application/ld+json">\n'
        + json.dumps(data, ensure_ascii=False, indent=2)
        + "\n</script>\n"
    )


def render_page(page: dict) -> str:
    path = page["path"]
    title = page["title"]
    desc = page["desc"]
    h1 = page["h1"]
    body = page["body"]
    crumbs = page.get("breadcrumb") or []
    extra_head = page.get("extra_head", "")
    hero = page.get("hero", "")

    chars = text_length(body)
    noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
    robots = (
        '<meta name="robots" content="noindex,follow">'
        if noindex
        else '<meta name="robots" content="index,follow">'
    )
    canonical = BASE_URL.rstrip("/") + "/" + path

    # 공통 구조화 데이터(Organization/WebSite/WebPage/BreadcrumbList) +
    # 페이지 고유 스키마(FAQPage 등)를 함께 head 에 주입한다.
    extra_head = build_schema(page, canonical, crumbs) + extra_head

    # 히어로가 있는 페이지(메인)는 H1을 히어로 안에서 출력한다.
    if hero:
        page_head = hero
    else:
        page_head = ""

    h1_html = "" if hero else f"<h1>{h1}</h1>"

    authority_html = "".join(
        f'<a href="{url}" target="_blank" rel="noopener">{label} ↗</a>'
        for label, url in AUTHORITY_LINKS
    )

    # 대표 이미지 — 모든 페이지에 노출.
    # 메인은 히어로 옆(hero-media)에서 출력하고, 나머지 페이지는 본문 상단에 노출한다.
    # 표시 이미지는 사용자가 교체하는 /assets/hero.png 를 전 페이지 공통으로 사용한다.
    cover_html = ""
    if not hero:
        cover_html = (
            f'<figure class="page-cover">'
            f'<img src="{HERO_IMAGE}" alt="{page.get("image_alt") or (BRAND + " 안내 이미지")}" '
            f'loading="lazy" decoding="async">'
            f"</figure>"
        )

    body, toc_items = inject_toc(body)
    toc_html = render_toc(toc_items)
    layout_cls = "page-layout has-toc" if toc_html else "page-layout"

    return f"""<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
{robots}
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="website">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">
<meta property="og:site_name" content="{BRAND}">
<meta property="og:image" content="{BASE_URL.rstrip('/')}{page.get('image') or '/assets/og-image.png'}">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{page.get('image_alt', BRAND)}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:image" content="{BASE_URL.rstrip('/')}{page.get('image') or '/assets/og-image.png'}">
<link rel="icon" href="/favicon.ico" sizes="48x48">
<link rel="icon" type="image/svg+xml" href="/assets/favicon.svg">
<link rel="icon" type="image/png" sizes="32x32" href="/assets/favicon-32.png">
<link rel="apple-touch-icon" href="/assets/apple-touch-icon.png">
<meta name="theme-color" content="#0a1120">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700&family=Noto+Serif+KR:wght@600;700;900&display=swap" rel="stylesheet">
<link rel="stylesheet" href="/assets/style.css">
{extra_head}</head>
<body>
<header class="site-header">
  <div class="header-accent" aria-hidden="true"></div>
  <div class="header-top">
    <div class="header-inner">
      <a class="brand" href="/"><span class="brand-mark">간</span> <span class="brand-text">{BRAND}</span></a>
      <p class="header-tagline"><span class="tag-gem">◆</span> 서울 전역 생활권 방문 안내 <span class="tag-gem">◆</span> 24시간 상담</p>
      <a class="header-call" href="tel:{PHONE}"><span class="call-label">예약전화</span> {PHONE_DISPLAY}</a>
      <button class="nav-toggle" aria-label="메뉴 열기" aria-expanded="false"><span></span><span></span><span></span></button>
    </div>
  </div>
  <nav class="main-nav" aria-label="주 메뉴">
    <div class="nav-inner"><ul class="nav-list">{render_nav(path)}</ul></div>
  </nav>
</header>
{page_head}<main class="site-main">
  <div class="container {layout_cls}">
    {toc_html}
    <article class="page-content">
      {render_breadcrumb(crumbs)}
      {h1_html}
      {cover_html}
      {body}
    </article>
  </div>
</main>
<footer class="site-footer">
  <div class="container footer-grid">
    <div class="footer-col footer-about">
      <p class="footer-brand">{BRAND}</p>
      <p class="footer-desc">서울 전역 생활권 방문 출장마사지·홈타이 안내 사이트입니다. 25개 구와 주요 생활권·역세권·이용 장소별 예약 전 확인사항을 안내하며, 모든 서비스는 안내된 관리 범위와 위생·안전 기준 안에서만 제공됩니다.</p>
      <address class="footer-contact">
        <span class="footer-contact-row"><span class="footer-label">상호</span> {COMPANY}</span>
        <span class="footer-contact-row"><span class="footer-label">예약전화</span> <a href="tel:{PHONE}">{PHONE_DISPLAY}</a></span>
        <span class="footer-contact-row"><span class="footer-label">상담시간</span> 연중무휴 24시간</span>
        <span class="footer-contact-row"><span class="footer-label">서비스 지역</span> 서울특별시 전역</span>
      </address>
      <div class="footer-cta">
        <a class="footer-cta-btn" href="{TELEGRAM_MAKE}" target="_blank" rel="noopener nofollow">
          <span class="footer-cta-ico" aria-hidden="true">✈</span> 웹사이트 제작문의
        </a>
        <a class="footer-cta-btn" href="{TELEGRAM_PARTNER}" target="_blank" rel="noopener nofollow">
          <span class="footer-cta-ico" aria-hidden="true">✈</span> 제휴문의
        </a>
      </div>
    </div>
    <nav class="footer-col" aria-label="지역 안내">
      <p class="footer-title">지역 안내</p>
      <ul>
        <li><a href="/#areas">권역 안내</a></li>
        <li><a href="/#districts">구별 안내</a></li>
        <li><a href="/#life">생활권 안내</a></li>
        <li><a href="/use/station-area/">역세권 이용</a></li>
        <li><a href="/nowon-gu/">노원구 안내</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="이용 안내">
      <p class="footer-title">이용 안내</p>
      <ul>
        <li><a href="/use/home/">자택 이용</a></li>
        <li><a href="/use/hotel/">호텔·숙소 이용</a></li>
        <li><a href="/use/officetel/">오피스텔 이용</a></li>
        <li><a href="/check/address/">예약 전 확인</a></li>
        <li><a href="/check/time/">예약 가능 시간</a></li>
      </ul>
    </nav>
    <nav class="footer-col" aria-label="정책 및 기준">
      <p class="footer-title">운영 기준</p>
      <ul>
        <li><a href="/policy/authors/">작성자·검수자 안내</a></li>
        <li><a href="/policy/privacy/">개인정보 처리방침</a></li>
        <li><a href="/policy/service-standard/">서비스 이용 기준</a></li>
        <li><a href="/policy/no-illegal/">불법·선정적 서비스 불가 안내</a></li>
        <li><a href="/policy/content-standard/">콘텐츠 작성 기준</a></li>
      </ul>
    </nav>
  </div>
  <nav class="footer-refs" aria-label="참고 기관">
    <div class="container footer-refs-inner">
      <span class="footer-refs-label">참고</span>
      {authority_html}
    </div>
  </nav>
  <div class="footer-bottom">
    <div class="container footer-bottom-inner">
      <p class="footer-copy">&copy; {COMPANY} ({BRAND}). All rights reserved.</p>
      <p class="footer-note">건전한 방문 관리 서비스를 운영하며, 불법적인 요청은 어떤 경우에도 응하지 않습니다.</p>
      <a class="footer-made" href="{TELEGRAM_MAKE}" target="_blank" rel="noopener nofollow">웹사이트 제작문의 ↗</a>
    </div>
  </div>
</footer>
<a class="call-fab" href="tel:{PHONE}" aria-label="전화 예약 {PHONE_DISPLAY}">
  <svg viewBox="0 0 24 24" aria-hidden="true"><path d="M6.62 10.79c1.44 2.83 3.76 5.14 6.59 6.59l2.2-2.2c.27-.27.67-.36 1.02-.24 1.12.37 2.33.57 3.57.57.55 0 1 .45 1 1V20c0 .55-.45 1-1 1-9.39 0-17-7.61-17-17 0-.55.45-1 1-1h3.5c.55 0 1 .45 1 1 0 1.25.2 2.45.57 3.57.11.35.03.74-.25 1.02l-2.2 2.2z"/></svg>
  <span class="call-fab-label">예약 전화</span>
</a>
<script src="/assets/nav.js"></script>
</body>
</html>
"""


def build() -> None:
    report = []
    sitemap_urls = []

    for page in PAGES:
        path = page["path"]  # "" 또는 "nowon-gu/wolgye-dong/" 형태
        out_dir = os.path.join(ROOT, path)
        os.makedirs(out_dir, exist_ok=True)
        html_out = render_page(page)
        with open(os.path.join(out_dir, "index.html"), "w", encoding="utf-8") as f:
            f.write(html_out)

        chars = text_length(page["body"])
        noindex = page.get("noindex", False) or chars < MIN_INDEX_CHARS
        if not noindex:
            loc = BASE_URL.rstrip("/") + "/" + path
            img = page.get("image")
            sitemap_urls.append((loc, img, page.get("image_alt", "")))
        report.append((path or "/", chars, "noindex" if noindex else "index"))

    # sitemap.xml (lastmod + 이미지 sitemap 포함)
    base = BASE_URL.rstrip("/")
    lastmod = date.today().isoformat()
    blocks = []
    for loc, img, alt in sitemap_urls:
        img_xml = ""
        if img:
            img_alt = html.escape(alt, quote=True)
            img_xml = (
                f"\n    <image:image><image:loc>{base}{img}</image:loc>"
                f"<image:title>{img_alt}</image:title></image:image>"
            )
        blocks.append(
            f"  <url><loc>{loc}</loc><lastmod>{lastmod}</lastmod>{img_xml}</url>"
        )
    urls = "\n".join(blocks)
    with open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write(
            '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"\n'
            '        xmlns:image="http://www.google.com/schemas/sitemap-image/1.1">\n'
            f"{urls}\n</urlset>\n"
        )

    # robots.txt
    with open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8") as f:
        f.write(
            "User-agent: *\nAllow: /\n\n"
            f"Sitemap: {BASE_URL.rstrip('/')}/sitemap.xml\n"
        )

    # .nojekyll (GitHub Pages)
    open(os.path.join(ROOT, ".nojekyll"), "w").close()

    width = max(len(p) for p, _, _ in report)
    print(f"{'PATH'.ljust(width)}  CHARS  ROBOTS")
    for p, c, r in sorted(report):
        flag = "" if (r == "noindex" or MIN_INDEX_CHARS <= c <= 2500) else "  ⚠"
        print(f"{p.ljust(width)}  {str(c).rjust(5)}  {r}{flag}")
    print(f"\n{len(report)} pages built, {len(sitemap_urls)} in sitemap.")


if __name__ == "__main__":
    build()

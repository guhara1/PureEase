# 코스별 기본 요금 블록 — 메인·전 지역 페이지 공용 컴포넌트
from .site import PHONE

PRICING = f"""
<section class="pricing">
<p class="pricing-badge">기본 요금 안내</p>
<h2>코스 시간으로 보는 기본 요금</h2>
<p class="pricing-lead">관리 시간(60·90·120분)을 기준으로 정리한 기본 금액입니다. 표시되지 않은 별도 비용은 두지 않는 것을 원칙으로 안내합니다.</p>
<div class="price-grid">
  <div class="price-card">
    <p class="price-name">60분 코스</p>
    <p class="price-value">90,000<span>원</span></p>
    <p class="price-time">60분</p>
    <p class="price-desc">핵심 부위 위주 가벼운 이완</p>
    <a class="price-btn" href="tel:{PHONE}">예약 문의</a>
  </div>
  <div class="price-card featured">
    <p class="price-badge">추천</p>
    <p class="price-name">90분 코스</p>
    <p class="price-value">150,000<span>원</span></p>
    <p class="price-time">90분</p>
    <p class="price-desc">전신 균형 표준 구성 · 아로마 포함</p>
    <a class="price-btn primary" href="tel:{PHONE}">예약 문의</a>
  </div>
  <div class="price-card">
    <p class="price-name">120분 코스</p>
    <p class="price-value">180,000<span>원</span></p>
    <p class="price-time">120분</p>
    <p class="price-desc">구석구석 집중하는 프리미엄 구성</p>
    <a class="price-btn" href="tel:{PHONE}">예약 문의</a>
  </div>
</div>
<p class="price-note">방문 지역과 시간대, 이동 거리에 따라 최종 금액은 통화 시 확정됩니다. <a href="/check/travel-fee/">요금·예약 기준 자세히 보기 →</a></p>
</section>
"""

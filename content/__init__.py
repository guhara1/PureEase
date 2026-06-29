# 전체 페이지 목록 집계
# 루트(/)는 서울 출장마사지 메인이 차지하고, 기존 노원 콘텐츠는
# /nowon-gu/ 이하(지역·역세권·테마·매거진 등)로 그대로 유지한다.
from . import areas, stations, themes, info, magazine, about
from .seoul import main as seoul_main
from .seoul import pages as seoul_pages
from .seoul import columns as seoul_columns

PAGES = (
    [seoul_main.PAGE]
    + seoul_pages.PAGES
    + seoul_columns.PAGES
    + areas.PAGES
    + stations.PAGES
    + themes.PAGES
    + info.PAGES
    + magazine.PAGES
    + [about.PAGE]
)

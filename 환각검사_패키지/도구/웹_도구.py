# -*- coding: utf-8 -*-
"""
인터넷에서 정보를 가져오는 도구 (모두 무료, API 키 필요 없음)

  웹_글_가져오기(주소)     : 웹 페이지를 열어 본문 글만 뽑음 (② 출처-답변 연관성)
  위키백과_찾기(검색어)    : 한국어 위키백과에서 검색해 가장 관련 있는 문서의 본문을 가져옴 (사실형 ⑤⑥)
  논문_찾기(제목, DOI)     : Crossref와 OpenAlex에서 논문을 찾아 서지 정보를 가져옴 (출처형 ⑤⑥)
  DOI_있나(DOI)           : doi.org 에 그 DOI가 등록되어 있는지 확인 (출처형 ⑤)

인터넷이 안 되거나 사이트가 응답하지 않으면 None 이나 빈 목록을 돌려줘요.
그러면 기준 파일들이 "확인 불가"로 처리해요. (프로그램이 멈추지 않게)

추가 설치 없이 파이썬 기본 기능(urllib, html.parser)만 써요.
"""
import json, re, urllib.error, urllib.parse, urllib.request
from html.parser import HTMLParser

import 설정


_주소_그대로 = "".join(chr(i) for i in range(33, 127))       # 영문·숫자·기호(이미 %로 바꾼 것 포함)는 그대로 둠


def _주소_다듬기(주소):
    """한글 같은 글자가 든 주소를 파이썬이 열 수 있는 모양으로 바꿈
    예) https://ko.wikipedia.org/wiki/대한민국 → https://ko.wikipedia.org/wiki/%EB%8C%80...
    도메인이 한글이면(예: 한글.kr) 인터넷 주소용 영문(xn--…)으로 바꿔요. 이미 영문뿐인 주소는 그대로예요."""
    주소 = 주소.strip()
    if 주소.isascii():
        return 주소
    나눔 = urllib.parse.urlsplit(주소)
    호스트 = 나눔.hostname or ""
    if not 호스트.isascii():
        새_호스트 = 호스트.encode("idna").decode("ascii")
        나눔 = 나눔._replace(netloc=나눔.netloc.replace(호스트, 새_호스트))
    return urllib.parse.urlunsplit(나눔._replace(
        path=urllib.parse.quote(나눔.path, safe=_주소_그대로),
        query=urllib.parse.quote(나눔.query, safe=_주소_그대로),
        fragment=urllib.parse.quote(나눔.fragment, safe=_주소_그대로)))


def _열기(주소, 형식="text"):
    요청 = urllib.request.Request(_주소_다듬기(주소), headers={"User-Agent": 설정.웹_사용자_이름})
    with urllib.request.urlopen(요청, timeout=설정.웹_시간제한_초) as 응답:
        내용 = 응답.read(5_000_000)
        글자셋 = 응답.headers.get_content_charset() or "utf-8"
    글 = 내용.decode(글자셋, "ignore")
    return json.loads(글) if 형식 == "json" else 글


class _본문뽑기(HTMLParser):
    건너뛸_태그 = {"script", "style", "noscript", "nav", "footer", "header", "svg", "form"}

    def __init__(self):
        super().__init__()
        self.깊이 = 0
        self.조각 = []

    def handle_starttag(self, tag, attrs):
        if tag in self.건너뛸_태그:
            self.깊이 += 1

    def handle_endtag(self, tag):
        if tag in self.건너뛸_태그 and self.깊이:
            self.깊이 -= 1
        if tag in ("p", "div", "li", "br", "h1", "h2", "h3", "tr"):
            self.조각.append("\n")

    def handle_data(self, data):
        if not self.깊이 and data.strip():
            self.조각.append(data.strip() + " ")


def 웹_글_가져오기(주소):
    """웹 페이지 본문 글. 실패하면 None"""
    try:
        html = _열기(주소)
    except Exception:
        return None
    뽑기 = _본문뽑기()
    try:
        뽑기.feed(html)
    except Exception:
        return None
    글 = re.sub(r"\n\s*\n+", "\n", "".join(뽑기.조각)).strip()
    return 글 or None


def 위키백과_찾기(검색어):
    """(문서 제목, 본문 글). 못 찾으면 (None, None)"""
    if not 검색어:
        return None, None
    try:
        주소 = ("https://ko.wikipedia.org/w/api.php?action=query&list=search&format=json&srlimit=1&srsearch="
              + urllib.parse.quote(검색어))
        찾음 = _열기(주소, "json")["query"]["search"]
        if not 찾음:
            return None, None
        제목 = 찾음[0]["title"]
        주소 = ("https://ko.wikipedia.org/w/api.php?action=query&prop=extracts&explaintext=1&format=json&titles="
              + urllib.parse.quote(제목))
        쪽들 = _열기(주소, "json")["query"]["pages"]
        본문 = next(iter(쪽들.values())).get("extract", "")
        return 제목, 본문 or None
    except Exception:
        return None, None


def _crossref_정리(항목):
    return {"출처": "Crossref",
            "제목": " ".join(항목.get("title") or []),
            "저자": [" ".join(x for x in (a.get("given"), a.get("family")) if x) for a in 항목.get("author") or []],
            "연도": str(((항목.get("issued") or {}).get("date-parts") or [[None]])[0][0] or ""),
            "학술지": " ".join(항목.get("container-title") or []),
            "권": str(항목.get("volume") or ""), "호": str(항목.get("issue") or ""),
            "DOI": 항목.get("DOI") or ""}


def _openalex_정리(항목):
    서지 = 항목.get("biblio") or {}
    출판 = ((항목.get("primary_location") or {}).get("source") or {})
    return {"출처": "OpenAlex",
            "제목": 항목.get("display_name") or "",
            "저자": [(a.get("author") or {}).get("display_name", "") for a in 항목.get("authorships") or []],
            "연도": str(항목.get("publication_year") or ""),
            "학술지": 출판.get("display_name") or "",
            "권": str(서지.get("volume") or ""), "호": str(서지.get("issue") or ""),
            "DOI": (항목.get("doi") or "").replace("https://doi.org/", "")}


def 논문_찾기(제목="", DOI=""):
    """논문 후보 목록 (최대 6개). 인터넷 오류면 None, 검색했지만 없으면 []"""
    후보 = []
    성공 = False
    try:
        if DOI:
            항목 = _열기("https://api.crossref.org/works/" + urllib.parse.quote(DOI), "json")["message"]
            후보.append(_crossref_정리(항목)); 성공 = True
    except Exception:
        pass
    if 제목:
        try:
            주소 = "https://api.crossref.org/works?rows=3&query.bibliographic=" + urllib.parse.quote(제목)
            후보 += [_crossref_정리(x) for x in _열기(주소, "json")["message"]["items"]]; 성공 = True
        except Exception:
            pass
        try:
            주소 = "https://api.openalex.org/works?per-page=3&search=" + urllib.parse.quote(제목)
            후보 += [_openalex_정리(x) for x in _열기(주소, "json")["results"]]; 성공 = True
        except Exception:
            pass
    return 후보 if 성공 else None


def DOI_있나(DOI):
    """DOI가 실제로 등록되어 있는지. True(있음) / False(없음: doi.org가 404) / None(인터넷 오류로 모름)"""
    if not DOI:
        return None
    요청 = urllib.request.Request("https://doi.org/api/handles/" + urllib.parse.quote(DOI),
                              headers={"User-Agent": 설정.웹_사용자_이름})
    try:
        with urllib.request.urlopen(요청, timeout=설정.웹_시간제한_초) as 응답:
            return json.loads(응답.read().decode("utf-8")).get("responseCode") == 1
    except urllib.error.HTTPError as e:
        return False if e.code == 404 else None
    except Exception:
        return None

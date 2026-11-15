# -*- coding: utf-8 -*-
"""
출처형 기준(⑤ 출처 실재 확인, ⑥ 서지 정보 일치)이 함께 쓰는 도구

  자료_뽑기(답변)          : 답변에서 인용한 자료(제목, 저자, 연도, 학술지, 권, 호, DOI)를 프로그램 규칙으로 뽑음
  자료_모으기(자료)        : 검사 AI가 뽑은 자료 목록이 있으면 그것을, 없으면 프로그램 규칙으로 뽑은 것을 씀
  같은_논문_정도(가, 나)   : 두 제목이 얼마나 같은지 (0~1)
  없다고_했나(답변)        : 답변이 "그런 자료는 없다/찾을 수 없다"고 했는지 (질문이 없는 자료를 물은 경우)
  찾아보기(자료하나)       : Crossref·OpenAlex·doi.org 에서 찾아본 결과

  예) "- **논문 제목:** *Computing Machinery and Intelligence*  - **발표 연도:** 1950년  - **학술지:** *Mind*"
      → {"제목": "Computing Machinery and Intelligence", "연도": "1950", "학술지": "Mind", ...}
"""
import os, re, sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from 도구.글_도구 import 마크다운_지우기, 비슷한_정도
from 도구 import 웹_도구
from 도구.결과 import 검사AI_값들
import 설정

_칸 = ["제목", "저자", "연도", "학술지", "권", "호", "DOI"]
_DOI = r"10\.\d{4,9}/[^\s,;)\]>\"']+"


def _줄_값(줄, 이름표):
    m = re.search(rf"(?:{이름표})\s*[:：]\s*(.+)", 줄)
    return m.group(1).strip(" .") if m else ""


def _권호(글):
    권 = re.search(r"제?\s*(\d+)\s*권|Vol(?:ume)?\.?\s*(\d+)", 글, re.I)
    호 = re.search(r"제?\s*(\d+)\s*호|(?<![A-Za-z])No\.?\s*(\d+)|Issue\s*(\d+)", 글, re.I)
    return (next((g for g in 권.groups() if g), "") if 권 else "", next((g for g in 호.groups() if g), "") if 호 else "")


def 자료_뽑기(답변):
    """프로그램 규칙으로 인용 자료 뽑기 (검사 AI가 없을 때 씀)"""
    줄들 = [마크다운_지우기(l).strip(" -•\t") for l in (답변 or "").splitlines()]
    자료들, 지금 = [], None
    for 줄 in 줄들:
        제목 = _줄_값(줄, r"(?:논문|책|기사|자료)?\s*제목")
        if 제목:
            if 지금 and 지금.get("제목"):
                자료들.append(지금)
            지금 = {"제목": re.sub(r"\s*\(.*?\)\s*$", "", 제목).strip("「」『』“”\"' ")}
            continue
        if 지금 is None:
            지금 = {}
        for 칸, 이름표 in (("저자", r"저자|지은이|저술"), ("학술지", r"학술지|저널|게재지|수록지"),
                        ("연도", r"(?:발표|출판|발행|게재)?\s*연도")):
            값 = _줄_값(줄, 이름표)
            if 값 and not 지금.get(칸):
                지금[칸] = re.sub(r"\s*\(.*?\)\s*$", "", 값).strip("「」『』“”\"' ")
        if re.search(r"권|호|Vol|No\.", 줄):
            권, 호 = _권호(줄)
            지금.setdefault("권", 권) if 권 else None
            지금.setdefault("호", 호) if 호 else None
    if 지금:
        자료들.append(지금)
    글 = 마크다운_지우기(답변)
    if not any(x.get("제목") for x in 자료들):                 # '제목:' 표시가 없으면 「…」, “…” 안의 글을 제목으로
        후보 = re.findall(r"[「“\"]([^」”\"]{8,200})[」”\"]", 글) + re.findall(r"(?<![*\w])\*([^*\n]{10,200})\*(?!\*)", 답변 or "")
        if 후보:
            남은 = 자료들[0] if 자료들 else {}
            자료들 = [dict(남은, 제목=후보[0].strip())]
    for x in 자료들:
        if not x.get("연도"):
            연도 = re.search(r"(?<!\d)(19\d{2}|20\d{2})(?!\d)", 글)
            x["연도"] = 연도.group(1) if 연도 else ""
        if not x.get("학술지"):
            학술지 = re.search(r"『([^』]{2,60})』", 글)
            x["학술지"] = 학술지.group(1) if 학술지 else ""
        if not x.get("권") and not x.get("호"):
            x["권"], x["호"] = _권호(글)
        DOI = re.search(_DOI, 답변 or "")
        x["DOI"] = x.get("DOI") or (DOI.group(0).rstrip(".") if DOI else "")
        for 칸 in _칸:
            x[칸] = str(x.get(칸) or "").strip()
        x["연도"] = (re.findall(r"(?:19|20)\d{2}|1[5-8]\d{2}", x["연도"]) or [""])[0]
        x["DOI"] = x["DOI"].strip("*_`.")
        x["제목"] = x["제목"].strip("*_` ").rstrip(".")
    return [x for x in 자료들 if x.get("제목") or x.get("DOI")]


def 자료_모으기(자료):
    """검사 AI가 뽑은 자료 목록 중 가장 많은 항목을 채운 것을 쓰고, 없으면 프로그램 규칙으로 뽑음"""
    AI목록 = [목록 for 목록 in 검사AI_값들(자료, "유형별_검사", "자료") if isinstance(목록, list) and 목록]
    if AI목록:
        가장 = max(AI목록, key=lambda 목록: sum(bool(str(v).strip()) for x in 목록 if isinstance(x, dict) for v in x.values()))
        목록 = [{칸: str(x.get(칸) or "").strip() for 칸 in _칸} for x in 가장 if isinstance(x, dict)]
        목록 = [x for x in 목록 if x["제목"] or x["DOI"]]
        if 목록:
            return 목록, "검사 AI"
    return 자료_뽑기(자료.get("답변", "")), "프로그램 규칙"


def 없다고_했나(답변):
    앞 = " ".join([l for l in (답변 or "").splitlines() if l.strip()][:3])
    return bool(re.search(r"존재하지 않|확인되지 않|찾을 수 없|실재하지 않|없는 논문|없는 자료", 앞)
                and re.search(r"논문|자료|문헌|책|기록|연구", 앞))


def 같은_논문_정도(가, 나):
    정리 = lambda s: re.sub(r"[^가-힣a-z0-9]", "", (s or "").lower())
    if 정리(가) and 정리(가) == 정리(나):
        return 1.0
    return 비슷한_정도(가, 나)


def 찾아보기(자료하나):
    """돌려주는 값: {"판정": 있음/비슷한 것만 있음/찾지 못함/DOI 없음/확인 불가, "찾은_논문": dict 또는 None, "비슷한_정도": 0~1}"""
    DOI = 자료하나.get("DOI", "")
    DOI결과 = 웹_도구.DOI_있나(DOI) if DOI else None
    후보 = 웹_도구.논문_찾기(자료하나.get("제목", ""), DOI)
    if DOI결과 is False and not 자료하나.get("제목"):
        return {"판정": "DOI 없음", "찾은_논문": None, "비슷한_정도": 0.0}
    if 후보 is None:
        return {"판정": "DOI 없음" if DOI결과 is False else "확인 불가", "찾은_논문": None, "비슷한_정도": 0.0}
    if not 자료하나.get("제목") and 후보:                    # 제목 없이 DOI로만 찾은 경우
        return {"판정": "있음", "찾은_논문": 후보[0], "비슷한_정도": 1.0}
    점수, 최고 = max(((같은_논문_정도(자료하나["제목"], c.get("제목", "")), c) for c in 후보), default=(0.0, None),
                   key=lambda t: t[0])
    if 점수 >= 설정.논문같음_기준:
        판정 = "있음"
    elif 점수 >= 설정.논문비슷_기준:
        판정 = "비슷한 것만 있음"
    else:
        판정 = "찾지 못함"
    if DOI결과 is False:
        판정 = "DOI 없음"
    return {"판정": 판정, "찾은_논문": 최고, "비슷한_정도": round(점수, 2)}

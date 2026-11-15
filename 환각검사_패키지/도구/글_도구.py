# -*- coding: utf-8 -*-
"""
여러 기준이 함께 쓰는 '글 다루기' 도구 모음

  글자쌍(글)            : 글을 '글자 2개씩 묶음'의 집합으로 바꿈. 조사·어미가 달라도 비교할 수 있게 하려고 씀
                          예) "자전거를" → {자전, 전거, 거를}
  덮는_비율(가, 나)      : 가의 글자쌍 중 나에 들어 있는 비율 (0~1)
  비슷한_정도(가, 나)    : 두 글이 얼마나 비슷한지 (0~1, 다이스 계수)
  마크다운_지우기(글)    : **굵게**, #제목, $수식$ 같은 표시를 지움
  문장_나누기(글)        : 글을 문장 목록으로 나눔
  숫자_뽑기(글)          : 글 속 숫자를 모두 뽑음 (쉼표 제거)
  최종답_뽑기(답변, 유형): 답변에서 '최종 답' 부분을 뽑음
  같은_답인가(가, 나, 유형): 두 최종 답이 같은지 (True / False / None=판단 못 함)
  코드_뽑기(질문)        : 질문에서 파이썬 코드 부분만 뽑음
"""
import re

# ------------------------------------------------------------------ 기본 도구
def 마크다운_지우기(글):
    글 = 글 or ""
    글 = re.sub(r"\$+([^$]*)\$+", r"\1", 글)                 # $수식$
    글 = 글.replace("\\times", "×").replace("\\div", "÷").replace("\\cdot", "×")
    글 = re.sub(r"\\frac\{([^}]*)\}\{([^}]*)\}", r"(\1)/(\2)", 글)
    글 = re.sub(r"\\[a-zA-Z]+", "", 글)
    글 = re.sub(r"[*#>`|_]", "", 글)
    return 글


def 글자쌍(글):
    글 = re.sub(r"[^가-힣a-z0-9]", "", (글 or "").lower())
    return {글[i:i + 2] for i in range(len(글) - 1)}


def 덮는_비율(가, 나):
    a, b = 글자쌍(가), 글자쌍(나)
    return len(a & b) / len(a) if a else 0.0


def 비슷한_정도(가, 나):
    a, b = 글자쌍(가), 글자쌍(나)
    return 2 * len(a & b) / (len(a) + len(b)) if a and b else 0.0


def 문장_나누기(글, 최소_글자=8):
    글 = 마크다운_지우기(글)
    조각 = re.split(r"(?<=[.!?다요])\s+|\n+", 글)
    return [x.strip(" -•\t") for x in 조각 if len(re.sub(r"\s", "", x)) >= 최소_글자]


def 숫자_뽑기(글):
    결과 = []
    for m in re.findall(r"-?\d[\d,]*\.?\d*", 글 or ""):
        m = m.replace(",", "").rstrip(".")
        try:
            결과.append(float(m))
        except ValueError:
            pass
    return 결과


# ------------------------------------------------------------------ 최종 답 뽑기
def 최종답_뽑기(답변, 유형=""):
    """답변에서 최종 답이라고 볼 수 있는 짧은 부분을 뽑음 (규칙 기반이라 완벽하지 않음)"""
    원문 = (답변 or "").strip()
    if not 원문:
        return ""
    if 유형 == "코드 결과형":
        블록 = re.search(r"```[a-zA-Z]*\n(.*?)```", 원문, re.S)
        if 블록:
            return 블록.group(1).strip()
        return 원문.splitlines()[0].strip()
    # 앞부분의 **굵은 글씨**를 최종 답으로 봄
    앞부분 = "\n".join(원문.splitlines()[:3])
    굵게 = re.findall(r"\*\*(.+?)\*\*", 앞부분)
    if 굵게:
        return 마크다운_지우기(굵게[0]).strip()
    글 = 마크다운_지우기(원문)
    for 패턴 in (r"(?:정답|최종 ?답|답)\s*[은는:]\s*(.+?)(?:입니다|이다|예요|이에요|\.|\n|$)",
                 r"따라서[, ]+(.+?)(?:입니다|이다|\.|\n|$)"):
        m = re.search(패턴, 글)
        if m and m.group(1).strip():
            return m.group(1).strip()[:80]
    첫문장 = 문장_나누기(글, 1)
    return 첫문장[0][:80] if 첫문장 else 글[:80]


def _정리(글):
    글 = 마크다운_지우기(글).lower()
    글 = re.sub(r"(입니다|이에요|예요|이다|임|요)\.?$", "", 글.strip())
    return re.sub(r"[^가-힣a-z0-9]", "", 글)


def 같은_답인가(가, 나, 유형=""):
    """두 최종 답이 같은지. 숫자가 있으면 숫자로, 짧은 글이면 글로 비교. 판단이 어려우면 None"""
    if not 가 or not 나:
        return None
    오류가, 오류나 = set(re.findall(r"[A-Za-z]+Error", 가)), set(re.findall(r"[A-Za-z]+Error", 나))
    if 오류가 or 오류나:                      # 오류 이름이 있으면 오류 이름으로 비교
        return 오류가 == 오류나
    수가, 수나 = 숫자_뽑기(가), 숫자_뽑기(나)
    if 유형 in ("수치 계산형", "코드 결과형") or (수가 and 수나):
        if 수가 and 수나:
            if 유형 == "코드 결과형":
                return 수가 == 수나 and _정리(가) == _정리(나) if len(_정리(가)) < 40 else 수가 == 수나
            return abs(수가[0] - 수나[0]) <= 1e-6 * max(1, abs(수나[0]))
        if 유형 == "코드 결과형":
            return _정리(가) == _정리(나)
    a, b = _정리(가), _정리(나)
    if not a or not b:
        return None
    if a == b:
        return True
    짧은, 긴 = sorted((a, b), key=len)
    if len(긴) <= 30:
        return 짧은 in 긴 if len(짧은) >= 2 else False
    return None     # 긴 서술형은 규칙으로 판단하지 않음 → 검사 AI에 맡김


# ------------------------------------------------------------------ 코드 뽑기
def 코드_뽑기(질문):
    """질문에서 파이썬 코드만 뽑음. ```로 감싼 부분이 있으면 그것, 없으면 첫 빈 줄 뒤의 내용"""
    질문 = 질문 or ""
    블록 = re.search(r"```[a-zA-Z]*\n(.*?)```", 질문, re.S)
    if 블록:
        return 블록.group(1).strip("\n")
    줄들 = 질문.splitlines()
    for i, 줄 in enumerate(줄들):
        if not 줄.strip() and i + 1 < len(줄들):
            나머지 = "\n".join(줄들[i + 1:]).strip("\n")
            if re.search(r"print\(|=|def |for |import ", 나머지):
                return 나머지
    코드줄 = [줄 for 줄 in 줄들 if re.search(r"print\(|^\s*\w+\s*=|^\s*(def|for|if|while|import|return) ", 줄)]
    코드 = "\n".join(코드줄)
    # 'print(sum([1,2,3])) 의 출력은?' 처럼 코드 뒤에 질문 글이 붙어 있으면 문법 오류가 나요.
    # 원래 코드가 문법 오류이고 따옴표·주석 밖에 한글이 있을 때만, 한글부터 끝까지 잘라 보고 문법이 맞으면 그것을 써요.
    # (진짜 문법 오류를 묻는 코드는 한글이 없어서 그대로 남아요)
    if 코드 and not _문법_맞나(코드):
        다듬음 = "\n".join(_한글_앞까지(줄) for 줄 in 코드줄).strip("\n")
        if 다듬음 and 다듬음 != 코드 and _문법_맞나(다듬음):
            return 다듬음
    return 코드


def _문법_맞나(코드):
    """코드를 실행하지 않고 문법만 확인"""
    try:
        compile(코드, "<질문>", "exec")
        return True
    except (SyntaxError, ValueError):
        return False


def _한글_앞까지(줄):
    """따옴표 안과 # 주석이 아닌 곳에 처음 나오는 한글 앞까지만 남김"""
    따옴표 = None
    for i, 글자 in enumerate(줄):
        if 따옴표:
            if 글자 == 따옴표:
                따옴표 = None
        elif 글자 in "\"'":
            따옴표 = 글자
        elif 글자 == "#":
            return 줄
        elif "가" <= 글자 <= "힣":
            return 줄[:i].rstrip()
    return 줄


# ------------------------------------------------------------------ 두 답변의 핵심이 같은지 (③에서 사용)
def _굵은글씨(글):
    return " ".join(re.findall(r"\*\*(.+?)\*\*", 글 or ""))


def 머리말(글, 문장수=2):
    """답변의 앞부분(처음 문장들 + 굵은 글씨) — 대부분의 AI는 결론을 먼저 말함"""
    return " ".join(문장_나누기(글, 2)[:문장수]) + " " + 마크다운_지우기(_굵은글씨(글))


def _후보_숫자(글):
    줄들 = [줄 for 줄 in (글 or "").splitlines() if 줄.strip()]
    후보 = 숫자_뽑기(_굵은글씨(글))
    if 줄들:
        후보 += 숫자_뽑기(줄들[0]) + 숫자_뽑기(줄들[-1])
    return set(후보)


def _코드_출력_후보(글):
    블록들 = [b.strip() for b in re.findall(r"```[a-zA-Z]*\n(.*?)```", 글 or "", re.S)]
    굵게 = re.findall(r"\*\*(.+?)\*\*", 글 or "")[:2]
    줄들 = [줄.strip() for 줄 in (글 or "").splitlines() if 줄.strip() and not 줄.strip().startswith("```")]
    첫줄 = [re.sub(r"^(실행 )?(출력 ?결과|출력|결과)(는|은)?\s*[:：]?\s*", "", 줄들[0])] if 줄들 else []
    후보 = [_정리(x) for x in 블록들 + 굵게 + 첫줄]
    return [x for x in 후보 if x and not re.fullmatch(r"(출력결과|다음과같습니다|출력결과는다음과같습니다|설명|해설)", x)]


def 핵심이_같은가(가, 나, 유형=""):
    """두 답변의 핵심(최종 답)이 같은지. True / False / None(규칙으로 판단 못 함 → 검사 AI에 맡김)"""
    if not 가 or not 나:
        return None
    오류가 = set(re.findall(r"[A-Za-z]+Error", 머리말(가, 3)))
    오류나 = set(re.findall(r"[A-Za-z]+Error", 머리말(나, 3)))
    if 유형 == "코드 결과형":
        if 오류가 or 오류나:
            return 오류가 == 오류나
        a_전체, b_전체 = _정리(가), _정리(나)
        a후보, b후보 = _코드_출력_후보(가), _코드_출력_후보(나)
        if not a후보 or not b후보:
            return None
        return any(x in a_전체 for x in b후보) and any(x in b_전체 for x in a후보)
    if 유형 == "수치 계산형":
        a후보, b후보 = _후보_숫자(가), _후보_숫자(나)
        a전체, b전체 = set(숫자_뽑기(가)), set(숫자_뽑기(나))
        if not a후보 or not b후보:
            return None
        return bool(a후보 & b전체) and bool(b후보 & a전체)
    # 서술형(사실, 논리, 출처, 지문): 앞부분의 숫자(연도 등)가 있으면 숫자로, 없으면 표현이 얼마나 겹치는지로
    a머리, b머리 = 머리말(가), 머리말(나)
    a수, b수 = set(숫자_뽑기(a머리)), set(숫자_뽑기(b머리))
    if a수 and b수:
        return bool(a수 & b수)
    겹침 = 비슷한_정도(a머리, b머리)
    if 겹침 >= 0.35:
        return True
    return None

# -*- coding: utf-8 -*-
"""
AI 호출 도구 (OpenRouter)

이 파일 하나에서 모든 AI 호출을 해요. 기준 파일들은 AI를 직접 부르지 않고 여기 함수를 써요.

  AI_부르기(모델_ID, 질문, 온도)        : AI 하나에게 질문 하나를 보내고 답을 글로 받음
  여러_모델에_묻기(모델_ID들, 질문)      : 여러 AI에게 같은 질문을 동시에 보냄 (상위 3개 모델에 다시 묻기)
  검사AI_실행(모델_ID들, 자료)          : 검사 AI 지시문을 여러 AI에 보내고 판정(JSON)을 받아 정리
  검사_지시문_만들기(자료)              : 검사 AI에게 보낼 지시문을 만듦 (화면에 보여 주거나 보고서에 넣을 때도 사용)
  키가_있나()                          : API 키가 설정되어 있는지
  사용량_보기()                        : 지금까지 쓴 AI 호출 수·토큰 수 (검사 한 번의 비용을 가늠할 때)
  크레딧_보기()                        : 이 API 키의 사용 한도와 남은 금액 (앱의 '🔬 정밀 검사' 메뉴)

API 키: 환경 변수 OPENROUTER_API_KEY 에서 읽어요. 코드나 화면에 키를 쓰지 마세요.
  - 윈도우 명령 프롬프트: setx OPENROUTER_API_KEY "키"  (설정 후 명령 프롬프트를 닫고 다시 열기)
  - Streamlit 앱: .streamlit/secrets.toml 에 OPENROUTER_API_KEY = "키" (이 파일은 절대 공유·업로드하지 않기)

추가 설치 없이 파이썬 기본 기능(urllib)만 써요.
"""
import json, os, re, threading, time, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

import 설정


def _키():
    키 = os.environ.get(설정.API_키_환경변수, "").strip()
    if not 키:
        try:                                    # Streamlit 앱에서 실행할 때는 secrets 에서 읽기
            import streamlit as st
            키 = str(st.secrets.get(설정.API_키_환경변수, "")).strip()
        except Exception:
            키 = ""
    return 키


def 키가_있나():
    return bool(_키())


class AI오류(Exception):
    pass


# 이번 실행에서 쓴 AI 호출 수와 토큰 수 (검사 한 번에 얼마나 썼는지 보고서에 보여 주려고 모아 둠)
사용량 = {"호출": 0, "실패": 0, "입력_토큰": 0, "출력_토큰": 0, "비용": 0.0}
_사용량_잠금 = threading.Lock()


def 사용량_보기():
    with _사용량_잠금:
        return dict(사용량)


def _사용량_더하기(받음=None, 실패=False):
    with _사용량_잠금:
        사용량["호출"] += 1
        if 실패:
            사용량["실패"] += 1
            return
        쓴것 = (받음 or {}).get("usage") or {}
        사용량["입력_토큰"] += int(쓴것.get("prompt_tokens") or 0)
        사용량["출력_토큰"] += int(쓴것.get("completion_tokens") or 0)
        try:                                    # OpenRouter가 비용을 알려 줄 때만 더함 (없으면 0)
            사용량["비용"] += float(쓴것.get("cost") or 0)
        except (TypeError, ValueError):
            pass


def AI_부르기(모델_ID, 질문, 온도=None, 최대_토큰=None):
    """AI 하나에게 질문을 보내고 답(글)을 돌려줌. 실패하면 AI오류를 일으킴
    잠깐 막힘(HTTP 429), 서버 오류(5xx), 연결 문제·시간 초과는 설정.AI_재시도_횟수 만큼 쉬었다가 다시 시도해요.
    키가 틀림(401), 크레딧 부족(402), 잘못된 요청(400)은 다시 해도 똑같아서 바로 멈춰요."""
    키 = _키()
    if not 키:
        raise AI오류("API 키가 없어요. 환경 변수 OPENROUTER_API_KEY 를 설정해 주세요.")
    내용 = {"model": 모델_ID, "messages": [{"role": "user", "content": 질문}],
            "max_tokens": 최대_토큰 or 설정.최대_토큰}
    if 온도 is not None:
        내용["temperature"] = 온도
    if getattr(설정, "AI_빠른_서버_우선", False):
        내용["provider"] = {"sort": "throughput"}       # 같은 모델 중 가장 빠른 서버로 (설정.py 참고)
    재시도 = getattr(설정, "AI_재시도_횟수", 0)
    for 번째 in range(재시도 + 1):
        요청 = urllib.request.Request(
            설정.API_주소, data=json.dumps(내용).encode("utf-8"), method="POST",
            headers={"Authorization": f"Bearer {키}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(요청, timeout=설정.AI_시간제한_초) as 응답:
                받음 = json.loads(응답.read().decode("utf-8"))
            break
        except urllib.error.HTTPError as e:
            if (e.code == 429 or e.code >= 500) and 번째 < 재시도:
                time.sleep(2 * (번째 + 1))
                continue
            _사용량_더하기(실패=True)
            raise AI오류(f"{모델_ID} 호출 실패 (HTTP {e.code}): {e.read().decode('utf-8', 'ignore')[:200]}")
        except Exception as e:                  # 연결 문제, 시간 초과
            if 번째 < 재시도:
                time.sleep(2 * (번째 + 1))
                continue
            _사용량_더하기(실패=True)
            raise AI오류(f"{모델_ID} 호출 실패: {e}")
    _사용량_더하기(받음)
    try:
        return 받음["choices"][0]["message"]["content"] or ""
    except (KeyError, IndexError, TypeError):
        raise AI오류(f"{모델_ID} 응답 형식이 이상해요: {str(받음)[:200]}")


def 여러_모델에_묻기(모델_ID들, 질문, 온도=None):
    """여러 AI에게 같은 질문을 동시에 보냄. 실패한 모델 자리에는 None"""
    def 하나(모델_ID):
        try:
            return AI_부르기(모델_ID, 질문, 온도)
        except AI오류:
            return None
    with ThreadPoolExecutor(max_workers=len(모델_ID들) or 1) as 일꾼:
        return list(일꾼.map(하나, 모델_ID들))


# ------------------------------------------------------------------ 검사 AI 지시문
유형별_검사 = {
    "사실 지식형": (
        "답변의 핵심 정보(누가, 언제, 어디서, 무엇)를 뽑고, 위키백과에서 찾을 검색어 하나를 정하라. "
        "그리고 질문이 묻지 않았는데 답변이 덧붙인 세부 사실을 모두 뽑아 각각 맞음/틀림/확인 불가로 판정하라.",
        '{"핵심정보": [{"항목": "연도", "값": "1919"}], "검색어": "...", '
        '"덧붙인_사실": [{"문장": "...", "판정": "맞음/틀림/확인 불가"}]}'),
    "수치 계산형": (
        "답변의 최종 답(숫자와 단위)을 뽑고, 질문이 요구한 단위·반올림·형식을 지켰는지 판정하라.",
        '{"최종답": "...", "단위": "...", "조건_지킴": "예/아니오/해당 없음", "근거": "..."}'),
    "논리 추론형": (
        "질문의 조건을 번호를 붙여 모두 뽑고, 답변의 최종 결론이 각 조건을 만족하는지 만족/위반으로 판정하라. "
        "또한 질문에 없는 정보를 사실처럼 단정한 문장이 있으면 모두 뽑아라.",
        '{"조건": [{"번호": 1, "내용": "...", "판정": "만족/위반"}], "임의_가정": ["..."]}'),
    "출처 인용형": (
        "답변이 제시한 자료(논문, 책, 기사)마다 제목, 저자, 연도, 학술지, 권, 호, DOI를 그대로 뽑아라. "
        "자료가 실제로 있는지는 판단하지 말고 뽑기만 하라. 없는 항목은 빈칸으로 둔다.",
        '{"자료": [{"제목": "", "저자": "", "연도": "", "학술지": "", "권": "", "호": "", "DOI": ""}]}'),
    "지문 이해형": (
        "지문에 없는 내용을 덧붙인 문장과, 지문의 중요한 내용을 빠뜨리거나 다르게 바꾼 부분을 각각 모두 뽑아라.",
        '{"덧붙인_문장": ["..."], "빠뜨리거나_바꾼_내용": ["..."]}'),
    "코드 결과형": (
        "답변이 말한 최종 출력값을 그대로 뽑고, 답변이 오류(에러)가 난다고 했는지 판정하라.",
        '{"답변_출력": "...", "오류라고_함": "예/아니오"}'),
}

공통_지시문 = """너는 AI 답변의 환각을 검사하는 검사관이다. 아래 [질문]과 [검사할 답변]을 읽고, 정해진 형식(JSON)으로만 답하라.
판단은 [질문]에 적힌 내용과 일반적으로 확인된 사실만 근거로 한다. 확실하지 않으면 "확인 불가"로 답한다.
JSON 밖에는 아무 글도 쓰지 마라.

[답변 유형] {유형}
[질문]
{질문}

[검사할 답변]
{답변}

[참고: 같은 질문에 대한 다른 AI 답변들]
{참고답변}

다음 항목을 검사하라.
1. 답변_거부: 답변이 질문에 답하기를 거부했는가? ("예"/"아니오")
2. 질문_일치: 답변이 질문이 묻는 것에 답했는가? 질문의 조건을 바꾸거나 질문에 없는 조건을 덧붙였는가? ("문제 있음"/"문제 없음", 근거 한 문장)
3. 앞뒤_모순: 답변 안에서 숫자, 이름, 결론이 앞뒤로 바뀌거나 서로 모순되는 곳이 있는가? ("있음"/"없음", 해당 문장)
4. 참고답변_일치: [검사할 답변]의 핵심 결론이 [참고] 답변 1, 2, 3 각각과 같은가? (순서대로 "예"/"아니오" 목록)
5. 유형별_검사: {유형별설명}

출력 형식:
{{"답변_거부": "예/아니오", "질문_일치": {{"판정": "...", "근거": "..."}}, "앞뒤_모순": {{"판정": "...", "문장": "..."}}, "참고답변_일치": ["예", "아니오", "예"], "유형별_검사": {유형별형식}}}"""


def 검사_지시문_만들기(자료):
    유형 = 자료.get("유형", "")
    설명, 형식 = 유형별_검사.get(유형, ("해당 없음", "{}"))
    추가 = 자료.get("추가_유형")                   # 유형이 애매하면 2순위 유형의 검사도 한 번에 물어봄 (AI 호출 수는 그대로)
    if 추가 in 유형별_검사 and 추가 != 유형:
        설명2, 형식2 = 유형별_검사[추가]
        설명 = f"(이 답변은 {유형}인지 {추가}인지 애매하니 두 가지를 모두 하라) (가) {설명} (나) {설명2}"
        형식 = 형식[:-1] + ", " + 형식2[1:]          # 두 유형의 항목 이름이 겹치지 않아서 한 JSON으로 합칠 수 있음
        유형 = f"{유형} 또는 {추가}"
    참고 = "\n\n".join(f"[참고 {i}]\n{(a or '(받지 못함)')[:3000]}"
                      for i, a in enumerate(자료.get("상위모델_답변들") or [], 1)) or "(없음)"
    return 공통_지시문.format(유형=유형, 질문=자료.get("질문", ""), 답변=자료.get("답변", ""),
                         참고답변=참고, 유형별설명=설명, 유형별형식=형식)


def JSON_뽑기(글):
    """AI 답에서 JSON 부분만 꺼냄. 실패하면 None"""
    if not 글:
        return None
    글 = re.sub(r"```(?:json)?", "", 글)
    시작, 끝 = 글.find("{"), 글.rfind("}")
    if 시작 < 0 or 끝 <= 시작:
        return None
    try:
        return json.loads(글[시작:끝 + 1])
    except json.JSONDecodeError:
        try:                                     # 흔한 실수(끝의 쉼표) 고쳐서 다시 시도
            return json.loads(re.sub(r",\s*([}\]])", r"\1", 글[시작:끝 + 1]))
        except json.JSONDecodeError:
            return None


def 검사AI_실행(모델_ID들, 자료):
    """검사 AI들의 판정 목록을 돌려줌. 실패하거나 JSON이 아닌 답은 빠짐"""
    지시문 = 검사_지시문_만들기(자료)
    답들 = 여러_모델에_묻기(모델_ID들, 지시문, 온도=설정.검사AI_온도)
    판정들 = []
    for 모델_ID, 답 in zip(모델_ID들, 답들):
        판정 = JSON_뽑기(답)
        if isinstance(판정, dict):
            판정["_모델"] = 모델_ID
            판정들.append(판정)
    return 판정들


def 크레딧_보기():
    """지금 쓰는 API 키의 사용 한도와 남은 금액(달러)을 OpenRouter에 물어봄 (앱의 '🔬 정밀 검사' 메뉴에서 씀)
    돌려주는 것: {"한도": 5.0 또는 None(한도 없음), "남은_금액": 3.77 또는 None, "쓴_금액": 1.23, "오늘_쓴_금액": 0.1}
    키 자체는 돌려주지 않아요. 실패하면 AI오류를 일으켜요. (계정 전체 잔액은 관리용 키로만 볼 수 있어서 여기서는 안 봐요)"""
    키 = _키()
    if not 키:
        raise AI오류("API 키가 없어요.")
    요청 = urllib.request.Request(설정.API_키정보_주소, headers={"Authorization": f"Bearer {키}"})
    try:
        with urllib.request.urlopen(요청, timeout=min(5, 설정.웹_시간제한_초)) as 응답:   # 화면이 오래 멈추지 않게 5초까지만
            받음 = json.loads(응답.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise AI오류(f"크레딧 확인 실패 (HTTP {e.code})")
    except Exception as e:                      # 연결 문제, 시간 초과
        raise AI오류(f"크레딧 확인 실패: {e}")
    자료 = (받음 or {}).get("data") or {}

    def 숫자(이름):
        try:
            return None if 자료.get(이름) is None else float(자료[이름])
        except (TypeError, ValueError):
            return None
    return {"한도": 숫자("limit"), "남은_금액": 숫자("limit_remaining"),
            "쓴_금액": 숫자("usage"), "오늘_쓴_금액": 숫자("usage_daily")}

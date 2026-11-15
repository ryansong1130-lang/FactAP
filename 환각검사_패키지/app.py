# -*- coding: utf-8 -*-
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 인터넷 배포(Streamlit Community Cloud)용 시작 파일
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

■ 언제 쓰나요?
  Streamlit Cloud 에 앱을 올릴 때 'Main file path' 에 app.py 를 적어요.
  내 컴퓨터에서 쓸 때는 지금처럼 앱_열기.bat (검은 창 없이: 바탕화면 FactAP 아이콘) 이나 streamlit run 앱_화면.py 를 쓰면 돼요.
  (파일 이름을 영어로 한 이유: 배포 사이트에서 한글 파일 이름 때문에 생길 수 있는 문제를 피하려고)

■ 하는 일
  FactAP 앱 화면(앱_화면.py)을 그대로 실행하되, 인터넷에 공개할 때 필요한 안전 설정만 먼저 켜요.
  검사 방법(기준, 점수, 등급)은 하나도 바꾸지 않아요.
  1) 코드 실행 끄기: 모르는 사람이 넣은 코드를 서버에서 실행하지 않게 해요.
     (서버에서 코드를 실행하면 API 키를 훔쳐 가는 코드도 실행될 수 있어요. 코드 ⑤는 '확인 불가'가 되고,
      코드 ⑥과 공통 기준은 검사 AI로 판단해요)
  2) 검사 기록 저장 끄기: 사용자가 넣은 질문·답변을 서버에 쌓지 않아요.
  3) 하루 AI 검사 한도: 앱 전체에서 하루에 AI 검사를 몇 번까지 할지 정해요 (기본 30번).
     한도를 넘으면 AI 없이 '간이 검사'로 바꾸고 화면에 알려 줘요. 날짜가 바뀌면(한국 시간) 다시 0부터 세요.
  4) 접속 비밀번호 (선택): Secrets 에 APP_PASSWORD 를 넣었을 때만 비밀번호를 물어요.

■ Streamlit Cloud 의 Secrets 칸에 넣는 것 (키는 여기에만 넣고, 코드·깃허브·보고서에는 절대 쓰지 않기)
  OPENROUTER_API_KEY = "sk-or-로 시작하는 키"
  DAILY_AI_LIMIT = 30                 # (선택) 하루 AI 검사 한도. 안 넣으면 30
  APP_PASSWORD = "비밀번호"            # (선택) 넣으면 비밀번호를 아는 사람만 들어올 수 있어요
  APP_URL = "https://○○○.streamlit.app"  # (선택) 오른쪽 위 📤 공유 메뉴가 앱 주소를 못 찾을 때만 (비밀 아님)
"""
import datetime
import os
import runpy
import sys
import threading

import streamlit as st

폴더 = os.path.dirname(os.path.abspath(__file__))
if 폴더 not in sys.path:
    sys.path.insert(0, 폴더)

import 설정        # noqa: E402  (폴더를 sys.path 에 넣은 뒤에 불러와야 해요)
import 검사_실행    # noqa: E402

기본_하루_한도 = 30
한국_시간 = datetime.timezone(datetime.timedelta(hours=9))


def _비밀값(이름, 기본=None):
    """Streamlit Cloud 의 Secrets(또는 환경 변수)에서 값을 읽어요. 없으면 기본값."""
    try:
        if 이름 in st.secrets:
            return st.secrets[이름]
    except Exception:            # secrets 파일이 아예 없을 때
        pass
    return os.environ.get(이름, 기본)


# ------------------------------------------------------------------ 1), 2) 배포용 안전 설정
설정.코드_실행_허용 = False
설정.기록_저장 = False

# ------------------------------------------------------------------ 3) 하루 AI 검사 한도
try:
    하루_한도 = int(_비밀값("DAILY_AI_LIMIT", 기본_하루_한도))
except (TypeError, ValueError):
    하루_한도 = 기본_하루_한도


@st.cache_resource
def _오늘_사용량():
    """앱 서버가 켜져 있는 동안 모든 사용자가 함께 쓰는 '오늘 AI 검사 횟수' (새로고침해도 유지)"""
    return {"날짜": None, "횟수": 0, "잠금": threading.Lock()}


def _AI_검사_한_번_쓰기():
    """한도 안이면 횟수를 1 늘리고 True, 한도를 넘었으면 False"""
    사용량 = _오늘_사용량()
    오늘 = datetime.datetime.now(한국_시간).date()
    with 사용량["잠금"]:
        if 사용량["날짜"] != 오늘:
            사용량["날짜"], 사용량["횟수"] = 오늘, 0
        if 사용량["횟수"] >= 하루_한도:
            return False
        사용량["횟수"] += 1
        return True


def _오늘_AI_검사_횟수():
    """(오늘 쓴 AI 검사 횟수, 하루 한도). 앱 화면의 '🔬 정밀 검사' 메뉴(API 크레딧)에 보여 줘요."""
    사용량 = _오늘_사용량()
    오늘 = datetime.datetime.now(한국_시간).date()
    with 사용량["잠금"]:
        return (사용량["횟수"] if 사용량["날짜"] == 오늘 else 0), 하루_한도


설정.하루_AI_사용량_보기 = _오늘_AI_검사_횟수


# 검사_실행.환각_검사 를 한 번 감싸서, AI를 쓰는 검사일 때만 횟수를 세요.
# (앱_화면.py 는 'from 검사_실행 import 환각_검사' 로 불러오므로 감싼 함수를 쓰게 돼요)
원래_검사 = vars(검사_실행).get("_원래_환각_검사", 검사_실행.환각_검사)   # 새로고침마다 두 번 감싸지 않게
검사_실행._원래_환각_검사 = 원래_검사


def 한도_있는_환각_검사(질문, 답변, 출처="", 유형=None, AI_사용=True, *나머지, **이름있는):
    한도_넘음 = False
    if AI_사용 and 검사_실행.AI_호출.키가_있나() and not _AI_검사_한_번_쓰기():
        AI_사용, 한도_넘음 = False, True
    보고서 = 원래_검사(질문, 답변, 출처, 유형, AI_사용, *나머지, **이름있는)
    if 한도_넘음:
        보고서["알림"].insert(0, f"오늘 AI 검사 한도({하루_한도}번)를 다 써서 AI 없이 간이 검사로 했어요. "
                                 "내일(한국 시간 자정 이후) 다시 하면 AI 검사가 돼요.")
        보고서["저장_안_함"] = True        # 앱_화면.py 가 이 결과를 '같은 입력 결과'로 저장하지 않게
    return 보고서


검사_실행.환각_검사 = 한도_있는_환각_검사

# ------------------------------------------------------------------ 화면 설정 (앱_화면.py 보다 먼저 해야 해서 여기서)
원래_페이지_설정 = vars(st).get("_원래_페이지_설정", st.set_page_config)
st._원래_페이지_설정 = 원래_페이지_설정
원래_페이지_설정(page_title="FactAP", page_icon="🔎", layout="centered")
st.set_page_config = lambda *a, **k: None      # 앱_화면.py 안의 같은 설정은 건너뛰어요 (두 번 하면 오류가 날 수 있어서)

# ------------------------------------------------------------------ 4) 접속 비밀번호 (APP_PASSWORD 를 넣었을 때만)
비밀번호 = str(_비밀값("APP_PASSWORD", "") or "")
if 비밀번호 and not st.session_state.get("비밀번호_통과"):
    st.title("FactAP")
    st.caption("AI 답변 환각 위험도 검사")
    입력 = st.text_input("비밀번호를 넣어 주세요", type="password")
    if 입력 == 비밀번호:
        st.session_state["비밀번호_통과"] = True
        st.rerun()
    elif 입력:
        st.error("비밀번호가 달라요.")
    st.stop()

# ------------------------------------------------------------------ 앱 화면 실행
runpy.run_path(os.path.join(폴더, "앱_화면.py"), run_name="__main__")
st.caption(f"인터넷 공개용 설정: 코드 실행 꺼짐 · 검사 기록 저장 꺼짐 · 하루 AI 검사 {하루_한도}번까지")

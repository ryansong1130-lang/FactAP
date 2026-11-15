# -*- coding: utf-8 -*-
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 FactAP 앱 화면 (Streamlit) · 대화형 AI 채팅 + 팩트체크 디자인 (2026-11-15, 결과 디자인 2026-11-16)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

■ 실행 방법 (패키지 폴더에서)
  1) 설치: pip install -r requirements.txt
  2) API 키 넣기: .streamlit/secrets.toml 파일을 만들고 아래 한 줄을 써요. (예시: .streamlit/secrets.toml.예시)
       OPENROUTER_API_KEY = "여기에 키"
     ※ 이 파일은 절대 다른 사람에게 보내거나, 깃허브에 올리거나, 화면을 캡처하지 마세요.
  3) 실행: streamlit run 앱_화면.py   → 브라우저가 열려요.

■ 화면 구성 (ChatGPT·Gemini·Claude 같은 채팅형)
  왼쪽 옆 메뉴: FactAP 로고, '＋ 새 검사'(대화 비우기), '최근 검사' 목록(등급 색 점, 누르면 그 결과를 펼쳐 보여 줌)
  오른쪽 위: '공유' 메뉴 (앱 링크 복사, QR코드, QR코드 그림 내려받기. 내 컴퓨터에서 열었으면 나누는 방법 안내)
             'FactAP 소개' 메뉴 (AI 환각이란?, 기준을 정한 이유, 상위 모델의 종류 등. 글은 앱_소개.py 에서 고쳐요)
             오른쪽 위 메뉴와 예시 카드는 이모티콘 없이, 메뉴 글은 보고서처럼 '~했다/~이다' 문체로 써요 (2026-11-15)
             Streamlit 의 ⋮ 메뉴는 Print, Record screen 만 남기고 숨겨요 (아래 _화면_꾸미기).
  가운데: 처음에는 인사말과 예시 카드, 검사하면 '내 입력(오른쪽 말풍선) → FactAP 결과(왼쪽)'가 대화처럼 쌓여요.
          가장 최근 결과(또는 옆 메뉴에서 고른 결과)만 자세히 펼치고, 나머지는 요약 카드로 보여 줘요.
  아래 입력창 (2026-11-15 대화형): ChatGPT·Gemini 처럼 화면 맨 아래에 입력창 하나만 있어요.
                 ① 질문 → ② AI의 답변 → ③ 출처를 붙여 넣거나 'Fact TAP' → 검사. ('질문: … 답변: …' 으로 한 번에 넣어도 돼요)
                 입력창 위 작은 버튼: 검사 모드(정밀 = AI 사용 / 간이 = AI 없이, 남은 크레딧), 답변 유형, 한 번에 입력(창)
                 (2026-11-16부터 화면의 이모티콘은 모두 Streamlit 의 작은 선 그림(:material/…: 아이콘)이나 CSS 색 점으로 바꿨어요)
  첫 화면: 큰 인사말(뒤에 은은한 빛), 이 앱이 하는 일(교차 확인·위키백과·기준 6개·형광펜), '예시로 해 보기' 카드 4개(유형 꼬리표)
  검사 중: '사실 확인하는 중…' 상자 안에 0~4단계가 차례로 나타나요 (지난 단계는 초록 체크, 지금 단계는 깜박이는 파란 점)
  결과는 '검증 리포트'처럼 보여 줘요 (사실을 검증하는 앱이라서). 2026-11-16 디자인:
        리포트 카드(반원 위험도 계기판: 세 등급 구간 + 바늘이 돌아가며 멈춤, ✓ ! ✕ 도장과 등급, 설명, 기준 N개 결과 막대, 유형 쪽지)
        → 답변 속 문제 문장 형광펜(문장 끝에 찾은 기준 번호) → 그 밖에 확인할 점
        → 검증 항목(체크리스트: 통과·의심·문제·해당 없음 동그라미와 작은 막대, 누르면 근거) → 의심되는 환각 종류(세 칸 카드)
        → 교차 확인(상위 모델 답변) → AI 사용량 → '다시 검사', 결과 내려받기(.txt)
        결과가 나올 때 카드가 살짝 떠오르고 막대가 자라나요 (기기에서 '움직임 줄이기'를 켜면 움직이지 않아요).
        계기판·막대 색과 '통과·의심·문제' 이름은 보여 주기만 할 뿐, 점수 계산(검사_실행.py, 설정.py)과는 상관없어요.
  로고는 '검증'을 뜻하는 방패 + 체크, 색은 파랑 → 청록이에요 (.streamlit/config.toml 의 primaryColor 도 같은 파랑).
  2026-11-16 글자색: 기기가 어두운 모드여도 글자색·바탕색을 밝은 화면 색으로 고정해요 (테마 파일이 없어도 입력칸 글씨, 말풍선,
        작은 설명 글, 메뉴 창, 도움말 글상자가 잘 보이게). _화면_꾸미기() 의 '기기가 어두운 모드여도' 부분이에요.
  유형이 애매하면 두 유형으로 모두 검사해 확률로 섞은 결과와 각 유형의 확률을 보여 줘요 (검사_실행.유형_섞기).
  같은 질문·답변·출처·유형·AI 사용으로 다시 검사하면 저장된 결과를 보여 주고 AI를 다시 부르지 않아요.
  '다시 검사'를 누르면 저장된 결과를 버리고 처음부터 검사해요. AI 호출이 일부 실패한 결과는 저장하지 않아요.
  검사할 때마다 결과를 기록/검사기록.jsonl 에 저장해요 (설정.기록_저장). 나중에 사람 판정을 적어 검증에 써요.
  휴대폰처럼 좁은 화면에서는 옆 메뉴가 접히고 칸이 위아래로 쌓여요.

이 파일은 '예시'예요. 디자인과 문구는 앱 담당 조원이 자유롭게 바꿔도 돼요.
화면 코드는 검사_실행.환각_검사() 의 결과(보고서)만 쓰기 때문에, 기준 파일을 고쳐도 화면은 그대로 동작해요.
"""
import base64, copy, html, io, ipaddress, math, os, re, threading
from urllib.parse import urlparse

import streamlit as st

import 설정
from 검사_실행 import 환각_검사, 기록_남기기, 등급_경계_글, 중요도, 보고서_글
from 도구 import AI_호출
from 도구.글_도구 import 마크다운_지우기
import 앱_소개

앱_이름 = "FactAP"
검사_버튼_이름 = "Fact TAP"
소개_메뉴_이름 = "FactAP 소개"            # 오른쪽 위 메뉴 버튼 이름 (예전 이름 '우리 활동'. 2026-11-15 이모티콘 뺌)
공유_메뉴_이름 = "공유"                    # 오른쪽 위, 소개 메뉴 왼쪽 (2026-11-15 추가)
# 로고: 사실을 '검증'한다는 뜻으로 방패 + 체크 (파랑 → 청록)
_로고_svg = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">'
            '<stop offset="0" stop-color="#1d4ed8"/><stop offset="1" stop-color="#0d9488"/></linearGradient></defs>'
            '<rect width="64" height="64" rx="16" fill="url(#g)"/>'
            '<path d="M32 11 L48.5 17.5 V30 C48.5 41.5 41 49.5 32 53 C23 49.5 15.5 41.5 15.5 30 V17.5 Z" fill="#fff"/>'
            '<path d="M24 31.5 L30 37.5 L41 26.5" fill="none" stroke="#0f766e" stroke-width="5" stroke-linecap="round" stroke-linejoin="round"/></svg>')
로고_그림 = "data:image/svg+xml;base64," + base64.b64encode(_로고_svg.encode()).decode()   # 결과 말풍선 옆 FactAP 그림
등급_코드 = {"문제 없음": "g", "보통": "y", "위험": "r"}         # 등급 색 (g 초록, y 주황, r 빨강). 옆 메뉴 점, 등급 뜻에 씀
판정_아이콘 = {"문제 없음": "✓", "보통": "!", "위험": "✕"}         # 결과 카드의 동그란 판정 도장
환각_뜻 = {"사실 상충": "알려진 사실과 다른 내용", "입력 상충": "질문·지문과 맞지 않는 내용", "맥락 상충": "답변 앞뒤가 맞지 않는 내용"}
최대_보여줄_문장 = 8
최대_저장_결과 = 100                                     # 저장해 둘 검사 결과 수 (넘으면 오래된 것부터 지움)


# ------------------------------------------------------------------ 오른쪽 위 'FactAP 소개' 메뉴
@st.cache_data(show_spinner=False)
def _예선_정확도():
    """상위 모델 표에 넣을 유형별 예선 정확도 (검증/예선_최종 채점 결과.xlsx 에서 한 번만 계산)"""
    return 앱_소개.예선_정확도()


def _활동_창(제목, 글):
    """메뉴 항목을 누르면 가운데에 창(dialog)으로 보여 줘요. 오래된 Streamlit 이면 펼치기로 보여 줘요."""
    if hasattr(st, "dialog"):
        @st.dialog(제목, width="large")
        def 창():
            st.markdown(글)
        창()
    else:
        with st.expander(제목, expanded=True):
            st.markdown(글)


# ------------------------------------------------------------------ 오른쪽 위 '공유' 메뉴
def _설정값(이름):
    """Streamlit Secrets(또는 환경 변수)에서 값을 읽어요. 없으면 빈 글. (키가 아닌 값만 읽어요)"""
    try:
        if 이름 in st.secrets:
            return str(st.secrets[이름]).strip()
    except Exception:                                  # secrets 파일이 아예 없을 때
        pass
    return os.environ.get(이름, "").strip()


def _공유_주소():
    """다른 사람에게 보낼 앱 주소.
    Secrets(또는 환경 변수)에 APP_URL 을 넣었으면 그 주소, 아니면 지금 브라우저에 열린 주소예요.
    Streamlit Cloud 는 앱을 '주소/~/+/' 안쪽 창에서 돌려서, 그 뒷부분을 잘라 내요."""
    주소 = _설정값("APP_URL")
    if not 주소:
        try:
            주소 = str(getattr(st.context, "url", "") or "")
        except Exception:
            주소 = ""
    if not 주소:
        try:
            호스트 = st.context.headers.get("Host", "")
            if 호스트:
                주소 = ("http://" if 호스트.startswith(("localhost", "127.")) else "https://") + 호스트
        except Exception:
            pass
    주소 = 주소.split("?")[0].split("#")[0]
    if "/~/+" in 주소:
        주소 = 주소.split("/~/+")[0]
    return 주소.rstrip("/")


def _내_컴퓨터_주소인가(주소):
    """localhost, 127.0.0.1, 192.168.… 처럼 다른 사람이 열 수 없는 주소면 True."""
    호스트 = (urlparse(주소).hostname or "").lower()
    if not 호스트 or 호스트 in ("localhost", "0.0.0.0") or 호스트.endswith(".local"):
        return True
    try:
        ip = ipaddress.ip_address(호스트)
        return ip.is_private or ip.is_loopback or ip.is_link_local
    except ValueError:
        return False


@st.cache_data(show_spinner=False)
def _QR코드(주소):
    """주소의 QR코드: (화면에 보일 그림 주소, 내려받을 PNG). segno 가 없으면 (None, None)."""
    try:
        import segno
    except ImportError:
        return None, None
    qr = segno.make(주소, error="m", micro=False)
    png = io.BytesIO()
    qr.save(png, kind="png", scale=12, border=4, dark="#0f172a")
    return qr.svg_data_uri(scale=5, border=2, dark="#0f172a"), png.getvalue()


def _공유_내용():
    주소 = _공유_주소()
    if 주소 and not _내_컴퓨터_주소인가(주소):
        st.markdown(f'<div class="fa-공유제목">{앱_이름} 공유하기</div>', unsafe_allow_html=True)
        st.caption("이 링크를 보내면 누구나 설치 없이 컴퓨터나 휴대폰에서 바로 사용할 수 있다.")
        st.code(주소, language=None)
        st.caption("링크 칸에 마우스를 올리면 오른쪽에 복사 버튼이 나타난다(휴대폰은 링크를 길게 눌러 복사). "
                   "카카오톡이나 문자에 붙여 넣으면 된다.")
        그림, png = _QR코드(주소)
        if 그림:
            st.markdown(f'<div class="fa-QR"><img src="{그림}" alt="{html.escape(주소)} QR코드"></div>', unsafe_allow_html=True)
            st.caption("휴대폰 카메라로 찍으면 바로 열린다. 발표 화면이나 포스터에 넣어 활용할 수 있다.")
            내려받기 = dict(label="QR코드 그림 내려받기", data=png, file_name=f"{앱_이름}_QR코드.png", mime="image/png",
                          use_container_width=True)
            try:
                st.download_button(**내려받기, icon=":material/qr_code_2:")
            except TypeError:                          # icon 을 못 쓰는 오래된 Streamlit
                st.download_button(**내려받기)
        else:
            st.caption("QR코드를 보려면 requirements.txt 의 segno 를 설치해야 한다.")
        안내 = "입력한 질문과 답변은 다른 사람의 화면에 보이지 않는다."
        하루_사용량 = getattr(설정, "하루_AI_사용량_보기", None)      # 인터넷 공개용(app.py)에서만 있어요
        if 하루_사용량:
            안내 += f" AI 검사는 이 앱을 쓰는 모든 사람을 합쳐 하루 {하루_사용량()[1]}번까지 할 수 있다."
        st.caption(안내)
    else:
        st.markdown(f'<div class="fa-공유제목">{앱_이름} 공유하기</div>', unsafe_allow_html=True)
        st.caption(f"지금 주소 `{주소 or 'http://localhost:8501'}` 는 이 컴퓨터에서만 열리므로, 다른 사람에게 보내도 열리지 않는다.")
        st.markdown(
            "**1. 인터넷 링크 (가장 쉬운 방법)**  \n"
            "Streamlit Cloud에 올리면 `https://○○○.streamlit.app` 링크가 생긴다. "
            f"그 앱에서 **{공유_메뉴_이름}** 버튼을 누르면 링크와 QR코드가 나온다. (README 11번)\n\n"
            "**2. 패키지 보내기 (조원끼리)**  \n"
            "`환각검사_패키지.zip`을 보내면, 받은 사람이 압축을 풀고 `바탕화면_아이콘_만들기.vbs`를 한 번 눌러 "
            "바탕화면 **FactAP** 아이콘으로 연다. API 키는 절대 함께 보내지 않는다.")
        st.caption("인터넷 링크를 Secrets(또는 환경 변수)에 APP_URL 로 넣어 두면, 내 컴퓨터에서도 그 링크와 QR코드를 보여 준다.")


def _소개_메뉴():
    """Streamlit 의 ⋮ 메뉴에는 항목을 새로 넣을 수 없어서, ⋮ 바로 옆에 우리 메뉴 버튼을 따로 둬요 (위치는 _화면_꾸미기).
    '공유' 와 'FactAP 소개' 두 버튼을 가로로 나란히 놓아요."""
    if not hasattr(st, "popover"):
        return
    try:
        상자 = st.container(key="factap_menu", horizontal=True, gap="small")   # 가로로 나란히 (Streamlit 1.48 이상)
    except TypeError:
        try:
            상자 = st.container(key="factap_menu")       # 'st-key-factap_menu' 라는 이름이 붙어서 CSS로 위치를 정할 수 있어요
        except TypeError:                              # key 를 못 쓰는 오래된 Streamlit: 화면 맨 위에 그냥 보여 줌
            상자 = st.container()
    with 상자:
        with st.popover(공유_메뉴_이름):
            _공유_내용()
        with st.popover(소개_메뉴_이름):
            st.caption(f"AI 환각의 개념과 {앱_이름}을 만들기 위해 우리 조가 수행한 활동을 정리하였다.")
            for 번호, (이름, 제목, 내용) in enumerate(앱_소개.메뉴):
                if st.button(이름, key=f"활동_메뉴_{번호}", use_container_width=True):
                    _활동_창(제목, 앱_소개.메뉴_글(내용, _예선_정확도()))


# ------------------------------------------------------------------ 검사 모드 메뉴 안의 API 크레딧
@st.cache_data(ttl=90, show_spinner=False)
def _크레딧_정보():
    """OpenRouter 에 이 키의 한도·남은 금액을 물어봄. 화면을 다시 그릴 때마다 묻지 않게 90초 동안 저장해 둬요."""
    try:
        return AI_호출.크레딧_보기()
    except Exception as e:
        return {"오류": str(e)[:150]}


def _크레딧_내용(키있음):
    """검사 모드 메뉴 안에 보여 줄 API 크레딧 (남은 금액, 오늘 쓴 횟수)"""
    st.markdown("**API 크레딧**")
    if not 키있음:
        st.caption("API 키가 없어서 크레딧을 확인할 수 없어요.")
    else:
        정보 = _크레딧_정보()
        if "오류" in 정보:
            st.caption(f"지금은 크레딧을 확인하지 못했어요. 잠시 뒤 다시 열어 보세요. ({정보['오류']})")
        else:
            한도, 남은, 쓴 = 정보.get("한도"), 정보.get("남은_금액"), 정보.get("쓴_금액")
            if 한도 is not None and 남은 is not None:
                st.metric("남은 금액", f"${남은:,.2f}")
                st.progress(max(0.0, min(1.0, 남은 / 한도)) if 한도 > 0 else 0.0)
                st.caption(f"이 키의 사용 한도 ${한도:,.2f} 중 ${(쓴 or 0):,.2f}를 썼어요.")
                비용 = ((st.session_state.get("보고서") or {}).get("AI_사용량") or {}).get("비용") or 0
                if 비용 > 0:
                    st.caption(f"방금 검사 비용(${비용:.3f}) 기준으로 약 {int(남은 // 비용)}번 더 검사할 수 있어요.")
            else:
                st.caption("이 키에는 사용 한도가 없어요. 계정에 남은 크레딧은 OpenRouter 사이트의 Credits 화면에서 확인해요.")
                if 쓴 is not None:
                    st.caption(f"이 키로 지금까지 쓴 금액: ${쓴:,.2f}")
            if 정보.get("오늘_쓴_금액") is not None:
                st.caption(f"오늘 쓴 금액: ${정보['오늘_쓴_금액']:,.2f} (세계 표준시 기준 하루)")
    하루_사용량 = getattr(설정, "하루_AI_사용량_보기", None)      # 인터넷 공개용(app.py)에서만 있어요
    if 하루_사용량:
        횟수, 한도 = 하루_사용량()
        st.caption(f"오늘 이 앱의 AI 검사: {횟수}번 / 하루 {한도}번까지")
    st.caption("숫자는 1~2분마다 새로 확인해요. 키는 화면에 보여 주지 않아요.")


# ------------------------------------------------------------------ 검사 결과 저장 (AI 다시 안 부르기)
# st.cache_data 를 쓰면 검사 중 진행 상황(0단계, 1단계…)을 화면에 보여 줄 수 없어서,
# 앱 서버가 켜져 있는 동안 유지되는 저장소(st.cache_resource)에 직접 저장해요. 새로고침해도 남아 있어요.
@st.cache_resource
def _결과_저장소():
    return {"결과": {}, "잠금": threading.Lock()}


def 저장된_결과(열쇠):
    저장소 = _결과_저장소()
    with 저장소["잠금"]:
        보고서 = 저장소["결과"].get(열쇠)
    return copy.deepcopy(보고서) if 보고서 else None


def 결과_저장(열쇠, 보고서):
    저장소 = _결과_저장소()
    with 저장소["잠금"]:
        저장소["결과"][열쇠] = copy.deepcopy(보고서)
        while len(저장소["결과"]) > 최대_저장_결과:
            저장소["결과"].pop(next(iter(저장소["결과"])))


def 결과_버리기(열쇠):
    저장소 = _결과_저장소()
    with 저장소["잠금"]:
        저장소["결과"].pop(열쇠, None)


# ------------------------------------------------------------------ 디자인 (CSS)
_글꼴 = ("'Pretendard Variable', Pretendard, -apple-system, BlinkMacSystemFont, 'Apple SD Gothic Neo', "
        "'Malgun Gothic', 'Noto Sans KR', sans-serif")


def _화면_꾸미기():
    """채팅형 AI 앱처럼: 하얀 바탕, 둥근 입력 상자, 오른쪽 말풍선, 왼쪽 옆 메뉴. 휴대폰에서도 깨지지 않게."""
    st.markdown("""
<style>
@import url("https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css");
:root { --fa-글: #1f2328; --fa-흐림: #5b6370; --fa-선: #e5e7eb; --fa-면: #f4f4f5; --fa-강조: #1d4ed8; --fa-강조2: #0d9488;
  --fa-초록: #15803d; --fa-노랑: #b45309; --fa-빨강: #b91c1c; }
/* 글꼴 (아이콘 글꼴이 있는 span 은 건드리지 않음) */
.stApp, .stApp p, .stApp li, .stApp label, .stApp textarea, .stApp input, .stApp button, .stApp summary,
.stApp h1, .stApp h2, .stApp h3, .stApp h4, [data-testid="stMarkdownContainer"] { font-family: FA_글꼴 !important; }
.stApp { background: #ffffff; color: var(--fa-글); }
[data-testid="stHeader"] { background: rgba(255,255,255,0.85); backdrop-filter: blur(6px); }
.block-container { max-width: 780px; padding-top: 3.2rem; padding-bottom: 4rem; }

/* 왼쪽 옆 메뉴 */
[data-testid="stSidebar"] { background: #f9fafb; border-right: 1px solid var(--fa-선); }
[data-testid="stSidebar"] .block-container, [data-testid="stSidebarUserContent"] { padding-top: 1rem; }
[data-testid="stSidebar"] .stButton button { justify-content: flex-start; text-align: left; border: none; background: transparent;
  border-radius: 10px; padding: 0.45rem 0.7rem; font-size: 0.92rem; color: var(--fa-글); box-shadow: none; }
[data-testid="stSidebar"] .stButton button:hover { background: #eceef1; }
[data-testid="stSidebar"] .stButton button > div { justify-content: flex-start; width: 100%; }
[data-testid="stSidebar"] .stButton button p { overflow: hidden; text-overflow: ellipsis; white-space: nowrap; text-align: left; }
[data-testid="stSidebar"] [data-testid="stVerticalBlock"] { gap: 0.2rem; }
.st-key-fa_new button { border: 1px solid var(--fa-선) !important; background: #fff !important; font-weight: 600; margin-bottom: 0.3rem; }
.st-key-fa_new button > div { justify-content: center !important; }
.st-key-fa_new button:hover { background: #f3f4f6 !important; }
.fa-옆로고 { display: flex; align-items: center; gap: 0.55rem; margin: 0.2rem 0 0.9rem 0.35rem; }
.fa-옆로고 img { width: 34px; height: 34px; }
.fa-옆로고 b { display: block; font-size: 1.25rem; font-weight: 800; letter-spacing: -0.02em; line-height: 1.1;
  background: linear-gradient(90deg, var(--fa-강조), var(--fa-강조2)); -webkit-background-clip: text; background-clip: text; color: transparent; }
.fa-옆로고 small { display: block; font-size: 0.72rem; color: var(--fa-흐림); font-weight: 600; }
.fa-옆제목 { font-size: 0.78rem; color: var(--fa-흐림); padding: 1.1rem 0 0.35rem 0.7rem; margin: 0; font-weight: 600; line-height: 1.2; }
/* Streamlit 이 HTML 글 상자 아래에 붙이는 -1rem 여백 때문에 다음 줄과 겹치지 않게 */
[data-testid="stMarkdownContainer"]:has(> .fa-옆제목, > .fa-옆빈칸, > .fa-옆로고, > .fa-진행) { margin-bottom: 0 !important; }
.fa-옆빈칸 { font-size: 0.85rem; color: var(--fa-흐림); margin: 0 0.4rem 0 0.7rem; line-height: 1.5; }

/* 처음 화면 인사말 */
.fa-hero { text-align: center; margin: 2.6rem 0 1.4rem 0; }
.fa-hero-그림 { width: 64px; height: 64px; display: block; margin: 0 auto 0.8rem auto; box-shadow: 0 10px 30px rgba(13, 148, 136, 0.25); border-radius: 16px; }
.fa-hero-로고 { display: inline-block; font-size: 0.85rem; font-weight: 700; color: var(--fa-강조); background: #eff6ff;
  padding: 0.22rem 0.8rem; border-radius: 999px; margin-bottom: 0.9rem; }
.fa-확인카드 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.6rem; margin: 1.4rem 0 0.3rem 0; text-align: left; }
.fa-확인카드 div { border: 1px solid var(--fa-선); border-radius: 14px; padding: 0.7rem 0.85rem; background: #fff; }
.fa-확인카드 b { display: block; font-size: 0.92rem; color: var(--fa-글); margin-bottom: 0.15rem; }
.fa-확인카드 b::before { content: ""; display: inline-block; width: 0.55rem; height: 0.55rem; border-radius: 50%;
  background: var(--fa-강조2); margin-right: 0.4rem; vertical-align: 0.05rem; }
.fa-확인카드 span { font-size: 0.82rem; color: var(--fa-흐림); }
.fa-확인제목 { font-size: 0.8rem; color: var(--fa-흐림); font-weight: 700; margin-top: 1.5rem; }
.fa-hero h1 { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.03em; line-height: 1.25; margin: 0 0 0.6rem 0; padding: 0;
  background: linear-gradient(90deg, var(--fa-강조), var(--fa-강조2)); -webkit-background-clip: text; background-clip: text; color: transparent; }
.fa-hero p { color: var(--fa-흐림); font-size: 1.02rem; margin: 0; }
/* 한글이 낱자 중간에서 줄이 바뀌지 않게 (긴 링크는 아래 overflow-wrap 으로 줄바꿈) */
.fa-hero, .fa-리포트, .fa-답변판, .fa-근거, .fa-통과줄, .fa-확인카드, .fa-종류, .fa-항목, .fa-계산, .fa-뜻줄 { word-break: keep-all; overflow-wrap: anywhere; }
.fa-단계 { display: flex; gap: 0.4rem; justify-content: center; align-items: center; flex-wrap: wrap; margin: 1rem 0 0.4rem 0;
  font-size: 0.86rem; color: var(--fa-흐림); }
.fa-단계 span { background: var(--fa-면); border-radius: 999px; padding: 0.3rem 0.75rem; color: var(--fa-글); }
.fa-단계 b { color: var(--fa-강조); margin-right: 0.3rem; }
.fa-단계 i { font-style: normal; color: #9ca3af; }

/* 대화 말풍선 */
[data-testid="stChatMessage"] { background: transparent; padding: 0.3rem 0; gap: 0.75rem; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) { flex-direction: row-reverse; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageAvatarUser"] { display: none; }
[data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] {
  background: var(--fa-면); border-radius: 20px 20px 6px 20px; padding: 0.75rem 1rem; max-width: 85%; margin-left: auto; flex-grow: 0; }
.fa-말 { font-size: 0.78rem; color: var(--fa-흐림); font-weight: 600; margin-bottom: 0.1rem; }

/* ====== 검증 리포트 (2026-11-16 디자인): 위험도 계기판 + 판정 + 기준 막대, 결과가 나올 때 부드럽게 떠오름 ====== */
/* 색 이름: g 통과·문제 없음(초록), y 의심·보통(주황), r 문제·위험(빨강), m 확인 못 함(진한 회색), n 해당 없음(회색) */
.fa-sg { --s: #22c55e; --s진: #15803d; --s연: #dcfce7; } .fa-sy { --s: #f59e0b; --s진: #b45309; --s연: #fef3c7; }
.fa-sr { --s: #ef4444; --s진: #b91c1c; --s연: #fee2e2; } .fa-sn { --s: #cbd5e1; --s진: #556070; --s연: #f1f5f9; }
.fa-sm { --s: #94a3b8; --s진: #475569; --s연: #e2e8f0; }
@keyframes fa-떠오름 { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: none; } }
@keyframes fa-바늘 { from { transform: rotate(0deg); } }
@keyframes fa-자람 { from { transform: scaleX(0); } }
.fa-리포트 { --c: #64748b; --c진: #334155; --c연: #f1f5f9; --c선: #e2e8f0; position: relative; overflow: hidden;
  border-radius: 22px; border: 1px solid var(--c선); margin: 0.2rem 0 0.7rem 0;
  background: radial-gradient(130% 100% at 0% 0%, var(--c연) 0%, #ffffff 60%);
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04), 0 14px 34px -14px rgba(15, 23, 42, 0.16); animation: fa-떠오름 0.45s ease-out both; }
.fa-리포트.fa-문제없음 { --c: #16a34a; --c진: #15803d; --c연: #e9fbef; --c선: #bbf7d0; }
.fa-리포트.fa-보통 { --c: #d97706; --c진: #b45309; --c연: #fff5e1; --c선: #fde68a; }
.fa-리포트.fa-위험 { --c: #dc2626; --c진: #b91c1c; --c연: #ffeeee; --c선: #fecaca; }
.fa-리포트::before { content: ""; position: absolute; left: 0; right: 0; top: 0; height: 4px; background: var(--c); }
.fa-리포트-머리 { display: flex; align-items: center; justify-content: space-between; gap: 0.6rem; flex-wrap: wrap;
  padding: 0.95rem 1.25rem 0 1.25rem; font-size: 0.78rem; font-weight: 700; color: var(--fa-흐림); }
.fa-리포트-머리 span { display: inline-flex; align-items: center; gap: 0.35rem; }
.fa-리포트-머리 svg { color: var(--c); }
.fa-리포트-몸 { display: grid; grid-template-columns: 13rem 1fr; gap: 1.4rem; align-items: center; padding: 0.5rem 1.25rem 1rem 1.25rem; }
.fa-리포트-몸.fa-단독 { grid-template-columns: 1fr; }
.fa-계기판 svg { width: 100%; height: auto; display: block; overflow: visible; }
.fa-계기판 text { font-family: inherit; }
/* 바늘 각도는 SVG 의 transform="rotate(각도)" 로 주고(Streamlit 이 style 속 변수를 지워서), 여기서는 0도에서 그 각도까지 돌아가게만 해요 */
.fa-바늘 { transform-origin: 100px 100px; animation: fa-바늘 1.1s cubic-bezier(0.22, 1, 0.36, 1) 0.15s both; }
.fa-바늘 circle { filter: drop-shadow(0 1px 2px rgba(15, 23, 42, 0.35)); }
.fa-등급줄 { display: flex; align-items: center; gap: 0.65rem; }
.fa-도장 { width: 2.35rem; height: 2.35rem; border-radius: 50%; background: var(--c); color: #fff; display: flex; align-items: center;
  justify-content: center; font-weight: 900; font-size: 1.15rem; flex-shrink: 0; box-shadow: 0 0 0 5px rgba(255, 255, 255, 0.9), 0 0 0 6px var(--c선); }
.fa-등급 { font-size: 1.8rem; font-weight: 800; letter-spacing: -0.03em; color: var(--c진); line-height: 1.15; }
.fa-리포트 p, .fa-리포트 div, .fa-항목-속 p, .fa-근거 div, .fa-답변판-글 { word-break: keep-all; }
.fa-기타 .fa-등급 { font-size: 1.35rem; } .fa-기타 .fa-도장 { width: 2rem; height: 2rem; font-size: 1rem; }
.fa-판정-설명 { margin: 0.55rem 0 0 0 !important; font-size: 0.95rem; color: #374151; line-height: 1.6; }
.fa-기준막대 { margin-top: 0.9rem; }
.fa-기준막대-제목 { font-size: 0.74rem; font-weight: 700; color: var(--fa-흐림); margin-bottom: 0.35rem; }
.fa-기준막대-줄 { display: flex; gap: 3px; height: 0.5rem; border-radius: 999px; overflow: hidden; }
.fa-기준막대-줄 span { height: 100%; background: var(--s); transform-origin: left; animation: fa-자람 0.7s ease-out 0.2s both; }
.fa-기준막대-글 { display: flex; flex-wrap: wrap; gap: 0.25rem 0.85rem; margin-top: 0.45rem; font-size: 0.8rem; color: #374151; }
.fa-기준막대-글 span { display: inline-flex; align-items: center; gap: 0.32rem; }
.fa-기준막대-글 i { width: 0.55rem; height: 0.55rem; border-radius: 50%; background: var(--s); }
.fa-기준막대-글 b { font-variant-numeric: tabular-nums; }
.fa-쪽지들 { display: flex; flex-wrap: wrap; gap: 0.35rem; padding: 0.7rem 1.25rem 0.85rem 1.25rem; border-top: 1px dashed var(--c선); }
.fa-쪽지 { font-size: 0.76rem; padding: 0.15rem 0.62rem; border-radius: 999px; background: rgba(255, 255, 255, 0.85);
  border: 1px solid var(--fa-선); color: #374151; }
/* 등급 뜻 (펼치기 안) */
.fa-뜻줄 { display: grid; grid-template-columns: 0.6rem 4.4rem 1fr auto; gap: 0.6rem; align-items: baseline; padding: 0.45rem 0.6rem;
  border-radius: 10px; font-size: 0.88rem; line-height: 1.5; }
.fa-뜻줄 i { width: 0.6rem; height: 0.6rem; border-radius: 50%; background: var(--s); align-self: center; }
.fa-뜻줄.fa-지금 { background: #f8fafc; box-shadow: inset 0 0 0 1px var(--fa-선); }
.fa-뜻줄 em { font-style: normal; font-size: 0.7rem; font-weight: 700; color: var(--fa-강조); background: #eff6ff; padding: 0.05rem 0.45rem;
  border-radius: 999px; white-space: nowrap; }
/* 결과 속 소제목 (작은 선 그림 + 제목) */
.fa-소제목 { display: flex; align-items: center; gap: 0.55rem; font-weight: 800; font-size: 1.02rem; letter-spacing: -0.01em;
  margin: 1.5rem 0 0.6rem 0; color: var(--fa-글); }
.fa-소제목-표 { width: 1.8rem; height: 1.8rem; border-radius: 9px; display: inline-flex; align-items: center; justify-content: center;
  background: linear-gradient(135deg, #eff6ff, #ecfeff); color: var(--fa-강조); flex-shrink: 0; box-shadow: inset 0 0 0 1px #dbeafe; }
.fa-소제목 small { font-weight: 600; color: var(--fa-흐림); font-size: 0.76rem; background: var(--fa-면); padding: 0.06rem 0.5rem; border-radius: 999px; }
/* 답변 속 문제 문장 형광펜 */
.fa-답변판 { border: 1px solid var(--fa-선); border-radius: 16px; background: #fff; overflow: hidden; box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04); }
.fa-답변판-머리 { display: flex; justify-content: space-between; align-items: center; gap: 0.6rem; flex-wrap: wrap; padding: 0.5rem 1rem;
  background: #f8fafc; border-bottom: 1px solid var(--fa-선); font-size: 0.76rem; font-weight: 700; color: var(--fa-흐림); }
.fa-범례 { display: inline-flex; gap: 0.75rem; font-weight: 600; }
.fa-범례 span { display: inline-flex; align-items: center; gap: 0.3rem; }
.fa-범례 i { width: 1.1rem; height: 0.55rem; border-radius: 3px; background: #fde68a; } .fa-범례 i.fa-강 { background: #fecaca; }
.fa-답변판-글 { padding: 0.85rem 1.05rem; line-height: 1.95; font-size: 0.95rem; max-height: 22rem; overflow-y: auto; }
.fa-형광 { background: linear-gradient(transparent 28%, #fde68a 28%, #fde68a 94%, transparent 94%); padding: 0 0.12rem; border-radius: 3px;
  color: inherit; -webkit-box-decoration-break: clone; box-decoration-break: clone; }
.fa-형광-강 { background: linear-gradient(transparent 28%, #fecaca 28%, #fecaca 94%, transparent 94%); }
.fa-형광 sup { font-size: 0.78rem; font-weight: 800; color: #b45309; margin-left: 0.15rem; }
.fa-형광-강 sup { color: #b91c1c; }
.fa-통과줄 { display: flex; align-items: center; gap: 0.6rem; border-radius: 14px; background: #f0fdf4; border: 1px solid #bbf7d0;
  color: var(--fa-초록); padding: 0.75rem 1rem; font-size: 0.93rem; font-weight: 600; }
.fa-근거 { border: 1px solid var(--fa-선); border-left: 4px solid var(--s); background: #fff; border-radius: 12px;
  padding: 0.6rem 0.9rem; margin: 0.45rem 0; font-size: 0.92rem; line-height: 1.6; }
.fa-근거 small { display: inline-block; font-size: 0.72rem; font-weight: 700; color: var(--s진); background: var(--s연);
  border-radius: 999px; padding: 0.04rem 0.55rem; margin-bottom: 0.3rem; }
.fa-근거 div { color: var(--fa-글); }
/* 검증 항목: 체크리스트 (누르면 근거가 펼쳐짐) */
.fa-항목들 { display: flex; flex-direction: column; gap: 0.45rem; }
.fa-항목 { border: 1px solid var(--fa-선); border-radius: 14px; background: #fff; transition: border-color 0.15s, box-shadow 0.15s;
  animation: fa-떠오름 0.4s ease-out both; }
.fa-항목:hover { border-color: #cbd5e1; box-shadow: 0 4px 14px rgba(15, 23, 42, 0.06); }
.fa-항목[open] { border-color: #cbd5e1; box-shadow: 0 8px 22px rgba(15, 23, 42, 0.08); }
.fa-항목 summary { list-style: none; cursor: pointer; display: flex; align-items: center; gap: 0.75rem; padding: 0.65rem 0.9rem; }
.fa-항목 summary::-webkit-details-marker { display: none; }
.fa-항목 summary::after { content: ""; width: 0.45rem; height: 0.45rem; border-right: 2px solid #94a3b8; border-bottom: 2px solid #94a3b8;
  transform: rotate(45deg) translateY(-2px); margin: 0 0.25rem 0 0.1rem; transition: transform 0.2s; flex-shrink: 0; }
.fa-항목[open] summary::after { transform: rotate(-135deg) translateY(-2px); }
.fa-표 { width: 1.65rem; height: 1.65rem; border-radius: 50%; background: var(--s연); color: var(--s진); display: inline-flex;
  align-items: center; justify-content: center; font-weight: 900; font-size: 0.85rem; flex-shrink: 0; }
.fa-항목-이름 { flex: 1; min-width: 0; }
.fa-항목-이름 b { display: block; font-size: 0.93rem; font-weight: 700; color: var(--fa-글); line-height: 1.35; }
.fa-항목-이름 small { display: block; font-size: 0.74rem; color: var(--fa-흐림); line-height: 1.35; }
.fa-항목-값 { display: flex; align-items: center; gap: 0.6rem; flex-shrink: 0; }
.fa-항목-값 em { font-style: normal; font-size: 0.75rem; font-weight: 700; color: var(--s진); background: var(--s연); padding: 0.1rem 0.6rem;
  border-radius: 999px; white-space: nowrap; }
.fa-항목-값 b { font-size: 0.85rem; font-variant-numeric: tabular-nums; color: var(--fa-글); min-width: 2.1rem; text-align: right; }
.fa-미니줄 { width: 4.5rem; height: 0.4rem; background: #f1f5f9; border-radius: 999px; overflow: hidden; }
.fa-미니줄 i { display: block; height: 100%; background: var(--s); border-radius: 999px; transform-origin: left; animation: fa-자람 0.7s ease-out 0.2s both; }
.fa-항목-속 { padding: 0.1rem 1rem 0.9rem 3.3rem; font-size: 0.9rem; color: #374151; line-height: 1.65; }
.fa-항목-속 p { margin: 0 0 0.4rem 0; }
.fa-항목-속 ul { margin: 0.2rem 0 0.5rem 1.1rem; padding: 0; } .fa-항목-속 li { margin: 0.1rem 0; }
.fa-항목-정보 { display: flex; flex-wrap: wrap; gap: 0.3rem; margin-top: 0.45rem; }
.fa-항목-정보 span { font-size: 0.72rem; color: var(--fa-흐림); background: var(--fa-면); border-radius: 999px; padding: 0.08rem 0.55rem; }
.fa-계산 { font-size: 0.8rem; color: var(--fa-흐림); margin: 0.6rem 0 0 0; padding: 0.6rem 0.85rem; border-radius: 12px; background: #f8fafc; line-height: 1.6; }
.fa-계산 b { color: #334155; margin-right: 0.35rem; }
/* 의심되는 환각 종류: 세 칸 카드 */
.fa-종류들 { display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.55rem; margin-bottom: 0.9rem; }
.fa-종류 { border: 1px solid var(--fa-선); border-radius: 14px; padding: 0.75rem 0.9rem 0.8rem 0.9rem; background: #fff; animation: fa-떠오름 0.4s ease-out both; }
.fa-종류.fa-sr { background: linear-gradient(180deg, #fff5f5, #fff); border-color: #fecaca; }
.fa-종류.fa-sy { background: linear-gradient(180deg, #fffaf0, #fff); border-color: #fde68a; }
.fa-종류-위 { display: flex; justify-content: space-between; align-items: baseline; gap: 0.4rem; font-weight: 700; font-size: 0.9rem; color: var(--fa-글); }
.fa-종류-위 b { font-size: 1.3rem; font-weight: 800; color: var(--s진); font-variant-numeric: tabular-nums; letter-spacing: -0.02em; }
.fa-종류-줄 { height: 0.4rem; background: #f1f5f9; border-radius: 999px; overflow: hidden; margin: 0.35rem 0 0.45rem 0; }
.fa-종류-줄 i { display: block; height: 100%; background: var(--s); border-radius: 999px; transform-origin: left; animation: fa-자람 0.8s ease-out 0.2s both; }
.fa-종류 small { font-size: 0.74rem; color: var(--fa-흐림); line-height: 1.4; display: block; }

/* 입력 상자 (둥근 카드) */
[data-testid="stForm"] { border: 1px solid var(--fa-선); border-radius: 26px; padding: 1rem 1.1rem 0.7rem 1.1rem;
  box-shadow: 0 6px 24px rgba(15, 23, 42, 0.07); background: #fff; }
[data-testid="stForm"] textarea { border: none !important; background: #f8f9fb !important; border-radius: 14px !important; }
[data-testid="stForm"] [data-baseweb="textarea"] { border: none !important; border-radius: 14px !important; background: #f8f9fb !important; }
[data-testid="stForm"] label p { font-size: 0.82rem !important; color: var(--fa-흐림) !important; font-weight: 600; }
[data-testid="stForm"] [data-testid="stFormSubmitButton"] button { border-radius: 999px; font-weight: 700; min-height: 2.6rem;
  background: linear-gradient(90deg, var(--fa-강조), var(--fa-강조2)); border: none; }
[data-testid="stForm"] [data-testid="stFormSubmitButton"] button:hover { filter: brightness(1.07); }
[data-testid="stForm"] [data-testid="stPopover"] button { border-radius: 999px; }
[data-testid="stForm"] [data-baseweb="select"] > div { border-radius: 999px; background: #f8f9fb; border-color: transparent; }
.fa-아래글 { text-align: center; color: var(--fa-흐림); font-size: 0.78rem; margin-top: 0.6rem; }

/* 기타 */
[data-testid="stExpander"] details { border-radius: 14px; border-color: var(--fa-선); }
.stButton button, [data-testid="stDownloadButton"] button { border-radius: 999px; }
[data-testid="stMetricValue"] { white-space: normal; word-break: keep-all; overflow-wrap: anywhere; }
.stMarkdown, .stAlert, [data-testid="stExpander"] summary { overflow-wrap: anywhere; }
textarea, input { font-size: 16px !important; }       /* 아이폰에서 입력칸을 누를 때 확대되지 않게 */
@media (max-width: 640px) {
  .block-container { padding: 3rem 0.8rem 3rem 0.8rem !important; }
  .fa-hero { margin-top: 1.2rem; } .fa-hero h1 { font-size: 1.55rem; }
  .fa-확인카드 { grid-template-columns: 1fr; gap: 0.4rem; } .fa-확인카드 div { padding: 0.5rem 0.75rem; }
  .fa-리포트-몸 { grid-template-columns: 1fr; gap: 0.3rem; justify-items: center; text-align: center; padding: 0.3rem 1rem 0.9rem 1rem; }
  .fa-리포트-머리 { padding: 0.9rem 1rem 0 1rem; } .fa-쪽지들 { padding: 0.65rem 1rem 0.8rem 1rem; justify-content: center; }
  .fa-계기판 { width: 12rem; } .fa-등급줄, .fa-기준막대-글 { justify-content: center; } .fa-등급 { font-size: 1.6rem; }
  .fa-종류들 { gap: 0.4rem; } .fa-종류 { padding: 0.55rem 0.65rem 0.6rem 0.65rem; }
  .fa-종류-위 { flex-direction: column; align-items: flex-start; gap: 0; font-size: 0.8rem; } .fa-종류-위 b { font-size: 1.15rem; }
  .fa-종류 small { display: none; }
  .fa-미니줄 { display: none; } .fa-항목 summary { gap: 0.55rem; padding: 0.6rem 0.7rem; } .fa-항목-속 { padding: 0.1rem 0.85rem 0.85rem 0.85rem; }
  .fa-뜻줄 { grid-template-columns: 0.6rem 4.2rem 1fr; } .fa-뜻줄 em { display: none; }
  [data-testid="stChatMessage"]:has([data-testid="stChatMessageAvatarUser"]) [data-testid="stChatMessageContent"] { max-width: 95%; }
  [data-testid="stForm"] { border-radius: 20px; padding: 0.8rem 0.8rem 0.5rem 0.8rem; } }

/* 오른쪽 위 ⋮ 메뉴: Print, Record screen 만 남기기 (테마·Rerun·Clear cache 등과 'Made with Streamlit' 줄은 숨김) */
[data-testid="stMainMenuList"] > *:not([data-testid="stMainMenuItem-print"]):not([data-testid="stMainMenuItem-recordScreencast"]) { display: none !important; }
[data-testid="stMainMenuList"] ~ * { display: none !important; }
/* 위 막대의 Deploy 버튼, 배포 사이트가 붙이는 버튼은 숨김 (소개 메뉴와 겹치지 않게) */
[data-testid="stAppDeployButton"], [data-testid="stToolbarActions"] { display: none !important; }
/* 'FactAP 소개' 메뉴 버튼을 ⋮ 바로 왼쪽에 고정 */
.st-key-factap_menu { position: fixed; top: 0.55rem; right: 3.3rem; z-index: 999991; width: auto !important; }
.st-key-factap_menu button { min-height: 2.1rem; padding: 0.1rem 0.85rem; border-radius: 999px; background: #fff; }
.st-key-factap_menu { flex-wrap: nowrap !important; gap: 0.4rem !important; }
.st-key-factap_menu > div { width: auto !important; flex: 0 0 auto !important; }
/* 공유 메뉴: 창 너비를 알맞게, 제목, QR코드 */
[data-testid="stPopoverBody"]:has(.fa-공유제목) { width: min(25rem, 92vw) !important; max-width: min(25rem, 92vw) !important; }
.fa-공유제목 { font-weight: 800; font-size: 1.05rem; margin-bottom: 0.1rem; }
.fa-QR { display: flex; justify-content: center; margin: 0.3rem 0 0.1rem 0; }
.fa-QR img { width: 172px; height: 172px; border-radius: 10px; border: 1px solid #e4e4e7; background: #fff; }
/* 메뉴 항목을 눌러 창이 열리면, 열려 있던 메뉴 목록은 창을 가리지 않게 숨김 (창을 닫으면 다시 보여요) */
body:has([data-testid="stDialog"]) [data-testid="stPopoverBody"] { display: none !important; }

/* ====== 대화형 (2026-11-15): Gemini·ChatGPT 같은 첫 화면, 아래 입력창, 입력창 도구 ====== */
.fa-인사 { text-align: center; margin: 3.2rem 0 1.6rem 0; word-break: keep-all; }
.fa-인사-그림 { width: 56px; height: 56px; display: block; margin: 0 auto 1rem auto; border-radius: 15px;
  box-shadow: 0 12px 32px rgba(29, 78, 216, 0.28); animation: fa-둥실 4s ease-in-out infinite; }
@keyframes fa-둥실 { 0%, 100% { transform: translateY(0); } 50% { transform: translateY(-5px); } }
.fa-인사-큰 { font-size: 2.5rem; font-weight: 800; letter-spacing: -0.035em; line-height: 1.2;
  background: linear-gradient(92deg, #1d4ed8 0%, #0d9488 55%, #7c3aed 100%); -webkit-background-clip: text; background-clip: text; color: transparent; }
.fa-인사-작은 { font-size: 1.6rem; font-weight: 700; letter-spacing: -0.03em; color: #6b7280; margin-top: 0.15rem; }
.fa-특징 { display: flex; flex-wrap: wrap; justify-content: center; gap: 0.4rem; margin-top: 1.3rem; }
.fa-특징 span { font-size: 0.82rem; padding: 0.28rem 0.75rem; border-radius: 999px; background: #f1f5f9; color: #334155; }
.fa-예시제목 { font-size: 0.8rem; font-weight: 700; color: var(--fa-흐림); margin: 0.4rem 0 0.1rem 0.2rem; }
.st-key-fa_examples .stButton button { min-height: 5.2rem; height: 100%; border-radius: 18px; border: 1px solid var(--fa-선);
  background: #fff; padding: 0.75rem 1rem; justify-content: flex-start; align-items: flex-start; text-align: left;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04); transition: all 0.15s ease; }
.st-key-fa_examples .stButton button:hover { border-color: #93c5fd; background: #f8fbff; transform: translateY(-1px);
  box-shadow: 0 6px 18px rgba(29, 78, 216, 0.10); color: var(--fa-글); }
.st-key-fa_examples .stButton button > div, .st-key-fa_examples .stButton button [data-testid="stMarkdownContainer"] { justify-content: flex-start; width: 100%; }
.st-key-fa_examples .stButton button p { text-align: left; font-size: 0.86rem; color: var(--fa-흐림); line-height: 1.45; word-break: keep-all; }
.st-key-fa_examples .stButton button strong { color: var(--fa-글); font-size: 0.95rem; }
.st-key-fa_examples .stButton button em { font-style: normal; }
.fa-찾는것 { text-align: center; font-size: 0.78rem; color: var(--fa-흐림); margin: 1rem 0 0.4rem 0; word-break: keep-all; line-height: 1.7; }
.fa-찾는것 b { color: #334155; }
.fa-버전 { font-size: 0.7rem; color: #6b7280; margin: 1.4rem 0 0 0.7rem; }
.fa-팝제목 { font-weight: 800; font-size: 0.95rem; margin-bottom: 0.2rem; }
.st-key-fa_flow .stButton button[kind="primary"], .st-key-fa_flow [data-testid="stBaseButton-primary"] {
  background: linear-gradient(90deg, var(--fa-강조), var(--fa-강조2)); border: none; font-weight: 700; min-height: 2.6rem; }
/* 아래 입력창 (둥글고 그림자, 보내기 버튼은 파란 동그라미) */
[data-testid="stBottom"] > div, [data-testid="stBottomBlockContainer"] { background: #ffffff; }
[data-testid="stBottomBlockContainer"] { max-width: 780px; padding-top: 0.6rem; padding-bottom: 0.7rem; }
[data-testid="stBottomBlockContainer"]::after { content: "FactAP도 틀릴 수 있어요. 중요한 내용은 다른 자료로 꼭 다시 확인하고, 개인정보는 넣지 마세요.";
  display: block; text-align: center; font-size: 0.72rem; color: var(--fa-흐림); margin-top: 0.45rem; word-break: keep-all; }
[data-testid="stChatInput"] { border: none !important; background: transparent !important; box-shadow: none !important; padding: 0 !important; }
[data-testid="stChatInput"] > div { border-radius: 26px !important; border: 1px solid #d4d4d8 !important; background: #fff !important;
  box-shadow: 0 6px 24px rgba(15, 23, 42, 0.08); padding: 0.3rem 0.35rem 0.3rem 0.7rem; }
/* 안내 글(자리 글)이 줄을 바꾸면 크롬이 입력창을 두 줄 크기로 키워 버려서, 한 줄로 두고 넘치면 … 으로 줄여요 */
[data-testid="stChatInput"] textarea::placeholder { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
[data-testid="stChatInput"] > div:focus-within { border-color: #93c5fd !important; box-shadow: 0 6px 24px rgba(29, 78, 216, 0.14); }
[data-testid="stChatInputSubmitButton"] { background: linear-gradient(135deg, var(--fa-강조), var(--fa-강조2)) !important;
  color: #fff !important; border-radius: 50% !important; }
[data-testid="stChatInputSubmitButton"] svg { color: #fff !important; fill: #fff !important; }
[data-testid="stChatInputSubmitButton"]:disabled { background: #e5e7eb !important; }
[data-testid="stChatInputSubmitButton"]:disabled svg { color: #9ca3af !important; fill: #9ca3af !important; }
/* 입력창 위 도구 줄 (검사 모드 · 유형 · 한 번에 입력) */
.st-key-fa_tools { gap: 0.35rem !important; flex-wrap: wrap !important; margin-bottom: 0.35rem; }
.st-key-fa_tools > div { width: auto !important; flex: 0 0 auto !important; }
.st-key-fa_tools button { min-height: 2rem !important; padding: 0.1rem 0.8rem !important; border-radius: 999px !important;
  font-size: 0.85rem !important; background: #fff !important; border: 1px solid var(--fa-선) !important; }
.st-key-fa_tools button:hover { border-color: #93c5fd !important; background: #f8fbff !important; }
.st-key-fa_tools button p { font-size: 0.85rem !important; }
[data-testid="stPopoverBody"]:has(.fa-팝제목) { width: min(23rem, 92vw) !important; max-width: min(23rem, 92vw) !important; }
/* 사실 확인 중 (반짝이는 글자, AI 앱의 '생각 중'처럼) */
@keyframes fa-반짝 { 0% { background-position: 200% 0; } 100% { background-position: -200% 0; } }
[data-testid="stExpander"] summary:has([data-testid="stExpanderIconSpinner"]) [data-testid="stMarkdownContainer"] p,
[data-testid="stExpander"] summary:has(.stSpinner) [data-testid="stMarkdownContainer"] p {
  background: linear-gradient(90deg, #64748b 0%, #64748b 40%, #1d4ed8 50%, #64748b 60%, #64748b 100%); background-size: 200% 100%;
  -webkit-background-clip: text; background-clip: text; color: transparent; animation: fa-반짝 2s linear infinite; font-weight: 600; }
@media (max-width: 640px) {
  .fa-인사 { margin-top: 1.6rem; } .fa-인사-큰 { font-size: 1.75rem; } .fa-인사-작은 { font-size: 1.2rem; }
  .fa-특징 span { font-size: 0.75rem; padding: 0.22rem 0.6rem; }
  .fa-인사 { margin: 0.6rem 0 0.9rem 0; } .fa-인사-그림 { width: 44px; height: 44px; margin-bottom: 0.6rem; border-radius: 12px; }
  .fa-특징 { margin-top: 0.8rem; }
  /* 휴대폰: 예시 카드를 2×2 로 작게 (제목만), 입력창 위 도구 줄은 한 줄로 옆으로 밀기 */
  .st-key-fa_examples [data-testid="stHorizontalBlock"] { flex-direction: row !important; flex-wrap: nowrap !important; gap: 0.5rem !important; }
  .st-key-fa_examples [data-testid="stColumn"] { min-width: 0 !important; width: 50% !important; flex: 1 1 50% !important; }
  .st-key-fa_examples .stButton button { min-height: 3.3rem; padding: 0.55rem 0.7rem; border-radius: 14px; }
  .st-key-fa_examples .stButton button em, .st-key-fa_examples .stButton button br { display: none; }
  .st-key-fa_examples .stButton button strong { font-size: 0.86rem; }
  .fa-찾는것 { margin-top: 0.5rem; font-size: 0.72rem; }
  .st-key-fa_tools { flex-wrap: nowrap !important; overflow-x: auto; scrollbar-width: none; }
  .st-key-fa_tools button { padding: 0.1rem 0.65rem !important; } .st-key-fa_tools button p { font-size: 0.8rem !important; white-space: nowrap; }
  [data-testid="stBottomBlockContainer"] { padding-left: 0.7rem !important; padding-right: 0.7rem !important; } }
/* ====== 디자인 다듬기 (2026-11-16) ====== */
/* 옆 메뉴 '최근 검사': 이모티콘 대신 등급 색 점, 지금 펼친 결과는 회색 바탕 */
[class*="st-key-fa_rec_"] button p::before { content: ""; display: inline-block; width: 0.5rem; height: 0.5rem; border-radius: 50%;
  margin-right: 0.6rem; vertical-align: 0.1rem; background: #cbd5e1; }
[class*="st-key-fa_rec_g_"] button p::before { background: #22c55e; }
[class*="st-key-fa_rec_y_"] button p::before { background: #f59e0b; }
[class*="st-key-fa_rec_r_"] button p::before { background: #ef4444; }
[class*="st-key-fa_rec_"][class*="_on_"] button { background: #eceef1 !important; }
[class*="st-key-fa_rec_"][class*="_on_"] button p { font-weight: 600; }
/* 검사 중: 단계 표시 (지난 단계는 체크, 지금 단계는 깜박이는 파란 점) */
@keyframes fa-맥박 { 0% { box-shadow: 0 0 0 0 rgba(29, 78, 216, 0.35); } 70% { box-shadow: 0 0 0 7px rgba(29, 78, 216, 0); }
  100% { box-shadow: 0 0 0 0 rgba(29, 78, 216, 0); } }
[data-testid="stExpander"]:has(.fa-진행) details { border-color: #dbeafe; background: linear-gradient(180deg, #f8fbff, #ffffff); }
[data-testid="stVerticalBlock"]:has(> .stElementContainer .fa-진행) { gap: 0.4rem; }
.fa-진행 { display: flex; align-items: center; gap: 0.65rem; font-size: 0.9rem; color: var(--fa-흐림); animation: fa-떠오름 0.3s ease-out both; }
.fa-진행-표 { width: 1.4rem; height: 1.4rem; border-radius: 50%; display: inline-flex; align-items: center; justify-content: center;
  font-size: 0.7rem; font-weight: 800; background: #dcfce7; color: #15803d; flex-shrink: 0; }
.stElementContainer:has(.fa-진행):not(:last-child) .fa-진행-표 { font-size: 0; }
.stElementContainer:has(.fa-진행):not(:last-child) .fa-진행-표::after { content: "✓"; font-size: 0.78rem; }
.stElementContainer:has(.fa-진행):last-child .fa-진행 { color: var(--fa-글); font-weight: 600; }
.stElementContainer:has(.fa-진행):last-child .fa-진행-표 { background: #dbeafe; color: var(--fa-강조); animation: fa-맥박 1.4s ease-out infinite; }
/* 검사하는 동안에는 바로 앞 화면(출처 묻기, Fact TAP 버튼)의 흐린 잔상을 숨겨요 */
.stApp:has(.fa-진행) [data-testid="stMainBlockContainer"] [data-stale="true"] { display: none !important; }
.stApp:has(.fa-진행) [data-testid="stMainBlockContainer"] [data-testid="stChatMessage"]:not(:has([data-stale="false"])) { display: none !important; }
/* 첫 화면: 인사말 뒤 은은한 빛, 특징 앞 작은 점, 예시 카드의 유형 꼬리표 */
.fa-인사 { position: relative; isolation: isolate; }
.fa-인사::before { content: ""; position: absolute; z-index: -1; left: 50%; top: -1.5rem; width: min(580px, 100%); height: 15rem;
  transform: translateX(-50%); pointer-events: none; filter: blur(18px);
  background: radial-gradient(40% 55% at 30% 45%, rgba(59, 130, 246, 0.16), transparent 70%),
              radial-gradient(40% 55% at 70% 40%, rgba(20, 184, 166, 0.15), transparent 70%),
              radial-gradient(35% 45% at 52% 72%, rgba(124, 58, 237, 0.10), transparent 70%); }
.fa-특징 span { background: rgba(255, 255, 255, 0.75); border: 1px solid var(--fa-선); }
.fa-특징 span::before { content: ""; display: inline-block; width: 0.42rem; height: 0.42rem; border-radius: 50%; margin-right: 0.42rem;
  vertical-align: 0.1rem; background: linear-gradient(135deg, var(--fa-강조), var(--fa-강조2)); }
.st-key-fa_examples .stButton button code { font-family: inherit !important; font-size: 0.7rem; font-weight: 700; color: var(--fa-강조);
  background: #eff6ff; border: none; border-radius: 999px; padding: 0.12rem 0.5rem; margin-right: 0.2rem; vertical-align: 0.08rem; }
/* ====== 기기가 어두운 모드여도 늘 밝은 화면 (2026-11-16 글자색) ======
   테마 파일(.streamlit/config.toml)이 없으면 Streamlit 은 기기 설정(어두운 모드)을 따라 밝은 글자색을 써요.
   그러면 하얀 바탕 위에 밝은 글자가 올라가 잘 안 보여서, 글자색과 바탕색을 여기서 직접 정해 둬요. */
html, body, .stApp { color-scheme: light; }
body { background: #ffffff; color: var(--fa-글); }
/* 일반 글자: 말풍선, 설명 글, 펼치기, 메뉴 창, 입력 이름표, 표, 제목 */
[data-testid="stChatMessageContent"], [data-testid="stText"], [data-testid="stExpander"] details, [data-testid="stExpander"] summary,
[data-testid="stExpanderDetails"], [data-testid="stPopoverBody"], [data-testid="stWidgetLabel"], [data-testid="stMetricLabel"],
[data-testid="stMetricValue"], [data-testid="stRadio"] label, [data-testid="stSidebarContent"], [data-testid="stDialog"] [role="dialog"],
[data-testid="stMarkdownContainer"] :is(h1, h2, h3, h4, h5, h6, th, td, blockquote) { color: var(--fa-글) !important; }
[data-testid="stMarkdownContainer"]:not(button *):not([data-testid="stAlertContainer"] *):not([data-testid="stCaptionContainer"] *) { color: var(--fa-글) !important; }
[data-testid="stText"] span { color: inherit !important; }
[data-testid="stCaptionContainer"], [data-testid="stCaptionContainer"] p, [data-testid="InputInstructions"] { color: var(--fa-흐림) !important; }
[data-testid="stCaptionContainer"] { opacity: 1 !important; }      /* Streamlit 은 작은 설명 글을 60%만 보이게 해서 더 흐려져요 */
[data-testid="stMarkdownContainer"] :is(th, td) { border-color: var(--fa-선) !important; }
[data-testid="stMarkdownContainer"] th { background: #f8fafc !important; }
[data-testid="stMarkdownContainer"] a { color: var(--fa-강조) !important; }
[data-testid="stMarkdownContainer"]:not(button *) code, [data-testid="stCaptionContainer"] code { color: #0f766e !important; background: #f1f5f9 !important; }
/* 아이콘(펼치기 화살표, 옆 메뉴 접기, 창 닫기 X, 위 막대) */
[data-testid="stExpander"] summary [data-testid="stIconMaterial"], [data-testid="stExpander"] summary svg { color: inherit !important; }
[data-testid="stSidebarCollapseButton"] button, [data-testid="stExpandSidebarButton"], [data-testid="stHeader"] button,
[data-testid="stDialog"] button[aria-label="Close"] { color: #4b5563 !important; }
[data-testid="stIconMaterial"] { color: inherit !important; }
[data-testid="stExpander"] summary { background-color: transparent !important; }
[data-testid="stExpander"] summary:hover { background-color: #f8fafc !important; }
/* 바탕: 메뉴 창, 큰 창, 고르기 목록, ⋮ 메뉴 */
[data-testid="stPopoverBody"], [data-testid="stDialog"] [role="dialog"], [data-testid="stMainMenuPopover"],
[data-baseweb="popover"] ul[role="listbox"], [data-baseweb="popover"] [role="option"] { background-color: #ffffff !important; }
[data-testid="stPopoverBody"], [data-testid="stDialog"] [role="dialog"] { border-color: var(--fa-선) !important; }
[data-testid="stDialog"] [role="dialog"] { box-shadow: 0 12px 40px rgba(15, 23, 42, 0.16) !important; }
[data-testid="stTooltipContent"] { background-color: #f8fafc !important; color: var(--fa-글) !important; border: 1px solid var(--fa-선);
  box-shadow: 0 4px 14px rgba(15, 23, 42, 0.10); }
[data-baseweb="popover"] [role="option"], [data-testid="stMainMenuPopover"] * { color: var(--fa-글) !important; }
[data-baseweb="popover"] [role="option"]:hover, [data-baseweb="popover"] [role="option"][aria-selected="true"] { background-color: #eff6ff !important; }
/* 입력칸: 쓴 글씨는 진하게, 안내 글은 흐리게, 깜박이는 막대는 파랑 */
textarea, input { color: var(--fa-글) !important; -webkit-text-fill-color: var(--fa-글) !important; caret-color: var(--fa-강조) !important; }
textarea::placeholder, input::placeholder { color: #80868f !important; -webkit-text-fill-color: #80868f !important; opacity: 1 !important; }
[data-baseweb="input"], [data-baseweb="base-input"], [data-baseweb="textarea"], [data-baseweb="select"] > div,
[data-testid="stTextInputRootElement"], [data-testid="stTextAreaRootElement"] { background-color: #f8f9fb !important; border-color: var(--fa-선) !important; }
[data-testid="stForm"] [data-testid="stTextAreaRootElement"] { border: 1px solid transparent !important; border-radius: 14px !important; }
[data-testid="stTextInputRootElement"]:focus-within, [data-testid="stTextAreaRootElement"]:focus-within { border-color: #93c5fd !important; }
[data-baseweb="select"] div, [data-baseweb="select"] span, [data-baseweb="select"] svg { color: var(--fa-글) !important; }
[data-testid="stSelectbox"] [role="group"] { background-color: #f8f9fb !important; border-color: var(--fa-선) !important; color: var(--fa-글) !important; }
[data-testid="stSelectbox"] [role="group"] * { color: var(--fa-글) !important; }
[data-testid="stSelectboxVirtualDropdown"], [role="listbox"] { background-color: #ffffff !important; color: var(--fa-글) !important; border-color: var(--fa-선) !important; }
[role="listbox"] [role="option"] { color: var(--fa-글) !important; }
[role="listbox"] [role="option"]:hover, [role="listbox"] [role="option"][aria-selected="true"], [role="listbox"] [role="option"][data-focused="true"] {
  background-color: #eff6ff !important; }
/* 버튼 (흰 버튼은 흰 바탕에 진한 글자) */
[data-testid="stBaseButton-secondary"], [data-testid="stPopoverButton"], [data-testid="stBaseButton-secondaryFormSubmit"] {
  background-color: #ffffff; color: var(--fa-글); border-color: #d4d4d8; }
[data-testid="stBaseButton-primary"] { color: #ffffff !important; }
/* 고르기 동그라미, 막대, 구분선, 코드 상자, 알림 상자 */
[data-testid="stRadioOption"] > div > div:first-child { background-color: #ffffff !important; border: 1px solid #9ca3af !important; }
[data-testid="stRadioOption"]:not(:has(input:checked)) > div > div:first-child > div { background-color: transparent !important; }
[data-testid="stRadioOption"]:has(input:checked) > div > div:first-child { background-color: var(--fa-강조) !important; border-color: var(--fa-강조) !important; }
[data-testid="stRadioOption"]:has(input:checked) > div > div:first-child > div { background-color: #ffffff !important; }
[data-testid="stProgressBarTrack"] { background-color: #e5e7eb !important; }
[data-testid="stProgressBarTrack"] > div { background: linear-gradient(90deg, var(--fa-강조), var(--fa-강조2)) !important; }
hr, [data-testid="stDivider"] hr { border-color: var(--fa-선) !important; background-color: var(--fa-선) !important; }
[data-testid="stCode"] pre, [data-testid="stCode"] code { background-color: #f4f4f5 !important; color: var(--fa-글) !important; }
[data-testid="stCode"] button { color: var(--fa-흐림) !important; background: transparent !important; }
div:has(> [data-testid="stElementToolbarButton"]) { background-color: #ffffff !important; border: 1px solid var(--fa-선); }
[data-testid="stElementToolbarButton"], [data-testid="stElementToolbarButton"] button { color: var(--fa-흐림) !important; }
[data-testid="stAlertContainer"] { color: var(--fa-글) !important; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentInfo"]) { background-color: #eff6ff !important; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentSuccess"]) { background-color: #f0fdf4 !important; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentWarning"]) { background-color: #fffbeb !important; }
[data-testid="stAlertContainer"]:has([data-testid="stAlertContentError"]) { background-color: #fef2f2 !important; }
[data-testid="stAlertContentInfo"], [data-testid="stAlertContentInfo"] * { color: #1e3a8a !important; }
[data-testid="stAlertContentSuccess"], [data-testid="stAlertContentSuccess"] * { color: #14532d !important; }
[data-testid="stAlertContentWarning"], [data-testid="stAlertContentWarning"] * { color: #78350f !important; }
[data-testid="stAlertContentError"], [data-testid="stAlertContentError"] * { color: #7f1d1d !important; }
/* 버튼에 마우스를 올리거나 누를 때 색: 테마 파일(.streamlit/config.toml)이 없어도 Streamlit 기본 빨강 대신 FactAP 파랑 */
.stButton button:not([kind="primary"]):hover, [data-testid="stDownloadButton"] button:hover, [data-testid="stPopover"] button:hover,
.stButton button:not([kind="primary"]):focus-visible, [data-testid="stPopover"] button:focus-visible {
  color: var(--fa-강조) !important; border-color: #93c5fd !important; }
.stButton button:not([kind="primary"]):active, [data-testid="stDownloadButton"] button:active { background: #eff6ff !important; color: var(--fa-강조) !important; }
[data-testid="stSidebar"] .stButton button:hover { color: var(--fa-글) !important; }
[data-testid="stExpander"] summary:hover, [data-testid="stExpander"] summary:hover * { color: var(--fa-강조) !important; }
[data-testid="stExpander"] summary p { word-break: keep-all; }
/* 결과 아래 버튼 */
[class*="st-key-fa_actions"] .stButton button, [class*="st-key-fa_actions"] [data-testid="stDownloadButton"] button { min-height: 2.6rem; font-weight: 600; }
@media (max-width: 640px) {
  .st-key-fa_examples .stButton button code { display: none; } }
/* 움직임을 줄이라고 설정한 기기에서는 움직이지 않게 */
@media (prefers-reduced-motion: reduce) {
  .fa-리포트, .fa-항목, .fa-종류, .fa-진행, .fa-바늘, .fa-기준막대-줄 span, .fa-미니줄 i, .fa-종류-줄 i, .fa-인사-그림,
  .stElementContainer:has(.fa-진행):last-child .fa-진행-표 { animation: none !important; } }
</style>""".replace("FA_글꼴", _글꼴), unsafe_allow_html=True)


def _상자(key):
    """CSS로 꾸밀 수 있게 이름(key) 붙인 상자. key 를 못 쓰는 오래된 Streamlit 이면 그냥 상자."""
    try:
        return st.container(key=key)
    except TypeError:
        return st.container()


def _줄이기(글, 최대):
    글 = str(글 or "").strip()
    return 글 if len(글) <= 최대 else 글[:최대].rstrip() + " …"


def _다시_확인할_문장들(보고서):
    """기준별 결과의 문제 문장을 모음. 같은 문장은 한 번만, 위험도가 높은 기준 것부터
    → [{"번호", "기준"(번호+이름), "위험도", "글"}]"""
    모음, 본것 = [], set()
    기준들 = sorted(보고서["기준결과들"], key=lambda x: -(x["결과"]["위험도"] or 0))
    for x in 기준들:
        for 문장 in x["결과"]["문제_문장"]:
            글 = str(문장).strip()
            if 글 and 글 not in 본것:
                본것.add(글)
                모음.append({"번호": x["정보"]["번호"], "기준": f"{x['정보']['번호']} {x['정보']['이름']}",
                           "위험도": x["결과"]["위험도"] or 0, "글": 글})
    return 모음


def _고르게(글):
    """비교용: 마크다운 기호와 띄어쓰기 차이를 없앰"""
    return re.sub(r"\s+", " ", 마크다운_지우기(str(글))).strip()


def _답변_표시(답변, 문제들):
    """AI 답변을 문장으로 나눠, 기준이 문제라고 본 문장에 형광펜을 칠한 HTML을 만듦.
    돌려주는 값: (HTML 또는 None, 답변 안에서 찾지 못한 문제들) — 찾지 못한 것은 '그 밖에 확인할 점'으로 따로 보여 줘요."""
    문제글 = [(_고르게(m["글"]), m) for m in 문제들]
    찾음 = set()
    줄들 = []
    for 줄 in str(답변).split("\n"):
        조각들 = [c for c in re.split(r"(?<=[.!?。])\s+", 줄) if c]
        칠한 = []
        for 조각 in 조각들:
            가 = _고르게(조각)
            맞은 = [m for 글, m in 문제글 if len(가) >= 6 and 글 and (가 in 글 or (len(글) >= 6 and 글 in 가))]
            if 맞은:
                찾음.update(id(m) for m in 맞은)
                번호들 = "".join(dict.fromkeys(m["번호"] for m in 맞은))
                강 = " fa-형광-강" if max(m["위험도"] for m in 맞은) >= 0.6 else ""
                칠한.append(f'<mark class="fa-형광{강}" title="{html.escape(", ".join(m["기준"] for m in 맞은))}">'
                           f'{html.escape(조각)}<sup>{html.escape(번호들)}</sup></mark>')
            else:
                칠한.append(html.escape(조각))
        줄들.append(" ".join(칠한))
    남은것 = [m for m in 문제들 if id(m) not in 찾음]
    if not 찾음:
        return None, 남은것
    머리 = ('<div class="fa-답변판-머리"><span>AI의 답변</span><span class="fa-범례"><span><i></i>의심</span>'
           '<span><i class="fa-강"></i>강한 의심</span></span></div>')
    return '<div class="fa-답변판">' + 머리 + '<div class="fa-답변판-글">' + "<br>".join(줄들) + "</div></div>", 남은것


def _내려받기_글(보고서):
    """내려받을 텍스트: 입력한 질문·답변 + 검사_실행.보고서_글"""
    줄 = [f"{앱_이름} 검사 결과 (AI 답변 환각 위험도)", f"검사 시각: {보고서.get('시각', '')}", "",
         "[질문]", 보고서.get("질문", ""), "", "[AI 답변]", 보고서.get("답변", "")]
    if 보고서.get("출처"):
        줄 += ["", "[출처]", 보고서["출처"]]
    줄 += ["", "-" * 50, 보고서_글(보고서), "", "※ 이 결과는 참고용이며 틀릴 수 있어요."]
    return "\n".join(줄)


def _내려받기_버튼(보고서, 번호):
    시각 = str(보고서.get("시각", "")).replace(":", "").replace("-", "").replace("T", "_")[:13]
    _버튼(st.download_button, "결과 내려받기 (.txt)", ":material/download:", data=_내려받기_글(보고서).encode("utf-8"),
          key=f"내려받기_{번호}", file_name=f"{앱_이름}_결과_{시각 or '결과'}.txt", mime="text/plain", use_container_width=True)


def _등급_뜻(지금_등급, 방법):
    """세 등급의 뜻 (지금 등급에 '지금 결과' 표시)"""
    줄 = []
    for 등급 in ["문제 없음", "보통", "위험"]:
        지금 = 등급 == 지금_등급
        줄.append(f'<div class="fa-뜻줄 fa-s{등급_코드[등급]}{" fa-지금" if 지금 else ""}"><i></i><b>{등급}</b>'
                 f'<span>{html.escape(설정.등급_설명.get(등급, ""))}</span>{"<em>지금 결과</em>" if 지금 else ""}</div>')
    with _펼침("등급은 무슨 뜻인가요?", ":material/help:"):
        st.markdown("".join(줄), unsafe_allow_html=True)
        st.caption(f"종합 위험도(0~1) 기준: {등급_경계_글(방법)}")


# ------------------------------------------------------------------ 결과 그리기 (2026-11-16 디자인: 계기판 · 체크리스트 · 종류 카드)
# 작은 선 그림 (이모티콘 대신). 모양은 Lucide 아이콘(ISC 라이선스)을 따랐어요.
_아이콘_모양 = {
    "방패": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72'
           'a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "형광펜": '<path d="m9 11-6 6v3h9l3-3"/><path d="m22 12-4.6 4.6a2 2 0 0 1-2.8 0l-5.2-5.2a2 2 0 0 1 0-2.8L14 4"/>',
    "주의": '<path d="m21.73 18-8-14a2 2 0 0 0-3.48 0l-8 14A2 2 0 0 0 4 21h16a2 2 0 0 0 1.73-3"/><path d="M12 9v4"/><path d="M12 17h.01"/>',
    "목록": '<path d="m3 17 2 2 4-4"/><path d="m3 7 2 2 4-4"/><path d="M13 6h8"/><path d="M13 12h8"/><path d="M13 18h8"/>',
    "과녁": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/>',
    "체크": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
}
# 기준 하나의 판정: 이름 → 색(g 초록, y 주황, r 빨강, m 진한 회색, n 회색)과 동그라미 안 글자
_판정_순서 = ["통과", "의심", "문제", "확인 못 함", "해당 없음"]
_판정_색 = {"통과": "g", "의심": "y", "문제": "r", "확인 못 함": "m", "해당 없음": "n"}
_판정_표 = {"통과": "✓", "의심": "!", "문제": "✕", "확인 못 함": "–", "해당 없음": "–"}


def _아이콘(이름, 크기=16):
    return (f'<svg viewBox="0 0 24 24" width="{크기}" height="{크기}" fill="none" stroke="currentColor" stroke-width="2" '
            f'stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{_아이콘_모양[이름]}</svg>')


def _소제목(아이콘, 제목, 덧붙임=""):
    st.markdown(f'<div class="fa-소제목"><span class="fa-소제목-표">{_아이콘(아이콘)}</span>{html.escape(제목)}'
                + (f"<small>{html.escape(덧붙임)}</small>" if 덧붙임 else "") + "</div>", unsafe_allow_html=True)


def _펼침(제목, 아이콘=None, **옵션):
    """st.expander + 작은 그림(아이콘). 아이콘을 못 쓰는 오래된 Streamlit 이면 그림 없이."""
    try:
        return st.expander(제목, icon=아이콘, **옵션)
    except TypeError:
        return st.expander(제목, **옵션)


def _버튼(만들기, 글, 아이콘=None, **옵션):
    """st.button · st.download_button + 작은 그림(아이콘). 오래된 Streamlit 이면 그림 없이."""
    try:
        return 만들기(글, icon=아이콘, **옵션)
    except TypeError:
        return 만들기(글, **옵션)


def _판정(r):
    """기준 하나의 결과 → '통과'·'의심'·'문제'·'확인 못 함'·'해당 없음' (화면 표시용 이름일 뿐, 점수 계산과는 상관없어요)"""
    v = r["위험도"]
    if v is None:      # 출처가 없을 때 ②처럼 '해당 없음'인 것과, AI·인터넷이 없어 '확인 못 함'인 것을 나눠 보여 줘요
        return "해당 없음" if r["상태"] == "해당 없음" else "확인 못 함"
    return "문제" if v >= 0.6 else "의심" if v >= 0.3 else "통과"


def _글_html(글):
    """근거 글을 HTML로: 특수 문자는 안전하게 바꾸고, **굵게** 와 줄바꿈만 살려요"""
    글 = html.escape(str(글 or ""))
    return re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", 글).replace("\n", "<br>")


def _눈금_위치(위험도, 방법):
    """위험도(0~1) → 계기판 위의 위치(%). 세 등급 구간을 같은 너비(1/3씩)로 그리고, 구간 안에서는 비례해서 놓아요."""
    경계 = 설정.등급_기준_방법별.get(방법 or 설정.합치는_방법, 설정.등급_기준)
    끝들 = [0.0] + [min(1.0, 상한) for 상한, _ in 경계]
    v = max(0.0, min(1.0, float(위험도)))
    for i in range(len(경계)):
        아래, 위 = 끝들[i], 끝들[i + 1]
        if v < 위 or i == len(경계) - 1:
            안 = 0 if 위 <= 아래 else (v - 아래) / (위 - 아래)
            return 100 * (i + max(0.0, min(1.0, 안))) / len(경계)
    return 100.0


def _계기판(위험도, 방법):
    """종합 위험도 계기판 (반원). 등급 구간(문제 없음 | 보통 | 위험)을 같은 각도로 그리고, 지금 구간만 진하게.
    동그란 바늘이 왼쪽 끝에서 출발해 _눈금_위치 까지 돌아가요. 구간 사이 숫자는 등급 경계(설정.py)예요."""
    경계 = 설정.등급_기준_방법별.get(방법 or 설정.합치는_방법, 설정.등급_기준)
    n = len(경계)
    v = max(0.0, min(1.0, float(위험도)))
    지금 = next((i for i, (상한, _) in enumerate(경계) if v < 상한), n - 1)      # 등급을 정할 때와 같은 방법
    색들 = ["#22c55e"] + ["#f59e0b"] * max(0, n - 2) + ["#ef4444"]

    def 점(각, 반지름):
        r = math.radians(각)
        return 100 + 반지름 * math.cos(r), 100 - 반지름 * math.sin(r)

    조각 = []
    for i in range(n):
        (x1, y1), (x2, y2) = 점(180 - i * 180 / n - (1.2 if i else 0), 80), 점(180 - (i + 1) * 180 / n + (1.2 if i < n - 1 else 0), 80)
        조각.append(f'<path d="M{x1:.2f} {y1:.2f} A80 80 0 0 1 {x2:.2f} {y2:.2f}" fill="none" stroke="{색들[i]}" '
                   f'stroke-width="15" opacity="{1 if i == 지금 else 0.2}"/>')
    흐린글 = 'text-anchor="middle" font-size="10" font-weight="600" fill="#94a3b8"'
    for i, (상한, _) in enumerate(경계[:-1]):
        x, y = 점(180 - (i + 1) * 180 / n, 99)
        조각.append(f'<text x="{x:.1f}" y="{y:.1f}" {흐린글}>{상한:g}</text>')
    조각.append(f'<text x="20" y="124" {흐린글}>0</text><text x="180" y="124" {흐린글}>1</text>'
               f'<text x="100" y="89" text-anchor="middle" font-size="34" font-weight="800" fill="#1f2328" letter-spacing="-1">{v:.2f}</text>'
               '<text x="100" y="108" text-anchor="middle" font-size="11" font-weight="600" fill="#6b7280">종합 위험도</text>'
               f'<g class="fa-바늘" transform="rotate({_눈금_위치(v, 방법) * 1.8:.1f})">'
               '<circle cx="20" cy="100" r="9" fill="#fff" stroke="#1f2328" stroke-width="4"/></g>')
    return (f'<div class="fa-계기판" title="등급 경계: {html.escape(등급_경계_글(방법))}">'
            f'<svg viewBox="0 -6 200 134" role="img" aria-label="종합 위험도 {v:.2f}">' + "".join(조각) + "</svg></div>")


def _항목_막대(결과들):
    """기준 N개의 판정을 한 줄 막대로 (통과 · 의심 · 문제 · 확인 못 함 · 해당 없음)"""
    세기 = {}
    for x in 결과들:
        판 = _판정(x["결과"])
        세기[판] = 세기.get(판, 0) + 1
    있는 = [p for p in _판정_순서 if 세기.get(p)]
    줄 = "".join(f'<span class="fa-s{_판정_색[p]}" style="flex:{세기[p]}"></span>' for p in 있는)
    글 = "".join(f'<span class="fa-s{_판정_색[p]}"><i></i>{p} <b>{세기[p]}</b></span>' for p in 있는)
    return (f'<div class="fa-기준막대"><div class="fa-기준막대-제목">기준 {len(결과들)}개 검사 결과</div>'
            f'<div class="fa-기준막대-줄">{줄}</div><div class="fa-기준막대-글">{글}</div></div>')


def _등급_카드(보고서):
    """검증 리포트의 머리: 위험도 계기판, 판정 도장(✓ ! ✕)과 등급, 설명, 기준 결과 막대, 쪽지(유형·AI 사용량)"""
    종합 = 보고서["종합"] or {}
    등급 = 종합.get("등급", "")
    색 = {"문제 없음": "fa-문제없음", "보통": "fa-보통", "위험": "fa-위험"}.get(등급, "fa-기타")
    위험도 = 종합.get("위험도")
    설명 = 종합.get("등급_설명") or (종합.get("근거") if 보고서["유형"] is None else "")
    쪽지 = []
    if 보고서["유형"]:
        쪽지.append(f"유형: {보고서['유형']}")
    섞기 = 종합.get("유형_섞기")
    if 섞기:
        쪽지 = ["두 유형으로 검사"] + [f"{t} {p:.0%}" for t, p in zip(섞기["유형"], 섞기["확률"])]
    u = 보고서.get("AI_사용량") or {}
    if u.get("호출"):
        쪽지.append(f"AI {u['호출']:.0f}번" + (f" · ${u['비용']:.3f}" if u.get("비용") else ""))
    결과들 = 보고서.get("기준결과들") or []
    계기 = "" if 위험도 is None else _계기판(위험도, 종합.get("방법"))
    막대 = _항목_막대(결과들) if 결과들 and 위험도 is not None else ""
    방식 = "" if 보고서["유형"] is None else ("간이 검사 · AI 없이" if 종합.get("간이_검사") else "정밀 검사 · AI 교차 확인")
    머리 = (f'<div class="fa-리포트-머리"><span>{_아이콘("방패", 15)}{앱_이름} 검증 리포트</span>'
           + (f"<span>{방식}</span>" if 방식 else "") + "</div>")
    판정 = (f'<div><div class="fa-등급줄"><span class="fa-도장">{판정_아이콘.get(등급, "i")}</span>'
           f'<span class="fa-등급">{html.escape(str(등급))}</span></div>'
           + (f'<p class="fa-판정-설명">{html.escape(str(설명))}</p>' if 설명 else "") + 막대 + "</div>")
    쪽지들 = ('<div class="fa-쪽지들">' + "".join(f'<span class="fa-쪽지">{html.escape(s)}</span>' for s in 쪽지) + "</div>") if 쪽지 else ""
    st.markdown(f'<div class="fa-리포트 {색}">{머리}<div class="fa-리포트-몸{"" if 계기 else " fa-단독"}">{계기}{판정}</div>{쪽지들}</div>',
                unsafe_allow_html=True)


def _항목_목록(결과들, 섞기):
    """검증 항목을 체크리스트처럼: 동그라미 판정 · 기준 이름 · 작은 막대 · 위험도. 누르면 근거와 문제 문장이 펼쳐져요."""
    줄 = []
    for x in 결과들:
        r, 기준 = x["결과"], x["정보"]
        판 = _판정(r)
        값 = r["위험도"]
        붙임 = f" ({x['유형']})" if 섞기 and x.get("유형") else ""
        이름 = f"{기준['번호']} {기준['이름']}{붙임}"
        막대 = "" if 값 is None else f'<span class="fa-미니줄"><i style="width:{max(값 * 100, 4) if 값 > 0 else 0:.0f}%"></i></span>'
        문장들 = "".join(f"<li>{html.escape(str(s))}</li>" for s in r["문제_문장"])
        속 = (f'<div class="fa-항목-속"><p>{_글_html(r["근거"])}</p>' + (f"<ul>{문장들}</ul>" if 문장들 else "")
              + f'<div class="fa-항목-정보"><span>맡는 환각 · {html.escape(str(기준["맡는_환각"]))}</span>'
                f'<span>방식 · {html.escape(str(기준["방식"]))}</span><span>중요도 · {중요도(기준):g}</span></div></div>')
        줄.append(f'<details class="fa-항목 fa-s{_판정_색[판]}"><summary><span class="fa-표">{_판정_표[판]}</span>'
                 f'<span class="fa-항목-이름"><b>{html.escape(이름)}</b>'
                 f'<small>{html.escape(str(기준["맡는_환각"]))}</small></span>'
                 f'<span class="fa-항목-값">{막대}<em>{판}</em>' + ("" if 값 is None else f"<b>{값:.2f}</b>") + f"</span></summary>{속}</details>")
    return '<div class="fa-항목들">' + "".join(줄) + "</div>"


def _결과_자세히(보고서, 번호):
    """가장 최근(또는 고른) 결과: 모든 내용을 보여 줌"""
    종합 = 보고서["종합"]
    섞기 = 종합.get("유형_섞기")
    정보 = 보고서.get("유형_정보") or {}
    if 섞기:      # 섞은 계산식은 아래 근거 글에 있어서, 여기서는 '직접 고르는 방법'만 알려 줘요
        st.caption(f"유형이 {섞기['유형'][0]}인지 {섞기['유형'][1]}인지 애매해서 두 유형의 점수를 확률로 섞었어요. "
                   "유형을 정확히 알면 아래 입력창 위의 '유형'에서 직접 골라 다시 검사해 보세요.")
    elif 정보.get("애매함"):
        st.caption(f"유형 분류가 애매했어요 (1순위 {정보.get('유형')}, 2순위 {정보.get('2순위')}). "
                   "다른 유형이 맞다면 '유형'에서 직접 골라 다시 검사해 보세요.")
    if 종합["등급"] in 등급_코드:
        _등급_뜻(종합["등급"], 종합.get("방법"))

    # 1) 답변 속 문제 문장에 형광펜
    문제들 = _다시_확인할_문장들(보고서)
    _소제목("형광펜", "답변 속 확인할 문장")
    판, 남은것 = _답변_표시(보고서["답변"], 문제들)
    if 판:
        st.markdown(판, unsafe_allow_html=True)
        st.caption("문장 끝의 작은 번호는 그 문장을 찾은 기준이에요. 아래 검증 항목에서 같은 번호를 누르면 근거를 볼 수 있어요.")
    elif not 문제들:
        st.markdown(f'<div class="fa-통과줄">{_아이콘("체크", 18)}기준들이 문제라고 표시한 문장이 없어요.</div>', unsafe_allow_html=True)
    else:      # 기준이 짚은 글이 답변 문장과 글자로 딱 맞지 않을 때 (예: 검사 AI가 문장을 바꿔 적음)
        st.caption("답변 문장 가운데 바로 칠할 곳은 찾지 못했어요. 기준이 찾은 내용은 바로 아래 '그 밖에 확인할 점'에 있어요.")
    if 남은것:
        _소제목("주의", "그 밖에 확인할 점", f"{len(남은것)}개")
        st.markdown("".join(
            f'<div class="fa-근거 fa-s{"r" if m["위험도"] >= 0.6 else "y"}"><small>{html.escape(m["기준"])}</small>'
            f'<div>{html.escape(m["글"])}</div></div>' for m in 남은것[:최대_보여줄_문장]), unsafe_allow_html=True)
        if len(남은것) > 최대_보여줄_문장:
            with st.expander(f"나머지 {len(남은것) - 최대_보여줄_문장}개 더 보기"):
                for m in 남은것[최대_보여줄_문장:]:
                    st.markdown(f"- {m['글']} ({m['기준']})")

    # 2) 검증 항목 (기준별 결과를 체크리스트처럼, 누르면 근거)
    결과들 = 보고서["기준결과들"]
    _소제목("목록", "검증 항목", f"기준 {len(결과들)}개")
    st.markdown(_항목_목록(결과들, 섞기), unsafe_allow_html=True)
    st.markdown(f'<div class="fa-계산"><b>종합 위험도 계산</b>{html.escape(str(종합["근거"]))}</div>', unsafe_allow_html=True)

    # 3) 어떤 환각이 의심되나요? (사실·입력·맥락 상충)
    if 종합.get("종류별"):
        _소제목("과녁", "의심되는 환각 종류")
        칸 = []
        for 종류, 값 in 종합["종류별"].items():
            값 = max(0.0, min(1.0, 값 or 0))
            코 = "r" if 값 >= 0.6 else "y" if 값 >= 0.3 else "g" if 값 > 0 else "n"
            칸.append(f'<div class="fa-종류 fa-s{코}"><div class="fa-종류-위"><span>{html.escape(종류)}</span><b>{값:.2f}</b></div>'
                     f'<div class="fa-종류-줄"><i style="width:{값 * 100:.0f}%"></i></div>'
                     f'<small>{html.escape(환각_뜻.get(종류, ""))}</small></div>')
        st.markdown('<div class="fa-종류들">' + "".join(칸) + "</div>", unsafe_allow_html=True)

    if 보고서["상위모델_답변들"]:
        with _펼침("교차 확인: 상위 모델들이 다시 답한 내용 보기", ":material/forum:"):
            for i, a in enumerate(보고서["상위모델_답변들"], 1):
                st.markdown(f"**상위 모델 {i}**")
                st.write(a)
    if 보고서.get("AI_사용량"):
        u = 보고서["AI_사용량"]
        st.caption(f"AI 호출 {u['호출']:.0f}번 · 입력 토큰 {u['입력_토큰']:.0f} · 출력 토큰 {u['출력_토큰']:.0f}"
                   + (f" · 비용 약 ${u['비용']:.4f}" if u.get("비용") else ""))
    for 글 in 보고서["알림"]:
        st.caption("※ " + 글)


def _내_말풍선(질문, 답변, 출처):
    with st.chat_message("user"):
        st.markdown('<div class="fa-말">질문</div>', unsafe_allow_html=True)
        st.text(_줄이기(질문, 500))
        st.markdown('<div class="fa-말">AI의 답변</div>', unsafe_allow_html=True)
        st.text(_줄이기(답변, 600))
        if 출처:
            st.markdown('<div class="fa-말">출처</div>', unsafe_allow_html=True)
            st.text(_줄이기(출처, 200))


def _한_차례(차례, 번호, 자세히):
    보고서 = 차례["보고서"]
    _내_말풍선(보고서["질문"], 보고서["답변"], 보고서["출처"])
    with st.chat_message("assistant", avatar=로고_그림):
        if 차례.get("저장됨"):
            st.caption("같은 입력의 저장된 결과예요. AI를 다시 부르지 않았어요. 처음부터 다시 하려면 '다시 검사'를 누르세요.")
        _등급_카드(보고서)
        if 보고서["유형"] is None:                    # 답변 거부 또는 입력 확인 필요
            if 자세히:
                _내려받기_버튼(보고서, 번호)
            return
        if 자세히:
            _결과_자세히(보고서, 번호)
            with _상자(f"fa_actions_{번호}"):
                칸1, 칸2 = st.columns(2)
                with 칸1:
                    _버튼(st.button, "다시 검사", ":material/refresh:", key=f"다시_{번호}", on_click=_다시_검사_누름, args=(번호,),
                          use_container_width=True, help="저장된 결과를 버리고 AI를 다시 불러 처음부터 검사해요.")
                with 칸2:
                    _내려받기_버튼(보고서, 번호)
        else:
            _버튼(st.button, "자세히 보기", ":material/expand_more:", key=f"펼치기_{번호}", on_click=_펼치기, args=(번호,))


# ------------------------------------------------------------------ 대화형 입력 (2026-11-15: ChatGPT·Gemini 처럼 아래 입력창 하나로)
# 순서: ① 질문 → ② AI의 답변 → ③ 출처(있으면) 또는 [Fact TAP] → 검사
# '질문: … / 답변: … / 출처: …' 처럼 한 번에 붙여 넣으면 알아서 나눠요. '한 번에 입력'(창)으로 넣어도 돼요.
화면_버전 = "2026-11-16 글자색"       # 화면을 고칠 때마다 날짜를 바꾸면, 새 화면이 올라갔는지 바로 알 수 있어요
예시들 = [   # 첫 화면 '예시로 해 보기' 카드: (제목, 꼬리표, 질문, 답변). 깔끔하게 보이도록 이모티콘은 넣지 않아요
    ("역사 사실 확인", "사실 지식형", "세종대왕이 훈민정음을 반포한 해는 언제인가요?",
     "세종대왕은 1443년에 훈민정음을 반포했습니다. 백성이 글을 쉽게 익히도록 만든 글자입니다."),
    ("계산 검산", "수치 계산형", "학생 5명의 수학 점수 평균이 72점입니다. 학생 1명이 더 들어와 6명의 평균이 75점이 되었다면, 새로 들어온 학생의 점수는 몇 점인가요?",
     "새로 들어온 학생의 점수는 93점입니다.\n1. 처음 5명의 총점: 72 × 5 = 360점\n2. 6명이 된 후 총점: 75 × 6 = 450점\n3. 새로 들어온 학생의 점수: 450 - 360 = 93점"),
    ("논리 추론 따지기", "논리 추론형", "A는 B의 아버지이고, B는 C의 아버지입니다. C는 A의 무엇인가요?", "C는 A의 손자입니다."),
    ("코드 결과 확인", "코드 결과형", "다음 Python 코드를 실행하면 무엇이 출력되나요?\n\nd = {\"사과\": 3, \"배\": 5}\nd[\"사과\"] += 2\nd[\"귤\"] = 1\nprint(len(d), d[\"사과\"])",
     "출력 결과는 4 5 입니다. 딕셔너리에 귤이 추가되어 길이가 4가 됩니다."),
]
_머리말 = re.compile(r"^[ \t]*(질문|Q|AI의 답변|AI 답변|답변|A|출처|S)[ \t]*[:：][ \t]*", re.M | re.I)
_머리_이름 = {"질문": "질문", "q": "질문", "ai의 답변": "답변", "ai 답변": "답변", "답변": "답변", "a": "답변", "출처": "출처", "s": "출처"}


def _한번에_나누기(글):
    """'질문: … 답변: … (출처: …)' 로 시작하는 글이면 칸별로 나눠요. 아니면 None."""
    찾음 = list(_머리말.finditer(글))
    if not 찾음 or 찾음[0].start() != len(글) - len(글.lstrip()) or _머리_이름[찾음[0].group(1).lower()] != "질문":
        return None
    칸 = {}
    for i, m in enumerate(찾음):
        끝 = 찾음[i + 1].start() if i + 1 < len(찾음) else len(글)
        이름 = _머리_이름[m.group(1).lower()]
        if 이름 not in 칸:
            칸[이름] = 글[m.end():끝].strip()
    return 칸 if 칸.get("질문") and 칸.get("답변") else None


def _팝업(글, 아이콘=None):
    """st.popover + 작은 그림(아이콘). 오래된 Streamlit 이면 그림 없이."""
    try:
        return st.popover(글, icon=아이콘)
    except TypeError:
        return st.popover(글)


def _진행_글(글):
    """검사 중 단계 글 ('2단계: …') → 동그라미 번호 + 글 (지난 단계는 CSS 가 체크로 바꿔요)"""
    m = re.match(r"\s*(\d+)\s*단계\s*[:：]\s*(.*)", str(글), re.S)
    번호, 내용 = (m.group(1), m.group(2)) if m else ("·", str(글))
    return f'<div class="fa-진행"><span class="fa-진행-표">{번호}</span><span>{html.escape(내용)}</span></div>'


def _라벨_글(글):
    """버튼 글자에서 마크다운 기호(*, _, #, '1.' 같은 번호, $ 등)가 꾸밈으로 바뀌지 않게 앞에 역슬래시를 붙여요"""
    return re.sub(r"([\\`*_{}\[\]()#+\-.!|~:$<>])", r"\\\1", str(글))


def _탭_그림():
    """브라우저 탭의 작은 그림: FactAP 로고 (도구/아이콘/FactAP.ico). 없으면 돋보기"""
    try:
        from PIL import Image
        return Image.open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "도구", "아이콘", "FactAP.ico"))
    except Exception:
        return "🔎"


def _처음부터():
    st.session_state["단계"] = "질문"
    st.session_state["임시"] = {}


def _새_검사():
    st.session_state["대화"] = []
    st.session_state["펼친"] = None
    st.session_state.pop("보고서", None)
    _처음부터()


def _펼치기(번호):
    st.session_state["펼친"] = 번호


def _다시_검사_누름(번호):
    st.session_state["다시_검사"] = 번호


def _예시_고름(번호):
    _, _, 질문, 답변 = 예시들[번호]
    st.session_state["임시"] = {"질문": 질문, "답변": 답변}
    st.session_state["단계"] = "출처"


def _바로_검사_누름():
    st.session_state["바로_검사"] = True


def _AI_쓰나(키있음):
    return bool(키있음) and st.session_state.get("모드", "정밀") == "정밀"


def _모드_글(키있음):
    return "정밀 검사" if _AI_쓰나(키있음) else "간이 검사"


def _모드_고르기(키있음):
    """ChatGPT 의 '모델 고르기'처럼: 정밀(AI 사용) / 간이(AI 없이) + 남은 크레딧"""
    with _팝업(_모드_글(키있음), ":material/science:" if _AI_쓰나(키있음) else ":material/bolt:"):
        st.markdown('<div class="fa-팝제목">검사 모드</div>', unsafe_allow_html=True)
        if 키있음:
            st.radio("검사 모드", ["정밀", "간이"], key="모드", label_visibility="collapsed",
                     format_func=lambda 값: {"정밀": "정밀 검사", "간이": "간이 검사"}[값],
                     captions=["상위 AI 3개에게 다시 묻고 검사 AI·위키백과·논문까지 대조해요. 1~2분, 한 번에 약 $0.05",
                               "AI 없이 프로그램으로 확인하는 기준만 써요. 몇 초, 무료. 사실·출처형은 놓치기 쉬워요"])
        else:
            st.caption("API 키가 없어서 지금은 간이 검사(AI 없이 프로그램 기준만)로 해요. "
                       "키를 넣으면 정밀 검사를 고를 수 있어요. (README 'API 키 넣기')")
        st.divider()
        _크레딧_내용(키있음)


def _유형_고르기():
    with _팝업(("유형 자동" if st.session_state.get("유형_입력", "유형 자동 분류") == "유형 자동 분류"
                             else st.session_state["유형_입력"]), ":material/sell:"):
        st.markdown('<div class="fa-팝제목">답변 유형</div>', unsafe_allow_html=True)
        st.selectbox("답변 유형", ["유형 자동 분류"] + 설정.유형목록, key="유형_입력", label_visibility="collapsed")
        st.caption("보통은 자동 분류로 두면 돼요. 분류가 애매하면 두 유형으로 모두 검사해서 확률로 섞어요.")


def _한번에_창():
    """질문·답변·출처를 한 번에 넣는 창 (예전 입력 상자)"""
    def 내용():
        with st.form("한번에"):
            질문 = st.text_area("질문", height=100, placeholder="AI에게 한 질문을 붙여 넣으세요. 지문이나 코드가 있으면 함께 넣어요.")
            답변 = st.text_area("AI의 답변", height=150, placeholder="AI가 한 답변을 그대로 붙여 넣으세요.")
            출처 = st.text_area("출처 (선택)", height=68, placeholder="AI가 참고한 링크나 글이 있으면 넣어요. 없으면 비워 둬요.")
            try:
                누름 = st.form_submit_button(검사_버튼_이름, type="primary", use_container_width=True, icon=":material/verified_user:")
            except TypeError:
                누름 = st.form_submit_button(검사_버튼_이름, type="primary", use_container_width=True)
        if 누름:
            if not 질문.strip() or not 답변.strip():
                st.warning("질문과 AI의 답변을 모두 넣어 주세요.")
            else:
                st.session_state["바로_요청"] = {"질문": 질문, "답변": 답변, "출처": 출처}
                st.rerun()
    if hasattr(st, "dialog"):
        st.dialog("한 번에 입력하기", width="large")(내용)()
    else:
        with st.expander("한 번에 입력하기", expanded=True):
            내용()


def _입력_도구줄(키있음):
    """아래 입력창 바로 위의 작은 버튼 줄 (검사 모드, 유형, 한 번에 입력). Gemini·ChatGPT 의 입력창 도구처럼."""
    바닥 = getattr(st, "bottom", None) or getattr(st, "_bottom", None) or st   # 입력창이 있는 화면 맨 아래 칸 (없는 버전이면 본문에)
    try:
        줄 = 바닥.container(key="fa_tools", horizontal=True, gap="small")
    except TypeError:
        줄 = 바닥.container()
    with 줄:
        _모드_고르기(키있음)
        _유형_고르기()
        if _버튼(st.button, "한 번에 입력", ":material/edit_note:", key="한번에_버튼"):
            _한번에_창()


def _자리글():
    단계 = st.session_state["단계"]
    if 단계 == "답변":
        return "AI의 답변을 붙여 넣으세요"
    if 단계 == "출처":
        return "출처를 넣거나 '없음'을 보내요"
    return "AI에게 한 질문을 붙여 넣으세요" if not st.session_state["대화"] else "다음 질문을 붙여 넣으세요"


_출처_없음 = {"없음", "없어", "없어요", "없습니다", "x", "-", "no", "none", "출처 없음"}


def _요청_만들기(질문, 답변, 출처, 키있음):
    유형 = st.session_state.get("유형_입력", "유형 자동 분류")
    if (출처 or "").strip().lower() in _출처_없음:         # '없음'이라고 쓰면 출처 없이 검사
        출처 = ""
    return {"질문": 질문, "답변": 답변, "출처": 출처 or "",
            "유형": None if 유형 == "유형 자동 분류" else 유형, "AI_사용": _AI_쓰나(키있음), "새로": False}


def _입력_받기(글, 키있음):
    """아래 입력창에 보낸 글을 지금 단계에 맞게 받아요. 바로 검사할 수 있으면 요청을 돌려줘요."""
    글 = 글.strip()
    if not 글:
        return None
    나눔 = _한번에_나누기(글)
    if 나눔:
        if "출처" in 나눔:
            return _요청_만들기(나눔["질문"], 나눔["답변"], 나눔["출처"], 키있음)
        st.session_state["임시"] = {"질문": 나눔["질문"], "답변": 나눔["답변"]}
        st.session_state["단계"] = "출처"
        st.rerun()
    단계 = st.session_state["단계"]
    임시 = st.session_state["임시"]
    if 단계 == "출처":
        return _요청_만들기(임시["질문"], 임시["답변"], 글, 키있음)
    if 단계 == "답변":
        임시["답변"], st.session_state["단계"] = 글, "출처"
    else:
        st.session_state["임시"], st.session_state["단계"] = {"질문": 글}, "답변"
    st.rerun()


def _옆_메뉴():
    with st.sidebar:
        st.markdown(f'<div class="fa-옆로고"><img src="{로고_그림}" alt=""><div><b>{앱_이름}</b><small>AI 답변 팩트체크</small></div></div>',
                    unsafe_allow_html=True)
        with _상자("fa_new"):
            st.button("＋ 새 검사", on_click=_새_검사, use_container_width=True)
        st.markdown('<div class="fa-옆제목">최근 검사</div>', unsafe_allow_html=True)
        대화 = st.session_state.get("대화") or []
        펼친 = st.session_state.get("펼친")
        펼친 = len(대화) - 1 if 펼친 is None else 펼친
        if not 대화:
            st.markdown('<div class="fa-옆빈칸">아직 검사한 답변이 없어요.</div>', unsafe_allow_html=True)
        for 번호 in range(len(대화) - 1, -1, -1):
            보고서 = 대화[번호]["보고서"]
            등급 = (보고서["종합"] or {}).get("등급", "")
            제목 = " ".join(str(보고서["질문"]).split())[:28] or "(질문 없음)"
            st.button(_라벨_글(제목), key=f"fa_rec_{등급_코드.get(등급, 'n')}_{'on_' if 번호 == 펼친 else ''}{번호}",
                      on_click=_펼치기, args=(번호,),
                      use_container_width=True, help=f"{등급} · {보고서.get('시각', '')}")
        st.markdown('<div class="fa-옆제목">도움말</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="fa-옆빈칸">아래 입력창에 <b>질문 → AI의 답변</b> 순서로 넣으면 돼요. '
                    f'오른쪽 위 <b>{소개_메뉴_이름}</b>에서 AI 환각과 기준을, <b>{공유_메뉴_이름}</b>에서 링크와 QR코드를 볼 수 있어요.</div>',
                    unsafe_allow_html=True)
        st.markdown(f'<div class="fa-버전">화면 버전 {화면_버전}</div>', unsafe_allow_html=True)


def _첫_화면(키있음):
    """Gemini·ChatGPT 의 첫 화면처럼: 큰 인사말 + 이 앱이 하는 일 + 예시 카드"""
    st.markdown(f"""
<div class="fa-인사">
  <img class="fa-인사-그림" src="{로고_그림}" alt="">
  <div class="fa-인사-큰">안녕하세요, {앱_이름}이에요</div>
  <div class="fa-인사-작은">어떤 AI 답변을 팩트체크할까요?</div>
  <div class="fa-특징"><span>상위 AI 3개와 교차 확인</span><span>위키백과·논문 대조</span><span>기준 6개로 판정</span><span>의심 문장 형광펜</span></div>
</div>""", unsafe_allow_html=True)
    st.markdown('<div class="fa-예시제목">예시로 해 보기</div>', unsafe_allow_html=True)
    with _상자("fa_examples"):
        칸들 = st.columns(2)
        for 번호, (제목, 꼬리표, 질문, _) in enumerate(예시들):
            with 칸들[번호 % 2]:
                st.button(f"`{꼬리표}` **{제목}**  \n*{_줄이기(' '.join(질문.split()), 34)}*", key=f"예시_{번호}",
                          on_click=_예시_고름, args=(번호,), use_container_width=True)
    st.markdown(f"""
<div class="fa-찾는것">이런 환각을 찾아요 · <b>사실 상충</b> {환각_뜻["사실 상충"]} · <b>입력 상충</b> {환각_뜻["입력 상충"]} ·
<b>맥락 상충</b> {환각_뜻["맥락 상충"]}</div>""", unsafe_allow_html=True)
    if not 키있음:
        st.caption("지금은 API 키가 없어 간이 검사(AI 없이 프로그램 기준만)로 해요. (README의 'API 키 넣기')")


def _진행_중_대화(키있음):
    """질문 → 답변 → 출처를 받는 동안의 대화"""
    단계, 임시 = st.session_state["단계"], st.session_state["임시"]
    with st.chat_message("user"):
        st.markdown('<div class="fa-말">질문</div>', unsafe_allow_html=True)
        st.text(_줄이기(임시.get("질문", ""), 500))
    if 단계 == "답변":
        with st.chat_message("assistant", avatar=로고_그림):
            st.markdown("좋아요! 이 질문에 **AI가 뭐라고 답했나요?** 아래 입력창에 답변을 그대로 붙여 넣어 주세요.")
            _버튼(st.button, "처음부터", ":material/undo:", key="처음부터_1", on_click=_처음부터)
        return
    with st.chat_message("user"):
        st.markdown('<div class="fa-말">AI의 답변</div>', unsafe_allow_html=True)
        st.text(_줄이기(임시.get("답변", ""), 600))
    with st.chat_message("assistant", avatar=로고_그림):
        st.markdown("AI가 참고한 **출처**(링크나 글)가 있으면 아래 입력창에 붙여 넣어 주세요. 없으면 바로 검사할게요.")
        with _상자("fa_flow"):
            try:
                칸1, 칸2 = st.columns([1.4, 1], vertical_alignment="center")
            except TypeError:
                칸1, 칸2 = st.columns([1.4, 1])
            with 칸1:
                try:
                    st.button(검사_버튼_이름, key="바로_검사_버튼", type="primary", on_click=_바로_검사_누름,
                              use_container_width=True, icon=":material/verified_user:")
                except TypeError:
                    st.button(검사_버튼_이름, key="바로_검사_버튼", type="primary", on_click=_바로_검사_누름, use_container_width=True)
            with 칸2:
                _버튼(st.button, "처음부터", ":material/undo:", key="처음부터_2", on_click=_처음부터, use_container_width=True)
        st.caption(f"{_모드_글(키있음)} · 유형: {st.session_state.get('유형_입력', '유형 자동 분류')}"
                   + (" · 1~2분 걸려요" if _AI_쓰나(키있음) else " · 몇 초면 끝나요"))


# ------------------------------------------------------------------ 화면
st.set_page_config(page_title=앱_이름, page_icon=_탭_그림(), layout="centered")
_화면_꾸미기()
_소개_메뉴()
st.session_state.setdefault("대화", [])
st.session_state.setdefault("펼친", None)
st.session_state.setdefault("단계", "질문")
st.session_state.setdefault("임시", {})
_옆_메뉴()
키있음 = AI_호출.키가_있나()
_입력_도구줄(키있음)
보낸_글 = st.chat_input(_자리글(), key="채팅_입력")

# 이번에 할 검사 정하기: 입력창, Fact TAP, 한 번에 입력, 또는 결과 아래 '다시 검사'
요청 = _입력_받기(보낸_글, 키있음) if 보낸_글 else None
if st.session_state.pop("바로_검사", False) and st.session_state["임시"].get("답변"):
    임시 = st.session_state["임시"]
    요청 = _요청_만들기(임시["질문"], 임시["답변"], "", 키있음)
바로 = st.session_state.pop("바로_요청", None)
if 바로:
    요청 = _요청_만들기(바로["질문"], 바로["답변"], 바로["출처"], 키있음)
다시 = st.session_state.pop("다시_검사", None)
if 다시 is not None and 다시 < len(st.session_state["대화"]):
    앞 = st.session_state["대화"][다시]
    요청 = {"질문": 앞["보고서"]["질문"], "답변": 앞["보고서"]["답변"], "출처": 앞["보고서"]["출처"],
          "유형": 앞["유형"], "AI_사용": 앞["AI_사용"], "새로": True}

대화 = st.session_state["대화"]
if not 대화 and not 요청 and st.session_state["단계"] == "질문":
    _첫_화면(키있음)
펼친 = st.session_state["펼친"] if st.session_state["펼친"] is not None else len(대화) - 1
for 번호, 차례 in enumerate(대화):
    _한_차례(차례, 번호, 자세히=(번호 == 펼친 and not 요청))
if 요청:
    _내_말풍선(요청["질문"], 요청["답변"], 요청["출처"])
    with st.chat_message("assistant", avatar=로고_그림):
        열쇠 = (요청["질문"], 요청["답변"], 요청["출처"], 요청["유형"], 요청["AI_사용"])   # 이 다섯 가지가 같으면 같은 검사로 봄
        if 요청["새로"]:
            결과_버리기(열쇠)
        보고서 = 저장된_결과(열쇠)
        저장됨 = bool(보고서)
        if not 보고서:
            상태 = st.status("사실 확인하는 중…" + (" (1~2분)" if 요청["AI_사용"] else ""), expanded=True)
            보고서 = 환각_검사(요청["질문"], 요청["답변"], 요청["출처"], 요청["유형"], 요청["AI_사용"],
                          진행_알림=lambda 글: 상태.markdown(_진행_글(글), unsafe_allow_html=True))
            상태.update(label="검증 완료", state="complete", expanded=False)
            기록_남기기(보고서)                      # 설정.기록_저장 이 True면 기록/검사기록.jsonl 에 저장
            if not any("AI 호출이 실패" in 글 for 글 in 보고서["알림"]) and not 보고서.get("저장_안_함"):
                # 실패가 섞인 결과, 하루 AI 한도를 넘어 간이 검사로 바뀐 결과(app.py)는 저장하지 않음
                결과_저장(열쇠, 보고서)
    대화.append({"보고서": 보고서, "유형": 요청["유형"], "AI_사용": 요청["AI_사용"], "저장됨": 저장됨})
    st.session_state["펼친"] = None                 # 새 결과(맨 아래)를 펼침
    st.session_state["보고서"] = 보고서              # 검사 모드 메뉴에서 방금 검사 비용으로 남은 횟수를 계산
    if not 요청["새로"]:
        _처음부터()                                  # 다음 검사는 다시 '질문'부터
    st.rerun()
elif st.session_state["단계"] in ("답변", "출처") and st.session_state["임시"].get("질문"):
    _진행_중_대화(키있음)

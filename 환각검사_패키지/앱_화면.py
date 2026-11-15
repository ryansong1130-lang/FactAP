# -*- coding: utf-8 -*-
"""
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
 FactAP 앱 화면 (Streamlit) · 대화형 AI 채팅 + 팩트체크 디자인 (2026-11-15)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

■ 실행 방법 (패키지 폴더에서)
  1) 설치: pip install -r requirements.txt
  2) API 키 넣기: .streamlit/secrets.toml 파일을 만들고 아래 한 줄을 써요. (예시: .streamlit/secrets.toml.예시)
       OPENROUTER_API_KEY = "여기에 키"
     ※ 이 파일은 절대 다른 사람에게 보내거나, 깃허브에 올리거나, 화면을 캡처하지 마세요.
  3) 실행: streamlit run 앱_화면.py   → 브라우저가 열려요.

■ 화면 구성 (ChatGPT·Gemini·Claude 같은 채팅형)
  왼쪽 옆 메뉴: FactAP 로고, '＋ 새 검사'(대화 비우기), '최근 검사' 목록(누르면 그 결과를 펼쳐 보여 줌)
  오른쪽 위: '공유' 메뉴 (앱 링크 복사, QR코드, QR코드 그림 내려받기. 내 컴퓨터에서 열었으면 나누는 방법 안내)
             'FactAP 소개' 메뉴 (AI 환각이란?, 기준을 정한 이유, 상위 모델의 종류 등. 글은 앱_소개.py 에서 고쳐요)
             오른쪽 위 메뉴와 예시 카드는 이모티콘 없이, 메뉴 글은 보고서처럼 '~했다/~이다' 문체로 써요 (2026-11-15)
             Streamlit 의 ⋮ 메뉴는 Print, Record screen 만 남기고 숨겨요 (아래 _화면_꾸미기).
  가운데: 처음에는 인사말과 예시 카드, 검사하면 '내 입력(오른쪽 말풍선) → FactAP 결과(왼쪽)'가 대화처럼 쌓여요.
          가장 최근 결과(또는 옆 메뉴에서 고른 결과)만 자세히 펼치고, 나머지는 요약 카드로 보여 줘요.
  아래 입력창 (2026-11-15 대화형): ChatGPT·Gemini 처럼 화면 맨 아래에 입력창 하나만 있어요.
                 ① 질문 → ② AI의 답변 → ③ 출처를 붙여 넣거나 'Fact TAP' → 검사. ('질문: … 답변: …' 으로 한 번에 넣어도 돼요)
                 입력창 위 작은 버튼: 검사 모드(🔬 정밀 = AI 사용 / ⚡ 간이 = AI 없이, 남은 크레딧), 🏷️ 답변 유형, 📝 한 번에 입력(창)
  첫 화면: 큰 인사말, 이 앱이 하는 일(교차 확인·위키백과·기준 6개·형광펜), '예시로 해 보기' 카드 4개
  결과는 '검증 리포트'처럼 보여 줘요 (사실을 검증하는 앱이라서):
        판정 카드(✓ ! ✕ 도장, 등급, 종합 위험도, 세 구간 위험도 눈금, 유형) → 답변 속 문제 문장 형광펜(옆에 찾은 기준 번호)
        → 그 밖에 확인할 점 → 검증 항목(기준별 통과·의심·문제·해당 없음, 펼치면 근거) → 의심되는 환각 종류(사실·입력·맥락 상충)
        → 교차 확인(상위 모델 답변) → AI 사용량 → '↻ 다시 검사', 결과 내려받기(.txt)
  로고는 '검증'을 뜻하는 방패 + 체크, 색은 파랑 → 청록이에요 (.streamlit/config.toml 의 primaryColor 도 같은 파랑).
  유형이 애매하면 두 유형으로 모두 검사해 확률로 섞은 결과와 각 유형의 확률을 보여 줘요 (검사_실행.유형_섞기).
  같은 질문·답변·출처·유형·AI 사용으로 다시 검사하면 저장된 결과를 보여 주고 AI를 다시 부르지 않아요.
  '↻ 다시 검사'를 누르면 저장된 결과를 버리고 처음부터 검사해요. AI 호출이 일부 실패한 결과는 저장하지 않아요.
  검사할 때마다 결과를 기록/검사기록.jsonl 에 저장해요 (설정.기록_저장). 나중에 사람 판정을 적어 검증에 써요.
  휴대폰처럼 좁은 화면에서는 옆 메뉴가 접히고 칸이 위아래로 쌓여요.

이 파일은 '예시'예요. 디자인과 문구는 앱 담당 조원이 자유롭게 바꿔도 돼요.
화면 코드는 검사_실행.환각_검사() 의 결과(보고서)만 쓰기 때문에, 기준 파일을 고쳐도 화면은 그대로 동작해요.
"""
import base64, copy, html, io, ipaddress, os, re, threading
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
등급_색 = {"위험": st.error, "보통": st.warning, "문제 없음": st.success}
등급_표시 = {"문제 없음": "🟢", "보통": "🟡", "위험": "🔴"}
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
:root { --fa-글: #1f2328; --fa-흐림: #6b7280; --fa-선: #e5e7eb; --fa-면: #f4f4f5; --fa-강조: #1d4ed8; --fa-강조2: #0d9488;
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
[data-testid="stMarkdownContainer"]:has(> .fa-옆제목, > .fa-옆빈칸, > .fa-옆로고) { margin-bottom: 0 !important; }
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
.fa-hero, .fa-카드, .fa-답변판, .fa-근거, .fa-통과줄, .fa-확인카드, .fa-종류 { word-break: keep-all; overflow-wrap: anywhere; }
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

/* 검증 리포트 카드 (판정 도장 + 위험도 눈금) */
.fa-카드 { border-radius: 18px; padding: 1rem 1.15rem 0.95rem 1.15rem; border: 1px solid; margin: 0.2rem 0 0.6rem 0; background: #fff; }
.fa-카드-위 { display: flex; align-items: center; justify-content: space-between; gap: 0.8rem; flex-wrap: wrap; }
.fa-판정 { display: flex; align-items: center; gap: 0.7rem; }
.fa-도장 { width: 2.6rem; height: 2.6rem; border-radius: 50%; display: flex; align-items: center; justify-content: center;
  font-size: 1.35rem; font-weight: 900; color: #fff; flex-shrink: 0; box-shadow: 0 0 0 4px rgba(255,255,255,0.9), 0 0 0 5px currentColor; }
.fa-판정-작은글 { font-size: 0.74rem; color: var(--fa-흐림); font-weight: 700; letter-spacing: 0.02em; }
.fa-등급 { font-size: 1.3rem; font-weight: 800; line-height: 1.2; }
.fa-점수 { font-size: 0.85rem; color: var(--fa-흐림); text-align: right; }
.fa-점수 b { font-size: 1.7rem; color: var(--fa-글); margin-left: 0.3rem; font-variant-numeric: tabular-nums; }
.fa-카드 p { margin: 0.6rem 0 0 0; font-size: 0.95rem; }
.fa-쪽지 { display: inline-block; font-size: 0.78rem; padding: 0.15rem 0.6rem; border-radius: 999px; background: #fff;
  border: 1px solid rgba(0,0,0,0.08); margin: 0.55rem 0.35rem 0 0; color: #374151; }
.fa-문제없음 { background: #f0fdf4; border-color: #bbf7d0; color: var(--fa-초록); } .fa-문제없음 .fa-도장 { background: var(--fa-초록); }
.fa-보통 { background: #fffbeb; border-color: #fde68a; color: var(--fa-노랑); } .fa-보통 .fa-도장 { background: #d97706; }
.fa-위험 { background: #fef2f2; border-color: #fecaca; color: var(--fa-빨강); } .fa-위험 .fa-도장 { background: #dc2626; }
.fa-기타 { background: #f8fafc; border-color: var(--fa-선); color: #334155; } .fa-기타 .fa-도장 { background: #64748b; }
.fa-카드 p, .fa-카드 .fa-점수 b { color: var(--fa-글); }
/* 위험도 눈금: 세 구간을 같은 너비로 (문제 없음 | 보통 | 위험), 안에서는 점수에 맞춰 위치 */
.fa-눈금 { margin: 0.85rem 0 0.1rem 0; }
.fa-눈금-줄 { position: relative; display: flex; height: 0.55rem; border-radius: 999px; overflow: visible; }
.fa-눈금-줄 span { flex: 1; height: 100%; }
.fa-눈금-줄 span:nth-child(1) { background: #86efac; border-radius: 999px 0 0 999px; }
.fa-눈금-줄 span:nth-child(2) { background: #fcd34d; }
.fa-눈금-줄 span:nth-child(3) { background: #fca5a5; border-radius: 0 999px 999px 0; }
.fa-눈금-줄 i { position: absolute; top: 50%; width: 1.05rem; height: 1.05rem; border-radius: 50%; background: #fff;
  border: 3px solid var(--fa-글); transform: translate(-50%, -50%); box-shadow: 0 1px 4px rgba(0,0,0,0.25); }
.fa-눈금-글 { display: flex; font-size: 0.72rem; color: var(--fa-흐림); margin-top: 0.3rem; }
.fa-눈금-글 span { flex: 1; text-align: center; }
.fa-소제목 { font-weight: 700; font-size: 1rem; margin: 1.1rem 0 0.4rem 0; color: var(--fa-글); }
.fa-소제목 small { font-weight: 500; color: var(--fa-흐림); font-size: 0.8rem; margin-left: 0.4rem; }
/* 답변 속 문제 문장 형광펜 */
.fa-답변판 { border: 1px solid var(--fa-선); border-radius: 14px; padding: 0.8rem 0.95rem; background: #fcfcfd;
  line-height: 1.85; font-size: 0.95rem; max-height: 22rem; overflow-y: auto; }
.fa-형광 { background: linear-gradient(transparent 35%, #fde68a 35%); padding: 0 0.1rem; border-radius: 2px; color: inherit; }
.fa-형광-강 { background: linear-gradient(transparent 35%, #fecaca 35%); }
.fa-형광 sup { font-size: 0.68rem; font-weight: 700; color: var(--fa-빨강); margin-left: 0.12rem; }
.fa-통과줄 { border-radius: 12px; background: #f0fdf4; color: var(--fa-초록); padding: 0.55rem 0.85rem; font-size: 0.92rem; }
.fa-근거 { border-left: 3px solid #f59e0b; background: #fffbeb; border-radius: 0 10px 10px 0; padding: 0.45rem 0.75rem; margin: 0.35rem 0; font-size: 0.9rem; }
.fa-근거 small { display: block; color: var(--fa-흐림); font-size: 0.75rem; font-weight: 700; margin-bottom: 0.1rem; }
/* 검증 항목 요약, 환각 종류 막대 */
.fa-항목요약 { display: flex; gap: 0.4rem; flex-wrap: wrap; margin-bottom: 0.4rem; }
.fa-항목요약 span { font-size: 0.8rem; border-radius: 999px; padding: 0.15rem 0.65rem; border: 1px solid var(--fa-선); background: #fff; }
.fa-종류들 { margin-bottom: 0.9rem; }
.fa-종류 { display: grid; grid-template-columns: 11rem 1fr 2.6rem; align-items: center; gap: 0.7rem; margin: 0.45rem 0; font-size: 0.9rem; }
.fa-종류 small { display: block; color: var(--fa-흐림); font-size: 0.72rem; line-height: 1.2; }
.fa-종류-줄 { height: 0.5rem; background: #f1f5f9; border-radius: 999px; overflow: hidden; }
.fa-종류-줄 span { display: block; height: 100%; border-radius: 999px; }
.fa-종류 b { text-align: right; font-variant-numeric: tabular-nums; font-size: 0.85rem; }

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
  .fa-종류 { grid-template-columns: 7.2rem 1fr 2.4rem; gap: 0.5rem; }
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
.fa-인사-작은 { font-size: 1.6rem; font-weight: 700; letter-spacing: -0.03em; color: #9ca3af; margin-top: 0.15rem; }
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
.fa-버전 { font-size: 0.7rem; color: #9ca3af; margin: 1.4rem 0 0 0.7rem; }
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
    return '<div class="fa-답변판">' + "<br>".join(줄들) + "</div>", 남은것


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
    st.download_button("📄 결과 내려받기 (.txt)", data=_내려받기_글(보고서).encode("utf-8"), key=f"내려받기_{번호}",
                       file_name=f"{앱_이름}_결과_{시각 or '결과'}.txt", mime="text/plain", use_container_width=True)


def _등급_뜻(지금_등급, 방법):
    """세 등급의 뜻 (지금 등급은 굵게)"""
    줄 = []
    for 등급 in ["문제 없음", "보통", "위험"]:
        글 = f"{등급_표시[등급]} {등급}: {설정.등급_설명.get(등급, '')}"
        줄.append(f"- **{글}** ← 지금 결과" if 등급 == 지금_등급 else f"- {글}")
    with st.expander("등급은 무슨 뜻인가요?"):
        st.markdown("\n".join(줄))
        st.caption(f"종합 위험도(0~1) 기준: {등급_경계_글(방법)}")


# ------------------------------------------------------------------ 결과 그리기
def _눈금_위치(위험도, 방법):
    """위험도(0~1) → 눈금 위의 위치(%). 세 등급 구간을 같은 너비(1/3씩)로 그리고, 구간 안에서는 비례해서 놓아요."""
    경계 = 설정.등급_기준_방법별.get(방법 or 설정.합치는_방법, 설정.등급_기준)
    끝들 = [0.0] + [min(1.0, 상한) for 상한, _ in 경계]
    v = max(0.0, min(1.0, float(위험도)))
    for i in range(len(경계)):
        아래, 위 = 끝들[i], 끝들[i + 1]
        if v < 위 or i == len(경계) - 1:
            안 = 0 if 위 <= 아래 else (v - 아래) / (위 - 아래)
            return 100 * (i + max(0.0, min(1.0, 안))) / len(경계)
    return 100.0


def _위험도_눈금(위험도, 방법):
    경계 = 설정.등급_기준_방법별.get(방법 or 설정.합치는_방법, 설정.등급_기준)
    위치 = _눈금_위치(위험도, 방법)
    글 = "".join(f"<span>{html.escape(이름)}</span>" for _, 이름 in 경계)
    return (f'<div class="fa-눈금" title="등급 경계: {html.escape(등급_경계_글(방법))}"><div class="fa-눈금-줄">'
            + "<span></span>" * len(경계) + f'<i style="left:{위치:.1f}%"></i></div><div class="fa-눈금-글">{글}</div></div>')


def _등급_카드(보고서):
    """검증 리포트의 머리: 판정 도장(✓ ! ✕), 등급, 종합 위험도, 위험도 눈금, 쪽지(유형·AI 사용량)"""
    종합 = 보고서["종합"] or {}
    등급 = 종합.get("등급", "")
    색 = {"문제 없음": "fa-문제없음", "보통": "fa-보통", "위험": "fa-위험"}.get(등급, "fa-기타")
    위험도 = 종합.get("위험도")
    점수 = "" if 위험도 is None else f'<span class="fa-점수">종합 위험도<b>{위험도:.2f}</b></span>'
    눈금 = "" if 위험도 is None else _위험도_눈금(위험도, 종합.get("방법"))
    설명 = 종합.get("등급_설명") or (종합.get("근거") if 보고서["유형"] is None else "")
    쪽지 = []
    if 보고서["유형"]:
        쪽지.append(f"유형: {보고서['유형']}")
    섞기 = 종합.get("유형_섞기")
    if 섞기:
        쪽지 = ["두 유형으로 검사"] + [f"{t} {p:.0%}" for t, p in zip(섞기["유형"], 섞기["확률"])]
    if 종합.get("간이_검사"):
        쪽지.append("간이 검사 (AI 없이)")
    u = 보고서.get("AI_사용량") or {}
    if u.get("호출"):
        쪽지.append(f"AI {u['호출']:.0f}번" + (f" · ${u['비용']:.3f}" if u.get("비용") else ""))
    판정 = (f'<div class="fa-판정"><span class="fa-도장">{판정_아이콘.get(등급, "i")}</span>'
            f'<div><div class="fa-판정-작은글">{앱_이름} 검증 결과</div><div class="fa-등급">{html.escape(str(등급))}</div></div></div>')
    st.markdown(
        f'<div class="fa-카드 {색}"><div class="fa-카드-위">{판정}{점수}</div>{눈금}'
        + (f"<p>{html.escape(str(설명))}</p>" if 설명 else "")
        + "".join(f'<span class="fa-쪽지">{html.escape(s)}</span>' for s in 쪽지) + "</div>",
        unsafe_allow_html=True)


def _결과_자세히(보고서, 번호):
    """가장 최근(또는 고른) 결과: 모든 내용을 보여 줌"""
    종합 = 보고서["종합"]
    섞기 = 종합.get("유형_섞기")
    정보 = 보고서.get("유형_정보") or {}
    if 섞기:      # 섞은 계산식은 아래 근거 글에 있어서, 여기서는 '직접 고르는 방법'만 알려 줘요
        st.caption(f"유형이 {섞기['유형'][0]}인지 {섞기['유형'][1]}인지 애매해서 두 유형의 점수를 확률로 섞었어요. "
                   "유형을 정확히 알면 아래 입력 상자의 '유형'에서 직접 골라 다시 검사해 보세요.")
    elif 정보.get("애매함"):
        st.caption(f"유형 분류가 애매했어요 (1순위 {정보.get('유형')}, 2순위 {정보.get('2순위')}). "
                   "다른 유형이 맞다면 '유형'에서 직접 골라 다시 검사해 보세요.")
    if 종합["등급"] in 등급_표시:
        _등급_뜻(종합["등급"], 종합.get("방법"))

    # 1) 답변 속 문제 문장에 형광펜
    문제들 = _다시_확인할_문장들(보고서)
    st.markdown('<div class="fa-소제목">🖍️ 답변 속 확인할 문장</div>', unsafe_allow_html=True)
    판, 남은것 = _답변_표시(보고서["답변"], 문제들)
    if 판:
        st.markdown(판, unsafe_allow_html=True)
        st.caption("형광펜 = 기준이 문제라고 본 문장 (빨간 형광펜은 더 강한 의심). 옆의 작은 번호는 그 문장을 찾은 기준이에요. "
                   "다른 자료로 꼭 확인해 보세요.")
    elif not 문제들:
        st.markdown('<div class="fa-통과줄">✓ 기준들이 문제라고 표시한 문장이 없어요.</div>', unsafe_allow_html=True)
    else:      # 기준이 짚은 글이 답변 문장과 글자로 딱 맞지 않을 때 (예: 검사 AI가 문장을 바꿔 적음)
        st.caption("답변 문장 가운데 바로 칠할 곳은 찾지 못했어요. 기준이 찾은 내용은 바로 아래 '그 밖에 확인할 점'에 있어요.")
    if 남은것:
        st.markdown(f'<div class="fa-소제목">그 밖에 확인할 점 <small>{len(남은것)}개</small></div>', unsafe_allow_html=True)
        for m in 남은것[:최대_보여줄_문장]:
            st.markdown(f'<div class="fa-근거"><small>{html.escape(m["기준"])}</small>{html.escape(m["글"])}</div>',
                        unsafe_allow_html=True)
        if len(남은것) > 최대_보여줄_문장:
            with st.expander(f"나머지 {len(남은것) - 최대_보여줄_문장}개 더 보기"):
                for m in 남은것[최대_보여줄_문장:]:
                    st.markdown(f"- {m['글']} ({m['기준']})")

    # 2) 검증 항목 (기준별 결과를 체크리스트처럼)
    결과들 = 보고서["기준결과들"]
    def 판정말(r):
        v = r["위험도"]
        if v is None:      # 출처가 없을 때 ②처럼 '해당 없음'인 것과, AI·인터넷이 없어 '확인 불가'인 것을 나눠 보여 줘요
            return ("➖", "해당 없음") if r["상태"] == "해당 없음" else ("➖", "확인 못 함")
        return ("❌", "문제") if v >= 0.6 else ("⚠️", "의심") if v >= 0.3 else ("✅", "통과")
    세기 = {}
    for x in 결과들:
        말 = 판정말(x["결과"])[1]
        세기[말] = 세기.get(말, 0) + 1
    st.markdown(f'<div class="fa-소제목">🧾 검증 항목 <small>기준 {len(결과들)}개</small></div>', unsafe_allow_html=True)
    st.markdown('<div class="fa-항목요약">' + "".join(
        f"<span>{아이콘} {이름} {세기[이름]}</span>" for 아이콘, 이름 in [("✅", "통과"), ("⚠️", "의심"), ("❌", "문제"), ("➖", "확인 못 함"), ("➖", "해당 없음")]
        if 세기.get(이름)) + "</div>", unsafe_allow_html=True)
    for x in 결과들:
        r, 기준 = x["결과"], x["정보"]
        아이콘, 말 = 판정말(r)
        값 = "" if r["위험도"] is None else f" ({r['위험도']:.2f})"
        붙임 = f" ({x['유형']})" if 섞기 and x.get("유형") else ""
        with st.expander(f"{아이콘} {기준['번호']} {기준['이름']}{붙임} · {말}{값}"):
            st.write(r["근거"])
            st.caption(f"맡는 환각: {기준['맡는_환각']} · 방식: {기준['방식']} · 중요도: {중요도(기준):g}")
            for 문장 in r["문제_문장"]:
                st.markdown(f"- {문장}")
    st.caption("종합 위험도 계산: " + str(종합["근거"]))

    # 3) 어떤 환각이 의심되나요? (사실·입력·맥락 상충)
    if 종합.get("종류별"):
        st.markdown('<div class="fa-소제목">🧭 의심되는 환각 종류</div>', unsafe_allow_html=True)
        줄 = []
        for 종류, 값 in 종합["종류별"].items():
            값 = max(0.0, min(1.0, 값 or 0))
            색 = "#ef4444" if 값 >= 0.6 else "#f59e0b" if 값 >= 0.3 else "#22c55e" if 값 > 0 else "#cbd5e1"
            줄.append(f'<div class="fa-종류"><div>{html.escape(종류)}<small>{html.escape(환각_뜻.get(종류, ""))}</small></div>'
                     f'<div class="fa-종류-줄"><span style="width:{max(값 * 100, 2):.0f}%;background:{색}"></span></div><b>{값:.2f}</b></div>')
        st.markdown('<div class="fa-종류들">' + "".join(줄) + "</div>", unsafe_allow_html=True)

    if 보고서["상위모델_답변들"]:
        with st.expander("🤖 교차 확인: 상위 모델들이 다시 답한 내용 보기"):
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
            st.caption("같은 입력의 저장된 결과예요. AI를 다시 부르지 않았어요. 처음부터 다시 하려면 '↻ 다시 검사'를 누르세요.")
        _등급_카드(보고서)
        if 보고서["유형"] is None:                    # 답변 거부 또는 입력 확인 필요
            if 자세히:
                _내려받기_버튼(보고서, 번호)
            return
        if 자세히:
            _결과_자세히(보고서, 번호)
            칸1, 칸2 = st.columns(2)
            with 칸1:
                st.button("↻ 다시 검사", key=f"다시_{번호}", on_click=_다시_검사_누름, args=(번호,),
                          use_container_width=True, help="저장된 결과를 버리고 AI를 다시 불러 처음부터 검사해요.")
            with 칸2:
                _내려받기_버튼(보고서, 번호)
        else:
            st.button("자세히 보기", key=f"펼치기_{번호}", on_click=_펼치기, args=(번호,))


# ------------------------------------------------------------------ 대화형 입력 (2026-11-15: ChatGPT·Gemini 처럼 아래 입력창 하나로)
# 순서: ① 질문 → ② AI의 답변 → ③ 출처(있으면) 또는 [Fact TAP] → 검사
# '질문: … / 답변: … / 출처: …' 처럼 한 번에 붙여 넣으면 알아서 나눠요. '📝 한 번에 입력'(창)으로 넣어도 돼요.
화면_버전 = "2026-11-16 대화형"       # 화면을 고칠 때마다 날짜를 바꾸면, 새 화면이 올라갔는지 바로 알 수 있어요
예시들 = [   # 첫 화면 '예시로 해 보기' 카드: (제목, 질문, 답변). 깔끔하게 보이도록 이모티콘은 넣지 않아요
    ("역사 사실 확인", "세종대왕이 훈민정음을 반포한 해는 언제인가요?",
     "세종대왕은 1443년에 훈민정음을 반포했습니다. 백성이 글을 쉽게 익히도록 만든 글자입니다."),
    ("계산 검산", "학생 5명의 수학 점수 평균이 72점입니다. 학생 1명이 더 들어와 6명의 평균이 75점이 되었다면, 새로 들어온 학생의 점수는 몇 점인가요?",
     "새로 들어온 학생의 점수는 93점입니다.\n1. 처음 5명의 총점: 72 × 5 = 360점\n2. 6명이 된 후 총점: 75 × 6 = 450점\n3. 새로 들어온 학생의 점수: 450 - 360 = 93점"),
    ("논리 추론 따지기", "A는 B의 아버지이고, B는 C의 아버지입니다. C는 A의 무엇인가요?", "C는 A의 손자입니다."),
    ("코드 결과 확인", "다음 Python 코드를 실행하면 무엇이 출력되나요?\n\nd = {\"사과\": 3, \"배\": 5}\nd[\"사과\"] += 2\nd[\"귤\"] = 1\nprint(len(d), d[\"사과\"])",
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
    _, 질문, 답변 = 예시들[번호]
    st.session_state["임시"] = {"질문": 질문, "답변": 답변}
    st.session_state["단계"] = "출처"


def _바로_검사_누름():
    st.session_state["바로_검사"] = True


def _AI_쓰나(키있음):
    return bool(키있음) and st.session_state.get("모드", "정밀") == "정밀"


def _모드_글(키있음):
    return "🔬 정밀 검사" if _AI_쓰나(키있음) else "⚡ 간이 검사"


def _모드_고르기(키있음):
    """ChatGPT 의 '모델 고르기'처럼: 정밀(AI 사용) / 간이(AI 없이) + 남은 크레딧"""
    with st.popover(_모드_글(키있음)):
        st.markdown('<div class="fa-팝제목">검사 모드</div>', unsafe_allow_html=True)
        if 키있음:
            st.radio("검사 모드", ["정밀", "간이"], key="모드", label_visibility="collapsed",
                     format_func=lambda 값: {"정밀": "🔬 정밀 검사", "간이": "⚡ 간이 검사"}[값],
                     captions=["상위 AI 3개에게 다시 묻고 검사 AI·위키백과·논문까지 대조해요. 1~2분, 한 번에 약 $0.05",
                               "AI 없이 프로그램으로 확인하는 기준만 써요. 몇 초, 무료. 사실·출처형은 놓치기 쉬워요"])
        else:
            st.caption("API 키가 없어서 지금은 ⚡ 간이 검사(AI 없이 프로그램 기준만)로 해요. "
                       "키를 넣으면 🔬 정밀 검사를 고를 수 있어요. (README 'API 키 넣기')")
        st.divider()
        _크레딧_내용(키있음)


def _유형_고르기():
    with st.popover("🏷️ " + ("유형 자동" if st.session_state.get("유형_입력", "유형 자동 분류") == "유형 자동 분류"
                             else st.session_state["유형_입력"])):
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
        st.dialog("📝 한 번에 입력하기", width="large")(내용)()
    else:
        with st.expander("📝 한 번에 입력하기", expanded=True):
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
        if st.button("📝 한 번에 입력", key="한번에_버튼"):
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
        if not 대화:
            st.markdown('<div class="fa-옆빈칸">아직 검사한 답변이 없어요.</div>', unsafe_allow_html=True)
        for 번호 in range(len(대화) - 1, -1, -1):
            보고서 = 대화[번호]["보고서"]
            등급 = (보고서["종합"] or {}).get("등급", "")
            제목 = " ".join(str(보고서["질문"]).split())[:28] or "(질문 없음)"
            st.button(f"{등급_표시.get(등급, '⚪')} {제목}", key=f"최근_{번호}", on_click=_펼치기, args=(번호,),
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
        for 번호, (제목, 질문, _) in enumerate(예시들):
            with 칸들[번호 % 2]:
                st.button(f"**{제목}**  \n*{_줄이기(' '.join(질문.split()), 34)}*", key=f"예시_{번호}",
                          on_click=_예시_고름, args=(번호,), use_container_width=True)
    st.markdown(f"""
<div class="fa-찾는것">이런 환각을 찾아요 · <b>사실 상충</b> {환각_뜻["사실 상충"]} · <b>입력 상충</b> {환각_뜻["입력 상충"]} ·
<b>맥락 상충</b> {환각_뜻["맥락 상충"]}</div>""", unsafe_allow_html=True)
    if not 키있음:
        st.caption("지금은 API 키가 없어 ⚡ 간이 검사(AI 없이 프로그램 기준만)로 해요. (README의 'API 키 넣기')")


def _진행_중_대화(키있음):
    """질문 → 답변 → 출처를 받는 동안의 대화"""
    단계, 임시 = st.session_state["단계"], st.session_state["임시"]
    with st.chat_message("user"):
        st.markdown('<div class="fa-말">질문</div>', unsafe_allow_html=True)
        st.text(_줄이기(임시.get("질문", ""), 500))
    if 단계 == "답변":
        with st.chat_message("assistant", avatar=로고_그림):
            st.markdown("좋아요! 이 질문에 **AI가 뭐라고 답했나요?** 아래 입력창에 답변을 그대로 붙여 넣어 주세요.")
            st.button("↩ 처음부터", key="처음부터_1", on_click=_처음부터)
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
                st.button("↩ 처음부터", key="처음부터_2", on_click=_처음부터, use_container_width=True)
        st.caption(f"{_모드_글(키있음)} · 유형: {st.session_state.get('유형_입력', '유형 자동 분류')}"
                   + (" · 1~2분 걸려요" if _AI_쓰나(키있음) else " · 몇 초면 끝나요"))


# ------------------------------------------------------------------ 화면
st.set_page_config(page_title=앱_이름, page_icon="🔎", layout="centered")
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

# 이번에 할 검사 정하기: 입력창, Fact TAP, 한 번에 입력, 또는 결과 아래 '↻ 다시 검사'
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
            상태 = st.status("🔎 사실 확인하는 중…" + (" (1~2분)" if 요청["AI_사용"] else ""), expanded=True)
            보고서 = 환각_검사(요청["질문"], 요청["답변"], 요청["출처"], 요청["유형"], 요청["AI_사용"],
                          진행_알림=lambda 글: 상태.write(글))
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

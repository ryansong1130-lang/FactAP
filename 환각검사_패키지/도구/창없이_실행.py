"""
창없이_실행.py : 검은 창(명령 프롬프트) 없이 FactAP 앱을 켜고 끄는 도우미 (2026-11-15)

[누가 부르나요?]
  - 앱_열기_창없이.vbs (바탕화면 'FactAP' 아이콘)  → 이 파일을 '켜기'로 불러요.
  - 앱_끄기.vbs        (바탕화면 'FactAP 끄기' 아이콘) → 이 파일을 '끄기'로 불러요.
  직접 실행할 일은 없어요. (확인용: python 도구/창없이_실행.py 켜기 / 끄기)

[켜기]
  1) 앱이 이미 켜져 있으면 브라우저만 열어요. (두 번 켜지지 않게)
  2) 필요한 프로그램(streamlit 1.40 이상, openpyxl)이 없으면 먼저 설치해요. (처음 한 번)
  3) 보이지 않게 앱을 켜요:  python -m streamlit run 앱_화면.py --server.headless true --server.port 8501 --server.address 127.0.0.1
     (127.0.0.1 = 이 컴퓨터 안에서만 열려요. 같은 와이파이의 다른 사람이 들어올 수 없고, 방화벽 경고 창도 안 떠요.
      다른 사람과 나눌 때는 인터넷 링크(Streamlit Cloud)를 써요. README 11번)
  4) 앱이 준비되면 브라우저로 http://localhost:8501 을 열어요.

[끄기]
  8501번 포트에서 돌고 있는 앱(파이썬 프로그램)을 찾아서 꺼요.
  그 포트를 쓰는 프로그램이 파이썬이 아니면 건드리지 않아요.

[문제가 생기면]
  앱이 내는 글(오류 포함)은 기록/앱_실행_기록.txt 에 남아요. (기록/ 폴더는 깃허브에 올라가지 않아요)
  앱이 안 열리면 이 파일을 보거나, 앱_열기.bat 로 열어서 검은 창에 나오는 오류를 보세요.

연구 값(기준, 점수, 등급)과는 상관없는 파일이에요. 앱을 여닫는 방법만 다뤄요.
"""
import os
import subprocess
import sys
import time
import traceback
import urllib.request
import webbrowser

폴더 = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # 패키지 폴더 (이 파일은 도구/ 안에 있어요)
포트 = 8501
주소 = f"http://localhost:{포트}"                  # 브라우저에 여는 주소
확인_주소 = f"http://127.0.0.1:{포트}/_stcore/health"   # 앱이 켜졌는지 물어보는 주소
기록_폴더 = os.path.join(폴더, "기록")
글_파일 = os.path.join(기록_폴더, "앱_실행_기록.txt")
윈도우 = os.name == "nt"
창_없이 = 0x08000000 if 윈도우 else 0          # CREATE_NO_WINDOW: 검은 창을 만들지 않아요
따로_묶기 = 0x00000200 if 윈도우 else 0         # CREATE_NEW_PROCESS_GROUP: 이 도우미가 끝나도 앱은 계속 돌아요
기다릴_초 = 90                                 # 앱이 켜질 때까지 기다리는 최대 시간 (처음 켤 때는 느릴 수 있어요)


# ------------------------------------------------------------------ 작은 도구들
def 알림(글, 종류="정보"):
    """윈도우에서는 작은 알림 창을, 다른 컴퓨터에서는 글을 보여 줘요."""
    if 윈도우:
        import ctypes
        아이콘 = {"정보": 0x40, "경고": 0x30, "오류": 0x10}[종류]
        맨_앞에 = 0x10000 | 0x40000                # MB_SETFOREGROUND | MB_TOPMOST (숨은 프로그램이라 앞으로 꺼내요)
        ctypes.windll.user32.MessageBoxW(None, 글, "FactAP", 아이콘 | 맨_앞에)
    else:
        print(f"[FactAP {종류}] {글}")


def 파이썬():
    """앱을 켤 파이썬. pythonw.exe 로 불렸으면 옆의 python.exe 를 써요 (창은 어차피 숨겨요)."""
    실행 = sys.executable
    if os.path.basename(실행).lower() == "pythonw.exe":
        옆 = os.path.join(os.path.dirname(실행), "python.exe")
        if os.path.exists(옆):
            return 옆
    return 실행


def 켜져_있나():
    """앱 서버가 대답하면 True. (프록시를 거치지 않고 내 컴퓨터에 바로 물어봐요)"""
    여는_도구 = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        with 여는_도구.open(확인_주소, timeout=1.5) as 응답:
            return 응답.status == 200
    except Exception:
        return False


def 실행(명령, **더):
    """창 없이 명령을 실행하고 끝날 때까지 기다려요."""
    return subprocess.run(명령, creationflags=창_없이, stdin=subprocess.DEVNULL, **더)


def 준비_됐나():
    """streamlit 1.40 이상, openpyxl, segno(공유용 QR코드)가 설치되어 있으면 True."""
    검사 = ("import openpyxl, segno, streamlit, sys; "
            "sys.exit(0 if tuple(int(x) for x in streamlit.__version__.split('.')[:2]) >= (1, 40) else 1)")
    try:
        return 실행([파이썬(), "-c", 검사], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode == 0
    except OSError:
        return False


def 기록_끝부분(줄_수=8):
    try:
        with open(글_파일, encoding="utf-8", errors="replace") as f:
            줄들 = [줄.rstrip() for 줄 in f if 줄.strip()]
        return "\n".join(줄들[-줄_수:])
    except OSError:
        return ""


# ------------------------------------------------------------------ 켜기
def 켜기(브라우저_열기=True):
    if 켜져_있나():                                   # 이미 켜져 있으면 브라우저만
        if 브라우저_열기:
            webbrowser.open(주소)
        return True

    os.makedirs(기록_폴더, exist_ok=True)
    환경 = dict(os.environ, PYTHONUTF8="1")
    with open(글_파일, "wb") as 글:                    # 켤 때마다 새로 써요 (파일이 계속 커지지 않게)
        글.write(f"[FactAP] {time.strftime('%Y-%m-%d %H:%M:%S')} 창 없이 켜기\n".encode("utf-8"))
        글.flush()

        if not 준비_됐나():                            # 처음 한 번: 필요한 프로그램 설치
            알림("처음 한 번 필요한 프로그램(streamlit, openpyxl, segno)을 설치해요.\n\n"
                 "확인을 누르고 몇 분 기다리면, 다 되었을 때 브라우저에 앱이 열려요.\n"
                 "(설치하는 동안에는 아무 창도 보이지 않아요)")
            설치 = 실행([파이썬(), "-m", "pip", "install", "-r", "requirements.txt"],
                       cwd=폴더, env=환경, stdout=글, stderr=subprocess.STDOUT)
            글.flush()
            if 설치.returncode != 0 or not 준비_됐나():
                알림("필요한 프로그램을 설치하지 못했어요.\n\n"
                     "인터넷 연결을 확인하고 다시 해 보세요. 그래도 안 되면 앱_열기.bat 를 두 번 클릭해서 "
                     "검은 창에 나오는 오류를 확인하세요.\n\n자세한 내용: 기록\\앱_실행_기록.txt", "오류")
                return False

        앱 = subprocess.Popen(
            [파이썬(), "-m", "streamlit", "run", "앱_화면.py",
             "--server.headless", "true", "--server.port", str(포트), "--server.address", "127.0.0.1"],
            cwd=폴더, env=환경, stdin=subprocess.DEVNULL, stdout=글, stderr=subprocess.STDOUT,
            creationflags=창_없이 | 따로_묶기, start_new_session=not 윈도우)

    끝 = time.time() + 기다릴_초
    while time.time() < 끝:
        if 켜져_있나():
            if 브라우저_열기:
                webbrowser.open(주소)
            return True
        if 앱.poll() is not None:                       # 앱이 켜지다가 멈췄어요
            끝부분 = 기록_끝부분()
            if "not available" in 끝부분 or "already in use" in 끝부분:
                알림(f"다른 프로그램이 {포트}번 포트를 쓰고 있어서 앱을 켜지 못했어요.\n\n"
                     "검은 창으로 연 FactAP(앱_열기.bat)이 있으면 그 창을 닫고, 컴퓨터를 다시 시작한 뒤 해 보세요.", "오류")
                return False
            알림("앱이 켜지지 않았어요.\n\n" + (끝부분 or "(오류 내용 없음)") +
                 "\n\n자세한 내용: 기록\\앱_실행_기록.txt\n앱_열기.bat 로 열면 검은 창에서 오류를 볼 수 있어요.", "오류")
            return False
        time.sleep(0.5)

    알림(f"앱이 평소보다 늦게 켜지고 있어요.\n\n1분쯤 뒤에 브라우저 주소창에 {주소} 를 넣어 보세요.\n"
         "그래도 안 열리면 앱_끄기.vbs 로 끈 뒤 앱_열기.bat 로 열어서 오류를 확인하세요.", "경고")
    return False


# ------------------------------------------------------------------ 끄기
def 포트_쓰는_번호들(netstat_글, 포트_번호=포트):
    """netstat -ano 결과에서 그 포트를 '듣고 있는' 프로그램 번호(PID)를 찾아요.
    상태 글(LISTENING)은 윈도우 언어마다 다를 수 있어서, 상대 주소가 0.0.0.0:0 / [::]:0 / *:* 인 줄을 봐요."""
    번호들 = set()
    for 줄 in netstat_글.splitlines():
        칸 = 줄.split()
        if len(칸) < 4 or 칸[0].upper() != "TCP":
            continue
        내_주소, 상대_주소, 번호 = 칸[1], 칸[2], 칸[-1]
        if 내_주소.rsplit(":", 1)[-1] == str(포트_번호) and 상대_주소 in ("0.0.0.0:0", "[::]:0", "*:*") and 번호.isdigit():
            if int(번호) > 0:
                번호들.add(int(번호))
    return 번호들


def _파이썬_프로그램인가(번호):
    """그 번호의 프로그램 이름이 python... 이면 True (다른 프로그램은 끄지 않아요)."""
    결과 = 실행(["tasklist", "/FI", f"PID eq {번호}", "/FO", "CSV", "/NH"], capture_output=True)
    첫칸 = 결과.stdout.decode("mbcs" if 윈도우 else "utf-8", errors="ignore").strip().split(",")[0].strip('"').lower()
    return 첫칸.startswith("python")


def 끄기(알리기=True):
    if not 켜져_있나():
        if 알리기:
            알림("켜져 있는 FactAP 앱이 없어요.")
        return True

    if 윈도우:
        결과 = 실행(["netstat", "-ano"], capture_output=True)
        번호들 = [번호 for 번호 in 포트_쓰는_번호들(결과.stdout.decode("mbcs", errors="ignore")) if _파이썬_프로그램인가(번호)]
        for 번호 in 번호들:
            실행(["taskkill", "/PID", str(번호), "/T", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    else:                                               # 맥·리눅스 (확인용)
        결과 = subprocess.run(["lsof", "-t", f"-iTCP:{포트}", "-sTCP:LISTEN"], capture_output=True, text=True)
        번호들 = [int(x) for x in 결과.stdout.split() if x.isdigit()]
        import signal
        for 번호 in 번호들:
            try:
                os.kill(번호, signal.SIGTERM)
            except OSError:
                pass

    for _ in range(20):                                 # 꺼질 때까지 최대 10초 기다려요
        if not 켜져_있나():
            if 알리기:
                알림("FactAP 앱을 껐어요.")
            return True
        time.sleep(0.5)
    if 알리기:
        알림(f"앱을 끄지 못했어요.\n\n컴퓨터를 다시 시작하면 꺼져요. 또는 작업 관리자에서 'Python'을 찾아 '작업 끝내기'를 누르세요.", "경고")
    return False


# ------------------------------------------------------------------ 시작
if __name__ == "__main__":
    할_일 = sys.argv[1] if len(sys.argv) > 1 else "켜기"
    try:
        if 할_일 in ("켜기", "start"):
            켜기()
        elif 할_일 in ("끄기", "stop"):
            끄기()
        else:
            print("사용법: python 도구/창없이_실행.py 켜기  또는  끄기")
    except Exception:
        알림("예상하지 못한 문제가 생겼어요.\n\n" + traceback.format_exc()[-800:] +
             "\n\n앱_열기.bat 로 열어서 검은 창에 나오는 오류를 확인하세요.", "오류")

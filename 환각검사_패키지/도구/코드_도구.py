# -*- coding: utf-8 -*-
"""
코드형 기준(⑤ 코드 직접 실행, ⑥ 오류 여부·출력 형식 일치)이 함께 쓰는 도구

  코드_실행(코드)          : 질문 속 파이썬 코드를 안전하게 실행해서 실제 출력이나 오류 이름을 얻음
  답변_주장_뽑기(답변)     : 답변이 '출력은 이것'이라고 주장한 부분(코드 블록, `…`, **…**, 첫 줄)을 뽑음
  오류라고_했나(답변)      : 답변 앞부분이 '에러가 난다'고 했는지

■ 안전하게 실행하는 방법
  - 새 파이썬을 따로 띄워서(-I: 사용자 설정 무시) 빈 임시 폴더에서 실행하고, 3초가 넘으면 멈춰요.
  - 파일·인터넷·운영체제를 건드리는 코드(os, sys, subprocess, socket, open(…), eval, exec 등)는
    실행하지 않고 "실행 안 함"으로 돌려줘요. 사용자가 넣은 코드가 컴퓨터를 망가뜨리지 못하게 하기 위해서예요.
  - input()이 있으면 입력을 기다리느라 멈추므로 실행하지 않아요.
  - random, time, datetime 을 쓰면 실행할 때마다 결과가 달라서 비교하지 않아요.
"""
import os, re, subprocess, sys, tempfile
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import 설정
from 도구.글_도구 import 마크다운_지우기

허용_모듈 = {"math", "itertools", "functools", "collections", "string", "re", "decimal", "fractions",
           "statistics", "operator", "heapq", "bisect", "copy", "dataclasses", "typing", "enum"}
위험_표현 = [r"\bopen\s*\(", r"\beval\s*\(", r"\bexec\s*\(", r"\bcompile\s*\(", r"__import__", r"__builtins__",
          r"__subclasses__", r"__globals__", r"__code__", r"\bglobals\s*\(", r"\bbreakpoint\s*\("]
매번_다름 = {"random", "time", "datetime", "secrets", "uuid"}


def _가져온_모듈(코드):
    모듈 = set(re.findall(r"^\s*import\s+([\w.]+)", 코드, re.M))
    모듈 |= set(re.findall(r"^\s*from\s+([\w.]+)\s+import", 코드, re.M))
    for 줄 in re.findall(r"^\s*import\s+(.+)$", 코드, re.M):            # import a, b
        모듈 |= {x.strip().split()[0] for x in 줄.split(",") if x.strip()}
    return {m.split(".")[0] for m in 모듈}


def 실행해도_되나(코드):
    """(된다/안 된다, 이유)"""
    if not 코드.strip():
        return False, "질문에서 코드를 찾지 못했어요"
    모듈 = _가져온_모듈(코드)
    if 모듈 & 매번_다름:
        return False, f"실행할 때마다 결과가 달라지는 모듈({', '.join(sorted(모듈 & 매번_다름))})을 써서 비교할 수 없어요"
    if 모듈 - 허용_모듈:
        return False, f"안전을 위해 실행하지 않는 모듈이 있어요: {', '.join(sorted(모듈 - 허용_모듈))}"
    if re.search(r"\binput\s*\(", 코드):
        return False, "input()이 있어 입력 없이 실행할 수 없어요"
    for 표현 in 위험_표현:
        if re.search(표현, 코드):
            return False, "파일이나 시스템을 건드릴 수 있는 코드가 있어 실행하지 않았어요"
    return True, ""


def _자원_제한():                         # 리눅스·맥에서만: 메모리 512MB, CPU 3초
    try:
        import resource
        resource.setrlimit(resource.RLIMIT_AS, (512 * 1024 * 1024,) * 2)
        resource.setrlimit(resource.RLIMIT_CPU, (설정.코드_시간제한_초 + 1,) * 2)
    except Exception:
        pass


def 코드_실행(코드):
    """돌려주는 값: {"상태": "출력"/"오류"/"시간 초과"/"실행 안 함", "출력": 글, "오류": 오류 이름, "메시지": 글}"""
    if not getattr(설정, "코드_실행_허용", True):
        return {"상태": "실행 안 함", "출력": "", "오류": "", "메시지": "설정에서 코드 실행을 껐어요 (설정.코드_실행_허용)"}
    된다, 이유 = 실행해도_되나(코드)
    if not 된다:
        return {"상태": "실행 안 함", "출력": "", "오류": "", "메시지": 이유}
    환경 = {"PYTHONIOENCODING": "utf-8", "PYTHONHASHSEED": "0", "PATH": os.environ.get("PATH", "")}
    if os.name == "nt":
        환경["SYSTEMROOT"] = os.environ.get("SYSTEMROOT", "")
    with tempfile.TemporaryDirectory() as 임시폴더:
        try:
            # -X utf8: -I 를 쓰면 PYTHONIOENCODING 이 무시되므로, 윈도우에서도 한글 출력이 UTF-8로 나오게 직접 지정
            r = subprocess.run([sys.executable, "-I", "-X", "utf8", "-c", 코드], capture_output=True, text=True, encoding="utf-8",
                               timeout=설정.코드_시간제한_초, cwd=임시폴더, env=환경,
                               preexec_fn=_자원_제한 if os.name != "nt" else None)
        except subprocess.TimeoutExpired:
            return {"상태": "시간 초과", "출력": "", "오류": "", "메시지": f"{설정.코드_시간제한_초}초 안에 끝나지 않았어요"}
    if r.returncode != 0:
        마지막 = (r.stderr.strip().splitlines() or [""])[-1]
        오류 = re.match(r"([A-Za-z_][\w.]*(?:Error|Exception|Interrupt|Exit))", 마지막)
        return {"상태": "오류", "출력": r.stdout, "오류": 오류.group(1).split(".")[-1] if 오류 else "오류", "메시지": 마지막}
    return {"상태": "출력", "출력": r.stdout, "오류": "", "메시지": ""}


# ------------------------------------------------------------------ 답변 읽기
def 답변_주장_뽑기(답변):
    """답변이 '출력값'이라고 내세운 부분들 (원래 모양 그대로)"""
    글 = 답변 or ""
    후보 = []
    for 블록 in re.findall(r"```([a-zA-Z]*)\n(.*?)```", 글, re.S):
        종류, 내용 = 블록
        if 종류.lower() in ("python", "py") or re.search(r"print\(|>>>|^\s*def |^\s*import ", 내용, re.M):
            continue                           # 코드 설명용 블록은 출력이 아님
        후보.append(내용.strip("\n"))
        if len(후보) >= 2:
            break
    앞부분 = "\n".join([l for l in 글.splitlines() if l.strip()][:4])
    후보 += re.findall(r"\*\*`?([^*`]+?)`?\*\*", 앞부분)
    후보 += re.findall(r"`([^`\n]+)`", 앞부분)
    for 줄 in [l for l in 글.splitlines() if l.strip() and not l.strip().startswith("```")][:2]:
        줄 = 마크다운_지우기(줄).strip()
        줄 = re.sub(r"^(실행\s*)?(출력\s*결과|출력값|출력|결과)\s*(는|은)?\s*[:：]?\s*", "", 줄)
        if 줄:
            후보.append(줄)
    return [x for x in 후보 if x.strip()]


def 느슨하게(글):
    """따옴표, 괄호, 쉼표, 띄어쓰기, 대소문자를 무시한 모양"""
    return re.sub(r"[\s'\"`,()\[\]{}]", "", 마크다운_지우기(글 or "")).lower()


def 엄격하게(글):
    """줄 끝 공백과 여러 칸 띄어쓰기만 정리한 모양 (형식까지 비교)"""
    return "\n".join(re.sub(r"[ \t]+", " ", l).strip() for l in (글 or "").strip().splitlines())


def 오류라고_했나(답변):
    """답변 앞부분이 오류(에러)가 난다고 했는지. 돌려주는 값: (했나, 말한 오류 이름 목록)"""
    줄들 = [l for l in (답변 or "").splitlines() if l.strip()][:6]
    앞 = "\n".join(줄들)
    이름 = list(dict.fromkeys(re.findall(r"[A-Z][A-Za-z]*(?:Error|Exception)", 앞)))
    부정 = re.search(r"(에러|오류|예외)[가는이]?\s*(발생하지|나지|없|일어나지)", 앞)
    if 이름 and not 부정:
        return True, 이름
    if not 이름 and re.search(r"(에러|오류|예외)[가이]?\s*(발생|납니다|나요|난다)", 앞) and not 부정:
        return True, []
    return False, 이름

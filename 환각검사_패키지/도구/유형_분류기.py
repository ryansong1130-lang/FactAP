# -*- coding: utf-8 -*-
"""
AI 답변 유형 분류기 (질문 + 답변 사용)

참고 논문: 김학수, 안영훈, 서정연(2003), 「한국어 질의응답시스템을 위한 지지벡터기계 기반의
질의유형분류기」, 정보과학회논문지: 소프트웨어 및 응용 30(5), 466-475.

논문의 4단계를 그대로 따름
  1) 자질 추출  : 단어(어휘) + 의미 표지(사전) + 슬라이딩 윈도(단어 쌍)      [논문 3.2]
  2) 자질 선택  : 카이 제곱 통계량, 유형별 최댓값으로 순위를 매겨 상위 K개만 사용 [논문 3.3, 식1, 식2]
  3) 질의 표현  : tfc 가중치 (논문에서 가장 좋았던 방법)                       [논문 3.4, 식6]
  4) 범주화     : 지지 벡터 기계(SVM), 유형마다 하나씩(one-vs-rest)             [논문 3.5]

논문과 다른 점
  - 형태소 분석기 대신 간단한 단어 자르기와 조사 떼기를 사용 (추가 설치 없이 실행되게)
  - 개체명 사전(47만 개) 대신 우리 6개 유형에 맞춘 작은 의미 표지 사전을 사용
  - 질문뿐 아니라 답변의 자질도 같이 사용 (질문 자질은 Q_, 답변 자질은 A_ 로 구분)

필요한 것: 파이썬 3, openpyxl (pip install openpyxl). 다른 설치는 필요 없음.

사용법 (명령 프롬프트에서 이 파일이 있는 폴더로 이동한 뒤)
  python 유형_분류기.py 학습        → 채점 결과 엑셀로 학습, 유형_분류_모델.json 저장
  python 유형_분류기.py 검증        → 질문 단위 교차검증, 유형_분류_검증결과.xlsx 저장
  python 유형_분류기.py 분류        → 질문과 답변을 직접 입력해서 유형 확인

앱에서 쓸 때
  from 유형_분류기 import 모델_불러오기, 분류하기
  모델 = 모델_불러오기("유형_분류_모델.json")
  결과 = 분류하기(모델, 질문, 답변)
  결과["유형"], 결과["확신도"], 결과["애매함"], 결과["유형_불일치"]

  같은 질문에 대한 다른 AI들의 답변도 있으면 같이 넣어 주면 입력 상충까지 확인함
  결과 = 분류하기(모델, 질문, 답변, 다른_답변들=[답변2, 답변3])
  결과["입력상충_의심"], 결과["근거없는_문장"]

두 가지 확인 기능
  - 유형_불일치  : 질문만 보고 정한 유형과, 질문+답변을 보고 정한 유형이 다름
                   (질문에서 묻지 않은 쪽으로 답했을 가능성)
  - 입력상충_의심: 지문 이해형에서, 답변 문장 중 지문에도 없고 다른 AI 답변에도 없는
                   표현이 많은 문장이 있음 (지문에 없는 내용을 덧붙였을 가능성)
"""
import json, math, os, random, re, sys
from collections import Counter, defaultdict

유형목록 = ["사실 지식형", "수치 계산형", "논리 추론형", "출처 인용형", "지문 이해형", "코드 결과형"]

# ------------------------------------------------------------------ 설정
설정 = {
    "윈도크기": 1,          # 슬라이딩 윈도 크기. 1이면 단어 쌍을 만들지 않음.
                            # 우리 자료에서는 1(93.7%)이 2(92.9%), 3(91.8%), 6(91.6%)보다 좋았음
                            # (논문은 질문 7,726개, 우리는 120개라 단어 쌍이 너무 드물게 나옴)
    "자질수": 3000,         # 카이 제곱으로 남길 자질 수
    "최소출현": 2,          # 두 개 이상의 질의에 나온 자질만 사용 (논문 4.2.1)
    "답변글자수": 600,      # 답변은 앞부분만 사용 (길이에 휘둘리지 않게)
    "답변가중": 1.0,        # 답변 자질 비중 (질문 자질은 1.0)
    "SVM_람다": 0.0005,     # SVM 규제 세기
    "SVM_반복": 30,         # SVM 학습 반복 횟수
    "애매기준": 0.5,        # 1등과 2등 점수 차이가 이보다 작으면 '애매함'
                            # (검증: 0.25 미만 정확도 60%, 0.25~0.5는 80%, 1.5 이상은 99.6%)
    "근거기준": 0.4,        # 한 문장에서 '지문에도 없고 다른 답변에도 없는' 표현의 비율이
                            # 이보다 크면 근거 없는 문장으로 봄
}

# ------------------------------------------------------------------ 1) 자질 추출
# 논문의 '의미 표지'에 해당하는 사전. 단어가 여기에 맞으면 단어 대신 표지를 사용 (논문 3.2)
의미표지사전 = [
    ("%의문_수량", r"^(얼마|몇|몇개|몇번|몇명|몇년|몇일|몇살|얼마나)"),
    ("%의문_시간", r"^(언제)"),
    ("%의문_장소", r"^(어디)"),
    ("%의문_인물", r"^(누구|누가)"),
    ("%의문_사물", r"^(무엇|무슨|어떤|어느)"),
    ("%계산어",    r"^(계산|합|합계|평균|확률|비율|넓이|부피|둘레|속력|속도|이자|할인|퍼센트|배수|약수|나머지|총)"),
    ("%논리어",    r"^(모든|반드시|항상|참|거짓|명제|조건|가정|만약|라면|이면|순서|모순|결론|추론|따라서|그러므로|즉)"),
    ("%출처어",    r"^(논문|학술지|저널|저자|출처|인용|doi|게재|발표|연구진|학회|출판|journal|et)"),
    ("%지문어",    r"^(다음|지문|글쓴이|본문|윗글|아래|위)"),
    ("%코드어",    r"^(def|print|return|for|while|if|else|import|range|len|코드|출력|실행|함수|변수|파이썬|python)"),
    ("%단위",      r"^\d*(cm|mm|km|m|kg|g|원|달러|개|명|시간|분|초|%|도|년|월|일|살)$"),
    ("%숫자",      r"^\d[\d,\.]*$"),
]
의미표지사전 = [(표지, re.compile(패턴, re.I)) for 표지, 패턴 in 의미표지사전]

조사 = ("으로부터", "에서는", "에게서", "이라면", "으로는", "이라고", "까지", "부터", "에서", "에게", "으로", "라면",
        "이다", "입니다", "이며", "하고", "와는", "과는", "보다", "처럼", "만큼", "은", "는", "이", "가", "을", "를",
        "의", "에", "와", "과", "도", "로", "만", "요")


def 단어로_자르기(글):
    글 = 글.lower()
    단어들 = re.findall(r"```|[a-z_]+\(|[가-힣]+|[a-z_]+|\d[\d,\.]*[a-z가-힣%]*|[=+\-*/×÷<>]", 글)
    결과 = []
    for w in 단어들:
        if re.fullmatch(r"[가-힣]+", w) and len(w) > 1:   # 조사 떼기 (형태소 분석 대신)
            for j in 조사:
                if w.endswith(j) and len(w) > len(j):
                    w = w[: -len(j)]
                    break
        결과.append(w)
    return 결과


def 표지_붙이기(단어):
    if 단어 == "```" or 단어.endswith("("):
        return "%코드기호"
    if re.fullmatch(r"[=+\-*/×÷<>]", 단어):
        return "%수식기호"
    for 표지, 패턴 in 의미표지사전:
        if 패턴.search(단어):
            return 표지
    return 단어


def 형식_자질(질문, 답변):
    """글의 형태에서 나오는 자질 (길이, 숫자 개수 등)"""
    f = []
    숫자수 = len(re.findall(r"\d[\d,\.]*", 질문))
    f.append("Q_#숫자" + ("0" if 숫자수 == 0 else "1" if 숫자수 == 1 else "2이상"))
    f.append("Q_#길이" + ("짧음" if len(질문) < 60 else "보통" if len(질문) < 250 else "김"))
    f.append("Q_#문장" + ("1" if len(re.findall(r"[.?!]\s", 질문)) < 1 else "2이상"))
    if "\n" in 질문:
        f.append("Q_#줄바꿈")
    if re.search(r"\d\s*[×x\*÷/\+\-=]\s*\d", 답변):
        f.append("A_#수식")
    return f


def 자질_추출(글, 앞말, 윈도):
    단어 = [표지_붙이기(w) for w in 단어로_자르기(글)]
    자질 = [앞말 + w for w in 단어]                                   # 단어 하나짜리 자질
    for i in range(len(단어)):                                        # 슬라이딩 윈도 (단어 쌍)
        for k in range(1, 윈도):
            if i + k < len(단어):
                자질.append(앞말 + 단어[i] + "/" + 단어[i + k])
    return 자질


def 전체_자질(질문, 답변, 설정값=설정):
    w = 설정값["윈도크기"]
    f = 자질_추출(질문, "Q_", w)
    if 답변 and 설정값["답변가중"] > 0:
        f += 자질_추출(답변[: 설정값["답변글자수"]], "A_", w)
    f += 형식_자질(질문, 답변 or "")
    return f


# ------------------------------------------------------------------ 2) 자질 선택 (카이 제곱)
def 카이제곱_선택(자질목록, 정답, 개수, 최소출현):
    N = len(자질목록)
    포함 = defaultdict(Counter)            # 자질 → 유형별 포함 문서 수
    유형수 = Counter(정답)
    for 자질, y in zip(자질목록, 정답):
        for t in set(자질):
            포함[t][y] += 1
    점수 = {}
    for t, c in 포함.items():
        전체 = sum(c.values())
        if 전체 < 최소출현:
            continue
        최고 = 0.0
        for 유형 in 유형수:                                       # 식1
            A = c[유형]; B = 전체 - A
            C = 유형수[유형] - A; D = N - 유형수[유형] - B
            분모 = (A + C) * (B + D) * (A + B) * (C + D)
            if 분모:
                최고 = max(최고, N * (A * D - C * B) ** 2 / 분모)  # 식2: 유형 중 최댓값
        점수[t] = 최고
    순위 = sorted(점수, key=lambda t: -점수[t])[:개수]
    return 순위, 점수


# ------------------------------------------------------------------ 3) tfc 가중치
def tfc_벡터(자질, idf, 답변가중):
    tf = Counter(자질)
    v = {}
    for t, f in tf.items():
        if t in idf:
            v[t] = f * idf[t] * (답변가중 if t.startswith("A_") else 1.0)
    길이 = math.sqrt(sum(x * x for x in v.values())) or 1.0       # 식6의 분모 (정규화)
    return {t: x / 길이 for t, x in v.items()}


# ------------------------------------------------------------------ 4) SVM (선형, one-vs-rest)
def SVM_학습(벡터들, 정답, 람다, 반복, 씨앗=0):
    """Pegasos 방식의 선형 SVM. 외부 라이브러리 없이 동작."""
    가중치 = {}
    rng = random.Random(씨앗)
    for 유형 in 유형목록:
        y = [1 if g == 유형 else -1 for g in 정답]
        if 1 not in y:
            continue
        w = defaultdict(float); b = 0.0; 배율 = 1.0; step = 0
        순서 = list(range(len(벡터들)))
        for _ in range(반복):
            rng.shuffle(순서)
            for i in 순서:
                step += 1
                η = 1.0 / (람다 * (step + 10))
                x = 벡터들[i]
                점 = 배율 * sum(w[t] * v for t, v in x.items()) + b
                배율 *= (1 - η * 람다)
                if 배율 < 1e-9:
                    for t in w: w[t] *= 배율
                    배율 = 1.0
                if y[i] * 점 < 1:
                    for t, v in x.items():
                        w[t] += η * y[i] * v / 배율
                    b += η * y[i] * 0.1
        가중치[유형] = ({t: v * 배율 for t, v in w.items() if abs(v * 배율) > 1e-6}, b)
    return 가중치


def 점수_계산(가중치, x):
    return {유형: sum(w.get(t, 0.0) * v for t, v in x.items()) + b for 유형, (w, b) in 가중치.items()}


# ------------------------------------------------------------------ 학습 / 분류
def 학습하기(데이터, 설정값=설정):
    """데이터: [(질문, 답변, 유형), ...]"""
    자질목록 = [전체_자질(q, a, 설정값) for q, a, _ in 데이터]
    정답 = [y for _, _, y in 데이터]
    선택, 점수 = 카이제곱_선택(자질목록, 정답, 설정값["자질수"], 설정값["최소출현"])
    선택집합 = set(선택)
    N = len(자질목록)
    df = Counter(t for f in 자질목록 for t in set(f) if t in 선택집합)
    idf = {t: math.log(N / df[t]) + 1.0 for t in 선택집합 if df[t]}
    벡터들 = [tfc_벡터(f, idf, 설정값["답변가중"]) for f in 자질목록]
    가중치 = SVM_학습(벡터들, 정답, 설정값["SVM_람다"], 설정값["SVM_반복"])
    # 질문만 보는 모델도 같이 학습 (입력 상충 의심 판단용)
    질문만설정 = dict(설정값, 답변가중=0)
    q자질 = [전체_자질(q, "", 질문만설정) for q, _, _ in 데이터]
    q선택, _ = 카이제곱_선택(q자질, 정답, 설정값["자질수"], 설정값["최소출현"])
    qdf = Counter(t for f in q자질 for t in set(f) if t in set(q선택))
    qidf = {t: math.log(N / qdf[t]) + 1.0 for t in q선택 if qdf[t]}
    q가중치 = SVM_학습([tfc_벡터(f, qidf, 1.0) for f in q자질], 정답, 설정값["SVM_람다"], 설정값["SVM_반복"])
    return {"설정": 설정값, "idf": idf, "가중치": 가중치, "질문_idf": qidf, "질문_가중치": q가중치,
            "상위자질": [(t, round(점수[t], 1)) for t in 선택[:200]]}


# ------------------------------------------------------------------ 지문 근거 확인 (입력 상충 의심)
def 글자쌍(글):
    """조사나 어미가 달라도 비교할 수 있게, 글자 2개씩 묶은 집합으로 바꿈 (예: '자전거' → 자전, 전거)"""
    글 = re.sub(r"[^가-힣a-z0-9]", "", 글.lower())
    return {글[i:i + 2] for i in range(len(글) - 1)}


def 문장_나누기(답변):
    답변 = re.sub(r"[*#>`|_]", "", 답변)
    조각 = re.split(r"(?<=[.!?다요])\s+|\n+", 답변)
    return [x.strip() for x in 조각 if len(re.sub(r"\s", "", x)) >= 8]


def 지문_근거_확인(질문, 답변, 다른_답변들=(), 기준=0.4):
    """답변의 각 문장에서, 질문(지문)에도 없고 다른 AI 답변에도 없는 표현의 비율을 계산.
    다른 답변이 2개 이상일 때 믿을 만함 (검증: 지문 이해형에서 입력 상충의 75%를 잡고, 정상 답변의 23%를 잘못 표시)."""
    질문쌍 = 글자쌍(질문)
    다른쌍 = [글자쌍(a) for a in 다른_답변들 if a]
    필요 = 1 if len(다른쌍) <= 3 else 2     # 다른 답변이 많으면 2개 이상이 쓴 표현만 '공통 표현'으로 인정
    의심문장 = []; 최대 = 0.0
    for 문장 in 문장_나누기(답변):
        쌍 = 글자쌍(문장)
        if len(쌍) < 10:
            continue
        새표현 = [g for g in 쌍 - 질문쌍 if sum(g in o for o in 다른쌍) < 필요]
        비율 = len(새표현) / len(쌍)
        최대 = max(최대, 비율)
        if 비율 >= 기준:
            의심문장.append((round(비율, 2), 문장))
    return 최대, 의심문장


def 분류하기(모델, 질문, 답변="", 다른_답변들=()):
    s = 모델["설정"]
    x = tfc_벡터(전체_자질(질문, 답변, s), 모델["idf"], s["답변가중"])
    점수 = 점수_계산(모델["가중치"], x)
    순위 = sorted(점수, key=lambda t: -점수[t])
    차이 = 점수[순위[0]] - 점수[순위[1]]
    결과 = {"유형": 순위[0], "2순위": 순위[1], "확신도": round(차이, 3),
            "애매함": 차이 < s["애매기준"], "점수": {t: round(v, 3) for t, v in 점수.items()}}
    if "질문_가중치" in 모델:
        qx = tfc_벡터(전체_자질(질문, "", dict(s, 답변가중=0)), 모델["질문_idf"], 1.0)
        q점수 = 점수_계산(모델["질문_가중치"], qx)
        결과["질문만_유형"] = max(q점수, key=q점수.get)
        결과["유형_불일치"] = 결과["질문만_유형"] != 결과["유형"]
    # 입력 상충 확인은 지문 이해형에만 적용 (사실형, 수치형 등은 지문 밖의 지식을 쓰는 게 정상이라)
    결과["입력상충_의심"] = False; 결과["근거없는_문장"] = []; 결과["근거없음_비율"] = None
    if 답변 and 결과["유형"] == "지문 이해형":
        if 다른_답변들:
            최대, 의심 = 지문_근거_확인(질문, 답변, 다른_답변들, s.get("근거기준", 0.4))
            결과["근거없음_비율"] = round(최대, 2)
            결과["근거없는_문장"] = 의심
            결과["입력상충_의심"] = bool(의심)
        else:
            결과["근거없음_비율"] = "다른 AI 답변이 없어 확인하지 않음"
    return 결과


def 모델_저장(모델, 경로):
    with open(경로, "w", encoding="utf-8") as f:
        json.dump(모델, f, ensure_ascii=False)


def 모델_불러오기(경로):
    with open(경로, encoding="utf-8") as f:
        return json.load(f)


# ------------------------------------------------------------------ 엑셀 읽기
def 채점결과_읽기(경로):
    import openpyxl
    wb = openpyxl.load_workbook(경로, data_only=True)
    데이터 = []
    for 유형 in 유형목록:
        시트 = next((wb[n] for n in wb.sheetnames if n.replace(" ", "") == 유형.replace(" ", "")), None)
        if 시트 is None:
            print("시트를 찾지 못함:", 유형); continue
        질문 = {}
        for r in range(1, 시트.max_row + 1):
            a, b = 시트.cell(r, 1).value, 시트.cell(r, 2).value
            d = 시트.cell(r, 4).value
            if a and b and re.fullmatch(r"[A-Za-z가-힣]+[-_ ]?\d+", str(a).strip()) and not re.fullmatch(r"M\d+", str(d or "").strip()):
                질문.setdefault(str(a).strip(), str(b))
        for r in range(1, 시트.max_row + 1):
            qid, 모델코드, 답변 = 시트.cell(r, 1).value, 시트.cell(r, 4).value, 시트.cell(r, 5).value
            if qid and 답변 and re.fullmatch(r"M\d+", str(모델코드 or "").strip()) and str(qid).strip() in 질문:
                종류 = 시트.cell(r, 8).value
                데이터.append((질문[str(qid).strip()], str(답변), 유형, str(qid).strip(), str(모델코드),
                             str(종류).strip() if 종류 else ""))
    return 데이터


def 엑셀_찾기():
    후보 = [f for f in os.listdir(".") if f.endswith(".xlsx") and "채점" in f and not f.startswith("~$")]
    if not 후보:
        sys.exit("같은 폴더에 '예선_최종 채점 결과.xlsx' 파일을 넣어 주세요.")
    후보.sort(key=lambda f: ("최종" not in f, f))
    return 후보[0]


# ------------------------------------------------------------------ 교차검증 (같은 질문이 학습과 시험에 동시에 들어가지 않게)
def 교차검증(데이터, 설정값=설정, 묶음=5, 씨앗=1):
    질문id = sorted({(d[2], d[3]) for d in 데이터})
    rng = random.Random(씨앗)
    유형별 = defaultdict(list)
    for 유형, qid in 질문id:
        유형별[유형].append(qid)
    배정 = {}
    for 유형, ids in 유형별.items():
        rng.shuffle(ids)
        for i, q in enumerate(ids):
            배정[(유형, q)] = i % 묶음
    예측 = [None] * len(데이터)
    for k in range(묶음):
        학습 = [d[:3] for d in 데이터 if 배정[(d[2], d[3])] != k]
        모델 = 학습하기(학습, 설정값)
        for i, d in enumerate(데이터):
            if 배정[(d[2], d[3])] == k:
                다른 = [e[1] for e in 데이터 if e[2] == d[2] and e[3] == d[3] and e[4] != d[4]]
                예측[i] = 분류하기(모델, d[0], d[1], 다른)
    return 예측


def 검증결과_저장(데이터, 예측, 경로):
    import openpyxl
    from openpyxl.styles import Font, PatternFill
    wb = openpyxl.Workbook()
    굵게 = Font(bold=True); 칠 = PatternFill("solid", fgColor="DDEBF7")
    맞음 = sum(p["유형"] == d[2] for d, p in zip(데이터, 예측))
    ws = wb.active; ws.title = "요약"
    줄 = [["항목", "값"], ["전체 답변 수", len(데이터)], ["정확도", f"{맞음 / len(데이터):.1%}"],
          ["애매함 표시 비율", f"{sum(p['애매함'] for p in 예측) / len(데이터):.1%}"],
          ["애매하지 않은 답변의 정확도",
           f"{sum(p['유형'] == d[2] for d, p in zip(데이터, 예측) if not p['애매함']) / max(1, sum(not p['애매함'] for p in 예측)):.1%}"],
          ["검증 방법", "질문 단위 5겹 교차검증: 같은 질문의 답변은 학습과 시험에 동시에 들어가지 않음"],
          [], ["유형", "정확도"]]
    for 유형 in 유형목록:
        n = [p["유형"] == d[2] for d, p in zip(데이터, 예측) if d[2] == 유형]
        줄.append([유형, f"{sum(n) / max(1, len(n)):.1%}"])
    for r in 줄: ws.append(r)
    ws["A1"].font = ws["B1"].font = 굵게
    ws.column_dimensions["A"].width = 30; ws.column_dimensions["B"].width = 70

    ws = wb.create_sheet("혼동행렬")
    ws.append(["실제 \\ 예측"] + 유형목록)
    for 유형 in 유형목록:
        c = Counter(p["유형"] for d, p in zip(데이터, 예측) if d[2] == 유형)
        ws.append([유형] + [c[t] for t in 유형목록])
    for c in ws[1]: c.font = 굵게; c.fill = 칠
    ws.column_dimensions["A"].width = 16

    ws = wb.create_sheet("입력 상충 확인")
    지문 = [(d, p) for d, p in zip(데이터, 예측) if d[2] == "지문 이해형"]
    실제 = [(d, p) for d, p in 지문 if d[5] == "입력 상충"]
    정상 = [(d, p) for d, p in 지문 if d[5] != "입력 상충"]
    ws.append(["지문 이해형 답변 수", len(지문)])
    ws.append(["채점에서 입력 상충으로 판정된 답변", len(실제)])
    ws.append(["그중 코드가 '입력 상충 의심'으로 잡은 답변", f"{sum(p['입력상충_의심'] for d, p in 실제)}"
               f" ({sum(p['입력상충_의심'] for d, p in 실제) / max(1, len(실제)):.0%})"])
    ws.append(["입력 상충이 아닌데 잘못 표시한 답변", f"{sum(p['입력상충_의심'] for d, p in 정상)}"
               f" ({sum(p['입력상충_의심'] for d, p in 정상) / max(1, len(정상)):.0%})"])
    ws.append(["참고", "다른 AI 9개의 답변을 함께 넣어서 확인함. 의심 표시는 '사람이 확인할 답변'을 고르는 용도"])
    ws.append([])
    ws.append(["문항ID", "모델코드", "채점 결과", "코드 판단", "근거없음 비율", "근거 없는 문장(앞부분)"])
    for d, p in 지문:
        if p["입력상충_의심"] or d[5] == "입력 상충":
            ws.append([d[3], d[4], d[5] or "정상", "의심" if p["입력상충_의심"] else "통과",
                       p["근거없음_비율"], " / ".join(문장[:80] for _, 문장 in p["근거없는_문장"][:2])])
    ws.column_dimensions["A"].width = 34; ws.column_dimensions["F"].width = 90

    ws = wb.create_sheet("틀린 답변")
    ws.append(["문항ID", "모델코드", "실제 유형", "예측 유형", "2순위", "확신도", "질문", "답변 앞부분"])
    for d, p in zip(데이터, 예측):
        if p["유형"] != d[2]:
            ws.append([d[3], d[4], d[2], p["유형"], p["2순위"], p["확신도"], d[0][:200], d[1][:200]])
    for c in ws[1]: c.font = 굵게; c.fill = 칠
    ws.column_dimensions["G"].width = 60; ws.column_dimensions["H"].width = 60
    wb.save(경로)


# ------------------------------------------------------------------ 실행
if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    명령 = sys.argv[1] if len(sys.argv) > 1 else "학습"
    if 명령 == "학습":
        데이터 = 채점결과_읽기(엑셀_찾기())
        print(f"답변 {len(데이터)}개로 학습합니다...")
        모델 = 학습하기([d[:3] for d in 데이터])
        모델_저장(모델, "유형_분류_모델.json")
        print("완료: 유형_분류_모델.json 저장")
    elif 명령 == "검증":
        데이터 = 채점결과_읽기(엑셀_찾기())
        print(f"답변 {len(데이터)}개로 교차검증합니다 (몇 분 걸릴 수 있어요)...")
        예측 = 교차검증(데이터)
        맞음 = sum(p["유형"] == d[2] for d, p in zip(데이터, 예측))
        print(f"정확도 {맞음 / len(데이터):.1%}")
        실제 = [p for d, p in zip(데이터, 예측) if d[2] == "지문 이해형" and d[5] == "입력 상충"]
        if 실제:
            print(f"입력 상충(지문 이해형) {len(실제)}건 중 {sum(p['입력상충_의심'] for p in 실제)}건을 잡음")
        검증결과_저장(데이터, 예측, "유형_분류_검증결과.xlsx")
        print("완료: 유형_분류_검증결과.xlsx 저장")
    elif 명령 == "분류":
        모델 = 모델_불러오기("유형_분류_모델.json")
        while True:
            q = input("\n질문 (끝내려면 엔터): ").strip()
            if not q: break
            a = input("답변: ").strip()
            r = 분류하기(모델, q, a)
            print(f"→ {r['유형']} (2순위 {r['2순위']}, 확신도 {r['확신도']})"
                  + ("  ※ 애매함" if r["애매함"] else "")
                  + ("  ※ 유형 불일치" if r.get("유형_불일치") else ""))
            if r["유형"] == "지문 이해형":
                print("  (지문 이해형은 같은 질문에 대한 다른 AI 답변을 넣으면 입력 상충도 확인해요."
                      " 앱에서는 분류하기(모델, 질문, 답변, 다른_답변들=[...]) 로 쓰세요)")
    else:
        print("사용법: python 유형_분류기.py 학습 | 검증 | 분류")

# -*- coding: utf-8 -*-
"""
위험도 실험에 쓸 답변을 예선 엑셀에서 골라 '검증/실험_자료_구성.xlsx' 로 정리해요. (API 키 필요 없음, 비용 0원)

  python 검증/실험_자료_만들기.py

무엇을 고르나요?
  ① 환각 답변 68개 전부 (환각 24 + 부분 환각 44)
  ② 정답 답변 68개: AI_포함_검증.py 가 고르는 것과 똑같은 68개 (조원이 이미 AI 검사를 돌린 답변이라 다시 돈이 안 들어요)
  ③ 예선 답변 거부 30개 (글로 쓴 거부 18 + 빈 답변 12)
  ④ 직접 만든 짧은 거부 12개 ("답변 불가", "모르겠습니다" 등, 유형마다 2개)
  ⑤ 거부처럼 보이지만 답을 한 헷갈리는 답변 8개
  문항 번호가 홀수면 '조정용'(기준을 고칠 때 보는 답변), 짝수면 '확인용'(고친 뒤 시험 보는 답변)이에요.
  ③~⑤ 는 0단계(답변 거부 거르기) 결과를 지금 프로그램으로 바로 채워 넣어요.
"""
import sys, os, re, collections
여기 = os.path.dirname(os.path.abspath(__file__))
P = os.path.dirname(여기)
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(여기, "실험_자료_구성.xlsx")
sys.path.insert(0, P); sys.path.insert(0, 여기)
import importlib, openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from 예선_검증 import 예선_읽기
from AI_포함_검증 import 고르기
거부 = importlib.import_module("기준.단계0_답변거부")
rows = 예선_읽기(os.path.join(P, "검증", "예선_최종 채점 결과.xlsx"))
보통답 = [a for a in rows if a["판정"] != "답변 거부"]
고른것, _ = 고르기(보통답, 68)
# 조원이 돌린 결과
wb0 = openpyxl.load_workbook(os.path.join(P, "검증", "AI_포함_검증_결과.xlsx"), data_only=True)
지난 = {(r[0], r[1], r[2]): (r[6], r[5]) for r in wb0["답변별"].iter_rows(min_row=2, values_only=True)}
assert {(a["유형"], a["문항"], a["모델"]) for a in 고른것} == set(지난), "조원 실행과 고른 답변이 달라요"
번호 = lambda q: int(re.search(r"(\d+)$", q).group(1))
나눔 = lambda q: "조정용" if 번호(q) % 2 else "확인용"
순서 = {t: i for i, t in enumerate(["사실 지식형", "수치 계산형", "논리 추론형", "출처 인용형", "지문 이해형", "코드 결과형"])}
질문표 = {(a["유형"], a["문항"]): a["질문"] for a in rows}

def 묶음(a):
    return "환각" if a["판정"] in ("환각", "부분 환각") else "정답"

본표 = sorted(고른것, key=lambda a: (나눔(a["문항"]) != "조정용", 묶음(a) != "환각", 순서[a["유형"]], 번호(a["문항"]), a["모델"]))

거부들 = sorted([a for a in rows if a["판정"] == "답변 거부"], key=lambda a: (순서[a["유형"]], 번호(a["문항"]), a["모델"]))
첫문항 = {t: f"{p}-01" for t, p in [("사실 지식형", "FACT"), ("수치 계산형", "CALC"), ("논리 추론형", "LOGIC"), ("출처 인용형", "CITE"), ("지문 이해형", "READ"), ("코드 결과형", "CODE")]}
둘째 = {t: q[:-2] + "02" for t, q in 첫문항.items()}
만든거부 = [
    ("사실 지식형", "답변 불가"), ("사실 지식형", "잘 모르겠습니다."),
    ("수치 계산형", "죄송하지만 답변드리기 어렵습니다."), ("수치 계산형", "모릅니다"),
    ("논리 추론형", "그 질문에는 답변할 수 없어요."), ("논리 추론형", "대답하기 어렵네요."),
    ("출처 인용형", "확인할 수 없습니다."), ("출처 인용형", "정보가 부족해서 답변드릴 수 없습니다."),
    ("지문 이해형", "답변이 어렵습니다."), ("지문 이해형", "알려 드릴 수 없습니다."),
    ("코드 결과형", "I don't know."), ("코드 결과형", "도와 드릴 수 없습니다."),
]
함정 = [
    ("사실 지식형", "잘 모르겠지만 아마 1592년일 거예요.", "모른다고 한 뒤 답을 덧붙임"),
    ("사실 지식형", "모르겠습니다. 다만 대략 300명 정도로 보입니다.", "모른다고 한 뒤 답을 덧붙임"),
    ("수치 계산형", "확실하지는 않지만 답은 42입니다.", "자신 없다고 하면서도 답을 함"),
    ("논리 추론형", "주어진 조건만으로는 알 수 없습니다.", "논리 문제의 정답일 수 있음"),
    ("출처 인용형", "요청하신 논문은 실제로 존재하지 않습니다.", "가짜 전제를 지적한 정답일 수 있음"),
    ("출처 인용형", "2024년 자료는 확인할 수 없습니다.", "범위를 말한 답 (숫자가 있음)"),
    ("지문 이해형", "주어진 글에는 그 정보가 없어서 답할 수 없습니다.", "지문 문제의 정답일 수 있음"),
    ("코드 결과형", "정확하지 않을 수 있지만 출력은 6입니다.", "자신 없다고 하면서도 답을 함"),
]

wb = openpyxl.Workbook()
머리 = PatternFill("solid", fgColor="1F4E78"); 머리글 = Font(bold=True, color="FFFFFF")
얇게 = Side(style="thin", color="BFBFBF"); 테두리 = Border(left=얇게, right=얇게, top=얇게, bottom=얇게)
칠 = {"조정용": PatternFill("solid", fgColor="FFF2CC"), "확인용": PatternFill("solid", fgColor="DDEBF7"),
     "맞음": PatternFill("solid", fgColor="E2EFDA"), "다름": PatternFill("solid", fgColor="FCE4D6")}

def 표(ws, 제목줄, 줄들, 너비, 시작=1, 줄높이=None):
    for j, h in enumerate(제목줄, 1):
        c = ws.cell(시작, j, h); c.fill = 머리; c.font = 머리글; c.alignment = Alignment(horizontal="center", vertical="center", wrap_text=True); c.border = 테두리
    for i, 줄 in enumerate(줄들, 시작 + 1):
        for j, v in enumerate(줄, 1):
            c = ws.cell(i, j, v); c.alignment = Alignment(vertical="top", wrap_text=True); c.border = 테두리
        if 줄높이: ws.row_dimensions[i].height = 줄높이
    for j, w in enumerate(너비, 1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(j)].width = w

# 1) 구성 요약
ws = wb.active; ws.title = "구성 요약"
ws["A1"] = "FactAP 위험도 실험 자료 구성"; ws["A1"].font = Font(bold=True, size=14)
ws["A2"] = "예선_최종 채점 결과.xlsx 에서 뽑았어요. 문항 번호가 홀수면 '조정용'(기준을 고칠 때 보는 답변), 짝수면 '확인용'(고친 뒤 시험 보는 답변)이에요."
ws["A3"] = "같은 답변으로 고치고 시험까지 보면 점수가 부풀려지기 때문에 둘로 나눴어요."
환 = [a for a in 고른것 if 묶음(a) == "환각"]; 정 = [a for a in 고른것 if 묶음(a) == "정답"]
cnt = lambda L, k: sum(1 for a in L if 나눔(a["문항"]) == k)
요약 = [
    ["① 환각 답변", len(환), cnt(환, "조정용"), cnt(환, "확인용"), "예선의 환각 24개 + 부분 환각 44개 전부", "위험도가 높게 나와야 하는 답변", "0원 (조원이 이미 AI 검사함)"],
    ["② 정답 답변", len(정), cnt(정, "조정용"), cnt(정, "확인용"), "정답 1,102개 중 68개 (조원이 AI 검사를 돌린 것과 같은 68개)", "'문제 없음'이 나와야 하는 답변. 지금 16개가 보통·위험으로 나옴", "0원 (조원이 이미 AI 검사함)"],
    ["③ 예선 답변 거부", len(거부들), cnt(거부들, "조정용"), cnt(거부들, "확인용"), "예선의 답변 거부 30개 (글로 쓴 거부 18개 + 빈 답변 12개)", "'답변 거부(환각 아님)' 또는 '입력 확인 필요'가 나와야 함", "0원 (0단계는 AI를 안 씀)"],
    ["④ 짧은 거부 (직접 만듦)", len(만든거부), "", "", "'답변 불가', '모르겠습니다' 같은 짧은 거부. 유형마다 2개", "이번 버그('답변 불가'→입력 상충)가 다시 안 생기는지 확인", "0원"],
    ["⑤ 헷갈리는 답변 (직접 만듦)", len(함정), "", "", "거부처럼 보이지만 답을 한 것 (예: '글에는 그 정보가 없습니다')", "'거부 아님'이 나와야 함. 정답을 거부로 잘못 거르지 않는지 확인", "0원"],
    ["합계", len(환) + len(정) + len(거부들) + len(만든거부) + len(함정), "", "", "", "", ""],
]
표(ws, ["묶음", "개수", "조정용", "확인용", "어디서 가져왔나", "왜 넣나", "비용"], 요약, [24, 7, 8, 8, 46, 46, 22], 시작=5)
for c in ws[11]: c.font = Font(bold=True)
ws["A13"] = "엑셀에서 쓰는 곳과 안 쓰는 곳"; ws["A13"].font = Font(bold=True, size=12)
쓰는곳 = [
    ["쓰는 곳", "유형 시트 6개 (사실 지식형 ~ 코드 결과형)", "③ 답변 입력 표 (47행부터): 문항 ID, 모델 코드, AI 답변, 판정, 환각 종류"],
    ["쓰는 곳", "유형 시트 6개", "② 문항 목록 (24~43행): 문항 ID로 질문 글을 찾음"],
    ["안 쓰는 곳", "안내, 전체 집계, 모델 대응표, 기준 요약 시트", "실험에 필요한 답변이 없음 (집계와 설명)"],
    ["안 쓰는 곳", "유형 시트의 채점자, 교차 채점, 메모 칸", "사람 판정은 '판정' 칸 하나만 쓰면 돼요"],
]
for r, x in enumerate([["구분", "시트", "칸"]] + 쓰는곳, 14):
    ws.merge_cells(start_row=r, start_column=2, end_row=r, end_column=4)
    for j, v in ((1, x[0]), (2, x[1]), (5, x[2])):
        c = ws.cell(r, j, v); c.alignment = Alignment(vertical="top", wrap_text=True)
        if r == 14: c.fill = 머리; c.font = 머리글
    ws.merge_cells(start_row=r, start_column=5, end_row=r, end_column=7)
    for j in range(1, 8): ws.cell(r, j).border = 테두리
    ws.row_dimensions[r].height = 32 if r > 14 else 18
ws["A20"] = "※ 유형 분류기는 예선 120문항으로 배웠기 때문에, 이 문항에서는 거의 다 맞혀요(100%). 처음 보는 질문에서는 약 94%라서, 확인용 결과도 실제 앱보다 좋게 나올 수 있어요."
ws["A21"] = "※ 그래서 마지막 확인은 새 질문(우리가 직접 앱에 넣어 본 것, 기록/검사기록.jsonl)으로도 해야 해요."
ws.freeze_panes = "A6"

# 2) 환각·정답 136
ws2 = wb.create_sheet("① ② 환각·정답")
줄들 = []
for i, a in enumerate(본표, 1):
    g, s = 지난[(a["유형"], a["문항"], a["모델"])]
    기대 = "보통 또는 위험" if 묶음(a) == "환각" else "문제 없음"
    맞음 = (g != "문제 없음") if 묶음(a) == "환각" else (g == "문제 없음")
    줄들.append([i, 나눔(a["문항"]), a["유형"], a["문항"], a["모델"], a["판정"], a["종류"] or "", a["질문"], a["답변"], 기대, g, s, "맞음" if 맞음 else "다름"])
표(ws2, ["번호", "나눔", "유형", "문항", "모델", "채점 판정", "환각 종류", "질문", "AI 답변", "나와야 할 등급", "지난 검사 등급 (조원 실행)", "지난 위험도", "맞았나"], 줄들,
   [6, 8, 12, 10, 6, 10, 10, 50, 60, 14, 14, 9, 8], 줄높이=60)
for r in range(2, len(줄들) + 2):
    ws2.cell(r, 2).fill = 칠[ws2.cell(r, 2).value]; ws2.cell(r, 13).fill = 칠[ws2.cell(r, 13).value]
ws2.freeze_panes = "C2"; ws2.auto_filter.ref = f"A1:M{len(줄들) + 1}"

# 3) 답변 거부
ws3 = wb.create_sheet("③ ④ ⑤ 답변 거부")
줄들 = []
def 판(답):
    p, _ = 거부.답변거부_판정(답); return p
for a in 거부들:
    p = 판(a["답변"]); 빈 = p == "입력 확인 필요" or not a["답변"].strip()
    기대 = "입력 확인 필요" if 빈 else "답변 거부"
    메모 = "빈 답변이나 기호만 있음" if 빈 else ""
    if p != 기대:
        메모 = "한 글자만 있는 잘린 답변. 프로그램은 답으로 보고 환각 검사를 계속함" if len(a["답변"].strip()) <= 2 else "애매하게 쓴 거부라 프로그램이 못 알아봄 (예선 때부터 알던 2건)"
    줄들.append(["③ 예선 거부", 나눔(a["문항"]), a["유형"], a["문항"], a["모델"], a["질문"], a["답변"], 기대, p, "맞음" if p == 기대 else "다름", 메모])
for t, 답 in 만든거부:
    q = 첫문항[t]; p = 판(답)
    줄들.append(["④ 짧은 거부", "", t, q, "직접", 질문표[(t, q)], 답, "답변 거부", p, "맞음" if p == "답변 거부" else "다름", ""])
for t, 답, 왜 in 함정:
    q = 둘째[t]; p = 판(답)
    줄들.append(["⑤ 헷갈리는 답변", "", t, q, "직접", 질문표[(t, q)], 답, "거부 아님", p, "맞음" if p == "거부 아님" else "다름", 왜])
표(ws3, ["묶음", "나눔", "유형", "문항", "모델", "질문", "AI 답변", "나와야 할 결과", "지금 프로그램 결과", "맞았나", "메모"], 줄들,
   [16, 8, 12, 10, 6, 45, 55, 14, 16, 8, 30], 줄높이=45)
for r in range(2, len(줄들) + 2):
    v = ws3.cell(r, 2).value
    if v: ws3.cell(r, 2).fill = 칠[v]
    ws3.cell(r, 10).fill = 칠[ws3.cell(r, 10).value]
ws3.freeze_panes = "C2"; ws3.auto_filter.ref = f"A1:K{len(줄들) + 1}"
wb.save(OUT)
c = collections.Counter(r[9] for r in 줄들)
print("거부 시트:", c, [ (r[0], r[2], r[3], r[6][:30], r[8]) for r in 줄들 if r[9] == "다름"])
c2 = collections.Counter((나눔(a["문항"]), 묶음(a)) for a in 고른것); print(c2)
print("완료", OUT)

# -*- coding: utf-8 -*-
"""
검사 AI·웹 기준까지 넣어서 예선 자료로 다시 검증하기 (API 키와 인터넷이 필요해요)

예선_검증.py 는 API 키 없이 돌아가는 프로그램 기준만 확인했어요.
이 파일은 실제 앱과 똑같이 모든 기준(①~⑥, 검사 AI, 위키백과, 논문 DB)을 실행해서
'등급 기준(문제 없음·보통·위험)이 AI까지 넣어도 맞는지'를 확인해요.

비용을 줄이는 방법
  - 상위 모델 답변은 다시 묻지 않고, 예선에서 받은 답변을 그대로 써요. (2단계 생략)
    → 답변 하나에 검사 AI 3번만 불러요.
  - 정답 답변 1,102개를 다 하지 않고, 환각 답변 68개 전부 + 정답 답변 일부(기본 68개)만 골라요.
    정답 답변을 일부만 골랐기 때문에, 등급별 환각 비율은 '정답 답변을 전체 수만큼 늘려서' 계산해요(가중치).
  - 결과를 검증/AI_검증_저장.jsonl 에 한 줄씩 저장해요. 중간에 멈춰도 다시 실행하면 이어서 해요.

사용법 (패키지 폴더에서)
  python 검증/AI_포함_검증.py --개수 5        ← 먼저 5개만 해 보고 OpenRouter 사용량(비용)을 확인하세요
  python 검증/AI_포함_검증.py                 ← 환각 68개 + 정답 68개
  python 검증/AI_포함_검증.py --정답개수 200   ← 정답 답변을 더 많이 (더 정확하지만 비용이 늘어요)
  → 화면에 표가 나오고 검증/AI_포함_검증_결과.xlsx 가 저장돼요.

※ 같은 예선 자료로 기준을 다듬었기 때문에, 진짜 성능은 새 질문(기록/검사기록.jsonl 에 사람 판정을 적은 것)으로 확인해야 해요.
"""
import argparse, json, os, random, sys
from collections import defaultdict
여기 = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(여기)); sys.path.insert(0, 여기)
import 설정
from 도구 import AI_호출
from 검사_실행 import 환각_검사
from 예선_검증 import 예선_읽기

저장_파일 = os.path.join(여기, "AI_검증_저장.jsonl")


def 고르기(답변들, 정답개수, 씨앗=2026):
    환각 = [a for a in 답변들 if a["판정"] in ("환각", "부분 환각")]
    정답 = [a for a in 답변들 if a["판정"] == "정답"]
    섞기 = random.Random(씨앗)
    섞기.shuffle(정답)
    고른것 = 환각 + 정답[:정답개수]
    섞기.shuffle(고른것)                       # --개수 로 앞부분만 해도 환각·정답이 섞여 있게
    return 고른것, len(정답)


def 저장된_것():
    본것 = {}
    if os.path.exists(저장_파일):
        with open(저장_파일, encoding="utf-8") as f:
            for 줄 in f:
                try:
                    x = json.loads(줄); 본것[(x["유형"], x["문항"], x["모델"])] = x
                except (json.JSONDecodeError, KeyError):
                    pass
    return 본것


def 실행(경로, 정답개수, 개수=None):
    if not AI_호출.키가_있나():
        sys.exit("API 키가 없어요. 환경 변수 OPENROUTER_API_KEY 를 설정한 뒤 다시 실행하세요. (README 'API 키 넣기')")
    답변들 = [a for a in 예선_읽기(경로) if a["판정"] != "답변 거부"]
    찾기 = {(a["유형"], a["문항"], a["모델"]): a for a in 답변들}
    고른것, 정답_전체 = 고르기(답변들, 정답개수)
    if 개수:
        고른것 = 고른것[:개수]
    본것 = 저장된_것()
    할것 = [a for a in 고른것 if (a["유형"], a["문항"], a["모델"]) not in 본것]
    print(f"검증할 답변 {len(고른것)}개 (이미 한 것 {len(고른것) - len(할것)}개, 새로 할 것 {len(할것)}개)")
    for i, a in enumerate(할것, 1):
        상위 = [m for m in 설정.상위모델[a["유형"]] if m != a["모델"]]
        참고 = [찾기[(a["유형"], a["문항"], m)]["답변"] for m in 상위 if (a["유형"], a["문항"], m) in 찾기]
        보고서 = 환각_검사(a["질문"], a["답변"], "", a["유형"], AI_사용=True, 상위모델_답변들=참고)
        종합 = 보고서["종합"] or {}
        한줄 = {"유형": a["유형"], "문항": a["문항"], "모델": a["모델"], "판정": a["판정"], "종류": a["종류"],
              "종합_위험도": 종합.get("위험도"), "등급": 종합.get("등급"),
              "기준별": {x["정보"]["번호"] + " " + x["정보"]["이름"]: x["결과"]["위험도"] for x in 보고서["기준결과들"]},
              "상태별": {x["정보"]["번호"] + " " + x["정보"]["이름"]: x["결과"]["상태"] for x in 보고서["기준결과들"]},
              "AI_사용량": 보고서.get("AI_사용량")}
        with open(저장_파일, "a", encoding="utf-8") as f:
            f.write(json.dumps(한줄, ensure_ascii=False) + "\n")
        본것[(a["유형"], a["문항"], a["모델"])] = 한줄
        print(f"  [{i}/{len(할것)}] {a['유형']} {a['문항']} {a['모델']} 채점:{a['판정']} → {종합.get('등급')} {종합.get('위험도')}")
    return 요약([본것[(a["유형"], a["문항"], a["모델"])] for a in 고른것], 정답_전체)


def 요약(결과들, 정답_전체):
    정답_고른수 = sum(1 for x in 결과들 if x["판정"] == "정답") or 1
    가중 = 정답_전체 / 정답_고른수                 # 정답 답변 하나가 전체에서 대표하는 답변 수
    환각임 = lambda x: x["판정"] in ("환각", "부분 환각")
    # 1) 등급별 실제 환각 비율 (정답 답변은 가중치를 곱함)
    등급 = defaultdict(lambda: [0.0, 0])
    for x in 결과들:
        g = x["등급"] or "판단 불가"
        등급[g][0] += 1 if 환각임(x) else 가중
        등급[g][1] += 환각임(x)
    print("\n등급별 실제 환각 비율 (정답 답변은 전체 수만큼 늘려 계산)")
    등급줄 = []
    for _, g in 설정.등급_기준 + [(None, "판단 불가")]:
        n, h = 등급.get(g, [0, 0])
        if n:
            등급줄.append([g, round(n), h, f"{h / n:.1%}"])
            print(f"  {g:<6} 답변 약 {n:>6.0f}개, 그중 환각 {h:>3}개 ({h / n:.1%})")
    # 2) 기준별 잡은 비율·잘못 잡은 비율
    기준 = defaultdict(lambda: {"환각": [0, 0], "정답": [0, 0], "확인 불가": 0})
    for x in 결과들:
        for 이름, v in x["기준별"].items():
            if v is None:
                if x["상태별"].get(이름) == "확인 불가":
                    기준[이름]["확인 불가"] += 1
                continue
            칸 = 기준[이름]["환각" if 환각임(x) else "정답"]
            칸[0] += 1; 칸[1] += v >= 0.5
    print("\n기준별 (위험도 0.5 이상을 '잡음'으로 봄)")
    기준줄 = []
    for 이름 in sorted(기준):
        c = 기준[이름]; h, o = c["환각"], c["정답"]
        기준줄.append([이름, f"{h[1]}/{h[0]}", f"{o[1]}/{o[0]}", c["확인 불가"]])
        print(f"  {이름:<18} 환각 잡음 {h[1]:>3}/{h[0]:<3} 정답 잘못 잡음 {o[1]:>3}/{o[0]:<3} 확인 불가 {c['확인 불가']}")
    # 3) 비용
    호출 = sum((x.get("AI_사용량") or {}).get("호출", 0) for x in 결과들)
    비용 = sum((x.get("AI_사용량") or {}).get("비용", 0) for x in 결과들)
    print(f"\nAI 호출 {호출:.0f}번" + (f", 비용 약 ${비용:.2f}" if 비용 else " (비용은 OpenRouter 사이트의 Activity에서 확인)"))
    try:
        import openpyxl
        wb = openpyxl.Workbook(); ws = wb.active; ws.title = "등급별 실제 환각 비율"
        ws.append(["등급", "답변 수(가중)", "그중 실제 환각", "실제 환각 비율"])
        for 줄 in 등급줄: ws.append(줄)
        ws2 = wb.create_sheet("기준별")
        ws2.append(["기준", "환각 중 잡은 수", "정답 중 잘못 잡은 수", "확인 불가"])
        for 줄 in 기준줄: ws2.append(줄)
        ws3 = wb.create_sheet("답변별")
        ws3.append(["유형", "문항", "모델", "채점 판정", "환각 종류", "종합 위험도", "등급"])
        for x in 결과들: ws3.append([x["유형"], x["문항"], x["모델"], x["판정"], x["종류"], x["종합_위험도"], x["등급"]])
        저장 = os.path.join(여기, "AI_포함_검증_결과.xlsx"); wb.save(저장); print("저장:", 저장)
    except Exception as e:
        print("엑셀 저장 실패:", e)
    return 등급줄, 기준줄


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="검사 AI까지 넣어 예선 자료로 검증")
    p.add_argument("경로", nargs="?", default=os.path.join(여기, "예선_최종 채점 결과.xlsx"))
    p.add_argument("--정답개수", type=int, default=68, help="고를 정답 답변 수 (기본 68)")
    p.add_argument("--개수", type=int, default=None, help="앞에서부터 이만큼만 (시험 삼아 돌릴 때)")
    인자 = p.parse_args()
    실행(인자.경로, 인자.정답개수, 인자.개수)

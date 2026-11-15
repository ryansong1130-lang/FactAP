# -*- coding: utf-8 -*-
"""
AI 모델 연결 확인

설정.모델_이름 에 있는 6개 모델에 아주 짧은 질문("1+1은? 숫자만 답해")을 한 번씩 보내서
응답이 오는지만 확인해요. 모델 이름이 바뀌었거나, 키·크레딧에 문제가 있으면 여기서 바로 보여요.

  - 모델마다 1번씩, 모두 6번 호출해요 (비용은 아주 적어요).
    단, 잠깐 막힘(429)이나 서버 오류(5xx)가 나면 AI_호출 이 최대 2번 더 시도해요.
  - 실패하면 HTTP 오류 번호와 이유를 표에 적어요.
  - 마지막에 AI_호출.사용량_보기() 로 호출 수, 토큰 수, 비용을 보여 줘요.
  - API 키 값은 읽거나 출력하지 않아요. 있는지(키가_있나)만 확인해요.

사용법 (패키지 폴더에서)
  python 검증/연결_확인.py
"""
import json, os, re, sys, time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import 설정
from 도구 import AI_호출

try:                                    # 윈도우 콘솔에서 한글이 깨지지 않게
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

질문 = "1+1은? 숫자만 답해"
최대_토큰 = 300        # 생각을 먼저 하는 모델도 답을 낼 수 있게 조금 여유를 둠 (그래도 아주 적음)


def 오류_풀기(메시지):
    """AI오류 메시지에서 HTTP 오류 번호와 이유를 꺼냄"""
    번호 = re.search(r"\(HTTP (\d+)\)", 메시지)
    if not 번호:                                  # 연결 문제·시간 초과 등
        return "-", 메시지.split("호출 실패:", 1)[-1].strip()[:120]
    본문 = 메시지.split("):", 1)[-1].strip()
    이유 = 본문
    try:                                          # OpenRouter 오류 본문: {"error": {"message": "..."}}
        이유 = json.loads(본문)["error"]["message"]
    except Exception:
        찾음 = re.search(r'"message"\s*:\s*"([^"]+)"', 본문)
        if 찾음:
            이유 = 찾음.group(1)
    return 번호.group(1), 이유[:120]


def 한_모델_확인(모델_ID):
    시작 = time.time()
    try:
        답 = AI_호출.AI_부르기(모델_ID, 질문, 최대_토큰=최대_토큰)
        걸린 = time.time() - 시작
        답 = (답 or "").strip().replace("\n", " ")
        return {"결과": "성공", "번호": "-", "내용": 답[:40] or "(빈 답)", "초": 걸린}
    except AI_호출.AI오류 as e:
        번호, 이유 = 오류_풀기(str(e))
        return {"결과": "실패", "번호": 번호, "내용": 이유, "초": time.time() - 시작}


def main():
    if not AI_호출.키가_있나():
        print("API 키가 없어요. 환경 변수 OPENROUTER_API_KEY 를 설정한 뒤 다시 실행해 주세요.")
        return 1

    print(f"질문: \"{질문}\"  (모델 {len(설정.모델_이름)}개에 1번씩)\n")
    줄들 = []
    for 번호, 모델_ID in 설정.모델_이름.items():
        print(f"  {번호} {모델_ID} 확인 중...", flush=True)
        줄들.append((번호, 모델_ID, 한_모델_확인(모델_ID)))

    print("\n| 번호 | 모델 | 결과 | HTTP | 걸린 시간 | 답 또는 실패 이유 |")
    print("|---|---|---|---|---|---|")
    for 번호, 모델_ID, r in 줄들:
        print(f"| {번호} | {모델_ID} | {r['결과']} | {r['번호']} | {r['초']:.1f}초 | {r['내용']} |")

    성공 = sum(r["결과"] == "성공" for _, _, r in 줄들)
    print(f"\n성공 {성공}개, 실패 {len(줄들) - 성공}개")

    쓴것 = AI_호출.사용량_보기()
    print(f"사용량: 호출 {쓴것['호출']}번 (실패 {쓴것['실패']}번), "
          f"입력 토큰 {쓴것['입력_토큰']}, 출력 토큰 {쓴것['출력_토큰']}, 비용 ${쓴것['비용']:.6f}")
    return 0 if 성공 == len(줄들) else 2


if __name__ == "__main__":
    sys.exit(main())

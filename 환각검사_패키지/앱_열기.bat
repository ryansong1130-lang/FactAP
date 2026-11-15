@echo off
rem 이 파일을 두 번 클릭하면 FactAP(환각 검사 앱)이 브라우저에서 열려요. (윈도우용)
cd /d "%~dp0"
set PYTHONUTF8=1
echo.
echo  [FactAP] 앱을 여는 중이에요. 잠시 뒤 브라우저가 열려요.
echo  - 안 열리면 브라우저 주소창에 http://localhost:8501 을 입력하세요.
echo  - 앱을 쓰는 동안 이 검은 창은 닫지 마세요. 다 쓰면 이 창을 닫으면 앱이 꺼져요.
echo.
rem streamlit 이 없거나 1.40 보다 오래된 버전이거나 segno(공유 QR코드)가 없으면 설치(업데이트)해요
python -c "import openpyxl, segno, streamlit, sys; sys.exit(0 if tuple(int(x) for x in streamlit.__version__.split('.')[:2]) >= (1, 40) else 1)" 2>nul || (
  echo  필요한 프로그램을 설치하거나 새 버전으로 바꾸고 있어요. 몇 분 걸릴 수 있어요.
  python -m pip install -r requirements.txt
)
python -m streamlit run 앱_화면.py
echo.
echo  앱이 꺼졌어요. 앱이 열리지 않았다면 위에 나온 오류 문장을 확인하세요.
echo  - 'python'을 찾을 수 없다고 나오면 파이썬 설치부터 해야 해요. 제작 안내서 1-1 참고
pause

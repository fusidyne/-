# 더마 카테고리 검색 트렌드 대시보드 (네이버 데이터랩)

키워드를 입력하면 네이버 데이터랩 API로 실시간 검색 관심도 추이를 가져오는 Streamlit 앱입니다.

## 1. 네이버 API 키 발급 (5분, 무료)
1. https://developers.naver.com/apps/#/register 접속 후 로그인
2. "애플리케이션 등록" 클릭
3. 사용 API에서 **"데이터랩(검색어 트렌드)"** 체크
4. 등록 완료 후 발급되는 **Client ID / Client Secret** 복사해두기

## 2. 로컬에서 실행해보기
```bash
pip install -r requirements.txt
streamlit run naver_trend_app.py
```
실행되면 브라우저가 열리고, 왼쪽 사이드바에 Client ID/Secret을 입력하면 바로 조회할 수 있습니다.

## 3. 팀이 함께 쓸 수 있게 배포하기 (Streamlit Community Cloud, 무료)
1. https://share.streamlit.io 가입 (GitHub 계정 연동)
2. 이 폴더(naver_trend_app.py, requirements.txt)를 GitHub 저장소에 업로드
3. Streamlit Cloud에서 "New app" → 방금 만든 저장소 선택 → main file은 `naver_trend_app.py`
4. **Settings → Secrets**에 아래처럼 등록해두면 팀원들이 매번 키를 입력할 필요 없음
   ```
   NAVER_CLIENT_ID = "발급받은 값"
   NAVER_CLIENT_SECRET = "발급받은 값"
   ```
5. 배포되면 마케팅팀 유튜브 대시보드처럼 URL 하나로 팀 전체 공유 가능

## 사용 방법
1. 비교하고 싶은 키워드(성분명, 제품군 등)를 그룹별로 입력 (예: 시카크림 / 판테놀크림 / 마데카소사이드)
2. 조회 기간, 디바이스, 성별, 연령대 필터 설정
3. "트렌드 조회" 클릭
4. 관심도 추이 그래프, 최근 상승세 키워드, 자동 인사이트 확인

## 참고 및 주의사항
- 지수는 **절대 검색량이 아닌 상대값**(조회 기간 내 최댓값 = 100)입니다. 기간이 다르면 지수를 그대로 비교하면 안 됩니다.
- 하루 API 호출 한도가 있으니(기본 25,000회/일), 여러 명이 동시에 쓸 경우 참고하세요.
- Client Secret은 절대 코드에 하드코딩하거나 공개 저장소에 노출하지 마세요. Streamlit Secrets 기능을 사용하세요.
- 이 데이터는 의사결정의 정답이 아니라, 신제품 기획·프로모션 타이밍 참고 자료로 활용하는 걸 권장합니다.
- 같은 API 계열의 **쇼핑인사이트(카테고리/기기별 클릭 트렌드)** API도 추가 신청하면, 검색 관심도뿐 아니라 실제 쇼핑 클릭 트렌드까지 확장 가능합니다.

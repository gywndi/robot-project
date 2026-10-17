# SO-ARM101 Robot Project v0.1
Apple Silicon Mac + Python 3.11 + LeRobot 기반 SO-ARM101 독립 제어 프로젝트.

## 확인 완료
- Follower 6개 모터 위치 읽기
- 집게 목표 2490 / 실제 2488 (시작 2470)
- 손목 3156 → 최대 3207 → 3159 왕복 및 육안 움직임 확인
- Python 파일 기반 Enter 키보드 제어 성공
- Leader USB 포트 식별 성공 (제어 미검증)

## 문서
`docs/` 설치, 하드웨어, API, 테스트 결과, 안전, 문제 해결, 로드맵.
`AGENTS.md`는 AI 코딩 에이전트용 작업 지침.
`examples/`는 검증한 API 기반 예제. **구동 예제는 사용자 확인 후에만 실행**.

**미해결:** Leader/Follower 연동 시 손목이 약 360도 비정상 회전한 이력. 자동 동작 전에 원인 규명 필요.

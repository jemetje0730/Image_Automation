# Image Automation - 이미지 기반 자동 클릭 프로그램

## 프로젝트 개요
- 이미지 기반으로 UI를 인식하여 마우스 클릭이나 키보드 입력을 자동화합니다.  
- 테스트 자동화, 반복 작업 제거, 간단한 매크로 등 다양한 목적으로 사용할 수 있습니다.

## 기술 스택
- 언어: Python
- 라이브러리: OpenCV, PyAutoGUI, NumPy

## 개발 환경 설정

### 필수 요구사항
- Python (3.8 이상)
- pip (패키지 설치 관리자)

### IDE 설정 (선택사항)
#### Visual Studio Code
- Python Extension 설치 (Microsoft 제공)

## 프로젝트 구조
```
image_automation/
├── action/                     # 마우스/키보드 등의 입력 동작 처리
│   ├── __init__.py
│   ├── common.py               # 마우스/키보드 이외 동작
│   ├── mouse.py                # 클릭, 드래그 등 마우스 동작
│   └── keyboard.py             # 타이핑, 키 입력 등 키보드 동작
│
├── detector/                   # 화면에서 이미지 찾기 등 탐지 로직
│   ├── __init__.py
│   └── image_detector.py       # findImageOnScreen, 매칭 로직
│
├── runners/                    # 시나리오 실행기 (입력 → 동작 매핑)
│   ├── __init__.py
│   └── scenario_runner.py      # csv, json, yaml 기반 자동화 시나리오 실행
│
├── scenarios/                  # 자동화 시나리오 정의
│   └── scenario_1.csv
│
├── utils/                      # 보조 유틸리티 함수들
│   ├── __init__.py
│   └── log.py                  # 로그 메시지 출력 방식 통일, INFO, DEBUG, ERROR 등등
│
├── config/                     # 설정 정보 분리
│   └── config.yaml             # 이미지 폴더 경로, threshold, 딜레이 등
│
├── assets/                     # 사용하는 이미지 리소스 저장소
│   ├── trash.png
│   ├── file.png
│   └── etc.png
│
├── tests/                      # pytest 사용 예정
│   ├── __init__.py  
│   ├── action/
│   │   ├── test_mouse.py
│   │   └── test_keyboard.py
│   ├── detector/
│   │   └── test_image_detector.py
│   └── runners/
│       └── test_scenario_runner.py
│
├── docs/                       
│   └── usage.md                # 실제 사용법, 옵션 설명, 시나리오 포맷 등 상세 문서
│
├── requirements.txt
├── README.md
└── main.py                     
```

## 빌드 및 실행

### 개발 빌드
```bash

```

### 릴리즈 빌드
```bash

```
### 패키지 설치
```bash
pip install pyautogui
pip install opencv-python
pip install numpy
pip install pytest
```

## 라이선스
MIT License

Copyright (c) 2025 Image Automation

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Third-Party Licenses
- pyautogui: BSD License
- numpy: BSD License
- opencv-python: Apache License 2.0

## Commit Style
- feat: 기능 추가
- fix: 버그 수정
- docs: 문서 수정
- test: 테스트 코드
- refactor: 리팩토링
- build: 빌드 파일 수정
- chore: 자잘한 수정
- rename: 파일명 변경
- remove: 파일 삭제
- release: 버전 릴리즈

## 프로젝트 목적


## 주요 기능
- 이미지(.png) 기반 UI 인식 및 마우스 클릭
- 다양한 해상도에서도 자동 스케일 조정 및 매칭
- 매칭 실패 시 최고 점수 기록 및 디버그 이미지 저장
- 시나리오 기반 반복 자동화 (CSV 등으로 정의 가능)
- PyAutoGUI를 통해 키보드 입력도 지원

---

## 사용 예시

```python
click_button("file.png")
click_button("file.png")
click_button("start.png")
```

## 디버깅
매칭이 실패하거나 정확도가 낮은 경우, `match_debug_*.png` 이미지가 자동 저장됩니다.
이를 통해 어떤 위치에서 탐지되었는지 시각적으로 확인할 수 있습니다.


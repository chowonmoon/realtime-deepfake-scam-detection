# 🚦 Green Light — 실시간 딥페이크 영상통화 스캠 탐지

영상통화 중 딥페이크를 **실시간으로** 탐지하고, 위험도를 Green / Yellow / Red 신호로 보여주어
사용자가 통화 도중 바로 판단하고 행동할 수 있게 돕는 멀티모달 보안 시스템입니다.

> 4인 팀 프로젝트 (2026.01–02)

[![Demo](https://img.youtube.com/vi/LQiC-fly_y4/0.jpg)](https://youtu.be/LQiC-fly_y4)

## Why
기존 딥페이크 탐지는 영상 업로드 후 **사후 분석**에 머뭅니다.
로맨스 스캠처럼 실시간 영상통화에서 벌어지는 사기에는 **통화 도중 경고**가 필요합니다.

## How It Works
| 신호 | 방법 |
|---|---|
| 얼굴 기반 딥페이크 확률 | Face crop → ViT 기반 탐지 모델, EMA smoothing (3프레임 간격) |
| 오디오-비디오 싱크 불일치 | 입 ROI + 16kHz MFCC → SyncNet, 2초 윈도우마다 offset·confidence 추정 |
| 눈 깜빡임 (Liveness) | MediaPipe FaceMesh EAR 기반 blink 검출 |

`final_risk = 0.75 × deepfake_prob + 0.25 × sync_risk` → **Green(<0.3) / Yellow(<0.7) / Red**

## Key Work

### 1. SyncNet 도메인 적응 파인튜닝
pretrained SyncNet은 실제 웹캠·마이크 환경에서 싱크가 맞는 영상에 오히려 낮은 점수를 주는 등 불안정했습니다.
- 실제 웹캠 환경에서 positive / negative(200~800ms 시간 이동) pair **41쌍** 직접 수집
- Contrastive loss 기반 파인튜닝 (Adam, lr 1e-5, 20 epochs, Colab T4)

| 평균 confidence (4쌍) | Pretrained | Fine-tuned |
|---|---|---|
| Positive (싱크 일치) | 4.55 | **7.87** |
| Negative (싱크 불일치) | 5.92 | **3.00** |

→ pretrained 모델은 4쌍 중 3쌍에서 불일치 영상에 더 높은 점수를 줬지만, 파인튜닝 후에는 4쌍 모두 일치 영상을 더 높게 판별
*(학습 데이터 내 샘플로 확인한 결과이며, 별도 테스트셋 검증은 향후 과제)*

`src/sync_compare.py`로 웹캠 실시간 입력에서 두 모델의 confidence를 나란히 비교할 수 있습니다.

### 2. Signal UI — 판단을 행동으로 연결
모델 확률을 그대로 보여주는 대신 **SAFE / CAUTION / DANGER** 3단계 신호로 변환했습니다.
- **Yellow**: 경고 문구 + 위험 근거(Risk Report) 표시
- **Red**: 5초 후 통화 자동 종료, 사용자가 `c`로 계속 진행 선택 가능

### 3. 경량 설명 가능성 — Laplacian Artifact Map
LIME 등 기존 XAI는 CPU 실시간 환경에서 너무 무거웠습니다.
Laplacian 고주파 성분으로 합성 흔적을 히트맵화하고, 위험도에 비례해 오버레이 강도를 조절합니다.

## Project Structure
```
src/
├── webcam.py          # 실시간 파이프라인 (메인)
├── greenlight_ui.py   # Signal UI
├── sync_compare.py    # 원본 vs 파인튜닝 SyncNet 실시간 비교
├── detector.py        # 얼굴 기반 딥페이크 탐지
└── preprocess.py      # 얼굴 crop
notebooks/
└── SyncNet_FineTuning.ipynb
```

## Getting Started
```bash
git clone https://github.com/chowonmoon/realtime-deepfake-scam-detection.git
cd realtime-deepfake-scam-detection
pip install -r requirements.txt

# SyncNet (외부 오픈소스)
git clone https://github.com/joonson/syncnet_python.git
cd syncnet_python && sh download_model.sh && cd ..

# 파인튜닝 가중치: Releases에서 syncnet_finetuned_final.pth를 받아 repo 최상위에 저장
python src/webcam.py
```

## Learnings
- 실시간 시스템에서는 모델 정확도보다 **latency · stability · 해석 가능성**이 더 큰 제약
- 단일 모델은 오탐이 잦아, **서로 다른 근거(multi-evidence)의 결합**이 안정성을 높임
- 탐지 결과는 **사용자 행동으로 이어질 때** 의미가 있음

## Tech Stack
Python · PyTorch · OpenCV · MediaPipe · Hugging Face Transformers · SyncNet

## Acknowledgements
- [SyncNet](https://github.com/joonson/syncnet_python) (Chung & Zisserman, 2016)
- Deepfake detector: `prithivMLmods/Deep-Fake-Detector-v2-Model` (Hugging Face)

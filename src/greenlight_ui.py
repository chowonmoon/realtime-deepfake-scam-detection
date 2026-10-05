import cv2
import numpy as np
from typing import Optional, List

# 색상 정의
GREEN = (0, 255, 0)
YELLOW = (0, 255, 255)
RED = (0, 0, 255)

def draw_greenlight_ui(
    frame,
    final_risk,
    fps,
    blink_count,
    overlay_lines: Optional[List[str]] = None,
):
    h, w = frame.shape[:2]

    # --- 1. 상단 바 배경 (배너 형태) ---
    cv2.rectangle(frame, (0, 0), (w, 90), (0, 0, 0), -1) 
    cv2.line(frame, (0, 90), (w, 90), (100, 100, 100), 2)

    # --- 2. 상태 결정 ---
    if final_risk < 0.3:
        status_color = GREEN
        status_text = "STATUS: SAFE (REAL)"
    elif final_risk < 0.7:
        status_color = YELLOW
        status_text = "STATUS: CAUTION (SYNC ISSUE)"
    else:
        status_color = RED
        status_text = "STATUS: DANGER (FAKE)"

    # --- 3. 상태 텍스트 (그림자 효과로 가독성 강화) ---
    text_pos = (max(10, w // 2 - 200), 65)
    # 검은색 외곽선 (두께 4)
    cv2.putText(frame, status_text, text_pos, 
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 0), 4, cv2.LINE_AA)
    # 본문 색상 (두께 2)
    cv2.putText(frame, status_text, text_pos, 
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, status_color, 2, cv2.LINE_AA)
    
    # 시스템 버전 정보 (좌측 상단 소형)
    cv2.putText(frame, "GREEN LIGHT SYSTEM v1.0", (10, 25), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1, cv2.LINE_AA)

    # --- 4. 중앙 경고 오버레이 (DANGER/CAUTION 시 문구) ---
    if overlay_lines:
        for i, line in enumerate(overlay_lines[:5]):
            y = 150 + i * 40 # 줄 간격 확보
            # 외곽선 효과
            cv2.putText(frame, line, (40, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 4, cv2.LINE_AA)
            cv2.putText(frame, line, (40, y), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2, cv2.LINE_AA)

    # --- 5. 하단 정보 레이아웃 (기존 스타일 보존) ---
    # 반투명 배경 박스 (선택 사항, 깔끔함을 위해 추가)
    # cv2.rectangle(frame, (w - 200, h - 100), (w, h), (0, 0, 0), 0.3) 

    info_color = (255, 255, 255)
    # 우측 하단에 Blinks, FPS, AV Sync 배치
    cv2.putText(frame, f"Blinks: {blink_count}", (w - 200, h - 80), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, info_color, 1, cv2.LINE_AA)
    cv2.putText(frame, f"FPS: {fps:.1f}", (w - 200, h - 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, info_color, 1, cv2.LINE_AA)
    
    sync_score = max(0, (1.0 - final_risk) * 100)
    # AV Sync 점수는 상태 색상에 맞춰 변화
    cv2.putText(frame, f"AV Sync: {sync_score:.1f}%", (w - 200, h - 20), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2, cv2.LINE_AA)
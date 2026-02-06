# 📐 AIoT Smart Cart – Hardware Specification

본 문서는 AIoT 스마트 쇼핑카트 프로젝트의 하드웨어 설계 기준 및 주요 컴포넌트 치수를 정의한다.  
3D 프린팅 기반 하우징 설계를 목적으로 하며, 모든 치수는 실제 제작 가능성을 고려하여 공차를 포함한다.

---

## 🖨 1. 3D Printer

### Printer Model
- **Bambu Lab HS2**

### Global Tolerance Policy
- 모든 끼워맞춤 구조물은 **±0.3 mm 공차**를 기본 적용한다.
- 나사산과 pitch의 규격은 기본 나사 규격을 따른다.

> 본 프로젝트의 모든 결합 구조는 *press-fit 기준*이며, 후가공 없이 조립 가능하도록 설계한다.

---

## 📺 2. LCD Display

### External Dimensions
| 항목 | 치수 |
|------|------|
| Width | 190.5 mm |
| Height | 114.6 mm |
| Depth | 16.7 mm |

### Active Display Area
| 항목 | 치수 |
|------|------|
| Width (Display Only) | 154.28 mm |
| Height (Display Only) | 86.12 mm |

### Design Notes
- 베젤 고정을 고려하여 전면 홀 가공 시 +0.3 mm 여유 적용
- Display only 영역은 화면 노출 영역으로 별도 컷팅 필요

---

## 🧠 3. Jetson Orin Nano

| 항목 | 치수 |
|------|------|
| Width | 103.5 mm |
| Height | 91 mm |
| Depth | 38 mm |

### Design Notes
- 방열 공간 확보 필요 (상부 최소 5 mm 권장)
- 마운트 홀 위치는 실제 PCB 기준으로 재확인 예정
- 육각 패턴 기반 패시브 쿨링 구조를 설계하여 Heat emission 구조 설계

---

## 🔋 4. Battery Housing

- 전원 설계 시 power bank는 사용 하지만 PD to C 케이블만 사용하고 따로 power bank의 하우징은 설계하지 않음
- power bank는 연결된 선이 Helix 구조에 따라 카트의 파이프에 묶이고 바구니와 카트 프레임 사이에 놓임

---

## 🛒 5. Cart Knob Support

| 항목 | 치수 |
|------|------|
| Width | 30 mm |
| Height | 50 mm |
| Depth | 36.3 mm |

### Notes
- 손잡이 체결부 기준 설계
- 내부 삽입 구조 시 0.2 mm 공차 적용 (비틀림 압입 방식)

---

## 📷 6. Camera Module

| 항목 | 치수 |
|------|------|
| Width | 36 mm |
| Height | 43 mm |
| Depth | 14 mm |

### Design Notes
- 전면 렌즈 홀은 돌출된 부분을 활용하여 웹캠 각도 자율 조정 고려
- 진동 방지를 위한 고무 패킹 구조 고려 -> 웹캠에 자체적으로 달려 있는 고무 패킹 구조를 활용

---

## 🔧 7. Cart Mount Assembly

### 7.1 Support Block

| 항목 | 치수 |
|------|------|
| Width | 30 mm |
| Height | 50 mm |
| Depth | 36 mm |
| Fillet Radius | 15 mm |

#### Port Clearance (Left Side Only)

Jetson Orin Nano의 HDMI / USB 포트를 고려하여 **Support Block 좌측면에만** 포트용 관통 홀을 설계한다.  
우측면에는 포트 홀이 존재하지 않는다. lid가 조립형 방식으로 들어간다.

| 항목 | 치수 |
|------|------|
| Width | 20 mm |
| Height | 13 mm |
| Depth | Through All |

##### Design Notes
- 포트 홀 위치 기준은 Jetson PCB 실측 기준으로 최종 보정
- 케이블 탈착 여유 확보를 위해 주변 +0.3 mm 공차 적용
- 해당 홀은 HDMI + USB 공용 접근용이며 직사각형 컷 형태
- 좌측 방향 기준: **Jetson 장착 기준 포트가 위치한 면**

### 7.2 Ring Clamp

| 항목 | 치수 |
|------|------|
| Radius | 13 mm |

### Design Notes
- 카트 파이프 기준 원형 클램프 구조
- Ring 파트는 비틀림 압입 체결 방식
- Support ↔ Ring 체결부는 분리형 구조

---


## 🔧 하드웨어 기술적 차별점

---

### 1. 비틀림 압입 기반 LCD 각도 조절 구조 설계

#### 기존 방식 적용 시 문제점
- 고정형 브라켓 사용 시 사용자 키·시야각 차이로 화면 가독성 저하
- 볼트 체결 방식 적용 시 공구 필요 및 반복 조정 불편
- 플라스틱 마운트 단독 사용 시 진동 및 사용 중 각도 풀림 발생

#### 적용한 기술적 해결 방법
- 카트 손잡이 고무 재질을 활용한 비틀림 압입(Twist-in Force Fit) 구조 설계
- 끼워맞춤 공차 적용을 통한 회전 마찰력 확보

---

### 2. Jetson Orin Nano · LCD 발열 대응 열 설계

#### 열 설계 미적용 시 문제점
- Jetson 연산 중 내부 온도 상승으로 프레임 드랍 및 객체 탐지 지연 발생
- LCD 패널 열 축적으로 인한 수명 단축 가능성

#### 적용한 기술적 해결 방법
- Jetson 및 LCD 주변 개방형 통풍 구조 설계 (사방 개방 구조)
- 밀폐 하우징 대신 육각 패턴 기반 패시브 쿨링 구조 적용

#### 기술 효과
- 온디바이스 추론 성능 안정화
- 장시간 사용 환경에서도 발열 누적 최소화

---

### 3. 실제 카트 장착을 전제로 한 컴팩트 온디바이스 패키징

- Jetson, LCD, 카메라, 센서 모듈 실물 치수 기반 패키징 설계
- 컨셉 모델이 아닌 실제 카트 장착 및 제작 중심 구조 설계
- 재설계 및 유지보수 시간 단축을 위해 Jetson, LCD, 카메라, 센서를 모듈 단위로 패키징

---


## 📌 General Mechanical Guidelines

- 모든 삽입 구조:
  - 기본 공차: +0.3 mm
- 비틀림 압입 구조:
  - 끼워 맞춤 공차: +0.2 mm
- 나사 체결부:
  - M3 기준 Hole Diameter: 3.2 mm
- 프린팅 방향:
  - 체결 하중 방향 기준 Layer 정렬
- Edge:
  - 외부 모서리 Fillet은 2 mm ~ 5 mm 사이 
  - 응력 집중 현상을 방지하여 하드웨어의 수명, 안정성 확보
  - 뾰족한 부분을 Fillet 처라하여 사용자의 안전성 또한 확보

---

## 📁 Revision

| Version | Date | Description |
|--------|------|-------------|
| v1.0 | 2026-01-22 | Initial hardware specification |
| v2.0 | 2026-01-26 | Integration hardware specification |

---

End of Document

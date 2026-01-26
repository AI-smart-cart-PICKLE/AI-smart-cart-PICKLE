# 📐 AIoT Smart Cart – Hardware Specification

본 문서는 AIoT 스마트 쇼핑카트 프로젝트의 하드웨어 설계 기준 및 주요 컴포넌트 치수를 정의한다.  
3D 프린팅 기반 하우징 설계를 목적으로 하며, 모든 치수는 실제 제작 가능성을 고려하여 공차를 포함한다.

---

## 🖨 1. 3D Printer

### Printer Model
- **Bambu Lab HS2**

### Global Tolerance Policy
- 모든 끼워맞춤 구조물은 **±0.3 mm 공차**를 기본 적용한다.

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

---

## 🔋 4. Battery Housing

- ❌ 현재 미적용
- 추후 전원 설계 확장(power bank 사용) 시 추가 예정

---

## 🛒 5. Cart Knob Support

| 항목 | 치수 |
|------|------|
| Width | 30 mm |
| Height | 50 mm |
| Depth | 36.3 mm |

### Notes
- 손잡이 체결부 기준 설계
- 내부 삽입 구조 시 0.3 mm 공차 적용

---

## 📷 6. Camera Module

| 항목 | 치수 |
|------|------|
| Width | 36 mm |
| Height | 43 mm |
| Depth | 14 mm |

### Design Notes
- 전면 렌즈 홀은 +0.5 mm 여유 권장
- 진동 방지를 위한 고무 패킹 구조 고려

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
우측면에는 포트 홀이 존재하지 않는다.

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
- Ring 파트는 탄성 체결 방식
- Support ↔ Ring 체결부는 분리형 구조 권장

---

## ⚖ 8. Load Cell Housing

- 현재 미정

---

## 📌 General Mechanical Guidelines

- 모든 삽입 구조:
  - 기본 공차: +0.3 mm
- 나사 체결부:
  - M3 기준 Hole Diameter: 3.2 mm
- 프린팅 방향:
  - 체결 하중 방향 기준 Layer 정렬
- Edge:
  - 외부 모서리 Fillet ≥ 2 mm 권장

---

## 📁 Revision

| Version | Date | Description |
|--------|------|-------------|
| v1.0 | 2026-01 | Initial hardware specification |

---

End of Document

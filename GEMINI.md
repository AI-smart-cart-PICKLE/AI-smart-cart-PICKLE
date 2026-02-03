너가 하는 말들 한글로 번역해서 보여줘.
로그,분석결과 이런것들 한국어로 말해.

아래의 api 명세서 .csv 파일을 반드시 보고 작성한다.
변수명은 snake case로 한다.
코드는 객체 지향적으로 유지, 보수, 재사용성이 쉽도록 작성한다.
backend 디렉토리에 있는 app 폴더 안에 db와 mobile_app 디렉토리 안에 UI를 보고 UI와 DB가 연동이 잘 됐는지 검증한다.
내부 통신 규걱은 http이고, 외부 통신 규격은 https이다.
```sql
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS vector;


CREATE TYPE user_provider AS ENUM ('LOCAL', 'GOOGLE');
CREATE TYPE cart_session_status AS ENUM ('ACTIVE', 'CHECKOUT_REQUESTED', 'PAID', 'CANCELLED');
CREATE TYPE detection_action_type AS ENUM ('ADD', 'REMOVE');
CREATE TYPE payment_method_type AS ENUM ('CARD', 'KAKAO_PAY');
CREATE TYPE pg_provider_type AS ENUM ('KAKAO_PAY', 'CARD_PG');
CREATE TYPE payment_status AS ENUM ('PENDING', 'APPROVED', 'FAILED', 'CANCELLED');
CREATE TYPE ledger_category AS ENUM ('GROCERY', 'MEAT', 'DAIRY', 'BEVERAGE', 'SNACK', 'HOUSEHOLD', 'ETC');



CREATE TABLE app_user (
  user_id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  provider user_provider NOT NULL DEFAULT 'LOCAL',
  nickname VARCHAR(40) NOT NULL,
  password_hash VARCHAR(255),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);


CREATE TABLE product_category (
  category_id BIGSERIAL PRIMARY KEY,
  name VARCHAR(60) NOT NULL UNIQUE,
  zone_code VARCHAR(30)
);


CREATE TABLE product (
  product_id BIGSERIAL PRIMARY KEY,
  category_id BIGINT,
  barcode VARCHAR(64) UNIQUE, 
  name VARCHAR(255) NOT NULL,
  price INTEGER NOT NULL,
  unit_weight_g INTEGER NOT NULL,
  stock_quantity INTEGER DEFAULT 0,
  image_url TEXT,
  product_info JSONB,

  embedding vector(1536),   
  created_at TIMESTAMPTZ DEFAULT now(),

  CONSTRAINT fk_product_category
    FOREIGN KEY (category_id) REFERENCES product_category (category_id)
);


CREATE INDEX idx_product_name_trgm
  ON product USING gin (name gin_trgm_ops);

CREATE INDEX idx_product_embedding
  ON product USING ivfflat (embedding vector_cosine_ops);


CREATE TABLE recipe (
  recipe_id BIGSERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  instructions TEXT,
  image_url TEXT,

  embedding vector(1536),   

  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE INDEX idx_recipe_embedding
  ON recipe USING ivfflat (embedding vector_cosine_ops);


CREATE TABLE recipe_ingredient (
  recipe_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity_info VARCHAR(50),
  importance_score INTEGER DEFAULT 1,

  PRIMARY KEY (recipe_id, product_id),

  CONSTRAINT fk_recipe
    FOREIGN KEY (recipe_id) REFERENCES recipe (recipe_id) ON DELETE CASCADE,

  CONSTRAINT fk_ingredient
    FOREIGN KEY (product_id) REFERENCES product (product_id)
);


CREATE TABLE saved_recipe (
  user_id BIGINT NOT NULL,
  recipe_id BIGINT NOT NULL,
  saved_at TIMESTAMPTZ DEFAULT now(),

  PRIMARY KEY (user_id, recipe_id),

  CONSTRAINT fk_saved_user
    FOREIGN KEY (user_id) REFERENCES app_user (user_id) ON DELETE CASCADE,

  CONSTRAINT fk_saved_recipe
    FOREIGN KEY (recipe_id) REFERENCES recipe (recipe_id) ON DELETE CASCADE
);


CREATE TABLE cart_device (
  cart_device_id BIGSERIAL PRIMARY KEY,
  device_code VARCHAR(64) NOT NULL UNIQUE  
);


CREATE TABLE cart_session (
  cart_session_id BIGSERIAL PRIMARY KEY,
  cart_device_id BIGINT NOT NULL,
  user_id BIGINT,

  status cart_session_status NOT NULL DEFAULT 'ACTIVE',
  budget_limit INTEGER DEFAULT 0,

  expected_total_g INTEGER DEFAULT 0,
  measured_total_g INTEGER DEFAULT 0,

  started_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  ended_at TIMESTAMPTZ,

  CONSTRAINT fk_cart_device
    FOREIGN KEY (cart_device_id) REFERENCES cart_device (cart_device_id),

  CONSTRAINT fk_cart_user
    FOREIGN KEY (user_id) REFERENCES app_user (user_id)
);


CREATE TABLE cart_item (
  cart_item_id BIGSERIAL PRIMARY KEY,
  cart_session_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,

  quantity  INTEGER NOT NULL DEFAULT 1,
  unit_price INTEGER NOT NULL,
  added_at TIMESTAMPTZ DEFAULT now(),

  CONSTRAINT uq_cart_item_session_product UNIQUE (cart_session_id, product_id), 

  CONSTRAINT fk_cart_session
    FOREIGN KEY (cart_session_id) REFERENCES cart_session (cart_session_id) ON DELETE CASCADE,

  CONSTRAINT fk_cart_product
    FOREIGN KEY (product_id) REFERENCES product (product_id)
);




CREATE TABLE cart_detection_log (
  log_id BIGSERIAL PRIMARY KEY,
  cart_session_id BIGINT NOT NULL,
  cart_device_id BIGINT NOT NULL,
  product_id BIGINT,       
  action_type detection_action_type NOT NULL, 
  confidence_score NUMERIC(5,2),  
  detected_weight_g INTEGER, 
  is_applied BOOLEAN DEFAULT FALSE,
  detected_at TIMESTAMPTZ DEFAULT now(), 
  created_at TIMESTAMPTZ DEFAULT now(),  

  CONSTRAINT fk_log_session
    FOREIGN KEY (cart_session_id) REFERENCES cart_session (cart_session_id) ON DELETE CASCADE,

  CONSTRAINT fk_log_device
    FOREIGN KEY (cart_device_id) REFERENCES cart_device (cart_device_id),

  CONSTRAINT fk_log_product
    FOREIGN KEY (product_id) REFERENCES product (product_id)
);


CREATE TABLE payment_method (
  method_id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,

  method_type payment_method_type NOT NULL,  

  billing_key VARCHAR(255),

  card_brand VARCHAR(30),       
  card_last4 CHAR(4),            


  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now(),

  CONSTRAINT fk_method_user
    FOREIGN KEY (user_id) REFERENCES app_user (user_id) ON DELETE CASCADE
);

CREATE UNIQUE INDEX uq_payment_method_user_billing_key
  ON payment_method (user_id, billing_key)
  WHERE billing_key IS NOT NULL;


CREATE TABLE payment (
  payment_id BIGSERIAL PRIMARY KEY,
  cart_session_id BIGINT UNIQUE,
  user_id BIGINT NOT NULL,

  method_id BIGINT,

  pg_provider pg_provider_type NOT NULL,  
  pg_tid VARCHAR(255),                    

  status payment_status NOT NULL DEFAULT 'PENDING',
  total_amount INTEGER NOT NULL,
  approved_at TIMESTAMPTZ,

  CONSTRAINT fk_payment_session
    FOREIGN KEY (cart_session_id) REFERENCES cart_session (cart_session_id),

  CONSTRAINT fk_payment_user
    FOREIGN KEY (user_id) REFERENCES app_user (user_id),

  CONSTRAINT fk_payment_method
    FOREIGN KEY (method_id) REFERENCES payment_method (method_id)
);


CREATE TABLE ledger_entry (
  ledger_entry_id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  payment_id BIGINT,

  spend_date DATE NOT NULL,
  category ledger_category NOT NULL DEFAULT 'ETC',
  amount INTEGER NOT NULL,

  CONSTRAINT fk_ledger_user
    FOREIGN KEY (user_id) REFERENCES app_user (user_id) ON DELETE CASCADE,

  CONSTRAINT fk_ledger_payment
    FOREIGN KEY (payment_id) REFERENCES payment (payment_id) ON DELETE SET NULL
);

```

```api 명세 csv파일
ID,백 구현,구분,method,URI,API,설명,담당,상태
API 상세,No,회원,POST,api/auth/signup,회원가입,"이메일
• 이메일 형식: xxx@xxx.xxx
• 중복 이메일 사용 불가
비밀번호
• 영문 + 숫자 혼합 필수
• 최소 8자 이상
• 공백 사용 불가
• 암호화(Hash) 후 저장됨
닉네임
• 한글, 영문만 사용 가능
• 최소 2자 이상, 최대 8자 이하
• 중복 닉네임 허용 
처리 흐름
1. 입력값 유효성 검사
2. 사용자 정보 저장
3. 회원가입 성공 시 사용자 ID 반환
예외 처리
• 이메일 중복: 400 Conflict
• 인증 코드 오류 또는 만료: 400 Bad Request
• 입력값 형식 오류: 400 Bad Request",", 전기정보공학과 전주연",시작 전
API 상세,No,회원,GET,api/auth/check-email,이메일 중복 검사,해당 이메일이 사용 가능한지 확인합니다.,", 전기정보공학과 전주연",시작 전
API 상세,No,회원,POST,api/auth/login,로그인,"• 이메일과 비밀번호로 사용자 인증
• 인증 성공 시 JWT Access/Refresh Token 발급",", 전기정보공학과 전주연",시작 전
API 상세,No,회원,POST,api/auth/refresh,토큰 갱신,Access Token 재발급,", 전기정보공학과 전주연",시작 전
API 상세,No,회원,GET,api/users/me,내 정보 조회,마이페이지 기본 정보 로딩,", 전기정보공학과 전주연",시작 전
API 상세,No,회원,PUT,api/users/me,내 정보 수정,"로그인된 사용자의 기본 정보를 수정한다.
마이페이지에서 닉네임 등 개인정보 변경 시 사용된다.
JWT Access Token 인증이 필요하다.",", 전기정보공학과 전주연",시작 전
,No,상품,GET,api/products/search,상품 검색,상품명을 입력받아 검색합니다. pg_trgm을 활용한 오타 허용(Fuzzy) 검색이 적용됩니다.,Jeonghui Hong,시작 전
API 상세,No,상품,GET,api/products/{id},상품 상세 조회,특정 상품의 상세 정보를 조회합니다. (영양 정보 등 JSONB 데이터 포함),Jeonghui Hong,시작 전
,No,상품,GET,api/products/{product_id}/location,상품 위치 안내,해당 상품이 매장 내 어느 구역(Zone)에 있는지 좌표와 함께 반환합니다.,Jeonghui Hong,시작 전
API 상세,No,회원,GET,api/carts/current-recipe,현재 레시피 확인,"Logic: 내 카트 세션에 selected_recipe_id가 있는지 확인하고, 있으면 레시피 상세 정보를 줍니다.

",", 전기정보공학과 전주연",시작 전
,No,카트,POST,api/carts/login/qr,카트 QR 로그인,"카트에 부착된 QR 코드를 사용자가 스캔하면, 해당 카트 디바이스와 앱에 로그인된 사용자 계정을 연결하여 카트 세션을 활성화한다.",", 전기정보공학과 전주연",시작 전
,No,카트,GET,api/carts/session,카트 세션 조회,"- 현재 카트에 연결된 사용자 정보와 카트 세션의 상태를 조회한다.
- 카트 사용 시작 시, 카트가 활성 상태인지, 결제 대기 상태인지, 취소 상태인지, 종료되었는지를 판단하는 기준 API.",", 전기정보공학과 전주연",시작 전
API 상세,No,카트,GET,api/carts/items,상품 목록 조회,"- 현재 카트 세션에 담긴 모든 상품 목록을 조회한다.
- 각 상품의 수량, 가격, 무게 정보를 포함한다. ",", 전기정보공학과 전주연",시작 전
API 상세,No,카트,POST,api/carts/items,카트 내의 상품 추가,"- 센서 감지 또는 AI 카메라 인식을 통해 확인된 상품을 카트 세션에 새로운 상품 항목으로 추가한다. 
- 서버는 상품의 기준 무게와 실제 측정 무게를 비교하여 (정상 추가/ 경고 상태 추가/ 사용자 확인 필요 상태) 중 하나로 처리한다. 
- 상품 추가 후 카트 요약 정보 및 무게 검증 결과를 함께 반환한다. ",", 전기정보공학과 전주연",시작 전
API 상세,No,카트,DELETE,api/carts/items/{cart_item_id},"카트에서 상품 제거 ","- 카트에 담긴 특정 상품을 제거한다.
- 상품 제거 이후에는 카트의 예상 무게와 실제 무게를 다시 비교하여 무게 검증 상태를 갱신한다.",", 전기정보공학과 전주연",시작 전
API 상세,No,카트,PATCH,api/carts/items/{cart_item_id},상품 수량 변경,"- 카트에 담긴 특정 상품의 수량을 직접 수정한다.
- 수량 변경 시 서버는 자동으로 : 
                                                       - 총 가격
                                                       - 총 예상 무게
                                                      - 무게 검증 상태
를 다시 계산하여 반환한다. ",", 전기정보공학과 전주연",시작 전
API 상세,No,카트,POST,api/carts/weight/validate,무게 검증,- 카트에 담긴 상품 목록의 예상 총 무게와 센서로 측정된 실제 무게를 비교하여 일치 여부를 검증한다.,", 전기정보공학과 전주연",시작 전
API 상세,No,카트,GET,api/carts/location,위치 조회,"상품 또는 카테고리 기준으로 매장 내 대략적인 위치 정보를 제공한다.

다음과 같은 상황에서 사용된다.
• 음성(STT) 검색: “우유 어디 있어?”
• 추천 상품 하단의 “위치 보기” 버튼 클릭
• 카테고리 기반 탐색 (유제품 코너 등)
서버는 상품의 카테고리 또는 사전 정의된 존(zone) 정보를 기반으로

매장 지도에 표시 가능한 위치 데이터를 반환한다.",", 전기정보공학과 전주연",시작 전
API 상세,No,카트,POST,api/carts/checkout,결제 요청,"무게 검증이 완료된 카트 세션을
결제 요청 상태(CHECKOUT_REQUESTED) 로 전환한다.
• 무게 불일치 상태에서는 호출할 수 없다.
• 실제 결제(PG 승인)는 이후 결제 API에서 처리된다.
• 이 API는 “결제 버튼 클릭” 행위에 대응한다.",", 전기정보공학과 전주연",시작 전
API 상세,No,카트,POST,api/carts/cancel,카트 세션 취소,"결제를 진행하지 않고 카트 사용을 종료한다.

카트 세션을 명시적으로 종료하고,

카트는 다음 사용자를 위해 초기화 상태로 돌아간다.
• 쇼핑 도중 중단
• 결제 포기
• 시스템 오류 발생 시 안전 종료 용도",", 전기정보공학과 전주연",시작 전
API 상세,No,카트,POST,api/carts/camera/open,카메라 뷰 열기,"카트에 장착된 AI 카메라 스트림을 활성화한다. ",", 전기정보공학과 전주연",시작 전
API 상세,No,카트,POST,api/carts/camera/close,카메라 뷰 종료,AI 카메라 스트림을 종료하고 카메라 세션을 정리한다.,", 전기정보공학과 전주연",시작 전
API 상세,No,카트,GET,api/carts/recommend/products,레시피 기반 연관 레시피 추천,"현재 카트에 담긴 최근 상품을 기준으로

레시피 기반의 연관 상품을 추천한다.
• 예: 우유 → 시리얼, 요거트
• 예: 파스타 → 소스, 치즈
추천 결과는 추가 구매 유도 UX를 위한 보조 기능이며,

상품 상세 정보와 함께 “위치 조회” 기능과 연동될 수 있다.",양수명,시작 전
API 상세,No,카트,GET,api/carts/recommendations,재료 기반 레시피 추천,"• Input: product_id (양파)
• Logic: importance_score 높은 순 정렬",양수명,시작 전
API 상세,No,카트,POST,api/carts/select-recipe,요리 선택 (동기화),"• ""나 이 요리 할래""라고 서버에 알림
• Input: recipe_id",양수명,시작 전
API 상세,No,결제,POST,api/payments/ready,결제 요청,"
앱에서 '결제하기' 버튼을 눌렀을 때 호출합니다. PG사(카카오페이)로부터 **결제 고유 번호(TID)**와 결제창 URL을 발급받습니다.

",양수명,시작 전
API 상세,No,결제,POST,api/payments/approve,결제 승인,"
사용자가 카카오톡에서 비밀번호 입력을 마치면, 앱이 **pg_token**을 받아옵니다. 이 토큰과 아까 받은 **tid**를 서버로 보내 최종 결제를 확정합니다.

",양수명,시작 전
API 상세,No,결제,GET,"/api/payments/{payment_id}
",결제 결과 조회,"특정 결제 건의 결과 상태를 조회한다.
결제 완료 여부, 결제 금액, 결제 시각 등을 확인한다.
결제 완료 화면 또는 주문 내역 조회 시 사용된다.
JWT Access Token 인증이 필요하다.",양수명,시작 전
API 상세,No,결제,POST,"/api/payments/{payment_id}/cancel
",결제 취소,"완료된 결제를 취소(환불) 요청한다.
결제 완료(COMPLETED) 상태인 경우에만 취소 가능하다.
JWT Access Token 인증이 필요하다.",양수명,시작 전
API 상세,No,결제,GET,/api/payments/methods,결제 수단 목록 조회,현재 사용자가 등록한 모든 결제 수단 리스트를 불러옵니다.,양수명,시작 전
API 상세,No,결제,POST,/api/payments/methods,결제 수단 등록 (카드/빌링키),새로운 결제 수단을 등록합니다. (실제 카드 정보는 보안상 PG사를 통해 빌링키 형태로 저장됩니다.),양수명,시작 전
API 상세,No,결제,DELETE,/api/payments/methods/{mehod_id},결제 수단 삭제,등록된 결제 수단을 삭제합니다.,양수명,시작 전
API 상세,No,결제,POST,/api/payments/ready,결제 준비 요청,"1. 앱에서 '결제하기' 버튼을 누르면 호출됩니다.
2. 서버는 PG사(카카오페이)에 결제 정보를 보내고 리다이렉트 URL과 **TID(거래고유번호)**를 받아옵니다.",양수명,시작 전
API 상세,No,결제,POST,/api/payments/approve,결제 승인 요청,"1. 사용자가 카카오톡에서 비밀번호 입력을 완료하면, 앱이 pg_token을 획득합니다.
2. 앱은 이 토큰과 아까 받은 tid를 서버로 보내 최종 승인을 요청합니다.",양수명,시작 전
API 상세,No,결제,POST,/api/payments/{payment_id},결제 내역 상세,특정 결제 건의 상세 내역(품목 리스트 포함)을 조회합니다.,양수명,시작 전
,No,가계부,GET,/api/ledger,가계부 내역 조회,"- 로그인한 사용자의 가계부 항목 목록을 조회한다.
- ledger_entry 테이블을 기준으로 조회한다.
- 기간 및 카테고리 필터링이 가능하다.",Jeonghui Hong,시작 전
,No,가계부,GET,/api/ledger/{ledger_entry_id},가계부 단건 상세 조회,특정 가계부 항목의 상세 정보를 조회한다.,Jeonghui Hong,시작 전
,No,가계부,PUT,/api/ledger/{ledger_entry_id},가계부 카테고리/ 메모 수정,"- 가계부 항목의 분류 정보(카테고리, 메모)를 수정한다.
- 결제 기반 데이터의 무결성을 위해 금액 및 날짜는 수정할 수 없다.",Jeonghui Hong,시작 전
,No,가계부,GET,/api/ledger/summary/monthly,가계부 월별 요약,"- 특정 월의 가계부 지출을 카테고리별로 요약 조회한다.
- 월간 소비 분석 및 통계 화면에 사용된다.",Jeonghui Hong,시작 전
,No,가계부,GET,/api/ledger/top-items,Top Item 조회,"- 특정 기간 동안 가장 많이 구매된 상품 상위 목록을 조회한다.
- 결제 완료된 건(payment.status = APPROVED)만 집계 대상이다
- 구매 횟수 기준으로 정렬한다.",Jeonghui Hong,시작 전
,No,가계부,GET,/api/ledger/top-categories,Top Category 조회,"- 특정 기간 동안 사용자의 카테고리별 지출 금액을 집계한다.
- 가계부 분석 화면의 TOP Category/Spending Breakdown 영역에 사용된다.
- 지출 금액 기준으로 정렬된다.",Jeonghui Hong,시작 전
,No,가계부,GET,/api/ledger/recent,최근 지출 내역 조회,"- 사용자의 최근 결제/지출 내역을 시간순으로 조회한다.
- 결제 완료(payment.status = APPROVED)된 내역만 조회 대상이다.
- 가계부(ledger_entry)와 결제(payment) 정보를 함께 제공한다.",Jeonghui Hong,시작 전
,No,가계부,GET,/api/ledger/calendar,캘린더,"- 특정 월의 일자별 지출 합계를 조회한다.
- 가계부 캘린더 UI에 사용된다.
- 하루에 여러 지출이 있어도 일 단위로 집계된다.",Jeonghui Hong,시작 전
```

```commit 컨벤션
# **Commit Convention Specification**

## **1. 목적 (Purpose)**

본 문서는 팀 내 Git 커밋 메시지 규칙(Commit Convention)을 정의하여,
 일관된 변경 이력 관리와 명확한 변경 의도 전달을 목표로 한다.

## **2. 기본 구조 (Structure)**

모든 커밋 메시지는 다음 형식을 따른다.

```
type: subject
```

- **type**: 커밋의 성격 (필수)
- **subject**: 변경 요약 (필수, 50자 이내)

## **3. Type 규칙**

| **Type** | **Description** |
| --- | --- |
| ✨ feat | 신규 기능 추가 |
| 🐛 fix | 버그 수정 |
| 📝 docs | 문서 관련 변경 |
| ♻️ refactor | 기능 변경 없는 코드 구조 개선 |
| 🚀 deploy | CI/CD 설정 변경 |
| 🔧 chore | 기능 외 자잘한 수정 (예: 설정, 환경 파일 등) |
| 🗑️ remove | 불필요한 파일 또는 코드 삭제 |
|  |  |

## **4. Subject 규칙**

- 메시지는 간결하고 명확하게 작성한다. (50자 이내)
- 변경 내용을 한눈에 파악할 수 있게 작성한다.
- 필요 시 여러 문단으로 구분 가능

예시:

```
refactor(user): 유효성 검사 로직 분리
- 기존 중복된 validation 로직을 common/utils로 이동하여 재사용성 확보
- 이로 인해 중복 코드 감소 및 유지보수 효율성 향상
```

## **5. 작성 규칙 요약**

- 커밋은 **의미 있는 최소 단위**로 분리한다.
- **하나의 커밋에는 하나의 목적**만 포함한다.
- PR 리뷰 시 `type`과 `scope`를 통해 변경 목적을 명확히 한다.
- 팀 전체가 동일한 형식을 준수하며, 필요 시 **commitlint**로 자동 검증한다.

## **6. 예시 목록**

```
feat: 회원가입 시 이메일 중복 검사 기능 추가
fix(auth): 토큰 만료 시 자동 로그아웃 처리
docs: README 설치 가이드 보완
refactor: userService 로직 분리 및 함수명 수정
deploy: GitHub Actions 테스트 단계 추가
chore: ESLint 설정 파일 업데이트
remove: 사용하지 않는 mock 데이터 삭제
```
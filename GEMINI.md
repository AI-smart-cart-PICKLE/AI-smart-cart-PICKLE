1.너가 하는 말들 한글로 번역해서 보여줘.
2.아래의 ERD 테이블을 반드시 보고 작성한다.
3,아래의 api 명세서 .csv 파일을 반드시 보고 작성한다.
4.변수명은 snake case로 한다.
5.코드는 객체 지향적으로 유지, 보수, 재사용성이 쉽도록 작성한다.
6.backend 디렉토리에 있는 app 폴더 안에 db와 mobile_app 디렉토리 안에 UI를 보고 UI와 DB가 연동이 잘 됐는지 검증한다.
7.내부 통신 규걱은 http이고, 외부 통신 규격은 https이다.
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
,Yes,회원(Auth),POST,/api/auth/signup,회원가입,이메일/비밀번호 기반 회원가입 (User Router),,구현 완료
,Yes,회원(Auth),POST,/api/auth/login,로그인,이메일 로그인 및 JWT 발급 (User Router),,구현 완료
,Yes,회원(Auth),POST,/api/auth/logout,로그아웃,리프레시 토큰 쿠키 삭제 (User Router),,구현 완료
,Yes,회원(Auth),POST,/auth/refresh,토큰 갱신,Refresh Token을 이용한 Access Token 재발급 (Auth Router),,구현 완료
,Yes,회원(Auth),POST,/auth/password/reset-request,비밀번호 재설정 요청,이메일로 재설정 링크 전송,,구현 완료
,Yes,회원(Auth),POST,/auth/password/reset,비밀번호 재설정,토큰 검증 후 새로운 비밀번호로 변경,,구현 완료
,Yes,회원(Auth),POST,/auth/google,구글 로그인,Google OAuth Code로 로그인 및 회원가입 처리,,구현 완료
,Yes,회원(Auth),GET,/auth/google/callback,구글 로그인 콜백,Google Redirect 용 (프론트엔드 연동용),,구현 완료
,Yes,회원(Auth),GET,/auth/kakao/login,카카오 로그인,카카오 인증 페이지 리다이렉트,,구현 완료
,Yes,회원(Auth),GET,/auth/kakao/callback,카카오 로그인 콜백,카카오 Code로 로그인 및 회원가입 처리,,구현 완료
,Yes,회원(User),GET,/api/users/me,내 정보 조회,현재 로그인된 사용자의 정보 조회,,구현 완료
,Yes,회원(User),PATCH,/api/users/me/nickname,닉네임 변경,사용자 닉네임 수정,,구현 완료
,Yes,회원(User),PATCH,/api/users/me/password,비밀번호 변경,기존 비밀번호 확인 후 변경 (로컬 유저 전용),,구현 완료
,Yes,회원(User),DELETE,/api/users/me,회원 탈퇴,계정 비활성화 (Soft Delete),,구현 완료
,Yes,상품,GET,/api/products/,상품 목록 조회,전체 상품 목록 조회,,구현 완료
,Yes,상품,GET,/api/products/search,상품 검색,상품명 유사도 기반 검색 (pg_trgm),,구현 완료
,Yes,상품,GET,/api/products/{product_id},상품 상세 조회,특정 상품의 상세 정보 조회,,구현 완료
,Yes,상품,GET,/api/products/{product_id}/location,상품 위치 안내,상품의 매장 내 구역(Zone) 및 매대 정보,,구현 완료
,Yes,카트,POST,/api/carts/pair/qr,카트 QR 로그인,QR 코드를 통해 카트 디바이스와 사용자 계정 연결,,구현 완료
,Yes,카트,POST,/api/carts/,카트 세션 생성,새로운 장바구니 세션 시작 (쇼핑 시작),,구현 완료
,Yes,카트,GET,/api/carts/{session_id},카트 세션 조회,장바구니 상태, 총액, 상품 목록 등 조회,,구현 완료
,Yes,카트,POST,/api/carts/{session_id}/items,카트 상품 추가,장바구니에 상품 추가 및 무게 검증 요청,,구현 완료
,Yes,카트,DELETE,/api/carts/items/{cart_item_id},카트 상품 삭제,장바구니에서 특정 상품 제거,,구현 완료
,Yes,카트,PATCH,/api/carts/items/{cart_item_id},카트 상품 수량 변경,상품 수량 수정 및 예상 무게 재계산,,구현 완료
,Yes,카트,POST,/api/carts/{session_id}/select-recipe,레시피 선택,쇼핑 중 레시피 선택 상태 동기화,,구현 완료
,Yes,카트,POST,/api/carts/weight/validate,무게 검증,카트의 예상 무게와 실제 측정 무게 비교 검증,,구현 완료
,Yes,카트,POST,/api/carts/{session_id}/cancel,카트 세션 취소,쇼핑 중단 및 카트 세션 종료,,구현 완료
,Yes,카트,POST,/api/carts/{cart_session_id}/camera/view/on,카메라 뷰 켜기,카트의 AI 카메라 스트림 활성화,,구현 완료
,Yes,카트,POST,/api/carts/{cart_session_id}/camera/view/off,카메라 뷰 끄기,카트의 AI 카메라 스트림 종료,,구현 완료
,Yes,추천,GET,/api/recommendations/by-product/{product_id},AI 레시피 추천,선택 상품과 벡터 유사도가 높은 레시피 추천,,구현 완료
,Yes,결제,POST,/api/payments/request,결제 요청 (자동),무게 검증 후 등록된 수단으로 자동 결제 진행,,구현 완료
,Yes,결제,POST,/api/payments/subscription/register/ready,정기결제 등록 준비,카카오페이 정기결제 등록 요청 (Redirect URL 발급),,구현 완료
,Yes,결제,GET,/api/payments/subscription/register/approve,정기결제 등록 승인,카카오페이 인증 후 빌링키 발급 및 저장,,구현 완료
,Yes,결제,POST,/api/payments/subscription/pay,정기결제 (테스트),저장된 빌링키를 이용한 즉시 결제 테스트,,구현 완료
,Yes,결제,GET,/api/payments/subscription/register/callback,정기결제 콜백,결제 수단 등록 결과 페이지,,구현 완료
,Yes,결제,POST,/api/payments/ready,단건 결제 준비,카카오페이 1회성 결제 준비 요청,,구현 완료
,Yes,결제,POST,/api/payments/approve,단건 결제 승인,카카오페이 1회성 결제 승인 처리,,구현 완료
,Yes,결제,GET,/api/payments/success,결제 성공 페이지,결제 승인 완료 안내 페이지,,구현 완료
,Yes,결제,GET,/api/payments/cancel,결제 취소 페이지,결제 중 취소 안내 페이지,,구현 완료
,Yes,결제,GET,/api/payments/fail,결제 실패 페이지,결제 실패 안내 페이지,,구현 완료
,Yes,결제,GET,/api/payments/methods,결제 수단 목록,등록된 카드/빌링키 목록 조회,,구현 완료
,Yes,결제,POST,/api/payments/methods,결제 수단 등록,결제 수단 수동 등록 (테스트/초기화용),,구현 완료
,Yes,결제,DELETE,/api/payments/methods/{method_id},결제 수단 삭제,등록된 결제 수단 제거,,구현 완료
,Yes,결제,GET,/api/payments/{payment_id},결제 상세 조회,특정 결제 건의 상세 정보 조회,,구현 완료
,Yes,결제,POST,/api/payments/{payment_id}/cancel,결제 취소,승인된 결제에 대한 환불(취소) 요청,,구현 완료
,Yes,가계부,POST,/api/ledger/from-payment/{payment_id},가계부 자동 생성,결제 완료 건을 가계부 내역으로 변환 및 저장,,구현 완료
,Yes,가계부,GET,/api/ledger,가계부 목록 조회,날짜 및 카테고리 필터링 조회,,구현 완료
,Yes,가계부,GET,/api/ledger/calendar,가계부 캘린더,월별 일자별 지출 합계 조회,,구현 완료
,Yes,가계부,GET,/api/ledger/summary/monthly,월별 지출 요약,카테고리별 지출 통계,,구현 완료
,Yes,가계부,GET,/api/ledger/top-categories,Top Categories,지출 금액 기준 상위 카테고리 조회,,구현 완료
,Yes,가계부,GET,/api/ledger/top-items,Top Items,구매 횟수 기준 상위 아이템(카테고리) 조회,,구현 완료
,Yes,가계부,GET,/api/ledger/recent,최근 지출 내역,최근 발생한 결제/지출 내역 조회,,구현 완료
,Yes,가계부,GET,/api/ledger/{ledger_entry_id},가계부 상세 조회,가계부 단건 상세 내용 조회,,구현 완료
,Yes,가계부,PUT,/api/ledger/{ledger_entry_id},가계부 수정,카테고리 및 메모 수정,,구현 완료

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
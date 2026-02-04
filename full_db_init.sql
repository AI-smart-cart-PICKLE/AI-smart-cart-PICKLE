-- =========================================================
-- 🚀 PICKLE Project: FULL DATABASE INITIALIZATION SCRIPT
-- 기존 데이터를 모두 지우고 최신 스키마로 초기화합니다.
-- =========================================================

-- 1. 기존 테이블 및 타입 삭제 (초기화)
DROP TABLE IF EXISTS ledger_entry CASCADE;
DROP TABLE IF EXISTS payment CASCADE;
DROP TABLE IF EXISTS payment_method CASCADE;
DROP TABLE IF EXISTS cart_detection_log CASCADE;
DROP TABLE IF EXISTS cart_item CASCADE;
DROP TABLE IF EXISTS cart_session CASCADE;
DROP TABLE IF EXISTS cart_device CASCADE;
DROP TABLE IF EXISTS saved_recipe CASCADE;
DROP TABLE IF EXISTS recipe_ingredient CASCADE;
DROP TABLE IF EXISTS recipe CASCADE;
DROP TABLE IF EXISTS product CASCADE;
DROP TABLE IF EXISTS product_category CASCADE;
DROP TABLE IF EXISTS app_user CASCADE;

DROP TYPE IF EXISTS user_provider CASCADE;
DROP TYPE IF EXISTS cart_session_status CASCADE;
DROP TYPE IF EXISTS detection_action_type CASCADE;
DROP TYPE IF EXISTS payment_method_type CASCADE;
DROP TYPE IF EXISTS pg_provider_type CASCADE;
DROP TYPE IF EXISTS payment_status CASCADE;
DROP TYPE IF EXISTS ledger_category CASCADE;

-- 2. 확장 기능 활성화
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS vector;

-- 3. 커스텀 타입 생성
CREATE TYPE user_provider AS ENUM ('LOCAL', 'GOOGLE', 'KAKAO');
CREATE TYPE cart_session_status AS ENUM ('ACTIVE', 'CHECKOUT_REQUESTED', 'PAID', 'CANCELLED');
CREATE TYPE detection_action_type AS ENUM ('ADD', 'REMOVE');
CREATE TYPE payment_method_type AS ENUM ('CARD', 'KAKAO_PAY');
CREATE TYPE pg_provider_type AS ENUM ('KAKAO_PAY', 'CARD_PG');
CREATE TYPE payment_status AS ENUM ('PENDING', 'APPROVED', 'FAILED', 'CANCELLED');
CREATE TYPE ledger_category AS ENUM ('GROCERY', 'MEAT', 'DAIRY', 'BEVERAGE', 'SNACK', 'HOUSEHOLD', 'ETC');

-- 4. 회원 테이블
CREATE TABLE app_user (
  user_id BIGSERIAL PRIMARY KEY,
  email VARCHAR(255) NOT NULL UNIQUE,
  provider user_provider NOT NULL DEFAULT 'LOCAL',
  nickname VARCHAR(40) NOT NULL,
  password_hash VARCHAR(255),
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ DEFAULT now()
);

-- 5. 상품 카테고리
CREATE TABLE product_category (
  category_id BIGSERIAL PRIMARY KEY,
  name VARCHAR(60) NOT NULL UNIQUE,
  zone_code VARCHAR(30)
);

-- 6. 상품 테이블
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
  CONSTRAINT fk_product_category FOREIGN KEY (category_id) REFERENCES product_category (category_id)
);
CREATE INDEX idx_product_name_trgm ON product USING gin (name gin_trgm_ops);
CREATE INDEX idx_product_embedding ON product USING ivfflat (embedding vector_cosine_ops);

-- 7. 레시피 테이블
CREATE TABLE recipe (
  recipe_id BIGSERIAL PRIMARY KEY,
  title VARCHAR(255) NOT NULL,
  description TEXT,
  instructions TEXT,
  image_url TEXT,
  embedding vector(1536),   
  created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX idx_recipe_embedding ON recipe USING ivfflat (embedding vector_cosine_ops);

-- 8. 레시피 재료
CREATE TABLE recipe_ingredient (
  recipe_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity_info VARCHAR(50),
  importance_score INTEGER DEFAULT 1,
  PRIMARY KEY (recipe_id, product_id),
  CONSTRAINT fk_recipe FOREIGN KEY (recipe_id) REFERENCES recipe (recipe_id) ON DELETE CASCADE,
  CONSTRAINT fk_ingredient FOREIGN KEY (product_id) REFERENCES product (product_id)
);

-- 9. 저장된 레시피
CREATE TABLE saved_recipe (
  user_id BIGINT NOT NULL,
  recipe_id BIGINT NOT NULL,
  saved_at TIMESTAMPTZ DEFAULT now(),
  PRIMARY KEY (user_id, recipe_id),
  CONSTRAINT fk_saved_user FOREIGN KEY (user_id) REFERENCES app_user (user_id) ON DELETE CASCADE,
  CONSTRAINT fk_saved_recipe FOREIGN KEY (recipe_id) REFERENCES recipe (recipe_id) ON DELETE CASCADE
);

-- 10. 카트 기기
CREATE TABLE cart_device (
  cart_device_id BIGSERIAL PRIMARY KEY,
  device_code VARCHAR(64) NOT NULL UNIQUE  
);

-- 11. 카트 세션 (무게 필드 포함)
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
  CONSTRAINT fk_cart_device FOREIGN KEY (cart_device_id) REFERENCES cart_device (cart_device_id),
  CONSTRAINT fk_cart_user FOREIGN KEY (user_id) REFERENCES app_user (user_id)
);

-- 12. 카트 아이템
CREATE TABLE cart_item (
  cart_item_id BIGSERIAL PRIMARY KEY,
  cart_session_id BIGINT NOT NULL,
  product_id BIGINT NOT NULL,
  quantity INTEGER NOT NULL DEFAULT 1,
  unit_price INTEGER NOT NULL,
  added_at TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT uq_cart_item_session_product UNIQUE (cart_session_id, product_id), 
  CONSTRAINT fk_cart_session FOREIGN KEY (cart_session_id) REFERENCES cart_session (cart_session_id) ON DELETE CASCADE,
  CONSTRAINT fk_cart_product FOREIGN KEY (product_id) REFERENCES product (product_id)
);

-- 13. 카트 감지 로그
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
  CONSTRAINT fk_log_session FOREIGN KEY (cart_session_id) REFERENCES cart_session (cart_session_id) ON DELETE CASCADE,
  CONSTRAINT fk_log_device FOREIGN KEY (cart_device_id) REFERENCES cart_device (cart_device_id),
  CONSTRAINT fk_log_product FOREIGN KEY (product_id) REFERENCES product (product_id)
);

-- 14. 결제 수단
CREATE TABLE payment_method (
  method_id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  method_type payment_method_type NOT NULL,  
  billing_key VARCHAR(255),
  card_brand VARCHAR(30),       
  card_last4 CHAR(4),            
  is_default BOOLEAN NOT NULL DEFAULT FALSE,
  created_at TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT fk_method_user FOREIGN KEY (user_id) REFERENCES app_user (user_id) ON DELETE CASCADE
);
CREATE UNIQUE INDEX uq_payment_method_user_billing_key ON payment_method (user_id, billing_key) WHERE billing_key IS NOT NULL;

-- 15. 결제 정보 (TID 인덱스 추가)
CREATE TABLE payment (
  payment_id BIGSERIAL PRIMARY KEY,
  cart_session_id BIGINT UNIQUE,
  user_id BIGINT NOT NULL,
  method_id BIGINT,
  pg_provider pg_provider_type NOT NULL,  
  pg_tid VARCHAR(255) UNIQUE,                    
  status payment_status NOT NULL DEFAULT 'PENDING',
  total_amount INTEGER NOT NULL,
  approved_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT fk_payment_session FOREIGN KEY (cart_session_id) REFERENCES cart_session (cart_session_id),
  CONSTRAINT fk_payment_user FOREIGN KEY (user_id) REFERENCES app_user (user_id),
  CONSTRAINT fk_payment_method FOREIGN KEY (method_id) REFERENCES payment_method (method_id)
);
CREATE INDEX idx_payment_pg_tid ON payment (pg_tid);

-- 16. 가계부 (메모 필드 추가)
CREATE TABLE ledger_entry (
  ledger_entry_id BIGSERIAL PRIMARY KEY,
  user_id BIGINT NOT NULL,
  payment_id BIGINT,
  spend_date DATE NOT NULL,
  category ledger_category NOT NULL DEFAULT 'ETC',
  amount INTEGER NOT NULL,
  memo TEXT,
  created_at TIMESTAMPTZ DEFAULT now(),
  CONSTRAINT fk_ledger_user FOREIGN KEY (user_id) REFERENCES app_user (user_id) ON DELETE CASCADE,
  CONSTRAINT fk_ledger_payment FOREIGN KEY (payment_id) REFERENCES payment (payment_id) ON DELETE SET NULL
);
CREATE INDEX idx_ledger_user_date ON ledger_entry (user_id, spend_date);

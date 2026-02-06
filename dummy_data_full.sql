-- [1. 초기화] 기존 데이터 삭제
TRUNCATE TABLE recipe_ingredient, recipe, cart_item, product, product_category CASCADE;

-- ========================================================
-- 🏷️ 1. 카테고리
-- ========================================================
INSERT INTO product_category (category_id, name, zone_code) VALUES 
(1, '채소/과일', 'A-01'),
(2, '정육/계란', 'B-02'),
(3, '수산/해산물', 'C-03'),
(4, '가공/유제품', 'D-04'),
(5, '양념/오일', 'E-05'),
(11, '통조림', 'A-10'),
(12, '소스류', 'A-20'),
(13, '면류', 'A-30'),
(14, '즉석식품', 'B-10'),
(15, '잼/스프레드', 'B-20'),
(16, '음료', 'C-10')
ON CONFLICT (category_id) DO UPDATE SET name = EXCLUDED.name, zone_code = EXCLUDED.zone_code;

-- ========================================================
-- 🥫 2. 상품 데이터 (AI 모델 라벨과 일치하도록 무게/용량 복구)
-- ========================================================
INSERT INTO product (product_id, category_id, barcode, name, price, unit_weight_g, stock_quantity, image_url, product_info) VALUES
(1, 11, '8801007512259', '스팸 200g', 5200, 200, 30, 'https://image.homeplus.kr/rtd/76da78d8-47c4-4b11-9e40-71bd3b2c47e8?w=750', '{"code":"spam_200g","brand":"CJ"}'),
(2, 12, '8801045100111', '토마토 케찹 300g', 2800, 300, 40, 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcR50JARhFjh8gVNI7-oE4p7XTFGOjYaF9yyL1v8shCbC-UreP7cesfWwmudaV-w--ZOuqW9PyvMeLj2WyjWSh6GR2deDLccnzBU5uA5aFk&s=10', '{"code":"tomato_ketchup_300g"}'),
(3, 13, '8801955025443', '스파게티면 500g', 3200, 500, 25, 'https://sitem.ssgcdn.com/41/54/93/item/1000544935441_i1_750.jpg', '{"code":"spaghetti_noodle_500g"}'),
(4, 11, '8801047111719', '살코기참치 90g', 2200, 90, 18, 'https://img.danawa.com/prod_img/500000/867/125/img/15125867_1.jpg?_v=20230802085619', '{"code":"tuna_lean_90g"}'),
(5, 14, '8801045290317', '3분카레 약간매운맛', 3500, 200, 20, 'https://cdn.daisomall.co.kr/file/PD/20250829/VJMu95jlQLMNkNaxabv9104529031_00_00VJMu95jlQLMNkNaxabv9.jpg/dims/resize/750/optimize', '{"code":"curry_3min_mildhot_200g","spicy":"mild"}'),
(6, 15, '8801214507475', '딸기잼 570g', 4800, 570, 15, 'https://m.organic-story.com/web/product/big/201901/d76c22fc86ea008266e16cc58b1d2b5e.jpg', '{"code":"strawberry_jam_570g"}'),
(7, 13, '8801043014809', '신라면', 950, 120, 100, 'https://i.namu.wiki/i/6QZPq7Jw-DfbTtWNA0LS9NzFYQlnskRzO_bCykNhUkYR_O1hik2sCOX-UXATBB_QPAwP_3WkqPs6YQ0qZ6gmmA.webp', '{"code":"shin_ramen","spicy":"hot"}'),
(8, 16, '8801000000008', '펩시 제로슈거 라임', 2100, 500, 50, 'https://lottemartzetta.com/images-v3/932dcbc7-fca8-4d43-bcde-f73d1ce3cc7d/481db501-e061-4521-af56-01bb572719f0/500x500.jpg', '{"code":"pepsi_zero_lime_500ml","sugar":"zero"}'),
(9, 16, '8801069070814', '서울우유 1L', 2950, 1000, 50, 'https://sitem.ssgcdn.com/04/96/58/item/1000010589604_i1_750.jpg', '{"brand":"서울우유"}'),
(10, 2, '8801234567890', '신선 특란 10구', 4500, 600, 30, 'https://img-cf.kurly.com/shop/data/goods/1586241551603l0.jpg', '{"brand":"풀무원"}')
ON CONFLICT (product_id) DO UPDATE SET 
    name = EXCLUDED.name, price = EXCLUDED.price, barcode = EXCLUDED.barcode, image_url = EXCLUDED.image_url;

INSERT INTO product (product_id, category_id, name, price, unit_weight_g, barcode, image_url) VALUES 
(100, 1, '햇 양파', 3500, 1000, '8801000001001', 'https://oasisprodproduct.edge.naverncp.com/5720/detail/1_ef19b10e-29a8-4e6e-bb3a-320ca54d9780.jpg'),
(101, 1, '대파 (한단)', 2800, 400, '8801000001002', 'https://sitem.ssgcdn.com/66/56/92/item/1000270925666_i1_750.jpg'),
(102, 1, '다진 마늘', 4500, 200, '8801000001003', 'https://static.megamart.com/product/image/1240/12408481/12408481_1_960.jpg'),
(103, 1, '청양고추', 1500, 100, '8801000001004', 'https://i.namu.wiki/i/dxUSR6KFuitN07Fgk0RpRd10qq_kxtmvwrOi_d30zUfxGIIdoe48dE0c4S_SzRSVju89AiTwpZsZ6-Du3RmUNQ.webp'),
(104, 1, '애호박', 1200, 300, '8801000001005', 'https://i.namu.wiki/i/UPAZ9-SXrFhXnAMKiRep2T6Whk2dsI0QpPdEQY3u7vezsNOCTEmaQ7_yPdnwBBDL34RYtQrLPVnklgmDfPBAoQ.webp'),
(105, 1, '감자 (흙감자)', 4000, 800, '8801000001006', 'https://m.health.chosun.com/site/data/img_dir/2023/06/27/2023062702164_0.jpg'),
(106, 1, '당근', 2000, 300, '8801000001007', 'https://i.namu.wiki/i/aD0cdxkIOd7Ov4vsrdamC04cSBaqI3KLwSI8PsYoEkdkmzLOM-Ke1pu5A5cuz8UbCXLVht2JVk1l44VFCx2d2g.webp'),
(108, 1, '양송이 버섯', 3500, 150, '8801000001009', 'https://sitem.ssgcdn.com/26/51/95/item/1000018955126_i1_750.jpg'),
(110, 2, '베이컨 120g', 4900, 120, '8801000002002', 'https://sitem.ssgcdn.com/79/53/33/item/1000010335379_i1_750.jpg'),
(111, 12, '폰타나 크림 소스', 5500, 430, '8801000012001', 'https://sitem.ssgcdn.com/39/37/87/item/1000010873739_i1_750.jpg'),
(112, 5, '무염 버터 200g', 8500, 200, '8801000005002', 'https://sitem.ssgcdn.com/01/01/10/item/0000008100101_i1_750.jpg'),
(113, 14, '햇반 210g', 1500, 210, '8801007201207', 'https://sitem.ssgcdn.com/04/30/01/item/1000011013004_i1_750.jpg'),
(114, 1, '슬라이스 치즈 10매', 4200, 200, '8801000001010', 'https://sitem.ssgcdn.com/76/01/08/item/1000010080176_i1_750.jpg'),
(115, 11, '유동 골뱅이 400g', 9900, 400, '8801000011002', 'https://sitem.ssgcdn.com/91/94/86/item/1000010869491_i1_750.jpg'),
(200, 2, '한돈 생삼겹살', 15900, 600, '8802000002001', 'https://oasisprodproduct.edge.naverncp.com/101939/detail/0_c43f2071-7994-4b16-87fc-aae0712174bc.jpg'),
(300, 4, '찌개용 두부', 1500, 300, '8803000003001', 'https://img.cjthemarket.com/images/file/product/012/20240201085335051.jpg?SF=webp&RS=550'),
(301, 4, '종가집 맛김치', 8900, 1000, '8803000003002', 'https://sitem.ssgcdn.com/41/30/36/item/0000008363041_i1_750.jpg'),
(303, 3, '부산 사각어묵', 3000, 250, '8803000003004', 'https://sitem.ssgcdn.com/99/93/86/item/1000020869399_i1_750.jpg'),
(400, 5, '태양초 고추장', 7500, 500, '8804000004001', 'https://www.costco.co.kr/medias/sys_master/images/h05/h05/243487987662878.jpg'),
(401, 5, '재래식 된장', 6900, 500, '8804000004002', 'https://www.chungjungone.com/wp-content/uploads/contents/prdtInfoMng/prdt_20161228051729000.jpg'),
(402, 5, '진간장', 5000, 900, '8804000004003', 'https://www.chungjungone.com/wp-content/uploads/contents/prdtInfoMng/prdt_20200720_1022158.jpg'),
(403, 5, '참기름', 8000, 300, '8804000004004', 'https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRMwOU9iOK299BbuXpbPIqN1Dq0cFC1wSPUMw&s'),
(404, 5, '설탕', 3000, 1000, '8804000004005', 'https://img.danawa.com/prod_img/500000/641/698/img/1698641_1.jpg?_v=20251106171807&shrink=360:360'),
(500, 4, '토스트용 식빵', 3200, 500, '8805000005001', 'https://sitem.ssgcdn.com/90/98/57/item/1000610579890_i1_750.jpg')
ON CONFLICT (product_id) DO UPDATE SET 
    name = EXCLUDED.name, price = EXCLUDED.price, barcode = EXCLUDED.barcode, image_url = EXCLUDED.image_url;

-- ========================================================
-- 🍳 3. 레시피
-- ========================================================
INSERT INTO recipe (recipe_id, title, description, instructions, image_url) VALUES 
(1, '돼지고기 김치찌개', '한국인의 소울푸드! 칼칼하고 깊은 맛의 김치찌개.', '설명 생략...', 'https://static.wtable.co.kr/image/production/service/recipe/291/a2421dff-e56c-40bd-8b40-06a91fc000a9.jpg?size=1050x590'),
(2, '차돌 된장찌개', '구수함의 끝판왕 된장찌개.', '설명 생략...', 'https://static.wtable.co.kr/image/production/service/recipe/788/a797dc08-cb1e-49f4-83c5-6a34e3a6c47e.jpg?size=800x800'),
(10, '의정부식 부대찌개', '스팸과 라면사리의 환상 조합! 집에서 즐기는 진한 부대찌개입니다.', '1. 냄비에 김치, 스팸, 소시지, 두부를 둘러 담습니다.\n2. 양념장(고추장, 마늘, 간장)을 얹고 물을 붓습니다.\n3. 끓어오르면 라면사리(신라면)를 넣습니다.\n4. 대파를 듬뿍 넣고 면이 익을 때까지 끓이면 완성!', 'https://semie.cooking/image/contents/recipe/ee/hy/xdlvlsdq/IRD/131722701nzmp.jpg'),
(11, '3분 컷 참치 김치찌개', '살코기 참치의 담백함이 국물에 쏙! 초간단 밥도둑.', '1. 냄비에 참기름을 두르고 김치를 볶습니다.\n2. 물을 붓고 끓으면 참치 기름까지 함께 넣습니다.\n3. 양파와 대파를 넣고 푹 끓여냅니다.', 'https://m.ndns.shop/web/product/big/202401/81dac6e1b697a3349bee3f81e1149b3d.jpg'),
(12, '추억의 나폴리탄 스파게티', '케찹으로 만드는 달콤새콤한 맛. 아이들이 정말 좋아해요.', '1. 끓는 물에 스파게티 면을 삶습니다.\n2. 팬에 기름을 두르고 편마늘, 양파, 소세지를 볶습니다.\n3. 삶은 면과 케찹 4큰술을 넣고 볶습니다.\n4. 면수를 약간 넣어 농도를 맞추면 완성!', 'https://static.wtable.co.kr/image/production/service/recipe/2590/81ba7beb-a8f5-4acf-9062-62c0dfc480fd.jpg?size=800x800'),
(13, '스팸 감자 고추장 볶음', '짭짤한 스팸과 포슬한 감자를 고추장 양념에 볶아낸 집밥 반찬.', '1. 감자와 양파를 먹기 좋은 크기로 썰어줍니다.\n2. 팬에 스팸을 먼저 볶아 기름을 냅니다.\n3. 감자와 양파를 넣고 함께 볶습니다.\n4. 고추장과 설탕을 넣고 약불에서 볶아 완성합니다.', 'https://recipe1.ezmember.co.kr/cache/recipe/2024/05/01/62b94b6a67c87cf76b544ac07b3a1b131.jpg'),
(14, '참치 두부 된장찌개', '담백한 참치와 구수한 된장이 어우러진 간단 찌개 요리.', '1. 냄비에 물을 붓고 된장을 풀어 끓입니다.\n2. 양파와 애호박을 넣고 끓입니다.\n3. 참치와 두부를 넣고 한소끔 더 끓이면 완성입니다.', 'https://mblogthumb-phinf.pstatic.net/MjAyNjAxMjZfNzMg/MDAxNzY5MzkxNDI2MDEw.ggCxeMd-S_QLX9dkFdlToENKYKXhEPylOiitgXbXOp4g.K86ZAdj8BH5w-NONTk-2BnRwz1HifSwLDI7x8LcNjYwg.JPEG/012DDEE_JA1_221.jpg?type=w800'),
(15, '딸기잼 토스트', '고소한 빵에 달콤한 딸기잼을 발라 즐기는 초간단 간식.', '1. 식빵을 토스터나 팬에 노릇하게 구워줍니다.\n2. 구운 빵 위에 딸기잼을 넉넉히 발라줍니다.\n3. 취향에 따라 버터를 함께 곁들여도 좋습니다.', 'https://mblogthumb-phinf.pstatic.net/MjAyMzA2MjdfNjYg/MDAxNjg3ODMzNjk1MzQ3.16Xr5HbAZyROIMVABctp-n736Z-cd_3pBsd3sD8BtYYg.LyrMWiWf544EcStWoRwmJMIWM08XWRCrfVLGwmDEmjUg.JPEG.youth121/SE-2aaf1b1f-91f7-4c44-adb7-51d6e63b7ece.jpg?type=w800'),
(16, '베이컨 크림 파스타', '집에서 즐기는 레스토랑 맛! 고소한 크림과 짭짤한 베이컨의 조화.', '1. 스파게티면을 삶습니다.\n2. 팬에 베이컨과 양송이를 볶습니다.\n3. 크림 소스를 붓고 끓이다가 면을 넣고 버무립니다.', 'https://static.wtable.co.kr/image/production/service/recipe/1053/6122a27d-944e-4861-8208-8e3d81b2c47e.jpg?size=800x800'),
(17, '스팸 계란 볶음밥', '반찬 없을 때 최고! 스팸과 계란만 있으면 끝.', '1. 스팸을 볶고 계란을 스크램블 합니다.\n2. 밥(햇반)을 넣고 센 불에서 볶아 완성합니다.', 'https://recipe1.ezmember.co.kr/cache/recipe/2016/11/04/e76e5d033732e73715d3885d9b62f7a51.jpg'),
(21, '촉촉한 프렌치 토스트', '부드럽고 달콤한 아침 식사.', '1. 계란과 우유를 섞어 식빵을 적십니다.\n2. 팬에 버터를 녹이고 노릇하게 굽습니다.', 'https://static.wtable.co.kr/image/production/service/recipe/722/02693575-b65a-4956-9d33-912b591b98a3.jpg?size=800x800'),
(22, '참치 딸기잼 샌드위치', '단짠단짠의 끝판왕 샌드위치.', '1. 참치를 마요네즈와 섞습니다.\n2. 식빵에 딸기잼을 바르고 참치와 치즈를 얹습니다.', 'https://recipe1.ezmember.co.kr/cache/recipe/2015/05/20/0034d612e3e9f45d58d97607a99f7f451.jpg')
ON CONFLICT (recipe_id) DO UPDATE SET 
    title = EXCLUDED.title, description = EXCLUDED.description, instructions = EXCLUDED.instructions, image_url = EXCLUDED.image_url;

-- ========================================================
-- 🔗 4. 레시피-재료 연결 (중복 제거된 최종 버전)
-- ========================================================
DELETE FROM recipe_ingredient;

INSERT INTO recipe_ingredient (recipe_id, product_id, quantity_info, importance_score) VALUES 
(1, 200, '300g', 5), (1, 301, '1/4포기', 5), (1, 300, '반 모', 3), (1, 101, '1대', 3),
(2, 401, '2큰술', 5), (2, 300, '반 모', 3), (2, 104, '1/3개', 3), (2, 105, '1개', 3),
(10, 1, '1캔', 5), (10, 7, '1개', 5), (10, 301, '반포기', 5), (10, 300, '한모', 3), (10, 101, '2대', 3),
(11, 4, '1캔', 5), (11, 301, '반포기', 5), (11, 100, '반개', 3), (11, 103, '1개', 1),
(12, 3, '1인분', 5), (12, 2, '4큰술', 5), (12, 100, '반개', 3), (12, 102, '1큰술', 1),
(13, 1, '1캔', 5), (13, 105, '1개', 4), (13, 100, '반개', 3), (13, 400, '1큰술', 3),
(14, 4, '1캔', 5), (14, 300, '한모', 4), (14, 401, '2큰술', 5), (14, 100, '반개', 3),
(15, 6, '적당량', 5), (15, 500, '2장', 5), 
(16, 3, '1인분', 5), (16, 110, '2줄', 5), (16, 111, '200ml', 5), (16, 108, '3개', 3),
(17, 1, '1/4캔', 5), (17, 10, '2알', 5), (17, 113, '1공기', 5), (17, 101, '약간', 2),
(21, 500, '2장', 5), (21, 10, '1알', 5), (21, 9, '50ml', 4), (21, 112, '1조각', 3),
(22, 4, '1캔', 5), (22, 6, '1큰술', 5), (22, 500, '2장', 5), (22, 114, '1장', 3)
ON CONFLICT (recipe_id, product_id) DO NOTHING;

"""Development/test seeder. Seeding is an explicit command (`make seed`), never part of service startup. Rows are inserted idempotently so re-running the seeder cannot duplicate fixtures: roles by `role_name`, banners by `name` (the banner seeder is not idempotent — see the in Planning.md), merchants by owner `user_id` (and only when that user exists, since the merchant seeder is also not idempotent)."""

from __future__ import annotations

import asyncio
from datetime import date, datetime, time

from sqlalchemy import text

from pkg.config.settings import get_settings
from pkg.database.database import Database
from pkg.logger.logger import get_logger

SERVICE_NAME = "seeder"

_INSERT_ROLE = """
INSERT INTO roles (role_name, created_at, updated_at, deleted_at)
VALUES (:role_name, :created_at, :created_at, :deleted_at)
ON CONFLICT (role_name) DO NOTHING
"""

# Banners have no unique constraint, so idempotency uses a guard on `name`.
# Two distinct bind names are required: asyncpg infers a parameter's type
# from its single use site, and reusing one name for both the SELECT list
# (text) and the varchar comparison raises AmbiguousParameterError.
# `created_at`/`updated_at` are left to the column defaults, exactly as the
# seeder does.
_INSERT_BANNER = """
INSERT INTO banners (name, start_date, end_date, start_time, end_time, is_active)
SELECT :name, :start_date, :end_date, :start_time, :end_time, :is_active
WHERE NOT EXISTS (SELECT 1 FROM banners WHERE name = :existing_name)
"""

# Categories have a UNIQUE `slug_category`, so `ON CONFLICT DO NOTHING`
# gives the same idempotency without a second bind name. the category
_INSERT_CATEGORY = """
INSERT INTO categories (name, description, slug_category, image_category)
VALUES (:name, :description, :slug_category, :image_category)
ON CONFLICT (slug_category) DO NOTHING
"""

# Sliders have no unique constraint either, so idempotency reuses the banner
# guard pattern (`WHERE NOT EXISTS` + a distinct bind name for the lookup) to
_INSERT_SLIDER = """
INSERT INTO sliders (name, image)
SELECT :name, :image
WHERE NOT EXISTS (SELECT 1 FROM sliders WHERE name = :existing_name)
"""

# Merchants reference a user (`merchants.user_id`), so the guard only inserts
# when the owner user exists (keeps the FK satisfied) *and* that user has no
# merchant yet (idempotency). the `merchantSeeder.Seed` is a plain INSERT
# `created_at`/`updated_at` are
# has no user seeder yet
# so on a fresh DB this is a no-op until users 1..8 exist (see Planning.md).
_INSERT_MERCHANT = """
INSERT INTO merchants (
    user_id, name, description, address, contact_email, contact_phone, status
)
SELECT :user_id, :name, :description, :address, :contact_email, :contact_phone, :status
WHERE EXISTS (SELECT 1 FROM users WHERE user_id = :user_id)
  AND NOT EXISTS (SELECT 1 FROM merchants WHERE user_id = :user_id)
"""

# Merchant details reference a merchant (`merchant_details.merchant_id`), so the
# guard only inserts when the merchant exists (keeps the FK satisfied) *and*
# that merchant has no detail yet (one detail per merchant → idempotency). The
# `merchantDetailSeeder.Seed` is a plain INSERT and is NOT idempotent; the
# port makes it so. `created_at`/`updated_at` are left to the column defaults,
_INSERT_MERCHANT_DETAIL = """
INSERT INTO merchant_details (
    merchant_id, display_name, cover_image_url, logo_url, short_description, website_url
)
SELECT
    :merchant_id, :display_name, :cover_image_url, :logo_url, :short_description, :website_url
WHERE EXISTS (SELECT 1 FROM merchants WHERE merchant_id = :merchant_id)
  AND NOT EXISTS (SELECT 1 FROM merchant_details WHERE merchant_id = :merchant_id)
"""

# Social links have no unique constraint, so idempotency guards on
# (merchant_detail_id, platform). Two distinct bind names are required for the
# platform: asyncpg infers a parameter's type from its single use site, and
# reusing one name for both the SELECT list (text) and the varchar comparison
# raises AmbiguousParameterError (same trap as the banner seeder, see #45).
_INSERT_MERCHANT_SOCIAL_LINK = """
INSERT INTO merchant_social_media_links (merchant_detail_id, platform, url)
SELECT :merchant_detail_id, :platform, :url
WHERE NOT EXISTS (
    SELECT 1 FROM merchant_social_media_links
    WHERE merchant_detail_id = :merchant_detail_id AND platform = :existing_platform
)
"""

# Awards reference a merchant (`merchant_certifications_and_awards.merchant_id`),
# so the guard only inserts when the merchant exists (keeps the FK satisfied)
# *and* that merchant has no award with the same title yet (idempotency).
# makes it so. Two distinct bind names for `title` avoid asyncpg's
# AmbiguousParameterError (same trap as the banner seeder, see #45).
_INSERT_MERCHANT_AWARD = """
INSERT INTO merchant_certifications_and_awards (
    merchant_id, title, description, issued_by,
    issue_date, expiry_date, certificate_url
)
SELECT
    :merchant_id, :title, :description, :issued_by,
    :issue_date, :expiry_date, :certificate_url
WHERE EXISTS (SELECT 1 FROM merchants WHERE merchant_id = :merchant_id)
  AND NOT EXISTS (
    SELECT 1 FROM merchant_certifications_and_awards
    WHERE merchant_id = :merchant_id AND title = :existing_title
  )
"""

# Business information references a merchant
# (`merchant_business_information.merchant_id`), so the guard only inserts when
# the merchant exists (keeps the FK satisfied) *and* that merchant has no
# business info yet (one per merchant → idempotency).
# `merchantBusinessSeeder.Seed` is a plain INSERT and is NOT idempotent; the
# port makes it so. `:merchant_id` is reused for both the EXISTS and NOT EXISTS
# comparisons; it is an integer everywhere, so asyncpg infers one type and does
# not raise AmbiguousParameterError.
_INSERT_MERCHANT_BUSINESS = """
INSERT INTO merchant_business_information (
    merchant_id, business_type, tax_id,
    established_year, number_of_employees, website_url
)
SELECT
    :merchant_id, :business_type, :tax_id,
    :established_year, :number_of_employees, :website_url
WHERE EXISTS (SELECT 1 FROM merchants WHERE merchant_id = :merchant_id)
  AND NOT EXISTS (
    SELECT 1 FROM merchant_business_information WHERE merchant_id = :merchant_id
  )
"""

# Policies reference a merchant (`merchant_policies.merchant_id`), so the guard
# only inserts when the merchant exists (keeps the FK satisfied) *and* that
# merchant has no policy with the same title yet. A merchant can legitimately
# own several policies, so idempotency keys on (merchant_id, title).
# makes it so. `:merchant_id` is an integer everywhere, so asyncpg infers one
# type and does not raise AmbiguousParameterError; the title comparison uses a
# distinct `:existing_title` binding (like the award seeder) because `:title` is
# both inserted and compared.
_INSERT_MERCHANT_POLICY = """
INSERT INTO merchant_policies (
    merchant_id, policy_type, title, description
)
SELECT
    :merchant_id, :policy_type, :title, :description
WHERE EXISTS (SELECT 1 FROM merchants WHERE merchant_id = :merchant_id)
  AND NOT EXISTS (
    SELECT 1 FROM merchant_policies
    WHERE merchant_id = :merchant_id AND title = :existing_title
  )
"""

# Products reference both a merchant and a category
# (`products.merchant_id`/`category_id`), so the guard only inserts when both
# parents exist (keeps the FKs satisfied) *and* that merchant has no product
# with the same name yet (idempotency). the `productSeeder.Seed` is a plain
# `:name` is both inserted
# and compared, so the lookup uses a distinct `:existing_name` binding (the
#
# NORMALISATION: the seeder passes
# `Rating: toFloat64Ptr(4.5)` etc. to `CreateProductParams`, but the generated
# `CreateProduct` query never binds `rating`, so seeded products all fall to
# the DB default `0.0`.
# normalized `create`/`update` repository behaviour.
_INSERT_PRODUCT = """
INSERT INTO products (
    merchant_id, category_id, name, description, price, count_in_stock,
    brand, weight, rating, slug_product, image_product
)
SELECT
    :merchant_id, :category_id, :name, :description, :price, :count_in_stock,
    :brand, :weight, :rating, :slug_product, :image_product
WHERE EXISTS (SELECT 1 FROM merchants WHERE merchant_id = :merchant_id)
  AND EXISTS (SELECT 1 FROM categories WHERE category_id = :category_id)
  AND NOT EXISTS (
    SELECT 1 FROM products
    WHERE merchant_id = :merchant_id AND name = :existing_name
  )
"""

# Reviews reference a user (`reviews.user_id`) and a product
# (`reviews.product_id`, ON DELETE CASCADE), so the guard only inserts when both
# parents exist (keeps the FKs satisfied) *and* that user has no review of the
# same product with the same comment yet (idempotency).
# so. `:user_id`/`:product_id`/`:comment` are both inserted and compared, so the
# lookups use distinct `:existing_*` bindings (the asyncpg AmbiguousParameterError
# insert; when the row already exists the SELECT after it recovers the id.
_INSERT_REVIEW = """
INSERT INTO reviews (user_id, product_id, name, comment, rating)
SELECT :user_id, :product_id, :name, :comment, :rating
WHERE EXISTS (SELECT 1 FROM users WHERE user_id = :existing_user_id)
  AND EXISTS (SELECT 1 FROM products WHERE product_id = :existing_product_id)
  AND NOT EXISTS (
    SELECT 1 FROM reviews
    WHERE user_id = :existing_user_id
      AND product_id = :existing_product_id
      AND comment = :existing_comment
  )
RETURNING review_id
"""

# Every seeded review gets exactly one attachment, matching the
# `reviewSeeder.Seed` (which creates a review_detail right after each review).
# The guard keeps one detail per review (idempotency); `:review_id` is both
# inserted and compared, so the lookup uses a distinct `:existing_review_id`
_INSERT_REVIEW_DETAIL = """
INSERT INTO review_details (review_id, type, url, caption)
SELECT :review_id, :type, :url, :caption
WHERE NOT EXISTS (
    SELECT 1 FROM review_details WHERE review_id = :existing_review_id
)
"""

# Orders reference a user (`orders.user_id`) and a merchant
# (`orders.merchant_id`), so the guard only inserts when both parents exist
# (keeps the FKs satisfied) *and* no order already matches
# (user_id, merchant_id, total_price) (idempotency). the `orderSeeder.Seed`
# `:user_id`/`:merchant_id`/`:total_price` are both inserted and compared, so
# the lookups use distinct `:existing_*` bindings (the asyncpg
# hands the id to the order-item insert; when the row already exists the SELECT
# after it recovers the id.
_INSERT_ORDER = """
INSERT INTO orders (user_id, merchant_id, total_price)
SELECT :user_id, :merchant_id, :total_price
WHERE EXISTS (SELECT 1 FROM users WHERE user_id = :existing_user_id)
  AND EXISTS (SELECT 1 FROM merchants WHERE merchant_id = :existing_merchant_id)
  AND NOT EXISTS (
    SELECT 1 FROM orders
    WHERE user_id = :existing_user_id
      AND merchant_id = :existing_merchant_id
      AND total_price = :existing_total_price
  )
RETURNING order_id
"""

# Every seeded order gets exactly one item, matching the `orderSeeder.Seed`
# (which creates an order item right after each order). The item references its
# order (`order_items.order_id`) and a product (`order_items.product_id`), so
# the guard only inserts when both parents exist (keeps the FKs satisfied) and
# that order has no item for the product yet (idempotency). `:order_id` /
# `:product_id` are both inserted and compared, so the lookups use distinct
_INSERT_ORDER_ITEM = """
INSERT INTO order_items (order_id, product_id, quantity, price)
SELECT :order_id, :product_id, :quantity, :price
WHERE EXISTS (SELECT 1 FROM orders WHERE order_id = :existing_order_id)
  AND EXISTS (SELECT 1 FROM products WHERE product_id = :existing_product_id)
  AND NOT EXISTS (
    SELECT 1 FROM order_items
    WHERE order_id = :existing_order_id AND product_id = :existing_product_id
  )
"""


# One transaction per seeded order (`transactionSeeder.Seed`). The insert
# guards on the order parent and on `order_id` not having a transaction yet
# (idempotency where re-inserts duplicates). `:order_id` is both inserted
# and compared, so the lookup uses a distinct `:existing_order_id` binding
_INSERT_TRANSACTION = """
INSERT INTO transactions (order_id, merchant_id, payment_method, amount, payment_status)
SELECT :order_id, :merchant_id, :payment_method, :amount, :payment_status
WHERE EXISTS (SELECT 1 FROM orders WHERE order_id = :existing_order_id)
  AND NOT EXISTS (
    SELECT 1 FROM transactions WHERE order_id = :existing_order_id
  )
RETURNING transaction_id
"""

# (name, image) — verbatim from the `sliderSeeder.Seed` fixture set.
BASE_SLIDERS: list[tuple[str, str]] = [
    ("Promo Akhir Tahun", "slider1.jpg"),
    ("Diskon Elektronik", "slider2.jpg"),
    ("Flash Sale Mingguan", "slider3.jpg"),
    ("Produk Terbaru", "slider4.jpg"),
    ("Promo Kesehatan", "slider5.jpg"),
    ("Belanja Hemat", "slider6.jpg"),
    ("Gaming Gear Diskon", "slider7.jpg"),
    ("Gratis Ongkir", "slider8.jpg"),
    ("Ramadhan Sale", "slider9.jpg"),
    ("Perlengkapan Bayi", "slider10.jpg"),
]

# (user_id, name, description, address, contact_email, contact_phone, status)
# — verbatim from the `merchantSeeder.Seed` fixture set. All eight are
# `status = "active"` and own distinct users 1..8.
BASE_MERCHANTS: list[tuple[int, str, str, str, str, str, str]] = [
    (
        1,
        "Elektronik Store",
        "Toko elektronik terpercaya dengan berbagai produk gadget dan aksesoris.",
        "Jl. Teknologi No.1, Jakarta",
        "support@elektronikstore.com",
        "081234567890",
        "active",
    ),
    (
        2,
        "Kecantikan Sehat",
        "Produk skincare dan kesehatan pilihan.",
        "Jl. Kesehatan No.5, Bandung",
        "cs@kecantikansehat.com",
        "082345678901",
        "active",
    ),
    (
        3,
        "Rumah Indah",
        "Peralatan rumah tangga berkualitas dan estetik.",
        "Jl. Rumah No.12, Surabaya",
        "info@rumahindah.com",
        "083456789012",
        "active",
    ),
    (
        4,
        "Mom & Baby Care",
        "Semua kebutuhan ibu dan bayi ada di sini.",
        "Jl. Keluarga No.7, Depok",
        "support@momandbaby.com",
        "084567890123",
        "active",
    ),
    (
        5,
        "Sport Zone",
        "Perlengkapan olahraga dan outdoor terlengkap.",
        "Jl. Atletik No.3, Yogyakarta",
        "halo@sportzone.com",
        "085678901234",
        "active",
    ),
    (
        6,
        "Fresh Mart",
        "Toko makanan dan minuman segar dan kemasan.",
        "Jl. Pasar No.10, Semarang",
        "fresh@mart.com",
        "086789012345",
        "active",
    ),
    (
        7,
        "Gamer Heaven",
        "Game, console, dan aksesori lengkap untuk gamers.",
        "Jl. Game No.8, Bekasi",
        "gamer@heaven.com",
        "087890123456",
        "active",
    ),
    (
        8,
        "AutoParts Store",
        "Toko perlengkapan otomotif terpercaya.",
        "Jl. Otomotif No.6, Medan",
        "service@autoparts.com",
        "088901234567",
        "active",
    ),
]

# (merchant_id, display_name, cover_image_url, logo_url, short_description,
# website_url) — verbatim from the `merchantDetailSeeder.Seed` fixture set.
# One detail per merchant 1..8; each detail then gets three social links
# (Facebook/Instagram/Twitter) whose URLs embed the merchant detail id.
BASE_MERCHANT_DETAILS: list[tuple[int, str, str, str, str, str]] = [
    (
        1,
        "Techno Store",
        "cover/techno.jpg",
        "logo/techno.png",
        "Pusat elektronik terpercaya sejak 2010",
        "https://technostore.com",
    ),
    (
        2,
        "Glow Beauty",
        "cover/beauty.jpg",
        "logo/beauty.png",
        "Produk kecantikan alami dan aman",
        "https://glowbeauty.id",
    ),
    (
        3,
        "Dapur Sehat",
        "cover/dapur.jpg",
        "logo/dapur.png",
        "Makanan sehat dan organik",
        "https://dapsehat.id",
    ),
    (
        4,
        "Gadget Hub",
        "cover/gadget.jpg",
        "logo/gadget.png",
        "Semua tentang gadget terbaru",
        "https://gadgethub.com",
    ),
    (
        5,
        "Bayi Ceria",
        "cover/bayi.jpg",
        "logo/bayi.png",
        "Produk terbaik untuk si kecil",
        "https://bayiceria.id",
    ),
    (
        6,
        "Toko Sehat",
        "cover/sehat.jpg",
        "logo/sehat.png",
        "Peralatan olahraga lengkap",
        "https://tokosehat.id",
    ),
    (
        7,
        "Game World",
        "cover/game.jpg",
        "logo/game.png",
        "Konsol dan game terbaik",
        "https://gameworld.com",
    ),
    (
        8,
        "Otomotif Mart",
        "cover/otomotif.jpg",
        "logo/otomotif.png",
        "Aksesori kendaraan terpercaya",
        "https://otomotifmart.com",
    ),
]

# (merchant_id, title, description, issued_by, issue_date, expiry_date,
# certificate_url) — verbatim from the `merchantAwardSeeder.Seed` fixture set.
# One award per merchant 1..8. the seeder builds expiry dates with
# `toDate(time.Time{})` for merchants 2/4/6/8, which yields the *zero* date
BASE_MERCHANT_AWARDS: list[tuple[int, str, str, str, str, str, str]] = [
    (
        1,
        "ISO 9001 Certified",
        "Manajemen mutu bersertifikat",
        "ISO Organization",
        "2020-01-15",
        "2025-01-15",
        "https://example.com/iso9001-cert.pdf",
    ),
    (
        2,
        "Top UMKM 2023",
        "Penghargaan untuk UMKM terbaik tahun 2023",
        "Kementerian Koperasi",
        "2023-07-01",
        "0001-01-01",
        "https://example.com/umkm-award-2023.pdf",
    ),
    (
        3,
        "Halal Certified",
        "Sertifikasi halal dari MUI",
        "Majelis Ulama Indonesia",
        "2021-03-12",
        "2024-03-12",
        "https://example.com/halal-cert.pdf",
    ),
    (
        4,
        "Best Food Product 2022",
        "Penghargaan untuk produk makanan terbaik tahun 2022",
        "Asosiasi Kuliner Indonesia",
        "2022-11-05",
        "0001-01-01",
        "https://example.com/best-food-2022.pdf",
    ),
    (
        5,
        "Eco-Friendly Business",
        "Sertifikasi bisnis ramah lingkungan",
        "Green Business Council",
        "2023-04-22",
        "2026-04-22",
        "https://example.com/eco-friendly-cert.pdf",
    ),
    (
        6,
        "Top Seller 2023",
        "Penjual terbaik platform e-commerce tahun 2023",
        "Tokopedia",
        "2024-01-10",
        "0001-01-01",
        "https://example.com/top-seller-2023.pdf",
    ),
    (
        7,
        "BPOM Certified",
        "Sertifikasi produk dari Badan Pengawas Obat dan Makanan",
        "Badan POM RI",
        "2022-08-03",
        "2025-08-03",
        "https://example.com/bpom-cert.pdf",
    ),
    (
        8,
        "Creativepreneur Award",
        "Penghargaan untuk wirausaha kreatif",
        "Kementerian Pariwisata dan Ekonomi Kreatif",
        "2023-12-15",
        "0001-01-01",
        "https://example.com/creativepreneur-award.pdf",
    ),
]

# (merchant_id, business_type, tax_id, established_year, number_of_employees,
# website_url) — verbatim from the `merchantBusinessSeeder.Seed` fixture set.
# wraps each in `toStringPtr`/`toInt32Ptr`), so no row is stored NULL.
BASE_MERCHANT_BUSINESSES: list[tuple[int, str, str, int, int, str]] = [
    (
        1,
        "Toko Elektronik",
        "01.234.567.8-999.000",
        2010,
        15,
        "https://technostore.com",
    ),
    (
        2,
        "Produk Kecantikan",
        "02.345.678.9-888.000",
        2015,
        10,
        "https://glowbeauty.id",
    ),
    (
        3,
        "Toko Makanan Organik",
        "03.456.789.0-777.000",
        2012,
        20,
        "https://dapsehat.id",
    ),
    (
        4,
        "Retail Gadget",
        "04.567.890.1-666.000",
        2018,
        8,
        "https://gadgethub.com",
    ),
    (
        5,
        "Produk Ibu & Bayi",
        "05.678.901.2-555.000",
        2019,
        6,
        "https://bayiceria.id",
    ),
    (
        6,
        "Peralatan Olahraga",
        "06.789.012.3-444.000",
        2016,
        12,
        "https://tokosehat.id",
    ),
    (
        7,
        "Gaming Store",
        "07.890.123.4-333.000",
        2020,
        5,
        "https://gameworld.com",
    ),
    (
        8,
        "Aksesori Otomotif",
        "08.901.234.5-222.000",
        2013,
        9,
        "https://otomotifmart.com",
    ),
]

# `merchantPolicySeeder.Seed` fixture set (one policy per merchant 1..8).
BASE_MERCHANT_POLICIES: list[tuple[int, str, str, str]] = [
    (
        1,
        "Shipping",
        "Free Shipping on Orders Above $50",
        "Kami menyediakan pengiriman gratis untuk pembelian di atas $50 di seluruh wilayah Indonesia.",
    ),
    (
        2,
        "Refund",
        "30-Day Refund Policy",
        "Pengembalian dana dapat dilakukan dalam waktu 30 hari setelah "
        "pembelian dengan syarat dan ketentuan yang berlaku.",
    ),
    (
        3,
        "Return",
        "Return Within 7 Days",
        "Produk dapat dikembalikan dalam waktu 7 hari jika tidak sesuai "
        "dengan deskripsi atau rusak saat diterima.",
    ),
    (
        4,
        "Shipping",
        "Next-Day Delivery in Major Cities",
        "Pengiriman pada hari berikutnya untuk alamat yang berada di "
        "kota-kota besar seperti Jakarta, Surabaya, dan Bandung.",
    ),
    (
        5,
        "Privacy",
        "Data Privacy Policy",
        "Kami menjaga privasi data pribadi pelanggan dengan sangat "
        "hati-hati dan tidak akan membagikan informasi kepada pihak ketiga.",
    ),
    (
        6,
        "Shipping",
        "International Shipping Available",
        "Kami menawarkan pengiriman internasional ke berbagai negara di Asia, Eropa, dan Amerika.",
    ),
    (
        7,
        "Return",
        "No Returns on Sale Items",
        "Barang yang dibeli dengan harga diskon atau promo tidak dapat dikembalikan.",
    ),
    (
        8,
        "Refund",
        "Refund for Defective Products",
        "Kami memberikan pengembalian dana penuh untuk produk yang rusak atau cacat pabrik.",
    ),
]

# (merchant_id, category_id, name, description, price, count_in_stock, brand,
# `productSeeder.Seed` fixture set. One product per merchant/category pair
# (1..8). keeps the fixture rating (the query drops it — see the
BASE_PRODUCTS: list[tuple[int, int, str, str, int, int, str, int, float, str, str]] = [
    (
        1,
        1,
        "Smartphone Galaxy X",
        "Smartphone dengan performa tinggi dan kamera canggih.",
        4500000,
        20,
        "Samsung",
        300,
        4.5,
        "smartphone-galaxy-x",
        "galaxy-x.jpg",
    ),
    (
        2,
        2,
        "Facial Cleanser Glow",
        "Pembersih wajah dengan formula ringan untuk semua jenis kulit.",
        75000,
        100,
        "GlowCare",
        150,
        4.2,
        "facial-cleanser-glow",
        "cleanser.jpg",
    ),
    (
        3,
        3,
        "Blender Serbaguna",
        "Blender 3-in-1 untuk keperluan dapur sehari-hari.",
        350000,
        50,
        "Maspion",
        2000,
        4.0,
        "blender-serbaguna",
        "blender.jpg",
    ),
    (
        4,
        4,
        "Paket Popok Bayi Premium",
        "Popok bayi dengan teknologi anti bocor dan lembut di kulit.",
        120000,
        70,
        "BabySoft",
        1000,
        4.6,
        "popok-premium",
        "popok.jpg",
    ),
    (
        5,
        5,
        "Matras Yoga Premium",
        "Matras anti slip dengan ketebalan ideal untuk yoga dan fitness.",
        220000,
        40,
        "FitZone",
        700,
        4.4,
        "matras-yoga-premium",
        "matras.jpg",
    ),
    (
        6,
        6,
        "Snack Kentang Balado",
        "Cemilan kentang renyah dengan rasa balado khas.",
        18000,
        200,
        "Snacky",
        100,
        4.1,
        "kentang-balado",
        "snack.jpg",
    ),
    (
        7,
        7,
        "Controller PS5 DualSense",
        "Stik PS5 dengan fitur haptic feedback dan adaptive triggers.",
        999000,
        30,
        "Sony",
        450,
        4.8,
        "controller-ps5",
        "ps5-controller.jpg",
    ),
    (
        8,
        8,
        "Oli Motor Full Synthetic",
        "Oli mesin motor dengan perlindungan maksimal dan efisiensi tinggi.",
        95000,
        60,
        "Motul",
        1000,
        4.3,
        "oli-motor-synthetic",
        "oli.jpg",
    ),
]

# `reviewSeeder.Seed` fixture set. Each entry also gets one `review_details`
# row (type "photo", url/caption derived from the reviewer name, exactly like
# The seeder guards on the parent user/product existing, so on a fresh DB
# these are a no-op until users 1..8 and products 1..8 exist (see Planning.md).
BASE_REVIEWS: list[tuple[int, int, str, str, int]] = [
    (1, 1, "John", "Produk bagus!", 5),
    (2, 2, "Anna", "Sangat puas dengan kualitasnya.", 4),
    (3, 3, "Budi", "Cukup oke untuk harga segini.", 3),
    (4, 4, "Siti", "Pengiriman cepat dan aman.", 4),
    (5, 5, "Rina", "Tidak sesuai ekspektasi.", 2),
    (6, 6, "Agus", "Top, pasti beli lagi!", 5),
    (7, 7, "Dian", "Cocok untuk hadiah.", 4),
    (8, 8, "Made", "Kualitas standar saja.", 3),
]

# (user_id, merchant_id, total_price, product_id, quantity, price) — generated
# by the `orderSeeder.Seed` loop (`i` from 1..8): order `i` belongs to user
# `i` and merchant `i` with `total_price = 10000*i`, and carries one item for
# product `i` (`quantity = i`, `price = 10000`). the seeder is a plain INSERT
# and is NOT idempotent; both inserts (see `_INSERT_ORDER`).
# The order/user/merchant/product parents must exist, so on a fresh DB this is
# a no-op until users 1..8, merchants 1..8 and products 1..8 exist.
BASE_ORDERS: list[tuple[int, int, int, int, int, int]] = [(i, i, 10000 * i, i, i, 10000) for i in range(1, 9)]

# (order_id, merchant_id, payment_method, amount, payment_status) — verbatim
# from the `transactionSeeder.Seed` fixture set (orders/merchants 1..8).
# the seeder is a plain INSERT and is NOT idempotent (`transactions` has no
# `order_id` (each seeded order carries exactly one transaction) inside the
# parent guards.
BASE_TRANSACTIONS: list[tuple[int, int, str, int, str]] = [
    (1, 1, "credit_card", 120000, "success"),
    (2, 2, "bank_transfer", 45000, "success"),
    (3, 3, "ewallet", 78900, "success"),
    (4, 4, "cash_on_delivery", 32000, "success"),
    (5, 5, "credit_card", 99999, "failed"),
    (6, 6, "bank_transfer", 150000, "failed"),
    (7, 7, "ewallet", 51000, "failed"),
    (8, 8, "credit_card", 67500, "failed"),
]

# (role_name, created_at, deleted_at) — timestamps kept from the seeder
# so active/trashed fixtures behave identically.
BASE_ROLES: list[tuple[str, str, str | None]] = [
    ("ROLE_ADMIN", "2024-01-01 10:00:00", None),
    ("ROLE_USER", "2024-01-02 10:00:00", None),
    ("ROLE_MERCHANT", "2024-01-03 10:00:00", None),
    ("ROLE_CUSTOMER", "2024-01-04 10:00:00", None),
    ("ROLE_MODERATOR", "2024-01-05 10:00:00", None),
    ("ROLE_SUPERVISOR", "2024-01-06 10:00:00", None),
    ("ROLE_ACCOUNTANT", "2024-01-07 10:00:00", None),
    ("ROLE_SUPPORT", "2024-01-08 10:00:00", None),
    ("ROLE_DEVELOPER", "2024-01-09 10:00:00", None),
    ("ROLE_MANAGER", "2024-01-10 10:00:00", None),
    ("ROLE_GUEST", "2024-01-11 10:00:00", "2024-02-01 10:00:00"),
    ("ROLE_TESTER", "2024-01-12 10:00:00", "2024-02-02 10:00:00"),
    ("ROLE_ANALYST", "2024-01-13 10:00:00", "2024-02-03 10:00:00"),
    ("ROLE_AUDITOR", "2024-01-14 10:00:00", "2024-02-04 10:00:00"),
    ("ROLE_CONSULTANT", "2024-01-15 10:00:00", "2024-02-05 10:00:00"),
    ("ROLE_CONTRACTOR", "2024-01-16 10:00:00", "2024-02-06 10:00:00"),
    ("ROLE_INTERN", "2024-01-17 10:00:00", "2024-02-07 10:00:00"),
    ("ROLE_TRAINER", "2024-01-18 10:00:00", "2024-02-08 10:00:00"),
    ("ROLE_COORDINATOR", "2024-01-19 10:00:00", "2024-02-09 10:00:00"),
    ("ROLE_ASSISTANT", "2024-01-20 10:00:00", "2024-02-10 10:00:00"),
    # Permission roles required by the gateway RequireRoles middleware.
    ("Admin_Role_10", "2024-01-21 10:00:00", None),
    ("Admin_Admin_14", "2024-01-22 10:00:00", None),
]

# (name, start_date, end_date, start_time, end_time, is_active) — verbatim
# from the `bannerSeeder.Seed` fixture set.
BASE_BANNERS: list[tuple[str, str, str, str, str, bool]] = [
    ("Banner 1", "2023-01-01", "2023-01-31", "08:00", "16:00", True),
    ("Banner 2", "2023-02-01", "2023-02-28", "09:00", "17:00", True),
    ("Banner 3", "2023-03-01", "2023-03-31", "10:00", "18:00", False),
    ("Banner 4", "2023-04-01", "2023-04-30", "07:00", "15:00", True),
    ("Banner 5", "2023-05-01", "2023-05-31", "06:00", "14:00", False),
    ("Banner 6", "2023-06-01", "2023-06-30", "12:00", "20:00", True),
    ("Banner 7", "2023-07-01", "2023-07-31", "08:30", "16:30", True),
    ("Banner 8", "2023-08-01", "2023-08-31", "09:30", "17:30", False),
]

# `categorySeeder.Seed` fixture set. the seeder logs "seeded 10" while
# inserting 8 rows; the 8 fixtures and does not reproduce the
# wrong log line.
BASE_CATEGORIES: list[tuple[str, str, str, str]] = [
    (
        "Elektronik",
        "Produk elektronik seperti smartphone, laptop, dan aksesori elektronik lainnya.",
        "elektronik",
        "elektronik.jpg",
    ),
    (
        "Kesehatan & Kecantikan",
        "Produk perawatan tubuh, skincare, dan suplemen kesehatan.",
        "kesehatan-kecantikan",
        "kesehatan.jpg",
    ),
    (
        "Peralatan Rumah Tangga",
        "Peralatan dapur, perlengkapan rumah, dan furnitur.",
        "peralatan-rumah",
        "rumah.jpg",
    ),
    (
        "Ibu & Bayi",
        "Produk khusus untuk ibu hamil, menyusui, dan bayi.",
        "ibu-bayi",
        "ibu-bayi.jpg",
    ),
    (
        "Olahraga & Outdoor",
        "Perlengkapan olahraga, fitness, dan kegiatan luar ruangan.",
        "olahraga-outdoor",
        "olahraga.jpg",
    ),
    (
        "Makanan & Minuman",
        "Makanan ringan, minuman, bahan makanan segar dan kemasan.",
        "makanan-minuman",
        "makanan.jpg",
    ),
    (
        "Gaming & Console",
        "Konsol game, aksesori, dan game terbaru dari berbagai platform.",
        "gaming-console",
        "gaming.jpg",
    ),
    (
        "Perlengkapan Otomotif",
        "Aksesori mobil dan motor, oli, serta sparepart kendaraan.",
        "otomotif",
        "otomotif.jpg",
    ),
]


def _parse(value: str | None) -> datetime | None:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S") if value else None


async def seed_roles(db: Database) -> int:
    inserted = 0
    async with db.transaction() as conn:
        for role_name, created_at, deleted_at in BASE_ROLES:
            await conn.execute(
                text(_INSERT_ROLE),
                {
                    "role_name": role_name,
                    "created_at": _parse(created_at),
                    "deleted_at": _parse(deleted_at),
                },
            )
            inserted += 1
    return inserted


async def seed_banners(db: Database) -> int:
    inserted = 0
    async with db.transaction() as conn:
        for name, start_date, end_date, start_time, end_time, is_active in BASE_BANNERS:
            await conn.execute(
                text(_INSERT_BANNER),
                {
                    "name": name,
                    "existing_name": name,
                    "start_date": date.fromisoformat(start_date),
                    "end_date": date.fromisoformat(end_date),
                    "start_time": time.fromisoformat(start_time),
                    "end_time": time.fromisoformat(end_time),
                    "is_active": is_active,
                },
            )
            inserted += 1
    return inserted


async def seed_categories(db: Database) -> int:
    inserted = 0
    async with db.transaction() as conn:
        for name, description, slug_category, image_category in BASE_CATEGORIES:
            await conn.execute(
                text(_INSERT_CATEGORY),
                {
                    "name": name,
                    "description": description,
                    "slug_category": slug_category,
                    "image_category": image_category,
                },
            )
            inserted += 1
    return inserted


async def seed_sliders(db: Database) -> int:
    inserted = 0
    async with db.transaction() as conn:
        for name, image in BASE_SLIDERS:
            await conn.execute(
                text(_INSERT_SLIDER),
                {"name": name, "image": image, "existing_name": name},
            )
            inserted += 1
    return inserted


async def seed_merchants(db: Database) -> int:
    inserted = 0
    async with db.transaction() as conn:
        for (
            user_id,
            name,
            description,
            address,
            contact_email,
            contact_phone,
            status,
        ) in BASE_MERCHANTS:
            await conn.execute(
                text(_INSERT_MERCHANT),
                {
                    "user_id": user_id,
                    "name": name,
                    "description": description,
                    "address": address,
                    "contact_email": contact_email,
                    "contact_phone": contact_phone,
                    "status": status,
                },
            )
            inserted += 1
    return inserted


def _social_links(merchant_detail_id: int) -> list[tuple[str, str]]:
    """The three social links attaches to every seeded detail. derives the URL from the loop index (`i + 1`); uses the actual `merchant_detail_id`, which is the same value on a fresh DB and correct even when the sequence has advanced."""
    return [
        ("Facebook", f"https://www.facebook.com/merchant{merchant_detail_id}"),
        ("Instagram", f"https://www.instagram.com/merchant{merchant_detail_id}"),
        ("Twitter", f"https://www.twitter.com/merchant{merchant_detail_id}"),
    ]


async def seed_merchant_details(db: Database) -> int:
    inserted = 0
    async with db.transaction() as conn:
        for (
            merchant_id,
            display_name,
            cover_image_url,
            logo_url,
            short_description,
            website_url,
        ) in BASE_MERCHANT_DETAILS:
            await conn.execute(
                text(_INSERT_MERCHANT_DETAIL),
                {
                    "merchant_id": merchant_id,
                    "display_name": display_name,
                    "cover_image_url": cover_image_url,
                    "logo_url": logo_url,
                    "short_description": short_description,
                    "website_url": website_url,
                },
            )
            inserted += 1

            detail_id = (
                await conn.execute(
                    text(
                        "SELECT merchant_detail_id FROM merchant_details "
                        "WHERE merchant_id = :merchant_id "
                        "ORDER BY merchant_detail_id LIMIT 1"
                    ),
                    {"merchant_id": merchant_id},
                )
            ).scalar()
            if detail_id is None:
                # Merchant absent → the detail insert was skipped; no links.
                continue

            for platform, url in _social_links(int(detail_id)):
                await conn.execute(
                    text(_INSERT_MERCHANT_SOCIAL_LINK),
                    {
                        "merchant_detail_id": detail_id,
                        "platform": platform,
                        "existing_platform": platform,
                        "url": url,
                    },
                )
    return inserted


async def seed_merchant_awards(db: Database) -> int:
    inserted = 0
    async with db.transaction() as conn:
        for (
            merchant_id,
            title,
            description,
            issued_by,
            issue_date,
            expiry_date,
            certificate_url,
        ) in BASE_MERCHANT_AWARDS:
            await conn.execute(
                text(_INSERT_MERCHANT_AWARD),
                {
                    "merchant_id": merchant_id,
                    "title": title,
                    "existing_title": title,
                    "description": description,
                    "issued_by": issued_by,
                    "issue_date": date.fromisoformat(issue_date),
                    "expiry_date": date.fromisoformat(expiry_date),
                    "certificate_url": certificate_url,
                },
            )
            inserted += 1
    return inserted


async def seed_merchant_businesses(db: Database) -> int:
    inserted = 0
    async with db.transaction() as conn:
        for (
            merchant_id,
            business_type,
            tax_id,
            established_year,
            number_of_employees,
            website_url,
        ) in BASE_MERCHANT_BUSINESSES:
            await conn.execute(
                text(_INSERT_MERCHANT_BUSINESS),
                {
                    "merchant_id": merchant_id,
                    "business_type": business_type,
                    "tax_id": tax_id,
                    "established_year": established_year,
                    "number_of_employees": number_of_employees,
                    "website_url": website_url,
                },
            )
            inserted += 1
    return inserted


async def seed_merchant_policies(db: Database) -> int:
    inserted = 0
    async with db.transaction() as conn:
        for (
            merchant_id,
            policy_type,
            title,
            description,
        ) in BASE_MERCHANT_POLICIES:
            await conn.execute(
                text(_INSERT_MERCHANT_POLICY),
                {
                    "merchant_id": merchant_id,
                    "policy_type": policy_type,
                    "title": title,
                    "description": description,
                    "existing_title": title,
                },
            )
            inserted += 1
    return inserted


async def seed_products(db: Database) -> int:
    inserted = 0
    async with db.transaction() as conn:
        for (
            merchant_id,
            category_id,
            name,
            description,
            price,
            count_in_stock,
            brand,
            weight,
            rating,
            slug_product,
            image_product,
        ) in BASE_PRODUCTS:
            await conn.execute(
                text(_INSERT_PRODUCT),
                {
                    "merchant_id": merchant_id,
                    "category_id": category_id,
                    "name": name,
                    "existing_name": name,
                    "description": description,
                    "price": price,
                    "count_in_stock": count_in_stock,
                    "brand": brand,
                    "weight": weight,
                    "rating": rating,
                    "slug_product": slug_product,
                    "image_product": image_product,
                },
            )
            inserted += 1
    return inserted


async def seed_reviews(db: Database) -> int:
    inserted = 0
    async with db.transaction() as conn:
        for user_id, product_id, name, comment, rating in BASE_REVIEWS:
            row = await conn.execute(
                text(_INSERT_REVIEW),
                {
                    "user_id": user_id,
                    "existing_user_id": user_id,
                    "product_id": product_id,
                    "existing_product_id": product_id,
                    "name": name,
                    "comment": comment,
                    "existing_comment": comment,
                    "rating": rating,
                },
            )
            review_id = row.scalar()
            if review_id is None:
                # Either the parents are absent (insert skipped) or the review
                # already exists; look it up so the detail insert can still run.
                review_id = (
                    await conn.execute(
                        text(
                            "SELECT review_id FROM reviews "
                            "WHERE user_id = :user_id AND product_id = :product_id "
                            "AND comment = :comment ORDER BY review_id LIMIT 1"
                        ),
                        {
                            "user_id": user_id,
                            "product_id": product_id,
                            "comment": comment,
                        },
                    )
                ).scalar()
            if review_id is None:
                # Parent user/product absent → nothing to attach a detail to.
                continue

            await conn.execute(
                text(_INSERT_REVIEW_DETAIL),
                {
                    "review_id": review_id,
                    "existing_review_id": review_id,
                    "type": "photo",
                    "url": f"https://example.com/review_{name}.jpg",
                    "caption": f"Foto review oleh {name}",
                },
            )
            inserted += 1
    return inserted


async def seed_orders(db: Database) -> int:
    inserted = 0
    async with db.transaction() as conn:
        for user_id, merchant_id, total_price, product_id, quantity, price in BASE_ORDERS:
            row = await conn.execute(
                text(_INSERT_ORDER),
                {
                    "user_id": user_id,
                    "existing_user_id": user_id,
                    "merchant_id": merchant_id,
                    "existing_merchant_id": merchant_id,
                    "total_price": total_price,
                    "existing_total_price": total_price,
                },
            )
            order_id = row.scalar()
            if order_id is None:
                # Either the parents are absent (insert skipped) or the order
                # already exists; look it up so the item insert can still run.
                order_id = (
                    await conn.execute(
                        text(
                            "SELECT order_id FROM orders "
                            "WHERE user_id = :user_id "
                            "AND merchant_id = :merchant_id "
                            "AND total_price = :total_price "
                            "ORDER BY order_id LIMIT 1"
                        ),
                        {
                            "user_id": user_id,
                            "merchant_id": merchant_id,
                            "total_price": total_price,
                        },
                    )
                ).scalar()
            if order_id is None:
                # Parent user/merchant absent → nothing to attach an item to.
                continue

            await conn.execute(
                text(_INSERT_ORDER_ITEM),
                {
                    "order_id": order_id,
                    "existing_order_id": order_id,
                    "product_id": product_id,
                    "existing_product_id": product_id,
                    "quantity": quantity,
                    "price": price,
                },
            )
            inserted += 1
    return inserted


async def seed_transactions(db: Database) -> int:
    inserted = 0
    async with db.transaction() as conn:
        for order_id, merchant_id, method, amount, status in BASE_TRANSACTIONS:
            row = await conn.execute(
                text(_INSERT_TRANSACTION),
                {
                    "order_id": order_id,
                    "existing_order_id": order_id,
                    "merchant_id": merchant_id,
                    "payment_method": method,
                    "amount": amount,
                    "payment_status": status,
                },
            )
            if row.scalar() is not None:
                inserted += 1
    return inserted


async def run() -> None:
    settings = get_settings()
    logger = get_logger(SERVICE_NAME)
    db = Database.create(settings.database, logger)
    try:
        await db.ping()
        role_count = await seed_roles(db)
        banner_count = await seed_banners(db)
        category_count = await seed_categories(db)
        slider_count = await seed_sliders(db)
        merchant_count = await seed_merchants(db)
        merchant_detail_count = await seed_merchant_details(db)
        merchant_award_count = await seed_merchant_awards(db)
        merchant_business_count = await seed_merchant_businesses(db)
        merchant_policy_count = await seed_merchant_policies(db)
        product_count = await seed_products(db)
        review_count = await seed_reviews(db)
        order_count = await seed_orders(db)
        transaction_count = await seed_transactions(db)
        logger.info(
            "seed completed",
            roles=role_count,
            banners=banner_count,
            categories=category_count,
            sliders=slider_count,
            merchants=merchant_count,
            merchant_details=merchant_detail_count,
            merchant_awards=merchant_award_count,
            merchant_businesses=merchant_business_count,
            merchant_policies=merchant_policy_count,
            products=product_count,
            reviews=review_count,
            orders=order_count,
            transactions=transaction_count,
        )
    finally:
        await db.close()


def main() -> None:
    asyncio.run(run())


__all__ = [
    "BASE_BANNERS",
    "BASE_CATEGORIES",
    "BASE_MERCHANT_AWARDS",
    "BASE_MERCHANT_BUSINESSES",
    "BASE_MERCHANT_DETAILS",
    "BASE_MERCHANT_POLICIES",
    "BASE_MERCHANTS",
    "BASE_ORDERS",
    "BASE_TRANSACTIONS",
    "BASE_PRODUCTS",
    "BASE_REVIEWS",
    "BASE_ROLES",
    "BASE_SLIDERS",
    "main",
    "run",
    "seed_banners",
    "seed_categories",
    "seed_merchant_awards",
    "seed_merchant_businesses",
    "seed_merchant_details",
    "seed_merchant_policies",
    "seed_merchants",
    "seed_orders",
    "seed_products",
    "seed_reviews",
    "seed_roles",
    "seed_sliders",
]

"""Milestone 1 — Data Foundation: synthetic/mock data generator.

Generates the complete synthetic dataset required by later milestones:
customers -> bank accounts -> payees -> cheque issuance registry ->
transaction/processing history -> reference signatures -> sample cheques
covering the documented fraud/test categories -> derived
validation/duplicate/anomaly/fraud evaluation datasets.

Per ADR-0005, every record here is synthetically generated. No real
customer, banking, or personal information is used anywhere in this
script or its output.

Run with the backend virtual environment (has pandas/numpy/Pillow):
    apps/backend/.venv/Scripts/python.exe scripts/generate_synthetic_data.py
"""

from __future__ import annotations

import csv
import hashlib
import json
import random
import shutil
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

# ---------------------------------------------------------------------------
# Setup
# ---------------------------------------------------------------------------

SEED = 20260823
random.seed(SEED)

REPO_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = REPO_ROOT / "data"
MOCK_DIR = DATA_DIR / "mock_banking_data"
SAMPLE_DIR = DATA_DIR / "sample_cheques"
TEST_DIR = DATA_DIR / "test_data"

PROCESSING_DATE = date(2026, 8, 23)  # "today" for this synthetic dataset
BANK_NAME = "DEMO NATIONAL BANK"
BANK_CODE = "DEMO001"
VALIDITY_PERIOD_DAYS = 180  # configurable cheque validity window (docs/16 S16)

FONT_REGULAR = ImageFont.load_default()
try:
    FONT_LARGE = ImageFont.load_default(size=22)
    FONT_MED = ImageFont.load_default(size=16)
    FONT_SMALL = ImageFont.load_default(size=13)
except TypeError:  # Pillow < 10.1 fallback
    FONT_LARGE = FONT_MED = FONT_SMALL = FONT_REGULAR

CATEGORIES = [
    "VALID",
    "DUPLICATE",
    "PAYEE_TAMPERED",
    "AMOUNT_TAMPERED",
    "SIGNATURE_MISMATCH",
    "INVALID_ACCOUNT",
    "STALE_CHEQUE",
    "STOPPED_CHEQUE",
    "CHEQUE_SERIES_ANOMALY",
    "MULTIPLE_ANOMALIES",
]
# Not one of the 10 required fraud categories, but explicitly required by
# docs/16_Validation_Engine.md Test Case 6 (future-dated cheque) as a
# distinct validation scenario from STALE_CHEQUE.
BONUS_CATEGORY = "FUTURE_DATED"

SAMPLES_PER_CATEGORY = 8
FUTURE_DATED_SAMPLES = 4

# ---------------------------------------------------------------------------
# Fictional name pools (fully synthetic; not derived from any real dataset)
# ---------------------------------------------------------------------------

FIRST_NAMES = [
    "Alex", "Priya", "Chen", "Maria", "James", "Fatima", "Liam", "Aiko",
    "Noah", "Sofia", "Omar", "Grace", "Ivan", "Nadia", "Tariq", "Elena",
    "Marcus", "Yuki", "Diego", "Amara", "Felix", "Ingrid", "Kwame", "Rosa",
    "Sanjay", "Chloe", "Hassan", "Mei", "Victor", "Lena", "Anton", "Zara",
    "Miguel", "Nora", "Kenji", "Tessa", "Rafael", "Sasha", "Dara", "Leo",
]
LAST_NAMES = [
    "Johnson", "Menon", "Wei", "Garcia", "Okafor", "Ahmed", "Sullivan",
    "Tanaka", "Petrov", "Brown", "Al-Farsi", "Kim", "Novak", "Silva",
    "Hendricks", "Costa", "Ibrahim", "Larsson", "Dube", "Fischer",
    "Rossi", "Yamamoto", "Osei", "Reyes", "Kapoor", "Moreau", "Haddad",
    "Lindgren", "Adeyemi", "Vance",
]
BUSINESS_WORDS_1 = [
    "Summit", "Harbor", "Cedar", "Meridian", "Northgate", "Riverside",
    "Lantern", "Granite", "Willow", "Beacon", "Foundry", "Orchard",
    "Compass", "Ironwood", "Bluepeak", "Anchor", "Crestline", "Maple",
]
BUSINESS_WORDS_2 = [
    "Supplies", "Traders", "Services", "Logistics", "Works", "Trading Co",
    "Distributors", "Partners", "Holdings", "Imports", "Systems", "Goods",
]

used_person_names: set[str] = set()
used_business_names: set[str] = set()


def fictional_person_name() -> str:
    while True:
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        if name not in used_person_names:
            used_person_names.add(name)
            return name


def fictional_business_name() -> str:
    while True:
        name = f"{random.choice(BUSINESS_WORDS_1)} {random.choice(BUSINESS_WORDS_2)}"
        if name not in used_business_names:
            used_business_names.add(name)
            return name


# ---------------------------------------------------------------------------
# Amount-in-words helper
# ---------------------------------------------------------------------------

_ONES = [
    "", "One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight",
    "Nine", "Ten", "Eleven", "Twelve", "Thirteen", "Fourteen", "Fifteen",
    "Sixteen", "Seventeen", "Eighteen", "Nineteen",
]
_TENS = [
    "", "", "Twenty", "Thirty", "Forty", "Fifty", "Sixty", "Seventy",
    "Eighty", "Ninety",
]


def _three_digit_words(n: int) -> str:
    parts = []
    if n >= 100:
        parts.append(f"{_ONES[n // 100]} Hundred")
        n %= 100
    if n >= 20:
        tens_word = _TENS[n // 10]
        ones = n % 10
        parts.append(f"{tens_word} {_ONES[ones]}".strip() if ones else tens_word)
    elif n > 0:
        parts.append(_ONES[n])
    return " ".join(parts)


def amount_to_words(amount: float) -> str:
    """Converts a monetary amount into cheque-style words, e.g. 25000.00 ->
    'Twenty Five Thousand Only', 17334.23 -> 'Seventeen Thousand Three
    Hundred Thirty Four and 23/100 Only'.

    Cents are represented via the standard "and NN/100" cheque-writing
    convention rather than silently dropped -- an earlier version of this
    function rounded the whole amount and lost the cents entirely, which
    made the amount-in-words inconsistent with the numeric amount for
    almost every generated cheque. That was only caught once Milestone 4
    implemented the real AMOUNT_CONSISTENCY check against this data."""
    dollars = int(amount)  # truncate towards zero; amounts here are always >= 0
    cents = int(round((amount - dollars) * 100))
    if cents >= 100:  # rounding edge case, e.g. 17334.999
        dollars += 1
        cents = 0

    whole = dollars
    if whole == 0:
        dollars_words = "Zero"
    else:
        groups = []
        for divisor, label in ((1_000_000, "Million"), (1_000, "Thousand")):
            if whole >= divisor:
                count = whole // divisor
                groups.append(f"{_three_digit_words(count)} {label}")
                whole %= divisor
        if whole > 0 or not groups:
            groups.append(_three_digit_words(whole))
        dollars_words = " ".join(g for g in groups if g).strip()

    if cents > 0:
        return f"{dollars_words} and {cents:02d}/100 Only"
    return f"{dollars_words} Only"


# ---------------------------------------------------------------------------
# Image generation helpers (fictional/generic cheque + signature rendering)
# ---------------------------------------------------------------------------

CHEQUE_W, CHEQUE_H = 1200, 560


def _text(draw: ImageDraw.ImageDraw, xy, txt, font, fill=(20, 20, 30)):
    draw.text(xy, txt, font=font, fill=fill)


def render_cheque_image(
    out_path: Path,
    *,
    bank_name: str,
    cheque_number: str,
    account_number: str,
    routing_transit_number: str,
    payee_name: str,
    amount: float,
    amount_words: str,
    cheque_date: date,
    signature_path: Path | None,
    watermark: str = "SYNTHETIC / NOT A REAL CHEQUE",
) -> None:
    """Draws a simple, clearly-fictional generic cheque layout. Used only to
    give later milestones (image preprocessing / OCR) real files to operate
    on -- no OCR or field-extraction logic is implemented here."""
    img = Image.new("RGB", (CHEQUE_W, CHEQUE_H), (250, 249, 244))
    draw = ImageDraw.Draw(img)

    draw.rectangle([4, 4, CHEQUE_W - 5, CHEQUE_H - 5], outline=(120, 120, 130), width=3)

    _text(draw, (30, 25), bank_name, FONT_LARGE)
    _text(draw, (30, 55), f"Bank Code: {BANK_CODE}", FONT_SMALL, fill=(90, 90, 100))
    _text(draw, (900, 30), f"Date: {cheque_date.strftime('%d/%m/%Y')}", FONT_MED)
    _text(draw, (900, 60), f"Cheque No: {cheque_number}", FONT_MED)

    _text(draw, (30, 130), "Pay to the order of:", FONT_SMALL, fill=(90, 90, 100))
    _text(draw, (30, 152), payee_name, FONT_LARGE)
    draw.line([(30, 185), (700, 185)], fill=(150, 150, 160), width=1)

    _text(draw, (30, 230), "Amount:", FONT_SMALL, fill=(90, 90, 100))
    _text(draw, (30, 252), f"${amount:,.2f}", FONT_LARGE)

    _text(draw, (30, 300), "Amount in words:", FONT_SMALL, fill=(90, 90, 100))
    _text(draw, (30, 322), amount_words, FONT_MED)
    draw.line([(30, 352), (1000, 352)], fill=(150, 150, 160), width=1)

    _text(draw, (30, 400), f"Account No: {account_number}", FONT_MED)
    _text(draw, (30, 422), f"Routing/Transit No: {routing_transit_number}", FONT_MED)

    # Signature area
    draw.rectangle([760, 400, 1140, 480], outline=(150, 150, 160), width=1)
    _text(draw, (770, 484), "Authorized Signature", FONT_SMALL, fill=(90, 90, 100))
    if signature_path is not None and signature_path.exists():
        sig = Image.open(signature_path).convert("RGBA")
        sig.thumbnail((360, 70))
        img.paste(sig, (770, 405 + (70 - sig.height) // 2), sig)

    # MICR-style line at the bottom (fictional/generic format)
    micr = f"{cheque_number}  {routing_transit_number}  {account_number}"
    _text(draw, (30, 510), micr, FONT_MED, fill=(40, 40, 50))

    _text(draw, (300, 520), watermark, FONT_SMALL, fill=(200, 60, 60))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, format="PNG")


def render_signature_image(out_path: Path, seed: int, *, style: str = "genuine") -> None:
    """Procedurally draws a simple, clearly-synthetic 'signature' -- a random
    stroke pattern, not a real handwriting sample. `style` controls how the
    same seed diverges (variation/forged/low_quality/etc.)."""
    rng = random.Random(seed)
    w, h = 360, 100
    img = Image.new("RGBA", (w, h), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    n_strokes = rng.randint(3, 5)
    color = (10, 10, 40, 255)
    jitter = 6 if style == "genuine_variation" else 2

    for _ in range(n_strokes):
        x = rng.randint(10, 60)
        y = rng.randint(30, 70)
        points = [(x, y)]
        for _step in range(rng.randint(6, 10)):
            x += rng.randint(15, 40)
            y += rng.randint(-25, 25) + rng.randint(-jitter, jitter)
            y = max(10, min(h - 10, y))
            x = min(w - 10, x)
            points.append((x, y))
        draw.line(points, fill=color, width=rng.randint(2, 3), joint="curve")

    if style == "forged":
        # A visually distinct stroke pattern (different seed offset & shape)
        rng2 = random.Random(seed + 999)
        for _ in range(2):
            x, y = rng2.randint(200, 260), rng2.randint(20, 40)
            pts = [(x, y)]
            for _s in range(5):
                x += rng2.randint(10, 30)
                y += rng2.randint(-15, 40)
                pts.append((x, y))
            draw.line(pts, fill=color, width=2, joint="curve")

    if style == "low_quality":
        img = img.filter(ImageFilter.GaussianBlur(radius=2.2))
        noise = Image.effect_noise((w, h), 40).convert("L")
        img.putalpha(noise.point(lambda p: 255 - p // 3))

    if style == "partial":
        crop_w = int(w * 0.45)
        cropped = Image.new("RGBA", (w, h), (255, 255, 255, 0))
        cropped.paste(img.crop((0, 0, crop_w, h)), (0, 0))
        img = cropped

    if style == "missing":
        img = Image.new("RGBA", (w, h), (255, 255, 255, 0))

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.convert("RGB").save(out_path, format="PNG")


def sha256_of_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def average_hash(path: Path, hash_size: int = 8) -> str:
    """Simple perceptual (average) hash, precomputed here purely as a
    reference value for later milestones to consume -- no comparison/
    duplicate-detection logic is implemented in this script."""
    img = Image.open(path).convert("L").resize((hash_size, hash_size))
    pixels = list(img.tobytes())
    avg = sum(pixels) / len(pixels)
    bits = "".join("1" if p > avg else "0" for p in pixels)
    return f"{int(bits, 2):0{hash_size * hash_size // 4}x}"


def hamming_distance_hex(hash_a: str, hash_b: str) -> int:
    a, b = int(hash_a, 16), int(hash_b, 16)
    return bin(a ^ b).count("1")


# ---------------------------------------------------------------------------
# Core entity generation
# ---------------------------------------------------------------------------


@dataclass
class Account:
    account_number: str
    customer_id: str
    account_status: str
    account_type: str
    balance: float
    routing_number: str
    cheque_series_start: str
    cheque_series_end: str
    has_history: bool = True


def generate_customers(n: int) -> list[dict]:
    customers = []
    for i in range(1, n + 1):
        customer_id = f"CUST-{i:04d}"
        name = fictional_person_name()
        status = "ACTIVE" if random.random() > 0.05 else "INACTIVE"
        customers.append(
            {
                "customer_id": customer_id,
                "customer_name": name,
                "email": f"{name.lower().replace(' ', '.')}@example-synthetic.test",
                "phone": f"555-{random.randint(1000, 9999):04d}",
                "status": status,
                "created_at": (PROCESSING_DATE - timedelta(days=random.randint(200, 1800))).isoformat(),
            }
        )
    return customers


def generate_accounts(customers: list[dict]) -> list[Account]:
    accounts: list[Account] = []
    acct_seq = 10001
    # Deliberately unbalanced status distribution so validation/fraud test
    # categories have real accounts to reference (docs/16 SS10-13).
    status_pool = (
        ["ACTIVE"] * 34
        + ["CLOSED"] * 4
        + ["BLOCKED"] * 3
        + ["FROZEN"] * 2
        + ["INACTIVE"] * 2
    )
    random.shuffle(status_pool)

    series_base = 100
    for idx, customer in enumerate(customers):
        n_accounts = 2 if idx >= len(customers) - 5 else 1  # last 5 customers get 2 accounts
        for _ in range(n_accounts):
            account_number = f"90000{acct_seq}"
            status = status_pool[(acct_seq - 10001) % len(status_pool)]
            series_start = series_base
            series_end = series_base + 49
            series_base += 100
            accounts.append(
                Account(
                    account_number=account_number,
                    customer_id=customer["customer_id"],
                    account_status=status,
                    account_type=random.choice(["CHECKING", "CHECKING", "SAVINGS"]),
                    balance=round(random.uniform(500, 85000), 2),
                    routing_number="121000358",  # single fictional routing number, DEMO001
                    cheque_series_start=f"{series_start:06d}",
                    cheque_series_end=f"{series_end:06d}",
                )
            )
            acct_seq += 1
    return accounts


def generate_payees(n: int) -> list[dict]:
    payees = []
    for i in range(1, n + 1):
        is_business = random.random() > 0.4
        name = fictional_business_name() if is_business else fictional_person_name()
        payees.append(
            {
                "payee_id": f"PAYEE-{i:03d}",
                "payee_name": name,
                "payee_type": "BUSINESS" if is_business else "INDIVIDUAL",
            }
        )
    return payees


def generate_cheque_issuance(accounts: list[Account], payees: list[dict]) -> tuple[list[dict], dict]:
    """Bank's cheque-book issuance registry: which cheque numbers are valid
    for which account, and their current status. Mirrors docs/16 S6 & S13."""
    rows = []
    # Track special cheques we deliberately create for targeted test
    # categories, keyed by category name -> issuance row.
    special: dict[str, dict] = {}

    for account in accounts:
        start = int(account.cheque_series_start)
        end = int(account.cheque_series_end)
        account_payees = random.sample(payees, k=min(4, len(payees)))

        for n in range(start, end + 1):
            cheque_number = f"{n:06d}"
            status = "ISSUED"
            payee = random.choice(account_payees)
            rows.append(
                {
                    "cheque_number": cheque_number,
                    "account_number": account.account_number,
                    "status": status,
                    "payee_name": payee["payee_name"],
                    "amount_limit": 500000.00,
                }
            )

        # Assign one STOPPED cheque per ACTIVE account with enough history,
        # used for the STOPPED_CHEQUE sample category.
        if account.account_status == "ACTIVE" and "STOPPED_CHEQUE" not in special:
            stop_n = start + 2
            for row in rows:
                if row["account_number"] == account.account_number and row["cheque_number"] == f"{stop_n:06d}":
                    row["status"] = "STOPPED"
                    special["STOPPED_CHEQUE"] = {**row, "account": account}
                    break

        if account.account_status == "ACTIVE" and "CANCELLED" not in special:
            cancel_n = start + 4
            for row in rows:
                if row["account_number"] == account.account_number and row["cheque_number"] == f"{cancel_n:06d}":
                    row["status"] = "CANCELLED"
                    special["CANCELLED"] = {**row, "account": account}
                    break

    return rows, special


def generate_transactions(
    accounts: list[Account], payees: list[dict]
) -> tuple[list[dict], dict[str, list[dict]]]:
    """Historical processed-transaction records used as the anomaly-detection
    baseline (docs/20) and as prior-processed data for duplicate detection
    (docs/19). Roughly the last 22% of accounts are left with little/no
    history to exercise the cold-start path (docs/20 S38)."""
    transactions: list[dict] = []
    by_account: dict[str, list[dict]] = {}
    txn_seq = 1

    cold_start_accounts = set(a.account_number for a in accounts[-10:])

    for account in accounts:
        by_account[account.account_number] = []
        if account.account_number in cold_start_accounts:
            n_txns = random.randint(0, 2)
        elif account.account_status != "ACTIVE":
            n_txns = random.randint(1, 4)
        else:
            n_txns = random.randint(6, 14)

        favored_payees = random.sample(payees, k=min(3, len(payees)))
        base_amount = random.uniform(4000, 20000)

        for i in range(n_txns):
            days_ago = random.randint(3, 150)
            txn_date = PROCESSING_DATE - timedelta(days=days_ago)
            amount = round(base_amount * random.uniform(0.7, 1.3), 2)
            payee = random.choice(favored_payees)
            txn = {
                "transaction_id": f"TXN{txn_seq:06d}",
                "account_number": account.account_number,
                "transaction_date": txn_date.isoformat(),
                "transaction_type": "CHEQUE",
                "amount": amount,
                "payee_name": payee["payee_name"],
            }
            transactions.append(txn)
            by_account[account.account_number].append(txn)
            txn_seq += 1

        by_account[account.account_number].sort(key=lambda t: t["transaction_date"])

    transactions.sort(key=lambda t: (t["account_number"], t["transaction_date"]))
    return transactions, by_account


# ---------------------------------------------------------------------------
# Reference signatures
# ---------------------------------------------------------------------------


def generate_reference_signatures(accounts: list[Account]) -> tuple[list[dict], dict[str, list[str]]]:
    sig_dir = MOCK_DIR / "reference_signatures"
    if sig_dir.exists():
        shutil.rmtree(sig_dir)
    sig_dir.mkdir(parents=True, exist_ok=True)

    index_rows: list[dict] = []
    genuine_by_account: dict[str, list[str]] = {}

    # Last 10 accounts (cold-start accounts) deliberately get NO reference
    # signature, to exercise the "signature unavailable" path (docs/18 A-005
    # / assumption A-005 in docs/05).
    no_signature_accounts = set(a.account_number for a in accounts[-10:])

    for account in accounts:
        if account.account_number in no_signature_accounts:
            continue
        n_refs = random.randint(2, 3)
        seed = hash(account.account_number) % (2**31)
        files = []
        for i in range(1, n_refs + 1):
            filename = f"SIG-{account.account_number}-{i}.png"
            path = sig_dir / filename
            style = "genuine" if i == 1 else "genuine_variation"
            render_signature_image(path, seed=seed + i, style=style)
            index_rows.append(
                {
                    "signature_id": f"SIG-{account.account_number}-{i}",
                    "account_number": account.account_number,
                    "signature_file": f"reference_signatures/{filename}",
                    "variant": style,
                }
            )
            files.append(filename)
        genuine_by_account[account.account_number] = files

    index_path = sig_dir / "signatures_index.csv"
    write_csv(index_path, index_rows, ["signature_id", "account_number", "signature_file", "variant"])

    return index_rows, genuine_by_account


# ---------------------------------------------------------------------------
# Sample cheque generation (the 10 documented categories + bonus)
# ---------------------------------------------------------------------------


@dataclass
class SampleCheque:
    cheque_id: str
    category: str
    image_path: str
    account_number: str
    cheque_number: str
    routing_transit_number: str
    bank_name: str
    payee_name: str
    amount: float
    amount_in_words: str
    cheque_date: str
    signature_image: str
    expected_account_status: str
    expected_cheque_status: str
    expected_payee_name: str
    expected_amount: float
    notes: str
    fraud_label: int
    fraud_type: str


def _pick_active_account(accounts: list[Account], *, with_history=True, with_signature=True,
                          genuine_by_account: dict[str, list[str]] | None = None,
                          by_account_txns: dict[str, list[dict]] | None = None,
                          rng: random.Random | None = None) -> Account:
    rng = rng or random
    pool = [a for a in accounts if a.account_status == "ACTIVE"]
    if with_history and by_account_txns is not None:
        pool = [a for a in pool if len(by_account_txns.get(a.account_number, [])) >= 4]
    if with_signature and genuine_by_account is not None:
        pool = [a for a in pool if a.account_number in genuine_by_account]
    return rng.choice(pool)


def generate_sample_cheques(
    accounts: list[Account],
    payees: list[dict],
    issuance_rows: list[dict],
    special_issuance: dict,
    genuine_by_account: dict[str, list[str]],
    by_account_txns: dict[str, list[dict]],
) -> tuple[list[SampleCheque], list[dict]]:
    """Returns (sample_cheques, image_hash_rows)."""
    samples: list[SampleCheque] = []
    image_hash_rows: list[dict] = []
    cheque_seq = 1

    issuance_by_account: dict[str, list[dict]] = {}
    for row in issuance_rows:
        issuance_by_account.setdefault(row["account_number"], []).append(row)

    def next_cheque_id() -> str:
        nonlocal cheque_seq
        cid = f"CHK-2026-{cheque_seq:06d}"
        cheque_seq += 1
        return cid

    def issued_row_for(account: Account, rng: random.Random) -> dict:
        candidates = [r for r in issuance_by_account[account.account_number] if r["status"] == "ISSUED"]
        return rng.choice(candidates)

    def save_image_and_record(cheque_id, category, account, cheque_number, payee_name, amount,
                               amount_words, cheque_date, signature_rel_path, notes,
                               expected_account_status, expected_cheque_status,
                               expected_payee_name, expected_amount, fraud_label, fraud_type,
                               watermark_extra="") -> SampleCheque:
        rel_dir = SAMPLE_DIR / category.lower()
        image_path = rel_dir / f"{cheque_id}.png"
        signature_full_path = (MOCK_DIR / signature_rel_path) if signature_rel_path else None
        render_cheque_image(
            image_path,
            bank_name=BANK_NAME,
            cheque_number=cheque_number,
            account_number=account.account_number,
            routing_transit_number=account.routing_number,
            payee_name=payee_name,
            amount=amount,
            amount_words=amount_words,
            cheque_date=cheque_date,
            signature_path=signature_full_path,
        )
        rel_image_path = str(image_path.relative_to(DATA_DIR)).replace("\\", "/")
        img_hash = sha256_of_file(image_path)
        phash = average_hash(image_path)
        image_hash_rows.append(
            {"cheque_id": cheque_id, "image_path": rel_image_path, "image_hash": img_hash, "perceptual_hash": phash}
        )
        return SampleCheque(
            cheque_id=cheque_id,
            category=category,
            image_path=rel_image_path,
            account_number=account.account_number,
            cheque_number=cheque_number,
            routing_transit_number=account.routing_number,
            bank_name=BANK_NAME,
            payee_name=payee_name,
            amount=amount,
            amount_in_words=amount_words,
            cheque_date=cheque_date.isoformat(),
            signature_image=signature_rel_path or "",
            expected_account_status=expected_account_status,
            expected_cheque_status=expected_cheque_status,
            expected_payee_name=expected_payee_name,
            expected_amount=expected_amount,
            notes=notes,
            fraud_label=fraud_label,
            fraud_type=fraud_type,
        )

    rng = random.Random(SEED + 1)

    # ---- VALID -------------------------------------------------------
    for _ in range(SAMPLES_PER_CATEGORY):
        account = _pick_active_account(accounts, genuine_by_account=genuine_by_account,
                                        by_account_txns=by_account_txns, rng=rng)
        issued = issued_row_for(account, rng)
        amount = round(rng.uniform(2000, 25000), 2)
        words = amount_to_words(amount)
        cheque_date = PROCESSING_DATE - timedelta(days=rng.randint(0, 20))
        sig_file = f"reference_signatures/{genuine_by_account[account.account_number][0]}"
        cid = next_cheque_id()
        samples.append(save_image_and_record(
            cid, "VALID", account, issued["cheque_number"], issued["payee_name"], amount, words,
            cheque_date, sig_file, "All checks expected to pass.",
            account.account_status, "ISSUED", issued["payee_name"], amount, 0, "NONE",
        ))

    # ---- DUPLICATE -----------------------------------------------------
    duplicate_source_records: list[dict] = []
    for _ in range(SAMPLES_PER_CATEGORY):
        account = _pick_active_account(accounts, genuine_by_account=genuine_by_account,
                                        by_account_txns=by_account_txns, rng=rng)
        issued = issued_row_for(account, rng)
        amount = round(rng.uniform(2000, 25000), 2)
        words = amount_to_words(amount)
        cheque_date = PROCESSING_DATE - timedelta(days=rng.randint(5, 30))
        sig_file = f"reference_signatures/{genuine_by_account[account.account_number][0]}"
        # original ("already processed") + duplicate resubmission share all
        # key fields, per docs/19 Rule D1 (exact composite match).
        original_id = next_cheque_id()
        original = save_image_and_record(
            original_id, "DUPLICATE", account, issued["cheque_number"], issued["payee_name"], amount,
            words, cheque_date, sig_file, "Original submission (already processed).",
            account.account_status, "ISSUED", issued["payee_name"], amount, 0, "NONE",
        )
        samples.append(original)
        duplicate_source_records.append({
            "cheque_id": original_id, "account_number": account.account_number,
            "cheque_number": issued["cheque_number"], "payee_name": issued["payee_name"],
            "amount": amount, "cheque_date": cheque_date.isoformat(),
            "image_path": original.image_path,
        })
        dup_id = next_cheque_id()
        samples.append(save_image_and_record(
            dup_id, "DUPLICATE", account, issued["cheque_number"], issued["payee_name"], amount, words,
            cheque_date, sig_file, f"Resubmission of {original_id}; confirmed duplicate expected.",
            account.account_status, "ISSUED", issued["payee_name"], amount, 1, "DUPLICATE",
        ))

    # ---- PAYEE_TAMPERED --------------------------------------------------
    for _ in range(SAMPLES_PER_CATEGORY):
        account = _pick_active_account(accounts, genuine_by_account=genuine_by_account,
                                        by_account_txns=by_account_txns, rng=rng)
        issued = issued_row_for(account, rng)
        tampered_payee = rng.choice([p for p in payees if p["payee_name"] != issued["payee_name"]])
        amount = round(rng.uniform(2000, 25000), 2)
        words = amount_to_words(amount)
        cheque_date = PROCESSING_DATE - timedelta(days=rng.randint(0, 20))
        sig_file = f"reference_signatures/{genuine_by_account[account.account_number][0]}"
        cid = next_cheque_id()
        samples.append(save_image_and_record(
            cid, "PAYEE_TAMPERED", account, issued["cheque_number"], tampered_payee["payee_name"], amount,
            words, cheque_date, sig_file,
            f"Payee on cheque ('{tampered_payee['payee_name']}') differs from bank record ('{issued['payee_name']}').",
            account.account_status, "ISSUED", issued["payee_name"], amount, 1, "PAYEE_TAMPERED",
        ))

    # ---- AMOUNT_TAMPERED ---------------------------------------------------
    for _ in range(SAMPLES_PER_CATEGORY):
        account = _pick_active_account(accounts, genuine_by_account=genuine_by_account,
                                        by_account_txns=by_account_txns, rng=rng)
        issued = issued_row_for(account, rng)
        true_amount = round(rng.uniform(2000, 15000), 2)
        modified_amount = round(true_amount * rng.uniform(2.0, 4.0), 2)
        words = amount_to_words(true_amount)  # words reflect the ORIGINAL amount
        cheque_date = PROCESSING_DATE - timedelta(days=rng.randint(0, 20))
        sig_file = f"reference_signatures/{genuine_by_account[account.account_number][0]}"
        cid = next_cheque_id()
        samples.append(save_image_and_record(
            cid, "AMOUNT_TAMPERED", account, issued["cheque_number"], issued["payee_name"], modified_amount,
            words, cheque_date, sig_file,
            f"Numeric amount ({modified_amount}) does not match amount in words ({words}).",
            account.account_status, "ISSUED", issued["payee_name"], true_amount, 1, "AMOUNT_TAMPERED",
        ))

    # ---- SIGNATURE_MISMATCH --------------------------------------------
    forged_sig_dir = MOCK_DIR / "reference_signatures"
    for i in range(SAMPLES_PER_CATEGORY):
        account = _pick_active_account(accounts, genuine_by_account=genuine_by_account,
                                        by_account_txns=by_account_txns, rng=rng)
        issued = issued_row_for(account, rng)
        amount = round(rng.uniform(2000, 25000), 2)
        words = amount_to_words(amount)
        cheque_date = PROCESSING_DATE - timedelta(days=rng.randint(0, 20))
        forged_filename = f"FORGED-{account.account_number}-{i}.png"
        render_signature_image(forged_sig_dir / forged_filename, seed=SEED + 5000 + i, style="forged")
        sig_file = f"reference_signatures/{forged_filename}"
        cid = next_cheque_id()
        samples.append(save_image_and_record(
            cid, "SIGNATURE_MISMATCH", account, issued["cheque_number"], issued["payee_name"], amount, words,
            cheque_date, sig_file, "Signature does not match any reference signature on file.",
            account.account_status, "ISSUED", issued["payee_name"], amount, 1, "SIGNATURE_MISMATCH",
        ))

    # ---- INVALID_ACCOUNT (account not found + closed/blocked variants) ---
    not_found_account_numbers = ["9000099901", "9000099902", "9000099903", "9000099904"]
    closed_blocked_accounts = [a for a in accounts if a.account_status in ("CLOSED", "BLOCKED", "FROZEN")]
    for i in range(SAMPLES_PER_CATEGORY):
        amount = round(rng.uniform(2000, 25000), 2)
        words = amount_to_words(amount)
        cheque_date = PROCESSING_DATE - timedelta(days=rng.randint(0, 20))
        cid = next_cheque_id()
        if i < len(not_found_account_numbers):
            fake_account_number = not_found_account_numbers[i]
            fake_account = Account(fake_account_number, "N/A", "NOT_FOUND", "UNKNOWN", 0.0,
                                    "121000358", "000000", "000000")
            payee = rng.choice(payees)
            samples.append(save_image_and_record(
                cid, "INVALID_ACCOUNT", fake_account, "000001", payee["payee_name"], amount, words,
                cheque_date, None, "Account number does not exist in mock banking records.",
                "NOT_FOUND", "UNKNOWN", payee["payee_name"], amount, 1, "INVALID_ACCOUNT",
            ))
        else:
            account = rng.choice(closed_blocked_accounts)
            issued = rng.choice(issuance_by_account[account.account_number])
            payee = rng.choice(payees)
            samples.append(save_image_and_record(
                cid, "INVALID_ACCOUNT", account, issued["cheque_number"], payee["payee_name"], amount, words,
                cheque_date, None, f"Account status is {account.account_status}; cheque should not be approved.",
                account.account_status, issued["status"], payee["payee_name"], amount, 1, "INVALID_ACCOUNT",
            ))

    # ---- STALE_CHEQUE ------------------------------------------------
    for _ in range(SAMPLES_PER_CATEGORY):
        account = _pick_active_account(accounts, genuine_by_account=genuine_by_account,
                                        by_account_txns=by_account_txns, rng=rng)
        issued = issued_row_for(account, rng)
        amount = round(rng.uniform(2000, 25000), 2)
        words = amount_to_words(amount)
        cheque_date = PROCESSING_DATE - timedelta(days=VALIDITY_PERIOD_DAYS + rng.randint(30, 150))
        sig_file = f"reference_signatures/{genuine_by_account[account.account_number][0]}"
        cid = next_cheque_id()
        samples.append(save_image_and_record(
            cid, "STALE_CHEQUE", account, issued["cheque_number"], issued["payee_name"], amount, words,
            cheque_date, sig_file,
            f"Cheque date is {(PROCESSING_DATE - cheque_date).days} days old; exceeds {VALIDITY_PERIOD_DAYS}-day validity window.",
            account.account_status, "ISSUED", issued["payee_name"], amount, 1, "STALE_CHEQUE",
        ))

    # ---- STOPPED_CHEQUE -----------------------------------------------
    stopped_row = special_issuance.get("STOPPED_CHEQUE")
    for i in range(SAMPLES_PER_CATEGORY):
        if stopped_row is not None and i == 0:
            account = stopped_row["account"]
            cheque_number = stopped_row["cheque_number"]
            payee_name = stopped_row["payee_name"]
        else:
            account = _pick_active_account(accounts, genuine_by_account=genuine_by_account,
                                            by_account_txns=by_account_txns, rng=rng)
            candidates = [r for r in issuance_by_account[account.account_number] if r["status"] == "ISSUED"]
            picked = rng.choice(candidates)
            picked["status"] = "STOPPED"  # mark this specific one as stopped for this sample
            cheque_number, payee_name = picked["cheque_number"], picked["payee_name"]
        amount = round(rng.uniform(2000, 25000), 2)
        words = amount_to_words(amount)
        cheque_date = PROCESSING_DATE - timedelta(days=rng.randint(0, 20))
        sig_file = f"reference_signatures/{genuine_by_account[account.account_number][0]}" \
            if account.account_number in genuine_by_account else None
        cid = next_cheque_id()
        samples.append(save_image_and_record(
            cid, "STOPPED_CHEQUE", account, cheque_number, payee_name, amount, words, cheque_date,
            sig_file, "Cheque has a STOPPED status in the bank's issuance registry.",
            account.account_status, "STOPPED", payee_name, amount, 1, "STOPPED_CHEQUE",
        ))

    # ---- CHEQUE_SERIES_ANOMALY ----------------------------------------
    for _ in range(SAMPLES_PER_CATEGORY):
        account = _pick_active_account(accounts, genuine_by_account=genuine_by_account,
                                        by_account_txns=by_account_txns, rng=rng)
        out_of_series = int(account.cheque_series_end) + rng.randint(200, 900)
        cheque_number = f"{out_of_series:06d}"
        payee = rng.choice(payees)
        amount = round(rng.uniform(2000, 25000), 2)
        words = amount_to_words(amount)
        cheque_date = PROCESSING_DATE - timedelta(days=rng.randint(0, 20))
        sig_file = f"reference_signatures/{genuine_by_account[account.account_number][0]}"
        cid = next_cheque_id()
        samples.append(save_image_and_record(
            cid, "CHEQUE_SERIES_ANOMALY", account, cheque_number, payee["payee_name"], amount, words,
            cheque_date, sig_file,
            f"Cheque number {cheque_number} falls outside account's issued series "
            f"[{account.cheque_series_start}-{account.cheque_series_end}].",
            account.account_status, "UNKNOWN", payee["payee_name"], amount, 1, "CHEQUE_SERIES_ANOMALY",
        ))

    # ---- MULTIPLE_ANOMALIES (2+ combined problems) ---------------------
    for i in range(SAMPLES_PER_CATEGORY):
        account = _pick_active_account(accounts, genuine_by_account=genuine_by_account,
                                        by_account_txns=by_account_txns, rng=rng)
        issued = issued_row_for(account, rng)
        tampered_payee = rng.choice([p for p in payees if p["payee_name"] != issued["payee_name"]])
        true_amount = round(rng.uniform(2000, 12000), 2)
        modified_amount = round(true_amount * rng.uniform(5.0, 15.0), 2)  # amount tampering + anomaly
        words = amount_to_words(true_amount)
        cheque_date = PROCESSING_DATE - timedelta(days=rng.randint(0, 10))
        forged_filename = f"FORGED-MULTI-{account.account_number}-{i}.png"
        render_signature_image(forged_sig_dir / forged_filename, seed=SEED + 9000 + i, style="forged")
        sig_file = f"reference_signatures/{forged_filename}"
        cid = next_cheque_id()
        samples.append(save_image_and_record(
            cid, "MULTIPLE_ANOMALIES", account, issued["cheque_number"], tampered_payee["payee_name"],
            modified_amount, words, cheque_date, sig_file,
            "Combines payee mismatch, amount tampering (numeric vs words), and signature mismatch.",
            account.account_status, "ISSUED", issued["payee_name"], true_amount, 1, "MULTIPLE_ANOMALIES",
        ))

    # ---- FUTURE_DATED (bonus, docs/16 Test Case 6) ---------------------
    for _ in range(FUTURE_DATED_SAMPLES):
        account = _pick_active_account(accounts, genuine_by_account=genuine_by_account,
                                        by_account_txns=by_account_txns, rng=rng)
        issued = issued_row_for(account, rng)
        amount = round(rng.uniform(2000, 25000), 2)
        words = amount_to_words(amount)
        cheque_date = PROCESSING_DATE + timedelta(days=rng.randint(5, 60))
        sig_file = f"reference_signatures/{genuine_by_account[account.account_number][0]}"
        cid = next_cheque_id()
        samples.append(save_image_and_record(
            cid, BONUS_CATEGORY, account, issued["cheque_number"], issued["payee_name"], amount, words,
            cheque_date, sig_file, "Cheque date is after the processing date (future-dated).",
            account.account_status, "ISSUED", issued["payee_name"], amount, 1, "FUTURE_DATED",
        ))

    return samples, image_hash_rows, duplicate_source_records


# ---------------------------------------------------------------------------
# Duplicate-detection test data (docs/19 S18)
# ---------------------------------------------------------------------------


def generate_duplicate_detection_dataset(samples: list[SampleCheque]) -> list[dict]:
    dd_dir = TEST_DIR / "duplicate_detection"
    for sub in ("exact_duplicates", "near_duplicates", "unique_cheques"):
        target = dd_dir / sub
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)

    manifest: list[dict] = []
    duplicate_samples = [s for s in samples if s.category == "DUPLICATE"]
    if not duplicate_samples:
        return manifest

    base = duplicate_samples[0]  # the "already processed" original
    base_path = DATA_DIR / base.image_path

    # Exact duplicate: byte-identical copy
    exact_path = dd_dir / "exact_duplicates" / f"{base.cheque_id}_exact_copy.png"
    shutil.copyfile(base_path, exact_path)
    manifest.append({
        "test_case": "exact_duplicate", "source_cheque_id": base.cheque_id,
        "file": str(exact_path.relative_to(DATA_DIR)).replace("\\", "/"),
        "expected_result": "CONFIRMED_DUPLICATE",
    })

    # Near duplicate: crop + rotate + JPEG-recompress the same base image
    img = Image.open(base_path).convert("RGB")
    w, h = img.size
    cropped = img.crop((10, 10, w - 10, h - 10)).resize((w, h))
    rotated = cropped.rotate(1.5, expand=False, fillcolor=(250, 249, 244))
    near_path = dd_dir / "near_duplicates" / f"{base.cheque_id}_near_variant.jpg"
    rotated.save(near_path, format="JPEG", quality=70)
    manifest.append({
        "test_case": "near_duplicate", "source_cheque_id": base.cheque_id,
        "file": str(near_path.relative_to(DATA_DIR)).replace("\\", "/"),
        "expected_result": "POTENTIAL_DUPLICATE",
    })

    # Unique cheques: copy a couple of unrelated VALID samples for contrast
    valid_samples = [s for s in samples if s.category == "VALID"][:3]
    for s in valid_samples:
        src = DATA_DIR / s.image_path
        dst = dd_dir / "unique_cheques" / f"{s.cheque_id}.png"
        shutil.copyfile(src, dst)
        manifest.append({
            "test_case": "unique_cheque", "source_cheque_id": s.cheque_id,
            "file": str(dst.relative_to(DATA_DIR)).replace("\\", "/"),
            "expected_result": "NEW",
        })

    return manifest


# ---------------------------------------------------------------------------
# Signature test dataset (docs/18 S26-27)
# ---------------------------------------------------------------------------


def generate_signature_test_dataset(genuine_by_account: dict[str, list[str]]) -> list[dict]:
    sig_test_dir = TEST_DIR / "signatures"
    for sub in ("genuine", "altered", "low_quality", "missing", "partial"):
        target = sig_test_dir / sub
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)

    manifest = []
    sample_accounts = list(genuine_by_account.items())[:4]
    for account_number, files in sample_accounts:
        # genuine
        src = MOCK_DIR / "reference_signatures" / files[0]
        dst = sig_test_dir / "genuine" / f"{account_number}_genuine.png"
        shutil.copyfile(src, dst)
        manifest.append({"account_number": account_number, "category": "genuine",
                          "file": str(dst.relative_to(DATA_DIR)).replace("\\", "/")})

    for i, (account_number, _files) in enumerate(sample_accounts):
        altered_path = sig_test_dir / "altered" / f"{account_number}_altered.png"
        render_signature_image(altered_path, seed=SEED + 7000 + i, style="forged")
        manifest.append({"account_number": account_number, "category": "altered",
                          "file": str(altered_path.relative_to(DATA_DIR)).replace("\\", "/")})

        low_q_path = sig_test_dir / "low_quality" / f"{account_number}_low_quality.png"
        render_signature_image(low_q_path, seed=SEED + 7100 + i, style="low_quality")
        manifest.append({"account_number": account_number, "category": "low_quality",
                          "file": str(low_q_path.relative_to(DATA_DIR)).replace("\\", "/")})

        partial_path = sig_test_dir / "partial" / f"{account_number}_partial.png"
        render_signature_image(partial_path, seed=SEED + 7200 + i, style="partial")
        manifest.append({"account_number": account_number, "category": "partial",
                          "file": str(partial_path.relative_to(DATA_DIR)).replace("\\", "/")})

        missing_path = sig_test_dir / "missing" / f"{account_number}_missing.png"
        render_signature_image(missing_path, seed=SEED + 7300 + i, style="missing")
        manifest.append({"account_number": account_number, "category": "missing",
                          "file": str(missing_path.relative_to(DATA_DIR)).replace("\\", "/")})

    return manifest


# ---------------------------------------------------------------------------
# Validation / anomaly / fraud evaluation datasets
# ---------------------------------------------------------------------------


def generate_validation_test_cases(samples: list[SampleCheque], accounts: list[Account]) -> list[dict]:
    """The 10 test cases from docs/16_Validation_Engine.md S43."""
    by_id = {s.cheque_id: s for s in samples}
    valid = next(s for s in samples if s.category == "VALID")
    duplicate = next(s for s in samples if s.category == "DUPLICATE" and s.fraud_label == 1)
    payee_mismatch = next(s for s in samples if s.category == "PAYEE_TAMPERED")
    amount_mismatch = next(s for s in samples if s.category == "AMOUNT_TAMPERED")
    series_anomaly = next(s for s in samples if s.category == "CHEQUE_SERIES_ANOMALY")
    future_dated = next(s for s in samples if s.category == BONUS_CATEGORY)
    closed_account = next(s for s in samples if s.category == "INVALID_ACCOUNT" and s.expected_account_status in ("CLOSED", "BLOCKED", "FROZEN"))
    not_found_account = next(s for s in samples if s.category == "INVALID_ACCOUNT" and s.expected_account_status == "NOT_FOUND")

    active_accounts_with_series = [a for a in accounts if a.account_status == "ACTIVE"]
    reference_account = active_accounts_with_series[0]

    cases = [
        {"test_id": "VAL-001", "name": "Valid Account", "cheque_id": valid.cheque_id,
         "input": f"account={valid.account_number}", "expected": "PASS"},
        {"test_id": "VAL-002", "name": "Unknown Account", "cheque_id": not_found_account.cheque_id,
         "input": f"account={not_found_account.account_number}", "expected": "FAIL"},
        {"test_id": "VAL-003", "name": "Closed Account", "cheque_id": closed_account.cheque_id,
         "input": f"account={closed_account.account_number} status={closed_account.expected_account_status}",
         "expected": "FAIL"},
        {"test_id": "VAL-004", "name": "Valid Cheque Series", "cheque_id": valid.cheque_id,
         "input": f"cheque_number={valid.cheque_number} series=[{reference_account.cheque_series_start}-{reference_account.cheque_series_end}]",
         "expected": "PASS"},
        {"test_id": "VAL-005", "name": "Invalid Cheque Series", "cheque_id": series_anomaly.cheque_id,
         "input": f"cheque_number={series_anomaly.cheque_number}", "expected": "FAIL"},
        {"test_id": "VAL-006", "name": "Future-Dated Cheque", "cheque_id": future_dated.cheque_id,
         "input": f"cheque_date={future_dated.cheque_date} processing_date={PROCESSING_DATE.isoformat()}",
         "expected": "FAIL"},
        {"test_id": "VAL-007", "name": "Payee Match", "cheque_id": valid.cheque_id,
         "input": f"payee={valid.payee_name} expected={valid.expected_payee_name}", "expected": "PASS"},
        {"test_id": "VAL-008", "name": "Payee Mismatch", "cheque_id": payee_mismatch.cheque_id,
         "input": f"payee={payee_mismatch.payee_name} expected={payee_mismatch.expected_payee_name}",
         "expected": "FAIL"},
        {"test_id": "VAL-009", "name": "Duplicate", "cheque_id": duplicate.cheque_id,
         "input": f"account={duplicate.account_number} cheque_number={duplicate.cheque_number}",
         "expected": "FAIL"},
        {"test_id": "VAL-010", "name": "Amount Mismatch", "cheque_id": amount_mismatch.cheque_id,
         "input": f"amount={amount_mismatch.amount} words='{amount_mismatch.amount_in_words}'",
         "expected": "FAIL"},
    ]
    return cases


def generate_anomaly_test_cases(
    accounts: list[Account], payees: list[dict], by_account_txns: dict[str, list[dict]]
) -> list[dict]:
    """docs/20_Anomaly_Detection.md S39: normal / amount / frequency / payee /
    sequence / combined anomaly scenarios, expressed as transaction-level
    records rather than full cheque images (matching the doc's own CSV-based
    examples)."""
    rng = random.Random(SEED + 2)
    rows = []
    seq = 1

    def add(account, amount, payee_name, category, note):
        nonlocal seq
        history = by_account_txns.get(account.account_number, [])
        avg = sum(t["amount"] for t in history) / len(history) if history else None
        rows.append({
            "test_id": f"ANOM-{seq:03d}",
            "account_number": account.account_number,
            "amount": amount,
            "payee_name": payee_name,
            "historical_average": round(avg, 2) if avg is not None else "",
            "historical_transaction_count": len(history),
            "category": category,
            "notes": note,
        })
        seq += 1

    active_with_history = [a for a in accounts if a.account_status == "ACTIVE" and len(by_account_txns.get(a.account_number, [])) >= 4]
    cold_start = [a for a in accounts if len(by_account_txns.get(a.account_number, [])) == 0]

    # Normal transactions (5)
    for _ in range(5):
        account = rng.choice(active_with_history)
        history = by_account_txns[account.account_number]
        avg = sum(t["amount"] for t in history) / len(history)
        payee = history[-1]["payee_name"]
        amount = round(avg * rng.uniform(0.85, 1.15), 2)
        add(account, amount, payee, "NORMAL", "Amount and payee consistent with history.")

    # Amount anomalies: extremely high (2) and extremely low (2)
    for _ in range(2):
        account = rng.choice(active_with_history)
        history = by_account_txns[account.account_number]
        avg = sum(t["amount"] for t in history) / len(history)
        payee = history[-1]["payee_name"]
        add(account, round(avg * rng.uniform(15, 40), 2), payee, "AMOUNT_ANOMALY_HIGH",
            "Amount far exceeds historical average.")
    for _ in range(2):
        account = rng.choice(active_with_history)
        history = by_account_txns[account.account_number]
        avg = sum(t["amount"] for t in history) / len(history)
        payee = history[-1]["payee_name"]
        add(account, round(max(avg * 0.02, 1.0), 2), payee, "AMOUNT_ANOMALY_LOW",
            "Amount far below historical average.")

    # Frequency anomalies (3) -- represented via note since this is a
    # transaction-level dataset; frequency is computed from repeated rows
    # sharing an account with the same test_id prefix in production logic.
    for _ in range(3):
        account = rng.choice(active_with_history)
        history = by_account_txns[account.account_number]
        avg = sum(t["amount"] for t in history) / len(history)
        payee = history[-1]["payee_name"]
        add(account, round(avg, 2), payee, "FREQUENCY_ANOMALY",
            "Represents one of >10 cheques issued on this account within 48 hours (see notes).")

    # Payee anomalies (3): brand-new payee not in the account's history
    for _ in range(3):
        account = rng.choice(active_with_history)
        history = by_account_txns[account.account_number]
        avg = sum(t["amount"] for t in history) / len(history)
        known_payees = {t["payee_name"] for t in history}
        new_payee = next(p["payee_name"] for p in payees if p["payee_name"] not in known_payees)
        add(account, round(avg, 2), new_payee, "PAYEE_ANOMALY", "Payee not previously seen on this account.")

    # Sequence anomalies (3): reuse CHEQUE_SERIES_ANOMALY-style accounts
    for _ in range(3):
        account = rng.choice(active_with_history)
        history = by_account_txns[account.account_number]
        avg = sum(t["amount"] for t in history) / len(history)
        payee = history[-1]["payee_name"]
        add(account, round(avg, 2), payee, "SEQUENCE_ANOMALY",
            "Cheque number gap far outside the account's expected sequence.")

    # Combined anomalies (2): high amount + new payee + high frequency together
    for _ in range(2):
        account = rng.choice(active_with_history)
        history = by_account_txns[account.account_number]
        avg = sum(t["amount"] for t in history) / len(history)
        known_payees = {t["payee_name"] for t in history}
        new_payee = next(p["payee_name"] for p in payees if p["payee_name"] not in known_payees)
        add(account, round(avg * rng.uniform(10, 20), 2), new_payee, "MULTIPLE_ANOMALIES",
            "High amount + new payee + high frequency combined.")

    # Cold-start cases: must NOT be auto-flagged as anomalous (docs/20 S38)
    for account in cold_start[:3]:
        payee = rng.choice(payees)["payee_name"]
        add(account, round(rng.uniform(3000, 10000), 2), payee, "COLD_START",
            "New account with insufficient history; must not be auto-classified as anomalous.")

    return rows


def generate_fraud_labels(samples: list[SampleCheque]) -> list[dict]:
    """docs/33_Fraud_Model_Evaluation.md S6 ground-truth label format."""
    return [
        {"cheque_id": s.cheque_id, "label": s.fraud_label, "fraud_type": s.fraud_type}
        for s in samples
    ]


def generate_fraud_test_case_mapping(samples: list[SampleCheque]) -> list[dict]:
    """docs/33 S20 FRA-001..FRA-010 mapping onto concrete generated samples."""
    by_category: dict[str, SampleCheque] = {}
    for s in samples:
        by_category.setdefault(s.category, s)

    closed_account_sample = next(
        (s for s in samples if s.category == "INVALID_ACCOUNT" and s.expected_account_status in ("CLOSED", "BLOCKED", "FROZEN")),
        None,
    )
    low_conf_review_sample = by_category.get("MULTIPLE_ANOMALIES")

    mapping = [
        {"test_id": "FRA-001", "scenario": "Normal cheque", "cheque_id": by_category["VALID"].cheque_id,
         "expected_result": "Legitimate"},
        {"test_id": "FRA-002", "scenario": "Duplicate cheque",
         "cheque_id": next(s.cheque_id for s in samples if s.category == "DUPLICATE" and s.fraud_label == 1),
         "expected_result": "Fraud indicator"},
        {"test_id": "FRA-003", "scenario": "Signature mismatch", "cheque_id": by_category["SIGNATURE_MISMATCH"].cheque_id,
         "expected_result": "Suspicious"},
        {"test_id": "FRA-004", "scenario": "Image tampering", "cheque_id": by_category["AMOUNT_TAMPERED"].cheque_id,
         "expected_result": "Suspicious/Fraud"},
        {"test_id": "FRA-005", "scenario": "Unusual amount", "cheque_id": by_category["MULTIPLE_ANOMALIES"].cheque_id,
         "expected_result": "Anomaly"},
        {"test_id": "FRA-006", "scenario": "Payee mismatch", "cheque_id": by_category["PAYEE_TAMPERED"].cheque_id,
         "expected_result": "Suspicious"},
        {"test_id": "FRA-007", "scenario": "Closed account",
         "cheque_id": closed_account_sample.cheque_id if closed_account_sample else "",
         "expected_result": "Validation failure"},
        {"test_id": "FRA-008", "scenario": "Multiple fraud indicators", "cheque_id": by_category["MULTIPLE_ANOMALIES"].cheque_id,
         "expected_result": "High risk"},
        {"test_id": "FRA-009", "scenario": "Clear legitimate cheque", "cheque_id": by_category["VALID"].cheque_id,
         "expected_result": "Low risk"},
        {"test_id": "FRA-010", "scenario": "Low-confidence OCR + anomaly",
         "cheque_id": low_conf_review_sample.cheque_id if low_conf_review_sample else "",
         "expected_result": "Review"},
    ]
    return mapping


# ---------------------------------------------------------------------------
# CSV writing helpers
# ---------------------------------------------------------------------------


def write_csv(path: Path, rows: list[dict], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, default=str)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    print("Milestone 1 - generating synthetic data foundation...")

    for d in (MOCK_DIR, SAMPLE_DIR, TEST_DIR):
        d.mkdir(parents=True, exist_ok=True)

    customers = generate_customers(40)
    accounts = generate_accounts(customers)
    payees = generate_payees(25)
    issuance_rows, special_issuance = generate_cheque_issuance(accounts, payees)
    transactions, by_account_txns = generate_transactions(accounts, payees)
    sig_index_rows, genuine_by_account = generate_reference_signatures(accounts)

    samples, image_hash_rows, duplicate_sources = generate_sample_cheques(
        accounts, payees, issuance_rows, special_issuance, genuine_by_account, by_account_txns
    )

    duplicate_manifest = generate_duplicate_detection_dataset(samples)
    signature_test_manifest = generate_signature_test_dataset(genuine_by_account)
    validation_test_cases = generate_validation_test_cases(samples, accounts)
    anomaly_test_cases = generate_anomaly_test_cases(accounts, payees, by_account_txns)
    fraud_labels = generate_fraud_labels(samples)
    fraud_test_case_mapping = generate_fraud_test_case_mapping(samples)

    # processed_cheques history (docs/19 S32) derived from transaction history
    # plus the "already processed" duplicate-source cheques.
    processed_cheques_rows = []
    seq = 1
    for txn in transactions:
        processed_cheques_rows.append({
            "cheque_id": f"PROC-{seq:06d}",
            "account_number": txn["account_number"],
            "cheque_number": "",
            "payee_name": txn["payee_name"],
            "amount": txn["amount"],
            "cheque_date": txn["transaction_date"],
            "image_hash": "",
            "perceptual_hash": "",
            "processing_status": "PAID",
            "processed_at": txn["transaction_date"],
        })
        seq += 1
    for dup in duplicate_sources:
        img_row = next(r for r in image_hash_rows if r["cheque_id"] == dup["cheque_id"])
        processed_cheques_rows.append({
            "cheque_id": dup["cheque_id"],
            "account_number": dup["account_number"],
            "cheque_number": dup["cheque_number"],
            "payee_name": dup["payee_name"],
            "amount": dup["amount"],
            "cheque_date": dup["cheque_date"],
            "image_hash": img_row["image_hash"],
            "perceptual_hash": img_row["perceptual_hash"],
            "processing_status": "PAID",
            "processed_at": dup["cheque_date"],
        })

    # ---- write mock_banking_data/ -------------------------------------
    write_csv(MOCK_DIR / "customers.csv", customers,
              ["customer_id", "customer_name", "email", "phone", "status", "created_at"])

    accounts_rows = [
        {
            "account_number": a.account_number, "customer_id": a.customer_id,
            "account_status": a.account_status, "account_type": a.account_type,
            "balance": a.balance, "routing_number": a.routing_number,
            "bank_code": BANK_CODE, "cheque_series_start": a.cheque_series_start,
            "cheque_series_end": a.cheque_series_end,
        }
        for a in accounts
    ]
    write_csv(MOCK_DIR / "accounts.csv", accounts_rows,
              ["account_number", "customer_id", "account_status", "account_type", "balance",
               "routing_number", "bank_code", "cheque_series_start", "cheque_series_end"])

    write_csv(MOCK_DIR / "payees.csv", payees, ["payee_id", "payee_name", "payee_type"])

    write_csv(MOCK_DIR / "cheque_issuance.csv", issuance_rows,
              ["cheque_number", "account_number", "status", "payee_name", "amount_limit"])

    write_csv(MOCK_DIR / "transactions.csv", transactions,
              ["transaction_id", "account_number", "transaction_date", "transaction_type", "amount", "payee_name"])

    write_csv(MOCK_DIR / "processed_cheques_history.csv", processed_cheques_rows,
              ["cheque_id", "account_number", "cheque_number", "payee_name", "amount", "cheque_date",
               "image_hash", "perceptual_hash", "processing_status", "processed_at"])

    # ---- write test_data/ ----------------------------------------------
    gt_rows = [
        {
            "cheque_id": s.cheque_id, "category": s.category, "image_path": s.image_path,
            "account_number": s.account_number, "cheque_number": s.cheque_number,
            "routing_transit_number": s.routing_transit_number, "bank_name": s.bank_name,
            "payee_name": s.payee_name, "amount": s.amount, "amount_in_words": s.amount_in_words,
            "cheque_date": s.cheque_date, "signature_image": s.signature_image,
            "expected_account_status": s.expected_account_status,
            "expected_cheque_status": s.expected_cheque_status,
            "expected_payee_name": s.expected_payee_name, "expected_amount": s.expected_amount,
            "notes": s.notes, "fraud_label": s.fraud_label, "fraud_type": s.fraud_type,
        }
        for s in samples
    ]
    write_csv(TEST_DIR / "cheques_ground_truth.csv", gt_rows,
              list(gt_rows[0].keys()))

    write_csv(TEST_DIR / "image_hashes.csv", image_hash_rows,
              ["cheque_id", "image_path", "image_hash", "perceptual_hash"])

    write_csv(TEST_DIR / "validation_test_cases.csv", validation_test_cases,
              ["test_id", "name", "cheque_id", "input", "expected"])

    write_csv(TEST_DIR / "anomaly_test_cases.csv", anomaly_test_cases,
              ["test_id", "account_number", "amount", "payee_name", "historical_average",
               "historical_transaction_count", "category", "notes"])

    write_csv(TEST_DIR / "fraud_labels.csv", fraud_labels, ["cheque_id", "label", "fraud_type"])

    write_csv(TEST_DIR / "fraud_test_cases.csv", fraud_test_case_mapping,
              ["test_id", "scenario", "cheque_id", "expected_result"])

    write_csv(TEST_DIR / "duplicate_detection" / "manifest.csv", duplicate_manifest,
              ["test_case", "source_cheque_id", "file", "expected_result"])

    write_csv(TEST_DIR / "signatures" / "manifest.csv", signature_test_manifest,
              ["account_number", "category", "file"])

    summary = {
        "generated_at": datetime.now().isoformat(),
        "seed": SEED,
        "processing_date": PROCESSING_DATE.isoformat(),
        "counts": {
            "customers": len(customers),
            "accounts": len(accounts),
            "payees": len(payees),
            "cheque_issuance_records": len(issuance_rows),
            "transactions": len(transactions),
            "reference_signatures": len(sig_index_rows),
            "sample_cheques": len(samples),
            "processed_cheques_history": len(processed_cheques_rows),
            "validation_test_cases": len(validation_test_cases),
            "anomaly_test_cases": len(anomaly_test_cases),
            "fraud_labels": len(fraud_labels),
            "duplicate_detection_manifest_entries": len(duplicate_manifest),
            "signature_test_manifest_entries": len(signature_test_manifest),
        },
        "categories_generated": sorted({s.category for s in samples}),
    }
    write_json(TEST_DIR / "generation_summary.json", summary)

    print(json.dumps(summary, indent=2))
    print("Done.")


if __name__ == "__main__":
    main()

import numpy as np
import pandas as pd
import mysql.connector
from app.config import settings

# CONFIG
np.random.seed(42)


# MYSQL CONNECTION
def get_connection():
    return mysql.connector.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASSWORD,
        database=settings.DB_NAME
    )


def generate_data(n_rows: int, insert_to_db: bool = False):
    size = n_rows

    # -------------------------
    # Generate Features
    # -------------------------
    age = np.random.randint(21, 61, size)
    income = np.random.randint(200_000, 2_500_001, size)

    cibil = np.clip(
        np.random.normal(700, 100, size).astype(int),
        300, 900
    )

    emp = np.random.choice(
        ["Salaried", "Self-Employed"],
        size=size,
        p=[0.65, 0.35]
    )

    existing_loans = np.random.randint(0, 6, size)

    loan_amt = np.random.randint(100_000, 5_000_001, size)
    tenure = np.random.randint(12, 241, size)

    # -------------------------
    # Interest Rate Logic
    # -------------------------
    rate = np.where(
        cibil >= 750, 0.09,
        np.where(cibil >= 650, 0.11,
                 np.where(cibil >= 600, 0.14, 0.18))
    )

    monthly_rate = rate / 12

    emi = (
        loan_amt * monthly_rate * (1 + monthly_rate) ** tenure
        / ((1 + monthly_rate) ** tenure - 1)
    ).astype(int)

    # -------------------------
    # Risk Score Logic (UNCHANGED)
    # -------------------------
    emi_ratio = emi / (income / 12)

    cibil_risk = np.where(cibil < 600, 2,
                          np.where(cibil < 700, 1, 0))

    emi_risk = np.where(emi_ratio > 0.50, 2,
                        np.where(emi_ratio > 0.40, 1, 0))

    employment_risk = np.where(emp == "Self-Employed", 1, 0)

    loan_burden_risk = np.where(existing_loans >= 3, 1, 0)

    age_risk = np.where((age < 25) | (age > 55), 1, 0)

    risk_score = (
            2 * cibil_risk +
            2 * emi_risk +
            1 * employment_risk +
            1 * loan_burden_risk +
            1 * age_risk
    )

    default_prob = 1 / (1 + np.exp(-(risk_score - 5)))
    default_prob = default_prob * 0.25
    default_prob += np.random.uniform(0, 0.02, size)
    default_prob = np.clip(default_prob, 0, 0.4)

    default = np.random.binomial(1, default_prob)

    # -------------------------
    # Create DataFrame (NEW)
    # -------------------------
    df = pd.DataFrame({
        "age": age,
        "annual_income": income,
        "cibil_score": cibil,
        "employment_type": emp,
        "loan_amount": loan_amt,
        "loan_tenure": tenure,
        "emi": emi,
        "existing_loans": existing_loans,
        "default": default
    })

    # -------------------------
    # Optional DB Insert (SAME LOGIC)
    # -------------------------
    if insert_to_db:
        conn = get_connection()
        cursor = conn.cursor()

        insert_query = """
        INSERT INTO loan_data
        (age, annual_income, cibil_score, employment_type,
         loan_amount, loan_tenure, emi, existing_loans, `default`)
        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """

        data = list(df.itertuples(index=False, name=None))

        cursor.executemany(insert_query, data)
        conn.commit()

        cursor.close()
        conn.close()

    return df


# -------------------------
# SCRIPT MODE (ORIGINAL BEHAVIOR)
# -------------------------
if __name__ == "__main__":
    TOTAL_ROWS = 10_000_000
    BATCH_SIZE = 100_000

    rows_inserted = 0

    while rows_inserted < TOTAL_ROWS:
        size = min(BATCH_SIZE, TOTAL_ROWS - rows_inserted)

        generate_data(size, insert_to_db=True)

        rows_inserted += size
        print(f"Inserted {rows_inserted:,} rows")

    print("10 Million Rows Inserted Successfully!")

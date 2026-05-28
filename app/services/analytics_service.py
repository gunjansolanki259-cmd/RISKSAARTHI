from app.services.db_service import get_connection
from app.utils.logger import user_activity_logger


# ------------------------------------------------
# ANALYTICS DASHBOARD
# ------------------------------------------------

def get_analytics_data(user_id=None, mode="user"):

    user_activity_logger.info(f"Analytics requested | mode={mode} | user_id={user_id}")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        # =================================================
        # BASE FILTER
        # =================================================

        where_clause = ""
        params = ()

        if mode == "user" and user_id:
            where_clause = "WHERE la.user_id = %s"
            params = (user_id,)

        # =================================================
        # HOME KPIs (ALL-TIME)
        # =================================================

        query = f"""
            SELECT COUNT(*) AS total
            FROM prediction_results pr
            JOIN loan_applications la
            ON la.application_id = pr.application_id
            {where_clause}
        """
        cursor.execute(query, params)
        total_all = cursor.fetchone().get("total", 0)

        query = f"""
            SELECT COUNT(*) AS high_risk
            FROM prediction_results pr
            JOIN loan_applications la
            ON la.application_id = pr.application_id
            {where_clause}
            AND pr.risk_category = 'High Risk'
        """ if where_clause else """
            SELECT COUNT(*) AS high_risk
            FROM prediction_results
            WHERE risk_category = 'High Risk'
        """

        cursor.execute(query, params if where_clause else ())
        high_risk_all = cursor.fetchone().get("high_risk", 0)

        query = f"""
            SELECT AVG(pr.credit_score) AS avg_score
            FROM prediction_results pr
            JOIN loan_applications la
            ON la.application_id = pr.application_id
            {where_clause}
        """
        cursor.execute(query, params)
        avg_all = cursor.fetchone().get("avg_score") or 0

        # =================================================
        # LAST 30 DAYS
        # =================================================

        query = f"""
            SELECT COUNT(*) AS total
            FROM prediction_results pr
            JOIN loan_applications la
            ON la.application_id = pr.application_id
            {where_clause}
            AND pr.prediction_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """ if where_clause else """
            SELECT COUNT(*) AS total
            FROM prediction_results
            WHERE prediction_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """

        cursor.execute(query, params if where_clause else ())
        total_30 = cursor.fetchone().get("total", 0)

        query = f"""
            SELECT COUNT(*) AS high_risk
            FROM prediction_results pr
            JOIN loan_applications la
            ON la.application_id = pr.application_id
            {where_clause}
            AND pr.risk_category = 'High Risk'
            AND pr.prediction_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """ if where_clause else """
            SELECT COUNT(*) AS high_risk
            FROM prediction_results
            WHERE risk_category = 'High Risk'
            AND prediction_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """

        cursor.execute(query, params if where_clause else ())
        high_risk_30 = cursor.fetchone().get("high_risk", 0)

        query = f"""
            SELECT AVG(pr.credit_score) AS avg_score
            FROM prediction_results pr
            JOIN loan_applications la
            ON la.application_id = pr.application_id
            {where_clause}
            AND pr.prediction_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """ if where_clause else """
            SELECT AVG(credit_score) AS avg_score
            FROM prediction_results
            WHERE prediction_time >= DATE_SUB(NOW(), INTERVAL 30 DAY)
        """

        cursor.execute(query, params if where_clause else ())
        avg_30 = cursor.fetchone().get("avg_score") or 0

        # =================================================
        # DISTRIBUTIONS
        # =================================================

        query = f"""
            SELECT pr.risk_category AS risk_level, COUNT(*) AS count
            FROM prediction_results pr
            JOIN loan_applications la
            ON la.application_id = pr.application_id
            {where_clause}
            GROUP BY pr.risk_category
        """ if where_clause else """
            SELECT risk_category AS risk_level, COUNT(*) AS count
            FROM prediction_results
            GROUP BY risk_category
        """

        cursor.execute(query, params if where_clause else ())
        risk_distribution = cursor.fetchall()

        query = f"""
            SELECT
                CASE
                    WHEN pr.risk_category = 'High Risk' THEN 'Likely Default'
                    ELSE 'Likely Non-Default'
                END AS default_status,
                COUNT(*) AS count
            FROM prediction_results pr
            JOIN loan_applications la
            ON la.application_id = pr.application_id
            {where_clause}
            GROUP BY default_status
        """ if where_clause else """
            SELECT
                CASE
                    WHEN risk_category = 'High Risk' THEN 'Likely Default'
                    ELSE 'Likely Non-Default'
                END AS default_status,
                COUNT(*) AS count
            FROM prediction_results
            GROUP BY default_status
        """

        cursor.execute(query, params if where_clause else ())
        default_distribution = cursor.fetchall()

        # =================================================
        # TOP HIGH RISK BORROWERS (FIXED)
        # =================================================

        query = """
            SELECT
                la.user_id,
                la.applicant_id,
                pr.credit_score,
                la.loan_amount,
                pr.default_probability AS risk_probability
            FROM loan_applications la
            JOIN prediction_results pr
                ON la.application_id = pr.application_id
        """

        params = ()

        # USER FILTER
        if mode == "user" and user_id:
            query += " WHERE la.user_id = %s AND pr.risk_category = 'High Risk'"
            params = (user_id,)
        else:
            query += " WHERE pr.risk_category = 'High Risk'"

        # SORT + LIMIT
        query += """
            ORDER BY pr.default_probability DESC
            LIMIT 5
        """

        cursor.execute(query, params)
        top_risk_borrowers = cursor.fetchall()

        # =================================================
        # REMAINING
        # =================================================

        # Income vs Loan
        query = f"""
            SELECT la.annual_income, la.loan_amount,
                COALESCE(pr.credit_score, 0) AS credit_score,
                COALESCE(pr.risk_category, 'Unknown') AS risk_level
            FROM loan_applications la
            LEFT JOIN prediction_results pr
            ON la.application_id = pr.application_id
            {where_clause}
        """
        cursor.execute(query, params)
        income_loan_relation = cursor.fetchall()

        # Monthly trend
        query = f"""
            SELECT
                DATE_FORMAT(pr.prediction_time, '%b %Y') AS month,
                COUNT(*) AS applications
            FROM prediction_results pr
            JOIN loan_applications la
            ON la.application_id = pr.application_id
            {where_clause}
            GROUP BY month
            ORDER BY MIN(pr.prediction_time)
        """ if where_clause else """
            SELECT
                DATE_FORMAT(prediction_time, '%b %Y') AS month,
                COUNT(*) AS applications
            FROM prediction_results
            GROUP BY month
            ORDER BY MIN(prediction_time)
        """

        cursor.execute(query, params if where_clause else ())
        monthly_trend = cursor.fetchall()

        # Credit Behavior
        query = f"""
            SELECT
                CASE
                    WHEN pr.credit_score BETWEEN 300 AND 500 THEN '300-500'
                    WHEN pr.credit_score BETWEEN 501 AND 650 THEN '501-650'
                    WHEN pr.credit_score BETWEEN 651 AND 700 THEN '651-700'
                    WHEN pr.credit_score BETWEEN 701 AND 750 THEN '701-750'
                    ELSE '751-900'
                END AS cibil_range,
                COUNT(*) AS borrowers
            FROM prediction_results pr
            JOIN loan_applications la
            ON la.application_id = pr.application_id
            {where_clause}
            GROUP BY cibil_range
        """
        cursor.execute(query, params)
        credit_behavior = cursor.fetchall()


        query = f"""
            SELECT
                CASE
                    WHEN la.annual_income < 300000 THEN 'Low Income'
                    WHEN la.annual_income BETWEEN 300000 AND 800000 THEN 'Middle Income'
                    ELSE 'High Income'
                END AS income_group,
                COALESCE(pr.risk_category, 'Unknown') AS risk_level,
                COUNT(*) AS count
            FROM loan_applications la
            LEFT JOIN prediction_results pr
            ON la.application_id = pr.application_id
            {where_clause}
            GROUP BY income_group, risk_level
        """
        cursor.execute(query, params)
        risk_by_income = cursor.fetchall()


        query = f"""
            SELECT 
                COALESCE(pr.credit_score, 0) AS credit_score,
                COALESCE(pr.default_probability, 0) AS risk_probability
            FROM loan_applications la
            LEFT JOIN prediction_results pr
            ON la.application_id = pr.application_id
            {where_clause}
        """
        cursor.execute(query, params)
        credit_vs_risk = cursor.fetchall()


        query = f"""
            SELECT loan_amount, COUNT(*) AS count
            FROM loan_applications la
            {where_clause}
            GROUP BY loan_amount
        """
        cursor.execute(query, params)
        loan_amount_distribution = cursor.fetchall()



        query = f"""
            SELECT la.age, la.loan_amount,
                COALESCE(pr.credit_score, 0) AS credit_score,
                COALESCE(pr.risk_category, 'Unknown') AS risk_level,
                COALESCE(pr.default_probability, 0) AS risk_probability
            FROM loan_applications la
            LEFT JOIN prediction_results pr
            ON la.application_id = pr.application_id
            {where_clause}
        """
        cursor.execute(query, params)
        age_vs_loan = cursor.fetchall()

        # =================================================
        # FINAL RESPONSE
        # =================================================

        return {
            "total_applications": total_all,
            "high_risk_cases": high_risk_all,
            "average_credit_score": round(avg_all, 2),

            "recent_total": total_30,
            "recent_high_risk": high_risk_30,
            "recent_avg_score": round(avg_30, 2),

            "top_risk_borrowers": top_risk_borrowers,
            "risk_distribution": risk_distribution,
            "default_distribution": default_distribution,
            "income_loan_relation": income_loan_relation,
            "credit_behavior": credit_behavior,
            "credit_vs_risk": credit_vs_risk,
            "monthly_trend": monthly_trend,

            "risk_by_income": risk_by_income,
            "loan_amount_distribution": loan_amount_distribution,
            "age_vs_loan": age_vs_loan
        }

    except Exception as e:
        user_activity_logger.error(f"Analytics Error: {str(e)}")
        raise

    finally:
        cursor.close()
        conn.close()


# ------------------------------------------------
# PREDICTION HISTORY
# ------------------------------------------------

def get_prediction_history(user_id=None, mode="user"):

    user_activity_logger.info(f"History requested | mode={mode} | user_id={user_id}")

    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:

        query = """
            SELECT
                la.applicant_id,
                la.age,
                la.annual_income,
                la.cibil_score,
                la.loan_amount,
                COALESCE(pr.risk_category, 'Unknown') AS risk_level,
                pr.credit_score,
                pr.default_probability AS risk_probability,
                pr.prediction_time
            FROM loan_applications la
            JOIN prediction_results pr
            ON la.application_id = pr.application_id
        """

        params = ()

        if mode == "user" and user_id:
            query += " WHERE la.user_id = %s"
            params = (user_id,)

        query += " ORDER BY pr.prediction_time DESC LIMIT 100"

        cursor.execute(query, params)

        return cursor.fetchall()

    except Exception as e:
        user_activity_logger.error(f"History Error: {str(e)}")
        raise

    finally:
        cursor.close()
        conn.close()

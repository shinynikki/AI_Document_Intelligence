# =========================================================
# Financial Validation Service
# =========================================================

from typing import Any, Optional


# =========================================================
# Generic Numeric Helpers
# =========================================================


def check_value(
    calculated: Optional[float],
    reported: Optional[float],
    tolerance: float = 0.01
) -> dict:
    """
    Compare a calculated value with a reported value.

    Missing values result in NOT_APPLICABLE instead of FAILED.
    This prevents incomplete OCR/LLM extraction from being
    incorrectly treated as a financial error.
    """

    if calculated is None or reported is None:
        return {
            "status": "NOT_APPLICABLE",
            "calculated": calculated,
            "reported": reported,
            "variance": None
        }

    variance = round(calculated - reported, 2)

    status = (
        "PASS"
        if abs(variance) <= tolerance
        else "FAILED"
    )

    return {
        "status": status,
        "calculated": round(calculated, 2),
        "reported": round(reported, 2),
        "variance": variance
    }


def safe_float(value: Any) -> Optional[float]:
    """
    Safely convert a value to float.

    Returns None for missing or invalid values.
    """

    if value is None:
        return None

    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate_tax(
    taxable_amount: Optional[float],
    tax_rate: Optional[float]
) -> Optional[float]:
    """
    Calculate tax from taxable amount and tax rate.
    """

    taxable_amount = safe_float(taxable_amount)
    tax_rate = safe_float(tax_rate)

    if taxable_amount is None or tax_rate is None:
        return None

    return round(
        taxable_amount * tax_rate / 100,
        2
    )


def append_validation(
    validations: list,
    check: str,
    result: dict,
    inputs: Optional[dict] = None,
    period: Optional[str] = None
) -> None:
    """
    Append a validation result in a consistent format.
    """

    validation = {
        "check": check,
        "inputs": inputs or {},
        **result
    }

    if period is not None:
        validation["period"] = period

    validations.append(validation)


# =========================================================
# Invoice Validation
# =========================================================


def validate_invoice(invoice) -> list:
    """
    Validate invoice calculations.

    Important invoice accounting logic:

        quantity × unit_price ≈ taxable_amount

        taxable_amount + tax_amount + round_off ≈ total_amount

    The final line amount may include tax. Therefore, it must
    not be compared directly against quantity × unit price.
    """

    validations = []

    # -----------------------------------------------------
    # 1. Validate every line item
    # -----------------------------------------------------

    for index, item in enumerate(
        invoice.line_items,
        start=1
    ):

        quantity = safe_float(item.quantity)
        unit_price = safe_float(item.unit_price)
        taxable_amount = safe_float(item.taxable_amount)
        reported_amount = safe_float(item.amount)
        tax_rate = safe_float(item.tax_rate)
        reported_tax = safe_float(item.tax_amount)

        # -------------------------------------------------
        # Check quantity × unit price ≈ taxable amount
        # -------------------------------------------------

        if (
            quantity is not None
            and unit_price is not None
        ):
            calculated_taxable_amount = round(
                quantity * unit_price,
                2
            )
        else:
            calculated_taxable_amount = None

        result = check_value(
            calculated_taxable_amount,
            taxable_amount,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            check=(
                f"Line item {index}: "
                "quantity × unit price ≈ taxable amount"
            ),
            inputs={
                "quantity": quantity,
                "unit_price": unit_price,
                "reported_taxable_amount": taxable_amount
            },
            result=result
        )

        # -------------------------------------------------
        # Check taxable amount + tax ≈ final line amount
        #
        # Only perform this when enough tax information exists.
        # -------------------------------------------------

        calculated_tax = reported_tax

        if calculated_tax is None:
            calculated_tax = calculate_tax(
                taxable_amount,
                tax_rate
            )

        if (
            taxable_amount is not None
            and calculated_tax is not None
            and reported_amount is not None
        ):

            calculated_line_total = round(
                taxable_amount + calculated_tax,
                2
            )

            result = check_value(
                calculated_line_total,
                reported_amount,
                tolerance=0.02
            )

            append_validation(
                validations=validations,
                check=(
                    f"Line item {index}: "
                    "taxable amount + tax ≈ line total"
                ),
                inputs={
                    "taxable_amount": taxable_amount,
                    "tax_rate": tax_rate,
                    "calculated_tax": calculated_tax,
                    "reported_tax": reported_tax,
                    "reported_line_total": reported_amount
                },
                result=result
            )

    # -----------------------------------------------------
    # 2. Sum of taxable amounts ≈ subtotal
    # -----------------------------------------------------

    taxable_amounts = [
        safe_float(item.taxable_amount)
        for item in invoice.line_items
        if safe_float(item.taxable_amount) is not None
    ]

    reported_subtotal = safe_float(invoice.subtotal)

    if taxable_amounts and reported_subtotal is not None:

        calculated_subtotal = round(
            sum(taxable_amounts),
            2
        )

        result = check_value(
            calculated_subtotal,
            reported_subtotal,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            check=(
                "Sum of taxable line amounts ≈ subtotal"
            ),
            inputs={
                "taxable_line_amounts": taxable_amounts,
                "reported_subtotal": reported_subtotal
            },
            result=result
        )

    else:

        append_validation(
            validations=validations,
            check=(
                "Sum of taxable line amounts ≈ subtotal"
            ),
            inputs={},
            result={
                "status": "NOT_APPLICABLE",
                "calculated": None,
                "reported": reported_subtotal,
                "variance": None
            }
        )

    # -----------------------------------------------------
    # 3. Taxable amount + tax + round off ≈ total amount
    # -----------------------------------------------------

    taxable_amount = safe_float(invoice.taxable_amount)
    tax_amount = safe_float(invoice.tax_amount)
    total_amount = safe_float(invoice.total_amount)
    round_off = safe_float(invoice.round_off)

    # If round_off is absent, treat it as zero because it is
    # an optional adjustment.
    if round_off is None:
        round_off = 0.0

    if (
        taxable_amount is not None
        and tax_amount is not None
        and total_amount is not None
    ):

        calculated_total = round(
            taxable_amount
            + tax_amount
            + round_off,
            2
        )

        result = check_value(
            calculated_total,
            total_amount,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            check=(
                "Taxable amount + tax + round off "
                "≈ total amount"
            ),
            inputs={
                "taxable_amount": taxable_amount,
                "tax_amount": tax_amount,
                "round_off": round_off,
                "reported_total": total_amount
            },
            result=result
        )

    else:

        append_validation(
            validations=validations,
            check=(
                "Taxable amount + tax + round off "
                "≈ total amount"
            ),
            inputs={},
            result={
                "status": "NOT_APPLICABLE",
                "calculated": None,
                "reported": total_amount,
                "variance": None
            }
        )

    return validations


# =========================================================
# Financial Statement Helper Functions
# =========================================================


def get_period_value(
    line_item,
    period
) -> Optional[float]:
    """
    Get the value of a financial line item for a period.
    """

    if line_item is None:
        return None

    values = getattr(line_item, "values", []) or []

    for period_value in values:

        if period_value.period == period:
            return safe_float(period_value.value)

    return None


def find_total(line_items):
    """
    Find a line item whose label contains Total.

    This is more tolerant than exact matching because extracted
    financial statements may contain labels such as:
        Total income
        Total expenditure
        Total assets
        Total liabilities
    """

    for item in line_items or []:

        label = str(
            getattr(item, "label", "")
        ).strip().lower()

        if label == "total" or label.startswith("total "):
            return item

    return None


def find_line_item(
    line_items,
    label
):
    """
    Find a financial line item by exact case-insensitive label.
    """

    target = label.strip().lower()

    for item in line_items or []:

        current_label = str(
            getattr(item, "label", "")
        ).strip().lower()

        if current_label == target:
            return item

    return None


def sum_line_items(
    line_items,
    period
) -> Optional[float]:
    """
    Sum all non-total line items for a period.

    If any component is missing, return None rather than
    inventing a value.
    """

    values = []

    for item in line_items or []:

        label = str(
            getattr(item, "label", "")
        ).strip().lower()

        if label == "total" or label.startswith("total "):
            continue

        value = get_period_value(
            item,
            period
        )

        if value is None:
            return None

        values.append(value)

    if not values:
        return None

    return round(sum(values), 2)


# =========================================================
# Balance Sheet Validation
# =========================================================


def validate_balance_sheet(balance_sheet) -> list:
    """
    Validate Balance Sheet relationships.
    """

    validations = []

    liabilities_total_item = find_total(
        balance_sheet.liabilities
    )

    assets_total_item = find_total(
        balance_sheet.assets
    )

    for period in balance_sheet.periods:

        liabilities_total = get_period_value(
            liabilities_total_item,
            period
        )

        assets_total = get_period_value(
            assets_total_item,
            period
        )

        # -------------------------------------------------
        # 1. Liabilities total ≈ Assets total
        # -------------------------------------------------

        result = check_value(
            liabilities_total,
            assets_total,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            period=period,
            check=(
                "Capital and liabilities total "
                "≈ assets total"
            ),
            inputs={
                "capital_and_liabilities_total": liabilities_total,
                "assets_total": assets_total
            },
            result=result
        )

        # -------------------------------------------------
        # 2. Sum of liability components ≈ liabilities total
        # -------------------------------------------------

        calculated_liabilities = sum_line_items(
            balance_sheet.liabilities,
            period
        )

        result = check_value(
            calculated_liabilities,
            liabilities_total,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            period=period,
            check=(
                "Sum of capital and liability components "
                "≈ reported total"
            ),
            inputs={
                "component_sum": calculated_liabilities,
                "reported_total": liabilities_total
            },
            result=result
        )

        # -------------------------------------------------
        # 3. Sum of asset components ≈ assets total
        # -------------------------------------------------

        calculated_assets = sum_line_items(
            balance_sheet.assets,
            period
        )

        result = check_value(
            calculated_assets,
            assets_total,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            period=period,
            check=(
                "Sum of asset components "
                "≈ reported total"
            ),
            inputs={
                "component_sum": calculated_assets,
                "reported_total": assets_total
            },
            result=result
        )

    return validations


# =========================================================
# Profit & Loss Validation
# =========================================================


def validate_profit_loss(profit_loss) -> list:
    """
    Validate Profit & Loss statement relationships.
    """

    validations = []

    income_total_item = find_total(
        profit_loss.income
    )

    expenditure_total_item = find_total(
        profit_loss.expenditure
    )

    profit_total_item = find_total(
        profit_loss.profit
    )

    appropriations_total_item = find_total(
        profit_loss.appropriations
    )

    net_profit_item = find_line_item(
        profit_loss.profit,
        "Net profit for the year"
    )

    minority_interest_item = find_line_item(
        profit_loss.profit,
        "Less: Minority interest"
    )

    associates_profit_item = find_line_item(
        profit_loss.profit,
        "Add: Share in profits of associates"
    )

    consolidated_profit_item = find_line_item(
        profit_loss.profit,
        "Consolidated profit for the year attributable to the Group"
    )

    amalgamation_item = find_line_item(
        profit_loss.profit,
        "Impact on amalgamation [Refer Schedule 18(1)]"
    )

    balance_brought_forward_item = find_line_item(
        profit_loss.profit,
        "Balance in Profit and Loss account brought forward"
    )

    for period in profit_loss.periods:

        # -------------------------------------------------
        # Get totals
        # -------------------------------------------------

        reported_income_total = get_period_value(
            income_total_item,
            period
        )

        reported_expenditure_total = get_period_value(
            expenditure_total_item,
            period
        )

        reported_profit_total = get_period_value(
            profit_total_item,
            period
        )

        reported_appropriations_total = get_period_value(
            appropriations_total_item,
            period
        )

        # -------------------------------------------------
        # Income components
        # -------------------------------------------------

        interest_earned_item = find_line_item(
            profit_loss.income,
            "Interest earned"
        )

        other_income_item = find_line_item(
            profit_loss.income,
            "Other income"
        )

        interest_earned = get_period_value(
            interest_earned_item,
            period
        )

        other_income = get_period_value(
            other_income_item,
            period
        )

        if (
            interest_earned is not None
            and other_income is not None
        ):

            calculated_income_total = round(
                interest_earned + other_income,
                2
            )

        else:

            calculated_income_total = None

        result = check_value(
            calculated_income_total,
            reported_income_total,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            period=period,
            check=(
                "Interest earned + other income "
                "≈ total income"
            ),
            inputs={
                "interest_earned": interest_earned,
                "other_income": other_income,
                "reported_total_income": reported_income_total
            },
            result=result
        )

        # -------------------------------------------------
        # All income components ≈ total income
        # -------------------------------------------------

        calculated_income_components = sum_line_items(
            profit_loss.income,
            period
        )

        result = check_value(
            calculated_income_components,
            reported_income_total,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            period=period,
            check=(
                "Sum of income components "
                "≈ reported total income"
            ),
            inputs={
                "component_sum": calculated_income_components,
                "reported_total": reported_income_total
            },
            result=result
        )

        # -------------------------------------------------
        # Expenditure components
        # -------------------------------------------------

        interest_expended_item = find_line_item(
            profit_loss.expenditure,
            "Interest expended"
        )

        operating_expenses_item = find_line_item(
            profit_loss.expenditure,
            "Operating expenses"
        )

        provisions_item = find_line_item(
            profit_loss.expenditure,
            "Provisions and contingencies"
        )

        interest_expended = get_period_value(
            interest_expended_item,
            period
        )

        operating_expenses = get_period_value(
            operating_expenses_item,
            period
        )

        provisions = get_period_value(
            provisions_item,
            period
        )

        if (
            interest_expended is not None
            and operating_expenses is not None
            and provisions is not None
        ):

            calculated_expenditure_total = round(
                interest_expended
                + operating_expenses
                + provisions,
                2
            )

        else:

            calculated_expenditure_total = None

        result = check_value(
            calculated_expenditure_total,
            reported_expenditure_total,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            period=period,
            check=(
                "Interest expended + operating expenses "
                "+ provisions and contingencies "
                "≈ total expenditure"
            ),
            inputs={
                "interest_expended": interest_expended,
                "operating_expenses": operating_expenses,
                "provisions_and_contingencies": provisions,
                "reported_total_expenditure": reported_expenditure_total
            },
            result=result
        )

        # -------------------------------------------------
        # All expenditure components ≈ total expenditure
        # -------------------------------------------------

        calculated_expenditure_components = sum_line_items(
            profit_loss.expenditure,
            period
        )

        result = check_value(
            calculated_expenditure_components,
            reported_expenditure_total,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            period=period,
            check=(
                "Sum of expenditure components "
                "≈ reported total expenditure"
            ),
            inputs={
                "component_sum": calculated_expenditure_components,
                "reported_total": reported_expenditure_total
            },
            result=result
        )

        # -------------------------------------------------
        # Total income - total expenditure ≈ net profit
        # -------------------------------------------------

        net_profit = get_period_value(
            net_profit_item,
            period
        )

        if (
            reported_income_total is not None
            and reported_expenditure_total is not None
        ):

            calculated_net_profit = round(
                reported_income_total
                - reported_expenditure_total,
                2
            )

        else:

            calculated_net_profit = None

        result = check_value(
            calculated_net_profit,
            net_profit,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            period=period,
            check=(
                "Total income - total expenditure "
                "≈ net profit for the year"
            ),
            inputs={
                "total_income": reported_income_total,
                "total_expenditure": reported_expenditure_total,
                "reported_net_profit": net_profit
            },
            result=result
        )

        # -------------------------------------------------
        # Net profit - minority interest
        # + associates profit ≈ consolidated profit
        # -------------------------------------------------

        minority_interest = get_period_value(
            minority_interest_item,
            period
        )

        associates_profit = get_period_value(
            associates_profit_item,
            period
        )

        consolidated_profit = get_period_value(
            consolidated_profit_item,
            period
        )

        if (
            net_profit is not None
            and minority_interest is not None
            and associates_profit is not None
        ):

            calculated_consolidated_profit = round(
                net_profit
                - minority_interest
                + associates_profit,
                2
            )

        else:

            calculated_consolidated_profit = None

        result = check_value(
            calculated_consolidated_profit,
            consolidated_profit,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            period=period,
            check=(
                "Net profit - minority interest "
                "+ share in profits of associates "
                "≈ consolidated profit attributable to the Group"
            ),
            inputs={
                "net_profit": net_profit,
                "minority_interest": minority_interest,
                "share_in_profits_of_associates": associates_profit,
                "reported_consolidated_profit": consolidated_profit
            },
            result=result
        )

        # -------------------------------------------------
        # Consolidated profit + amalgamation
        # + brought-forward balance ≈ total
        # -------------------------------------------------

        amalgamation = get_period_value(
            amalgamation_item,
            period
        )

        balance_brought_forward = get_period_value(
            balance_brought_forward_item,
            period
        )

        if (
            consolidated_profit is not None
            and amalgamation is not None
            and balance_brought_forward is not None
        ):

            calculated_profit_total = round(
                consolidated_profit
                + amalgamation
                + balance_brought_forward,
                2
            )

        else:

            calculated_profit_total = None

        result = check_value(
            calculated_profit_total,
            reported_profit_total,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            period=period,
            check=(
                "Consolidated profit + impact on amalgamation "
                "+ balance brought forward ≈ total"
            ),
            inputs={
                "consolidated_profit": consolidated_profit,
                "impact_on_amalgamation": amalgamation,
                "balance_brought_forward": balance_brought_forward,
                "reported_total": reported_profit_total
            },
            result=result
        )

        # -------------------------------------------------
        # Appropriations components ≈ total appropriations
        # -------------------------------------------------

        calculated_appropriations = sum_line_items(
            profit_loss.appropriations,
            period
        )

        result = check_value(
            calculated_appropriations,
            reported_appropriations_total,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            period=period,
            check=(
                "Sum of appropriation components "
                "≈ reported appropriation total"
            ),
            inputs={
                "component_sum": calculated_appropriations,
                "reported_total": reported_appropriations_total
            },
            result=result
        )

    return validations


# =========================================================
# Cash Flow Validation
# =========================================================


def normalize_label(label: str) -> str:
    """
    Normalize a financial line-item label for tolerant matching.

    Handles differences in:
    - Capitalization
    - Multiple spaces
    - Punctuation
    - Parentheses
    - Slashes
    - Hyphens
    """

    if not label:
        return ""

    normalized = str(label).strip().lower()

    # Replace common dash variants with a normal hyphen
    normalized = (
        normalized
        .replace("–", "-")
        .replace("—", "-")
    )

    # Replace punctuation with spaces
    for character in [
        "(",
        ")",
        "/",
        ",",
        ".",
        ":",
        ";",
        "-"
    ]:
        normalized = normalized.replace(
            character,
            " "
        )

    # Collapse multiple spaces
    normalized = " ".join(
        normalized.split()
    )

    return normalized


def find_line_item_contains(
    line_items,
    *possible_labels
):
    """
    Find a financial line item using tolerant label matching.

    Handles variations such as:

        Net cash flow used in investing activities

        Net cash used in investing activities

        Net cash flow from / (used in) financing activities

        Net cash generated from financing activities
    """

    normalized_targets = [
        normalize_label(label)
        for label in possible_labels
    ]

    for item in line_items or []:

        current_label = normalize_label(
            getattr(item, "label", "")
        )

        for target in normalized_targets:

            if not target:
                continue

            # Exact normalized match
            if current_label == target:
                return item

            # Contains match
            if target in current_label:
                return item

    return None


def validate_cash_flow(cash_flow) -> list:
    """
    Validate Cash Flow Statement relationships.

    Checks:

        Operating cash flow
        + Investing cash flow
        + Financing cash flow
        + FX adjustment
        ≈ Net increase / decrease in cash

    And:

        Opening cash
        + Net increase / decrease
        ≈ Closing cash

    Missing values result in NOT_APPLICABLE.
    Actual calculation mismatches remain FAILED.
    """

    validations = []

    # -----------------------------------------------------
    # Find total activity line items
    # -----------------------------------------------------

    operating_total_item = find_line_item_contains(
        cash_flow.operating_activities,

        "Net cash flow from operating activities",
        "Net cash flow used in operating activities",
        "Net cash flow (used in) / from operating activities",
        "Net cash from operating activities",
        "Net cash used in operating activities"
    )

    investing_total_item = find_line_item_contains(
        cash_flow.investing_activities,

        "Net cash flow from investing activities",
        "Net cash flow used in investing activities",
        "Net cash used in investing activities",
        "Net cash from investing activities"
    )

    financing_total_item = find_line_item_contains(
        cash_flow.financing_activities,

        "Net cash flow from financing activities",
        "Net cash flow used in financing activities",
        "Net cash flow from / (used in) financing activities",
        "Net cash generated from financing activities",
        "Net cash from financing activities"
    )

    # -----------------------------------------------------
    # Find reconciliation line items
    # -----------------------------------------------------

    net_change_item = find_line_item_contains(
        cash_flow.reconciliation,

        "Net increase in cash and cash equivalents",
        "Net decrease in cash and cash equivalents",
        "Net increase / (decrease) in cash and cash equivalents",
        "Net increase (decrease) in cash and cash equivalents",
        "Net change in cash and cash equivalents"
    )

    opening_cash_item = find_line_item_contains(
        cash_flow.reconciliation,

        "Cash and cash equivalents as at April 1st",
        "Cash and cash equivalents as at April 1",
        "Cash and cash equivalents at April 1st",
        "Cash and cash equivalents at April 1",
        "Opening cash"
    )

    closing_cash_item = find_line_item_contains(
        cash_flow.reconciliation,

        "Cash and cash equivalents as at March 31st",
        "Cash and cash equivalents as at March 31",
        "Cash and cash equivalents at March 31st",
        "Cash and cash equivalents at March 31",
        "Closing cash"
    )

    # -----------------------------------------------------
    # Find FX adjustment
    # -----------------------------------------------------

    fx_item = find_line_item_contains(
        getattr(cash_flow, "other_items", []),

        "Effect of exchange fluctuation on translation reserve",
        "Effect of exchange fluctuation",
        "Exchange fluctuation"
    )

    # -----------------------------------------------------
    # Validate each financial period
    # -----------------------------------------------------

    for period in cash_flow.periods:

        operating_total = get_period_value(
            operating_total_item,
            period
        )

        investing_total = get_period_value(
            investing_total_item,
            period
        )

        financing_total = get_period_value(
            financing_total_item,
            period
        )

        fx_amount = get_period_value(
            fx_item,
            period
        )

        net_change = get_period_value(
            net_change_item,
            period
        )

        opening_cash = get_period_value(
            opening_cash_item,
            period
        )

        closing_cash = get_period_value(
            closing_cash_item,
            period
        )

        # -------------------------------------------------
        # 1. Operating + Investing + Financing + FX
        #    ≈ Net Increase / Decrease in Cash
        # -------------------------------------------------

        if (
            operating_total is not None
            and investing_total is not None
            and financing_total is not None
            and net_change is not None
        ):

            calculated_net_change = round(
                operating_total
                + investing_total
                + financing_total
                + (fx_amount or 0.0),
                2
            )

        else:

            calculated_net_change = None

        result = check_value(
            calculated_net_change,
            net_change,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            period=period,
            check=(
                "Operating + investing + financing + FX "
                "≈ net increase / decrease in cash"
            ),
            inputs={
                "operating_cash_flow": operating_total,
                "investing_cash_flow": investing_total,
                "financing_cash_flow": financing_total,
                "fx_adjustment": fx_amount,
                "reported_net_change": net_change
            },
            result=result
        )

        # -------------------------------------------------
        # 2. Opening Cash + Net Change ≈ Closing Cash
        # -------------------------------------------------

        if (
            opening_cash is not None
            and net_change is not None
        ):

            calculated_closing_cash = round(
                opening_cash + net_change,
                2
            )

        else:

            calculated_closing_cash = None

        result = check_value(
            calculated_closing_cash,
            closing_cash,
            tolerance=0.02
        )

        append_validation(
            validations=validations,
            period=period,
            check=(
                "Opening cash + net increase / decrease "
                "≈ closing cash"
            ),
            inputs={
                "opening_cash": opening_cash,
                "net_change": net_change,
                "reported_closing_cash": closing_cash
            },
            result=result
        )

    return validations


# =========================================================
# Overall Status
# =========================================================


def get_overall_status(validations: list) -> str:
    """
    Determine the overall validation status.

    FAILED takes priority.

    If at least one validation passes and none fails:
        PASS

    If no validation can be performed:
        NOT_APPLICABLE
    """

    statuses = [
        validation.get("status")
        for validation in validations
    ]

    if "FAILED" in statuses:
        return "FAILED"

    if "PASS" in statuses:
        return "PASS"

    return "NOT_APPLICABLE"


# =========================================================
# Direct Test
# =========================================================


if __name__ == "__main__":

    print(
        "Financial validation service "
        "loaded successfully."
    )
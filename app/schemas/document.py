# =========================================================
# Document Schemas
# =========================================================


from typing import Any, Union


from pydantic import BaseModel, Field


# =========================================================
# Common
# =========================================================


class Evidence(BaseModel):
    """
    Source evidence for an extracted value or line item.
    """

    text: str | None = None

    page_number: int | None = None


# =========================================================
# Invoice
# =========================================================


class PartyDetails(BaseModel):

    name: str | None = None

    address: str | None = None

    gstin: str | None = None

    email: str | None = None

    phone: str | None = None

    salesman: str | None = None

    market_area: str | None = None


class TaxBreakdown(BaseModel):

    tax_type: str | None = None

    rate: float | None = None

    amount: float | None = None


class LineItem(BaseModel):

    description: str | None = None

    hsn_sac: str | None = None

    quantity: float | None = None

    unit: str | None = None

    unit_price: float | None = None

    discount: float | None = None

    taxable_amount: float | None = None

    tax_rate: float | None = None

    tax_amount: float | None = None

    amount: float | None = None

    evidence: Evidence | None = None


class PaymentDetails(BaseModel):

    payment_method: str | None = None

    amount_paid: float | None = None

    change: float | None = None

    payment_date: str | None = None


class BankDetails(BaseModel):

    bank_name: str | None = None

    account_number: str | None = None

    branch: str | None = None

    ifsc_code: str | None = None


class InvoiceData(BaseModel):

    invoice_number: str | None = None

    invoice_date: str | None = None

    currency: str | None = None

    seller: PartyDetails | None = None

    buyer: PartyDetails | None = None

    line_items: list[LineItem] = Field(
        default_factory=list
    )

    subtotal: float | None = None

    discount: float | None = None

    taxable_amount: float | None = None

    tax_amount: float | None = None

    round_off: float | None = None

    total_amount: float | None = None

    tax_breakdown: list[TaxBreakdown] = Field(
        default_factory=list
    )

    payment_details: PaymentDetails | None = None

    bank_details: BankDetails | None = None

    references: str | None = None

    other_fields: str | None = None


# =========================================================
# Financial Statements - Common Structures
# =========================================================


class PeriodValue(BaseModel):
    """
    A single financial value belonging to a specific period.

    Example:
    {
        "period": "31-Mar-17",
        "value": 5125091
    }
    """

    period: str

    value: float | None = None


class FinancialLineItem(BaseModel):
    """
    A financial statement line item.

    Example:
    {
        "label": "Capital",
        "values": [
            {
                "period": "31-Mar-17",
                "value": 5125091
            },
            {
                "period": "31-Mar-16",
                "value": 5056373
            }
        ]
    }
    """

    label: str

    values: list[PeriodValue] = Field(
        default_factory=list
    )

    evidence: Evidence | None = None


# =========================================================
# Balance Sheet
# =========================================================


class BalanceSheetData(BaseModel):

    statement_title: str | None = None

    unit: str | None = None

    periods: list[str] = Field(
        default_factory=list
    )

    liabilities: list[FinancialLineItem] = Field(
        default_factory=list
    )

    assets: list[FinancialLineItem] = Field(
        default_factory=list
    )

    other_items: list[FinancialLineItem] = Field(
        default_factory=list
    )


# =========================================================
# Profit & Loss Statement
# =========================================================


class ProfitLossData(BaseModel):

    statement_title: str | None = None

    unit: str | None = None

    periods: list[str] = Field(
        default_factory=list
    )

    income: list[FinancialLineItem] = Field(
        default_factory=list
    )

    expenditure: list[FinancialLineItem] = Field(
        default_factory=list
    )

    profit: list[FinancialLineItem] = Field(
        default_factory=list
    )

    appropriations: list[FinancialLineItem] = Field(
        default_factory=list
    )

    earnings_per_share: list[FinancialLineItem] = Field(
        default_factory=list
    )

    other_items: list[FinancialLineItem] = Field(
        default_factory=list
    )


# =========================================================
# Cash Flow Statement
# =========================================================


class CashFlowData(BaseModel):

    statement_title: str | None = None

    unit: str | None = None

    periods: list[str] = Field(
        default_factory=list
    )

    operating_activities: list[FinancialLineItem] = Field(
        default_factory=list
    )

    investing_activities: list[FinancialLineItem] = Field(
        default_factory=list
    )

    financing_activities: list[FinancialLineItem] = Field(
        default_factory=list
    )

    other_items: list[FinancialLineItem] = Field(
        default_factory=list
    )

    reconciliation: list[FinancialLineItem] = Field(
        default_factory=list
    )


# =========================================================
# Generic Financial Statement
# =========================================================


class FinancialStatementData(BaseModel):

    periods: list[str] = Field(
        default_factory=list
    )

    fields: dict[str, Any] = Field(
        default_factory=dict
    )

    tables: list[dict[str, Any]] = Field(
        default_factory=list
    )

    other_fields: dict[str, Any] = Field(
        default_factory=dict
    )


# =========================================================
# Final Document Structure
# =========================================================


class DocumentData(BaseModel):

    document_type: str

    data: Union[
        InvoiceData,
        BalanceSheetData,
        ProfitLossData,
        CashFlowData,
        FinancialStatementData
    ]
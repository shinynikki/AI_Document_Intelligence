from app.schemas.document import CashFlowData
from app.services.financial_validation import (
    validate_cash_flow,
    get_overall_status
)


cash_flow = CashFlowData(
    statement_title="Consolidated Cash Flow Statement",
    unit="= in '000",

    periods=[
        "31-Mar-17",
        "31-Mar-16"
    ],

    operating_activities=[
        {
            "label": "Net cash flow (used in) / from operating activities",
            "values": [
                {
                    "period": "31-Mar-17",
                    "value": -344353663
                },
                {
                    "period": "31-Mar-16",
                    "value": None
                }
            ]
        }
    ],

    investing_activities=[
        {
            "label": "Net cash used in investing activities",
            "values": [
                {
                    "period": "31-Mar-17",
                    "value": -8655510
                },
                {
                    "period": "31-Mar-16",
                    "value": None
                }
            ]
        }
    ],

    financing_activities=[
        {
            "label": "Net cash generated from financing activities",
            "values": [
                {
                    "period": "31-Mar-17",
                    "value": -58929743
                },
                {
                    "period": "31-Mar-16",
                    "value": 378151341
                }
            ]
        }
    ],

    other_items=[
        {
            "label": "Effect of exchange fluctuation on translation reserve",
            "values": [
                {
                    "period": "31-Mar-17",
                    "value": -282622
                },
                {
                    "period": "31-Mar-16",
                    "value": 282433
                }
            ]
        },
        {
            "label": "Cash and cash equivalents on amalgamation",
            "values": [
                {
                    "period": "31-Mar-17",
                    "value": 295617
                },
                {
                    "period": "31-Mar-16",
                    "value": None
                }
            ]
        }
    ],

    reconciliation=[
        {
            "label": "Net increase / (decrease) in cash and cash equivalents",
            "values": [
                {
                    "period": "31-Mar-17",
                    "value": 102422381
                },
                {
                    "period": "31-Mar-16",
                    "value": 25424601
                }
            ]
        },
        {
            "label": "Cash and cash equivalents as at April 1st",
            "values": [
                {
                    "period": "31-Mar-17",
                    "value": 390688815
                },
                {
                    "period": "31-Mar-16",
                    "value": 365264214
                }
            ]
        },
        {
            "label": "Cash and cash equivalents as at March 31st",
            "values": [
                {
                    "period": "31-Mar-17",
                    "value": 493111196
                },
                {
                    "period": "31-Mar-16",
                    "value": 390688815
                }
            ]
        }
    ]
)


# =========================================================
# Run validation
# =========================================================

validations = validate_cash_flow(cash_flow)


print(
    "\n========== VALIDATION RESULTS ==========\n"
)

for validation in validations:
    print(validation)


overall_status = get_overall_status(
    validations
)


print(
    "\n========== OVERALL STATUS ==========\n"
)

print(overall_status)
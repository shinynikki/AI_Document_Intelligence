import json

from app.schemas.document import ProfitLossData
from app.services.financial_validation import (
    validate_profit_loss,
    get_overall_status
)


# =========================================================
# Previously Extracted Profit & Loss JSON
# =========================================================

profit_loss_json = """
{
  "statement_title": "Consolidated Statement of Profit and Loss",
  "unit": "₹ in '000",
  "periods": [
    "31-Mar-17",
    "31-Mar-16"
  ],
  "income": [
    {
      "label": "Interest earned",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 732713529.0
        },
        {
          "period": "31-Mar-16",
          "value": 631615614.0
        }
      ]
    },
    {
      "label": "Other income",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 128776329.0
        },
        {
          "period": "31-Mar-16",
          "value": 112116541.0
        }
      ]
    },
    {
      "label": "Total",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 861489858.0
        },
        {
          "period": "31-Mar-16",
          "value": 743732155.0
        }
      ]
    }
  ],
  "expenditure": [
    {
      "label": "Interest expended",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 380415844.0
        },
        {
          "period": "31-Mar-16",
          "value": 340695748.0
        }
      ]
    },
    {
      "label": "Operating expenses",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 207510707.0
        },
        {
          "period": "31-Mar-16",
          "value": 178318808.0
        }
      ]
    },
    {
      "label": "Provisions and contingencies",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 120689285.0
        },
        {
          "period": "31-Mar-16",
          "value": 96544349.0
        }
      ]
    },
    {
      "label": "Total",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 708615836.0
        },
        {
          "period": "31-Mar-16",
          "value": 615558905.0
        }
      ]
    }
  ],
  "profit": [
    {
      "label": "Net profit for the year",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 152874022.0
        },
        {
          "period": "31-Mar-16",
          "value": 128173250.0
        }
      ]
    },
    {
      "label": "Less: Minority interest",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 367165.0
        },
        {
          "period": "31-Mar-16",
          "value": 197212.0
        }
      ]
    },
    {
      "label": "Add: Share in profits of associates",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 23393.0
        },
        {
          "period": "31-Mar-16",
          "value": 37278.0
        }
      ]
    },
    {
      "label": "Consolidated profit for the year attributable to the Group",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 152530250.0
        },
        {
          "period": "31-Mar-16",
          "value": 128013316.0
        }
      ]
    },
    {
      "label": "Impact on amalgamation [Refer Schedule 18(1)]",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 274507.0
        },
        {
          "period": "31-Mar-16",
          "value": null
        }
      ]
    },
    {
      "label": "Balance in Profit and Loss account brought forward",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 248255886.0
        },
        {
          "period": "31-Mar-16",
          "value": 195508642.0
        }
      ]
    },
    {
      "label": "Total",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 401060643.0
        },
        {
          "period": "31-Mar-16",
          "value": 323521958.0
        }
      ]
    }
  ],
  "appropriations": [
    {
      "label": "Transfer to Statutory Reserve",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 37771634.0
        },
        {
          "period": "31-Mar-16",
          "value": 31809345.0
        }
      ]
    },
    {
      "label": "Proposed dividend [Refer Schedule 18(3)]",
      "values": [
        {
          "period": "31-Mar-17",
          "value": null
        },
        {
          "period": "31-Mar-16",
          "value": 24017772.0
        }
      ]
    },
    {
      "label": "Tax (including cess) on interim / proposed dividend",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 255959.0
        },
        {
          "period": "31-Mar-16",
          "value": 5123529.0
        }
      ]
    },
    {
      "label": "Dividend (including tax / cess thereon) pertaining to previous year paid during the year, net of dividend tax credits",
      "values": [
        {
          "period": "31-Mar-17",
          "value": -16909.0
        },
        {
          "period": "31-Mar-16",
          "value": -117135.0
        }
      ]
    },
    {
      "label": "Transfer to General Reserve",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 14549641.0
        },
        {
          "period": "31-Mar-16",
          "value": 12296213.0
        }
      ]
    },
    {
      "label": "Transfer to Capital Reserve",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 3134100.0
        },
        {
          "period": "31-Mar-16",
          "value": 2221532.0
        }
      ]
    },
    {
      "label": "Transfer to / (from) Investment Reserve Account",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 42934.0
        },
        {
          "period": "31-Mar-16",
          "value": -85184.0
        }
      ]
    },
    {
      "label": "Balance carried over to Balance Sheet",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 345323284.0
        },
        {
          "period": "31-Mar-16",
          "value": 248255886.0
        }
      ]
    },
    {
      "label": "Total",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 401060643.0
        },
        {
          "period": "31-Mar-16",
          "value": 323521958.0
        }
      ]
    }
  ],
  "earnings_per_share": [
    {
      "label": "Basic",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 59.95
        },
        {
          "period": "31-Mar-16",
          "value": 50.85
        }
      ]
    },
    {
      "label": "Diluted",
      "values": [
        {
          "period": "31-Mar-17",
          "value": 59.16
        },
        {
          "period": "31-Mar-16",
          "value": 50.24
        }
      ]
    }
  ],
  "other_items": []
}
"""


# =========================================================
# Convert JSON into Pydantic Model
# =========================================================

profit_loss = ProfitLossData.model_validate(
    json.loads(profit_loss_json)
)


# =========================================================
# Run Validation
# =========================================================

validations = validate_profit_loss(
    profit_loss
)


# =========================================================
# Print Validation Results
# =========================================================

print(
    "\n========== VALIDATION RESULTS ==========\n"
)

for validation in validations:
    print(validation)


# =========================================================
# Overall Status
# =========================================================

overall_status = get_overall_status(
    validations
)

print(
    "\n========== OVERALL STATUS ==========\n"
)

print(overall_status)
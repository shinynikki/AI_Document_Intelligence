from app.schemas.document import InvoiceData, LineItem


invoice = InvoiceData(
    invoice_number="SCI/25-26/3331",
    invoice_date="16-Jul-25",
    line_items=[
        LineItem(
            description="SAFED 800GM (24PKT)",
            quantity=48,
            unit="PCS",
            unit_price=61.45,
            amount=2499.84
        )
    ],
    subtotal=5815.17,
    tax_amount=1046.72,
    total_amount=6862.00
)


print(invoice.model_dump_json(indent=4))
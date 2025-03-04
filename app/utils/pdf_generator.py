from io import BytesIO
from typing import Optional
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_financial_report(
        client_name: str,
        transactions: Optional[list],
        invoices: Optional[list]
    ) -> BytesIO:
    """Generate a PDF report with transactions and invoices history.
    
    Args:
        client_name: Name of the client
        transactions: Optional list of financial transactions
        invoices: Optional list of invoices
        
    Returns:
        BytesIO: PDF file as bytes
    """
    # Create a buffer to store PDF
    buffer = BytesIO()
    
    # Create the PDF object using the buffer
    doc = SimpleDocTemplate(
        buffer,
        pagesize=letter,
        rightMargin=72,
        leftMargin=72,
        topMargin=72,
        bottomMargin=72
    )

    # Container for the 'Flowable' objects
    elements = []
    
    # Get styles
    styles = getSampleStyleSheet()
    title_style = styles['Heading1']
    subtitle_style = styles['Heading2']
    
    # Add title and date
    elements.append(Paragraph(f"Financial Report - {client_name}", title_style))
    elements.append(Paragraph(f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M')}", styles['Normal']))
    elements.append(Spacer(1, 20))
    
    # Transactions section
    if transactions is not None:
        elements.append(Paragraph("Transactions History", subtitle_style))
        elements.append(Spacer(1, 12))

        if transactions:
            # Create transactions table
            transactions_data = [['Date', 'Amount', 'Category', 'Description']]
            for t in transactions:
                transactions_data.append([
                    t.transaction_date.strftime('%Y-%m-%d'),
                    f"${t.amount:,.2f}",
                    t.category or '',
                    t.description or ''
                ])
            
            t = Table(transactions_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(t)

            # Add transaction summary
            elements.append(Spacer(1, 12))
            total_amount = sum(t.amount for t in transactions)
            elements.append(Paragraph(f"Total Transaction Amount: ${total_amount:,.2f}", styles['Normal']))
            elements.append(Paragraph(f"Number of Transactions: {len(transactions)}", styles['Normal']))
        else:
            elements.append(Paragraph("No transactions found.", styles['Normal']))
        
        elements.append(Spacer(1, 20))
    
    # Invoices section
    if invoices is not None:
        elements.append(Paragraph("Invoices History", subtitle_style))
        elements.append(Spacer(1, 12))

        if invoices:
            # Create invoices table
            invoices_data = [['Invoice Date', 'Due Date', 'Amount Due', 'Amount Paid', 'Status']]
            for i in invoices:
                invoices_data.append([
                    i.invoice_date.strftime('%Y-%m-%d'),
                    i.due_date.strftime('%Y-%m-%d'),
                    f"${i.amount_due:,.2f}",
                    f"${i.amount_paid:,.2f}",
                    i.status
                ])
            
            t = Table(invoices_data)
            t.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 14),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 12),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            elements.append(t)

            # Add invoice summary
            elements.append(Spacer(1, 12))
            total_due = sum(i.amount_due for i in invoices)
            total_paid = sum(i.amount_paid for i in invoices)
            elements.append(Paragraph(f"Total Amount Due: ${total_due:,.2f}", styles['Normal']))
            elements.append(Paragraph(f"Total Amount Paid: ${total_paid:,.2f}", styles['Normal']))
            elements.append(Paragraph(f"Number of Invoices: {len(invoices)}", styles['Normal']))
        else:
            elements.append(Paragraph("No invoices found.", styles['Normal']))

    # Build PDF
    doc.build(elements)
    
    # Get the value of the BytesIO buffer
    buffer.seek(0)
    return buffer
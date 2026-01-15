import time
import markdown
from xhtml2pdf import pisa
from pathlib import Path
from io import BytesIO

def generate_jyotish_report(kundli_b64:str, gochar_b64:str, dasha_text:str, report_markdown:str):
    def format_b64(b64_str):
        if not b64_str.startswith('data:image'):
            return f"data:image/png;base64,{b64_str}"
        return b64_str

    kundli_src = format_b64(kundli_b64)
    gochar_src = format_b64(gochar_b64)

    report_html = markdown.markdown(report_markdown, extensions=['extra', 'nl2br'])

    dasha_html = dasha_text.replace('\n', '<br/>')

    full_html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            @page {{
                size: A4;
                margin: 1cm;
            }}
            body {{
                font-family: Helvetica, sans-serif;
                font-size: 12pt;
                color: #333;
            }}
            h1 {{
                font-family: 'Times New Roman', serif;
                text-align: center;
                color: #2c3e50;
                text-decoration: underline;
                margin-bottom: 30px;
            }}
            h2 {{
                color: #e67e22; /* Saffron/Orange tint for Astrological feel */
                border-bottom: 1px solid #ddd;
                padding-bottom: 5px;
                margin-top: 20px;
            }}
            table.charts {{
                width: 100%;
                margin-bottom: 20px;
            }}
            td {{
                width: 50%;
                text-align: center;
                vertical-align: top;
                padding: 10px;
            }}
            img.chart {{
                width: 300px;
                height: auto;
                border: 1px solid #ccc;
            }}
            .caption {{
                margin-top: 5px;
                font-weight: bold;
                font-size: 10pt;
                color: #555;
            }}
            .dasha-box {{
                background-color: #f9f9f9;
                border: 1px solid #eee;
                padding: 15px;
                font-family: Courier, monospace; /* Monospace for tabular plain text */
                font-size: 10pt;
            }}
            .report-content {{
                line-height: 1.6;
                text-align: justify;
            }}
            .page-break {{
                page-break-before: always;
            }}
        </style>
    </head>
    <body>

        <h1>Jyotish Report</h1>

        <table class="charts">
            <tr>
                <td>
                    <img src="{kundli_src}" class="chart"><br/>
                    <div class="caption">Birth Chart (Lagna)</div>
                </td>
                <td>
                    <img src="{gochar_src}" class="chart"><br/>
                    <div class="caption">Gochar Phal (Transit)</div>
                </td>
            </tr>
        </table>

        <h2>Vimshottari Dasha</h2>
        <div class="dasha-box">
            {dasha_html}
        </div>

        <h2 class="page-break">Detailed Analysis</h2>
        <div class="report-content">
            {report_html}
        </div>

    </body>
    </html>
    """
    
    downloads = Path.home() / "Downloads"
    downloads.mkdir(exist_ok=True)

    filename = f"jyotish_report_{int(time.time())}.pdf"
    pdf_path = downloads / filename

    # Write PDF
    with open(pdf_path, "wb") as f:
        pisa_status = pisa.CreatePDF(full_html, dest=f)

    if pisa_status.err:
        return None

    return str(pdf_path)

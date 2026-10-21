"""Email HTML rendering. renders bodies with a `text/template` over a `map[string]string`. The template references `{{.Subject}}` in the `<title>` although every caller only passes `Title`/`Message`/`Button`/`Link` — so the title tag renders EMPTY (map lookup of a missing key yields the zero value, no error). verbatim: a missing key renders as the empty string."""

from __future__ import annotations

_EMAIL_TEMPLATE = """
\t<!DOCTYPE html>
\t<html lang="en">
\t<head>
\t\t<meta charset="UTF-8">
\t\t<meta name="viewport" content="width=device-width, initial-scale=1.0">
\t\t<title>{{.Subject}}</title>
\t\t<style>
\t\t\tbody {
\t\t\t\tfont-family: 'Arial', sans-serif;
\t\t\t\tbackground-color: #f9f9f9;
\t\t\t\tmargin: 0;
\t\t\t\tpadding: 0;
\t\t\t\ttext-align: center;
\t\t\t\tcolor: #333;
\t\t\t}
\t\t\t.container {
\t\t\t\tmax-width: 600px;
\t\t\t\tmargin: 20px auto;
\t\t\t\tbackground-color: #ffffff;
\t\t\t\tborder-radius: 8px;
\t\t\t\tbox-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
\t\t\t\tpadding: 30px;
\t\t\t\tfont-size: 16px;
\t\t\t}
\t\t\t.header {
\t\t\t\tbackground-color: #007bff;
\t\t\t\tcolor: white;
\t\t\t\tpadding: 20px 0;
\t\t\t\tborder-radius: 8px 8px 0 0;
\t\t\t}
\t\t\t.header h1 {
\t\t\t\tfont-size: 28px;
\t\t\t\tmargin: 0;
\t\t\t}
\t\t\t.content {
\t\t\t\tpadding: 20px 0;
\t\t\t}
\t\t\t.cta-button {
\t\t\t\tdisplay: inline-block;
\t\t\t\tpadding: 12px 25px;
\t\t\t\tbackground-color: #28a745;
\t\t\t\tcolor: white;
\t\t\t\ttext-decoration: none;
\t\t\t\tborder-radius: 5px;
\t\t\t\tfont-weight: bold;
\t\t\t\tmargin-top: 20px;
\t\t\t\tfont-size: 16px;
\t\t\t}
\t\t\t.cta-button:hover {
\t\t\t\tbackground-color: #218838;
\t\t\t}
\t\t\t.footer {
\t\t\t\tbackground-color: #f1f1f1;
\t\t\t\tcolor: #777;
\t\t\t\tpadding: 15px;
\t\t\t\tfont-size: 12px;
\t\t\t\tborder-radius: 0 0 8px 8px;
\t\t\t}
\t\t\t.footer p {
\t\t\t\tmargin: 0;
\t\t\t}
\t\t\t@media (max-width: 600px) {
\t\t\t\t.container {
\t\t\t\t\twidth: 100% !important;
\t\t\t\t\tpadding: 15px;
\t\t\t\t}
\t\t\t\t.header h1 {
\t\t\t\t\tfont-size: 24px;
\t\t\t\t}
\t\t\t\t.cta-button {
\t\t\t\t\tpadding: 10px 20px;
\t\t\t\t\tfont-size: 14px;
\t\t\t\t}
\t\t\t}
\t\t</style>
\t</head>
\t<body>
\t\t<div class="container">
\t\t\t<div class="header">
\t\t\t\t<h1>{{.Title}}</h1>
\t\t\t</div>
\t\t\t<div class="content">
\t\t\t\t<p>{{.Message}}</p>
\t\t\t\t<a href="{{.Link}}" class="cta-button">{{.Button}}</a>
\t\t\t</div>
\t\t\t<div class="footer">
\t\t\t\t<p>This is an automated email. Please do not reply. For assistance, contact support@sanedge.com</p>
\t\t\t</div>
\t\t</div>
\t</body>
\t</html>"""


def generate_email_html(data: dict[str, str]) -> str:
    """Execute the email template over `data` (missing keys render empty)."""
    rendered = _EMAIL_TEMPLATE
    for key in ("Subject", "Title", "Message", "Button", "Link"):
        rendered = rendered.replace("{{." + key + "}}", data.get(key, ""))
    return rendered


__all__ = ["generate_email_html"]

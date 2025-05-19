import re
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs

# Regex patterns for different types of data we might want to pull out
# Keeping things simple but trying to handle basic edge cases
PATTERNS = {
    "Emails": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),
    "URLs": re.compile(r'https?://[^\s<>"]+'),
    "Phone Numbers": re.compile(
        r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'
    ),
    "Credit Cards": re.compile(
        r'\b(?:\d{4}[-\s]?){3}\d{4}\b'
    ),
    "Times": re.compile(
        r'\b((1[0-2]|0?[1-9]):[0-5][0-9]\s?(AM|PM))\b|'  # Like 09:45 AM
        r'\b([01]?[0-9]|2[0-3]):[0-5][0-9]\b'             # 24-hour format like 14:30
        , re.IGNORECASE),
}

# Basic HTML layout - just using vanilla HTML + inline styling to keep it easy
HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Regex Data Extractor</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f9f9f9; }}
        textarea {{ width: 100%; height: 150px; font-size: 16px; padding: 10px; }}
        input[type=submit] {{ margin-top: 10px; padding: 10px 20px; font-size: 16px; }}
        .results {{ margin-top: 30px; background: #fff; padding: 20px; border-radius: 5px; }}
        h2 {{ border-bottom: 1px solid #ddd; padding-bottom: 5px; }}
        ul {{ list-style-type: none; padding-left: 0; }}
        li {{ background: #e2e8f0; margin-bottom: 6px; padding: 6px; border-radius: 3px; word-wrap: break-word; }}
    </style>
</head>
<body>
    <h1>Regex Data Extraction - Junior Developer Challenge</h1>
    <form method="POST" action="/">
        <label for="inputtext">Paste your text below to extract:</label><br/>
        <textarea name="inputtext" id="inputtext" placeholder="Paste text here...">{input_text}</textarea><br/>
        <input type="submit" value="Extract Data" />
    </form>

    {results_section}

</body>
</html>
"""

# Goes through the input and checks each regex pattern
def extract_data(text):
    results = {}
    for key, pattern in PATTERNS.items():
        found = pattern.findall(text)

        # Regex might return tuples if there are groups. Just grab what's useful.
        flat_found = []
        for item in found:
            if isinstance(item, tuple):
                match = next((m for m in item if m), '')  # get the first non-empty match
                flat_found.append(match)
            else:
                flat_found.append(item)

        # Remove duplicates just in case and sort them alphabetically
        results[key] = sorted(set(flat_found))
    return results

# Builds the results section as HTML
def build_results_html(results):
    if not any(results.values()):
        return "<div class='results'><h2>No matches found.</h2></div>"
    
    html = "<div class='results'><h2>Extracted Data:</h2>"
    for category, items in results.items():
        html += f"<h3>{category} ({len(items)})</h3><ul>"
        for item in items:
            html += f"<li>{item}</li>"
        html += "</ul>"
    html += "</div>"
    return html

# Handles GET and POST requests to the mini web server
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()

        # Show empty form on page load
        self.wfile.write(HTML_FORM.format(input_text="", results_section="").encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get('content-length', 0))
        post_data = self.rfile.read(length).decode('utf-8')
        params = parse_qs(post_data)
        input_text = params.get('inputtext', [""])[0]

        # Extract matches using our regex rules
        results = extract_data(input_text)

        # Format them into the HTML page
        results_html = build_results_html(results)

        # Return the form again with the results shown
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        response = HTML_FORM.format(input_text=input_text, results_section=results_html)
        self.wfile.write(response.encode("utf-8"))

# Start the server
if __name__ == "__main__":
    port = 8080
    print(f"Starting server at http://localhost:{port}")
    server = HTTPServer(("localhost", port), SimpleHTTPRequestHandler)
    server.serve_forever()

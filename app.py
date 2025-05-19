import re  # needed for regex stuff obviously
from http.server import HTTPServer, BaseHTTPRequestHandler  # built-in http stuff
from urllib.parse import parse_qs  # this helps with form input

# just put all my patterns here for what I want to extract from the user text
PATTERNS = {
    "Emails": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b'),  # standard email regex
    "URLs": re.compile(r'https?://[^\s<>"]+'),  # simple URL checker
    "Phone Numbers": re.compile(r'(\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4})'),  # phone number matcher
    "Credit Cards": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),  # pattern for 16-digit card numbers
    "Times": re.compile(  # trying to get both 12h and 24h formats here
        r'\b((1[0-2]|0?[1-9]):[0-5][0-9]\s?(AM|PM))\b|'  
        r'\b([01]?[0-9]|2[0-3]):[0-5][0-9]\b', re.IGNORECASE),
}

# basic HTML form here with styles just to make it look a bit nicer
HTML_FORM = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Regex Data Extractor</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; background: #f0f4f8; color: #333; }}
        textarea {{ width: 100%; height: 150px; font-size: 16px; padding: 10px; }}
        input[type=submit], button {{ margin-top: 10px; padding: 10px 20px; font-size: 16px; cursor: pointer; }}
        .results {{ margin-top: 30px; background: #fff; padding: 20px; border-radius: 8px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
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

    <script>
        function downloadResults() {{
            const text = document.getElementById('resultsText').textContent;
            const blob = new Blob([text], {{ type: 'text/plain' }});
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'extracted_results.txt';
            link.click();
        }}
    </script>
</body>
</html>
"""

# I use this function to loop through all patterns and grab stuff
def extract_data(text):
    results = {}
    for key, pattern in PATTERNS.items():
        found = pattern.findall(text)  # try to find everything for this pattern
        flat_found = []
        for item in found:
            if isinstance(item, tuple):  # sometimes regex returns tuples
                match = next((m for m in item if m), '')
                flat_found.append(match)
            else:
                flat_found.append(item)
        results[key] = sorted(set(flat_found))  # remove duplicates
    return results

# this one builds a small results box in HTML with download option
def build_results_html(results):
    if not any(results.values()):  # if we didn’t find anything
        return "<div class='results'><h2>No matches found.</h2></div>"
    html = "<div class='results'><h2>Extracted Data:</h2><pre id='resultsText'>"
    for category, items in results.items():
        html += f"{category} ({len(items)}):\n" + '\n'.join(items) + "\n\n"
    html += "</pre><button onclick='downloadResults()'>Download Results</button></div>"
    return html

# basic http handler to respond to GET and POST
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML_FORM.format(input_text="", results_section="").encode("utf-8"))

    def do_POST(self):
        length = int(self.headers.get('content-length', 0))
        post_data = self.rfile.read(length).decode('utf-8')
        params = parse_qs(post_data)  # split the form data
        input_text = params.get('inputtext', [""])[0]

        results = extract_data(input_text)  # extract patterns
        results_html = build_results_html(results)  # build html

        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        response = HTML_FORM.format(input_text=input_text, results_section=results_html)
        self.wfile.write(response.encode("utf-8"))

# just run the server on port 8080 locally
if __name__ == "__main__":
    port = 8080
    print(f"Starting server at http://localhost:{port}")
    server = HTTPServer(("localhost", port), SimpleHTTPRequestHandler)
    server.serve_forever()

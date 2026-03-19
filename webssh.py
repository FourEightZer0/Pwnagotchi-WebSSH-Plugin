import logging
from urllib.parse import urlparse, urlunparse

import pwnagotchi.plugins as plugins
from flask import Response


class WebSSH(plugins.Plugin):
    __author__ = "cbirchem0724"
    __version__ = "1.0.1"
    __license__ = "MIT"
    __description__ = "Embeds a browser terminal URL in the Pwnagotchi web UI."

    def on_loaded(self):
        logging.info("[webssh] plugin loaded")

    def _resolve_ttyd_url(self, ttyd_url, request):
        parsed = urlparse(ttyd_url)

        # If ttyd points to localhost, rewrite it to the current device host so
        # remote browsers can connect to the terminal service.
        if parsed.hostname in ("127.0.0.1", "localhost", "::1"):
            req_host = request.host.split(":")[0]
            scheme = parsed.scheme or ("https" if request.is_secure else "http")
            port = parsed.port or 7681
            parsed = parsed._replace(scheme=scheme, netloc=f"{req_host}:{port}")

        return urlunparse(parsed)

    def on_webhook(self, path, request):
        ttyd_url = self.options.get("ttyd_url", "http://127.0.0.1:7681")
        ttyd_url = self._resolve_ttyd_url(ttyd_url, request)
        title = self.options.get("title", "Web SSH")

        page = f"""<!doctype html>
<html>
<head>
  <meta charset=\"utf-8\"> 
  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">
  <title>{title}</title>
  <style>
    body {{
      margin: 0;
      background: #111;
      color: #ddd;
      font-family: sans-serif;
    }}
    .header {{
      padding: 10px 14px;
      border-bottom: 1px solid #2a2a2a;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .header a {{ color: #9ecbff; text-decoration: none; }}
    .wrap {{
      width: 100%;
      height: calc(100vh - 48px);
    }}
    iframe {{
      border: 0;
      width: 100%;
      height: 100%;
      background: #000;
    }}
  </style>
</head>
<body>
  <div class=\"header\">
    <div>{title}</div>
    <a href=\"{ttyd_url}\" target=\"_blank\" rel=\"noopener noreferrer\">Open in new tab</a>
  </div>
  <div class=\"wrap\">
    <iframe src=\"{ttyd_url}\"></iframe>
  </div>
</body>
</html>
"""
        return Response(page, mimetype="text/html")

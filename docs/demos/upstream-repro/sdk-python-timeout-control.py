# Same scenario as the JS crash repro: headers flushed, body never ends, client times out.
# JS: leaks 1 unhandled rejection per timeout and kills a default Node process.
import asyncio, threading, warnings
from http.server import BaseHTTPRequestHandler, HTTPServer
from typesafe_sdk import AsyncTypeSafeClient

warnings.simplefilter("error")  # surface any ResourceWarning as a failure


class H(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("content-type", "application/json")
        self.end_headers()
        self.wfile.flush()
        import time

        time.sleep(10)  # never finish the body

    def log_message(self, *a):
        pass


srv = HTTPServer(("127.0.0.1", 0), H)
threading.Thread(target=srv.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{srv.server_address[1]}"

leaked = []


def handler(loop, context):
    leaked.append(context.get("message"))


async def main():
    asyncio.get_running_loop().set_exception_handler(handler)
    c = AsyncTypeSafeClient(api_key="k", base_url=base, timeout=0.2)
    try:
        await c.models.list()
    except Exception as e:
        print("consumer caught:", type(e).__name__)
    await asyncio.sleep(1.0)
    print("loop-level leaked exceptions:", len(leaked), leaked[:2])


asyncio.run(main())
print("SURVIVED: process reached the end")

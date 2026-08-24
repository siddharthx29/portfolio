import asyncio
import json
import subprocess
import time
import os
import requests
import websockets
import base64

CHROME_PATH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
PORT = 9222

async def cdp_test():
    # Start chrome with remote debugging
    chrome_proc = subprocess.Popen([
        CHROME_PATH,
        "--headless=new",
        f"--remote-debugging-port={PORT}",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-sandbox"
    ])
    
    await asyncio.sleep(2)
    
    try:
        # Get target websocket URL
        r = requests.get(f"http://127.0.0.1:{PORT}/json")
        targets = r.json()
        print("Targets:", targets)
        ws_url = targets[0]["webSocketDebuggerUrl"]
        
        async with websockets.connect(ws_url) as ws:
            msg_id = 1
            
            async def send_cmd(method, params=None):
                nonlocal msg_id
                cmd = {"id": msg_id, "method": method, "params": params or {}}
                msg_id += 1
                await ws.send(json.dumps(cmd))
                while True:
                    res = json.loads(await ws.recv())
                    if res.get("id") == cmd["id"]:
                        return res.get("result", {})
            
            await send_cmd("Page.enable")
            await send_cmd("DOM.enable")
            
            print("Navigating to /projects...")
            await send_cmd("Page.navigate", {"url": "http://127.0.0.1:5050/projects"})
            await asyncio.sleep(2)
            
            # Get scroll height
            eval_res = await send_cmd("Runtime.evaluate", {
                "expression": "JSON.stringify({width: Math.max(document.documentElement.scrollWidth, document.body.scrollWidth, 1440), height: Math.max(document.documentElement.scrollHeight, document.body.scrollHeight)})"
            })
            dimensions = json.loads(eval_res["result"]["value"])
            print("Page dimensions:", dimensions)
            
            # Set emulation for full page
            await send_cmd("Emulation.setDeviceMetricsOverride", {
                "width": dimensions["width"],
                "height": dimensions["height"],
                "deviceScaleFactor": 1.5,
                "mobile": False
            })
            await asyncio.sleep(1)
            
            # Capture full page screenshot
            shot_res = await send_cmd("Page.captureScreenshot", {
                "format": "png",
                "captureBeyondViewport": True
            })
            
            img_data = base64.b64decode(shot_res["data"])
            test_file = r"c:\Users\HP\Downloads\PortFolio-main\PortFolio-main\screenshots_output\test_full_projects.png"
            with open(test_file, "wb") as f:
                f.write(img_data)
            
            print(f"Saved full screenshot: {test_file}, size: {len(img_data)} bytes")
            
    finally:
        chrome_proc.terminate()

if __name__ == "__main__":
    asyncio.run(cdp_test())

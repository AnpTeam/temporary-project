import json
import requests
import uuid
import os
# pyrefly: ignore [missing-import]
import websocket

COMFY_API_URL = "http://127.0.0.1:8188"
OUTPUT_DIR = "assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def upload_image(local_path):
    url = f"{COMFY_API_URL}/upload/image"
    with open(local_path, "rb") as f:
        files = {"image": f}
        data = {"type": "input", "overwrite": "true"}
        response = requests.post(url, files=files, data=data)
        return response.json()["name"]

def run_workflow(local_image_path, prompt_text):
    # 1. Upload
    comfy_filename = upload_image(local_image_path)
    
    # 2. Load and Update Workflow
    with open("assets\config\img2vdo-api.json", "r", encoding="utf-8") as f:
        workflow = json.load(f)
        
    workflow["11"]["inputs"]["image"] = comfy_filename # LoadImage node
    workflow["69:56"]["inputs"]["text"] = prompt_text   # Positive Prompt
    
    # 3. Queue Prompt
    client_id = str(uuid.uuid4())
    payload = {"prompt": workflow, "client_id": client_id}
    response = requests.post(f"{COMFY_API_URL}/prompt", json=payload)
    prompt_id = response.json().get("prompt_id")
    
    # 4. Wait for completion via WebSocket
    ws = websocket.WebSocket()
    ws.connect(f"ws://127.0.0.1:8188/ws?clientId={client_id}")
    while True:
        out = ws.recv()
        if isinstance(out, str):
            msg = json.loads(out)
            if msg['type'] == 'executing' and msg['data']['node'] is None:
                break
    ws.close()
    
    # 5. Fetch and Save Video
    download_video(prompt_id)

def download_video(prompt_id):
    history = requests.get(f"{COMFY_API_URL}/history/{prompt_id}").json()
    outputs = history[prompt_id]['outputs']
    
    for node_id in outputs:
        if 'videos' in outputs[node_id]:
            vid = outputs[node_id]['videos'][0]
            view_url = f"{COMFY_API_URL}/view"
            params = {"filename": vid['filename'], "subfolder": vid.get('subfolder', ''), "type": "output"}
            resp = requests.get(view_url, params=params)
            
            save_path = os.path.join(OUTPUT_DIR, vid['filename'])
            with open(save_path, "wb") as f:
                f.write(resp.content)
            print(f"Video saved to: {save_path}")

# Run the process
# run_workflow("path/to/your/image.jpg", "Cinematic horizontal pan, slow movement...")
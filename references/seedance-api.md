# Seedance 2.0 API reference

Seedance 2.0 (Dreamina Seedance 2.0) is a BytePlus ModelArk video generation model. It can be used as an alternative to HeyGen for both:
- **A-roll** (talking-head generation with a portrait asset)
- **B-roll** (cinematic text-to-video or image-to-video generation)

Required env vars:
- `BYTEPLUS_ARK_API_KEY` — ModelArk API key
- `TOS_ACCESS_KEY`, `TOS_SECRET_KEY`, `TOS_ENDPOINT`, `TOS_REGION`, `TOS_BUCKET` — TOS object storage credentials (needed for portrait upload pre-step)

Do NOT hardcode any credentials.

Docs: https://docs.byteplus.com/en/docs/ModelArk/1520757

---

## Model IDs

| Use case | Model ID |
|---|---|
| Talking-head A-roll | `dreamina-seedance-2-0-260128` |
| Cinematic B-roll | `dreamina-seedance-2-0-260128` |

---

## Step 0 — Portrait asset upload (A-roll only)

Before generating talking-head A-roll with Seedance, a portrait image must be uploaded and approved. This is a one-time step per portrait; reuse the `AssetId` for all subsequent videos with the same person.

The CreateAsset API requires a **URL** for the portrait image, not raw bytes. The workflow is therefore:

```
local image file
    → Step 0a: upload to BytePlus TOS → get presigned URL
    → Step 0b: CreateAssetGroup → get AssetGroupId
    → Step 0c: CreateAsset (with TOS URL) → get AssetId
    → Step 0d: poll GetAsset until Status == "approved"
    → ark://asset/<AssetId>  ← use this in video generation
```

### 0a. Upload portrait image to TOS

Use the `tos-upload` skill to stage the portrait image on TOS first:

```bash
# Verify TOS credentials are set
python3 /Users/bytedance/.claude/skills/tos-upload/scripts/upload.py \
    <local_image_path> \
    --expires 86400 \
    --key "seedance-portraits/<project-slug>/<filename>"
```

This prints JSON — capture the `url` field:
```json
{
  "bucket": "...",
  "key": "seedance-portraits/my-video/portrait.jpg",
  "url": "https://<bucket>.tos-ap-singapore.bytepluses.com/seedance-portraits/...?X-Tos-Signature=...",
  "expires_at": "2026-05-06T14:00:00+00:00",
  "size_bytes": 245000,
  "content_type": "image/jpeg"
}
```

Save the `url` as `TOS_PORTRAIT_URL`. Use `--expires 86400` (24h) to ensure the URL stays valid through the review period.

**TOS credentials setup** (one-time):
```bash
# Export env vars (preferred; wins over credentials file):
export TOS_ACCESS_KEY="<ak>"
export TOS_SECRET_KEY="<sk>"
export TOS_ENDPOINT="tos-ap-southeast-3.bytepluses.com"
export TOS_REGION="ap-southeast-3"
export TOS_BUCKET="<bucket>"
```
Or fill in `/Users/bytedance/.claude/skills/tos-upload/tos_credentials.json`.

### 0b. Create an asset group

```bash
curl -X POST "https://ark.ap-southeast-1.byteplusapi.com/?Action=CreateAssetGroup&Version=2024-01-01" \
  -H "Authorization: Bearer $BYTEPLUS_ARK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "Name": "portrait-group-<slug>",
    "Description": "Portrait for <video project name>"
  }'
```

Response:
```json
{
  "ResponseMetadata": { "RequestId": "...", "Action": "CreateAssetGroup" },
  "Result": { "AssetGroupId": "ag-xxxxxxxxxxxx" }
}
```

Save `AssetGroupId` for the next step.

### 0c. Create asset (using TOS URL)

```bash
curl -X POST "https://ark.ap-southeast-1.byteplusapi.com/?Action=CreateAsset&Version=2024-01-01" \
  -H "Authorization: Bearer $BYTEPLUS_ARK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "AssetGroupId": "<AssetGroupId from 0b>",
    "Name": "portrait-<slug>",
    "ContentType": "image/jpeg",
    "Url": "<TOS_PORTRAIT_URL from 0a>"
  }'
```

Response:
```json
{
  "ResponseMetadata": { "RequestId": "...", "Action": "CreateAsset" },
  "Result": {
    "AssetId": "asset-xxxxxxxxxxxx",
    "Status": "pending_review"
  }
}
```

Full API spec: https://docs.byteplus.com/en/docs/ModelArk/2333565

### 0d. Poll for asset approval

Asset review is typically automatic and takes 30-120 seconds.

```bash
curl -X POST "https://ark.ap-southeast-1.byteplusapi.com/?Action=GetAsset&Version=2024-01-01" \
  -H "Authorization: Bearer $BYTEPLUS_ARK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"AssetId": "<AssetId from 0c>"}'
```

Poll every 10s until `Status == "approved"`. If `Status == "rejected"`, the image doesn't meet requirements.

Once approved, the asset URI is: `ark://asset/<AssetId>`

**Portrait image requirements:**
- Format: JPEG, PNG, WEBP, GIF, HEIC
- Size: < 30 MB
- Dimensions: at least 300×300 px, max 6000 px on either side
- Aspect ratio: between 0.4 and 2.5 (W/H)
- Content: front-facing, single person, clear face, no heavy occlusion

---

## Step 1 — Create a video generation task

### For A-roll (talking head)

```bash
curl -X POST "https://ark.ap-southeast-1.byteplusapi.com/api/v3/contents/generations/tasks" \
  -H "Authorization: Bearer $BYTEPLUS_ARK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dreamina-seedance-2-0-260128",
    "content": [
      {
        "type": "text",
        "text": "<speaking prompt, e.g.: Person speaking directly to camera, professional tone: '\''This is DeerFlow.'\''>"
      },
      {
        "type": "asset_uri",
        "asset_uri": "ark://asset/<AssetId>"
      }
    ],
    "parameters": {
      "aspect_ratio": "9:16",
      "duration": 5,
      "resolution": "720p"
    }
  }'
```

### For B-roll (text-to-video, no portrait)

```bash
curl -X POST "https://ark.ap-southeast-1.byteplusapi.com/api/v3/contents/generations/tasks" \
  -H "Authorization: Bearer $BYTEPLUS_ARK_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "dreamina-seedance-2-0-260128",
    "content": [
      {"type": "text", "text": "<cinematic prompt>"}
    ],
    "parameters": {
      "aspect_ratio": "9:16",
      "duration": 5,
      "resolution": "720p"
    }
  }'
```

### Parameters

| Parameter | Type | Values | Notes |
|---|---|---|---|
| `aspect_ratio` | string | `"9:16"`, `"16:9"`, `"1:1"`, `"4:3"` | Use `"9:16"` for TikTok/Shorts |
| `duration` | integer | 5–10 | Seconds; 5 is cheapest |
| `resolution` | string | `"720p"`, `"1080p"` | `"720p"` matches HyperFrames 720×1280 |

Response:
```json
{
  "id": "task-xxxxxxxxxxxx",
  "status": "queued",
  "model": "dreamina-seedance-2-0-260128",
  "created_at": 1234567890
}
```

---

## Step 2 — Poll task status

```bash
curl "https://ark.ap-southeast-1.byteplusapi.com/api/v3/contents/generations/tasks/<task_id>" \
  -H "Authorization: Bearer $BYTEPLUS_ARK_API_KEY"
```

Poll every 15s until `status` is terminal:

| Status | Meaning |
|---|---|
| `queued` | Waiting in queue |
| `running` | Generating |
| `succeeded` | Done — `output.url` has the video |
| `failed` | Failed — check `error.message` |

Download from `output.url` to `./assets/<segment>.mp4`.

---

## When to use Seedance vs HeyGen

| Scenario | Prefer Seedance | Prefer HeyGen |
|---|---|---|
| A-roll (talking head) | When portrait asset is already approved; higher cinematic quality desired | When speed matters; HeyGen has better lip sync on short segments |
| B-roll cinematic | Good default; no extra credits needed | When HeyGen Video Agent plan is already being used anyway |
| Talking head first use | ❌ TOS upload + asset review adds ~3-5 min one-time setup | ✅ Faster first-run with HeyGen avatar |
| Repeated use / same person | ✅ AssetId approved once, reused freely | HeyGen avatar also reusable |

**Key constraint for A-roll:** Seedance talking head has no voice cloning — the generated person speaks the words from the text prompt. Voice accuracy depends on prompt quality. For exact pronunciation of technical terms, prefer HeyGen with a cloned voice.

---

## Python helpers

```python
import os, subprocess, json, time, requests

BYTEPLUS_ARK_API_KEY = os.environ["BYTEPLUS_ARK_API_KEY"]
BASE_URL = "https://ark.ap-southeast-1.byteplusapi.com"
HEADERS = {"Authorization": f"Bearer {BYTEPLUS_ARK_API_KEY}", "Content-Type": "application/json"}
TOS_SCRIPT = "/Users/bytedance/.claude/skills/tos-upload/scripts/upload.py"


def upload_to_tos(local_path: str, key: str, expires: int = 86400) -> str:
    """Upload a local file to TOS and return the presigned URL."""
    result = subprocess.check_output([
        "python3", TOS_SCRIPT, local_path,
        "--key", key,
        "--expires", str(expires),
    ])
    return json.loads(result)["url"]


def create_asset_group(name: str) -> str:
    r = requests.post(
        f"{BASE_URL}/?Action=CreateAssetGroup&Version=2024-01-01",
        json={"Name": name}, headers=HEADERS
    )
    r.raise_for_status()
    return r.json()["Result"]["AssetGroupId"]


def create_asset(asset_group_id: str, name: str, tos_url: str, content_type: str = "image/jpeg") -> str:
    r = requests.post(
        f"{BASE_URL}/?Action=CreateAsset&Version=2024-01-01",
        json={"AssetGroupId": asset_group_id, "Name": name,
              "ContentType": content_type, "Url": tos_url},
        headers=HEADERS
    )
    r.raise_for_status()
    return r.json()["Result"]["AssetId"]


def poll_asset_approval(asset_id: str, interval: int = 10, timeout: int = 300) -> str:
    """Returns ark://asset/<asset_id> once approved."""
    for _ in range(timeout // interval):
        r = requests.post(
            f"{BASE_URL}/?Action=GetAsset&Version=2024-01-01",
            json={"AssetId": asset_id}, headers=HEADERS
        )
        r.raise_for_status()
        status = r.json()["Result"]["Status"]
        if status == "approved":
            return f"ark://asset/{asset_id}"
        if status == "rejected":
            raise RuntimeError(f"Asset {asset_id} rejected — check image requirements")
        time.sleep(interval)
    raise TimeoutError(f"Asset {asset_id} review timed out after {timeout}s")


def upload_portrait(local_image_path: str, project_slug: str) -> str:
    """Full portrait pipeline: TOS → CreateAssetGroup → CreateAsset → poll → return asset URI."""
    import os
    filename = os.path.basename(local_image_path)
    tos_url = upload_to_tos(local_image_path, f"seedance-portraits/{project_slug}/{filename}")
    group_id = create_asset_group(f"portrait-group-{project_slug}")
    asset_id = create_asset(group_id, f"portrait-{project_slug}", tos_url)
    return poll_asset_approval(asset_id)


def create_video_task(model: str, content: list, parameters: dict) -> str:
    r = requests.post(
        f"{BASE_URL}/api/v3/contents/generations/tasks",
        json={"model": model, "content": content, "parameters": parameters},
        headers=HEADERS
    )
    r.raise_for_status()
    return r.json()["id"]


def poll_task(task_id: str, interval: int = 15, timeout: int = 600) -> str:
    """Returns the output video URL once the task succeeds."""
    for _ in range(timeout // interval):
        r = requests.get(
            f"{BASE_URL}/api/v3/contents/generations/tasks/{task_id}",
            headers=HEADERS
        )
        r.raise_for_status()
        data = r.json()
        if data["status"] == "succeeded":
            return data["output"]["url"]
        if data["status"] == "failed":
            raise RuntimeError(f"Task {task_id} failed: {data.get('error', {}).get('message')}")
        time.sleep(interval)
    raise TimeoutError(f"Task {task_id} did not complete within {timeout}s")
```

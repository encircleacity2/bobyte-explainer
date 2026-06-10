# API profile and proxy reference

The explainer pipeline touches several paid providers: ModelArk/Seedance, Seedream, TTS,
music, storage, and sometimes LLMs for script work. Keep provider selection and keys out of
individual project files.

## Config model

`~/.explainer-video/config.json` may contain direct profiles:

```json
{
  "default_api_profile": "byteplus",
  "api_proxy_url": "",
  "api_profiles": {
    "byteplus": {
      "provider": "byteplus",
      "base_url": "https://ark.ap-southeast.bytepluses.com/api/v3",
      "api_key_env": "BYTEPLUS_API_KEY"
    },
    "volcengine": {
      "provider": "volcengine",
      "base_url": "https://ark.cn-beijing.volces.com/api/v3",
      "api_key_env": "ARK_API_KEY"
    }
  }
}
```

Or proxy mode:

```json
{
  "default_api_profile": "byteplus-prod",
  "api_proxy_url": "http://127.0.0.1:8787",
  "api_profiles": {}
}
```

## Direct profile mode

Use direct mode for solo/local work:

- Resolve `profile = config.api_profiles[config.default_api_profile]`.
- Read the key from `profile.api_key_env`; if missing, fall back to a provider-specific config key.
- Never print full key values.
- Do not copy `config.json` into project folders.

## Proxy mode

Use proxy mode for teams:

- The project sends semantic tasks such as `/tts`, `/chat`, `/seedance`, `/image`.
- The proxy owns provider credentials, routing, logging, and rate limits.
- The project passes `profile`, model/resource IDs, prompt/script, and asset refs.
- The proxy can switch providers without changing storyboard or render code.

Suggested proxy endpoints:

| Endpoint | Purpose |
|---|---|
| `POST /tts` | Generate narration audio. |
| `POST /chat/completions` | Script/storyboard assistance. |
| `POST /video/seedance` | Seedance task creation / polling wrapper. |
| `POST /image/seedream` | Portrait restyle / image generation. |
| `POST /storage/upload` | TOS or asset-library upload. |

## Provider switching rules

- Storyboards should refer to capabilities, not hardcoded vendors, unless the user requires one.
- Production code should accept `provider`, `profile`, `base_url`, and `resource_id` separately.
- Keep generated assets provider-neutral: `assets/audio/seg01.m4a`, not `byteplus_seg01.m4a`.
- Log provider/profile names and request IDs, but not secrets or full prompts containing sensitive customer content.

## Key hygiene

- Put long-lived keys in the OS keychain, environment variables, or `~/.explainer-video/config.json` with mode `600`.
- Do not commit filled credential sheets.
- Do not paste keys into storyboards, prompts, docs, or rendered overlays.
- When reporting failures, redact keys and signed URLs.

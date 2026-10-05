# Optional native avatar control

The `.veado` project contains four named states:

- Maple Idle: neutral image, with blink image in its automatic blink slots
- Maple Speaking: open-mouth image, with speaking-blink image in its blink slots
- Maple Blink: forced closed eyes
- Maple Speaking Blink: forced closed eyes and open mouth

The Speaking states include a restrained bounce. Its live appearance has not been verified. The file builder implements the documented container and RAW image formats; it does not bundle or modify the veadotube executable.

## Explicitly target your own running instance

Download and install the app from the [official source](https://olmewe.itch.io/veadotube-mini), review its [terms](https://veado.tube/docs/terms/), and load the supplied avatar. Then:

```sh
python3 tools/maple_statectl.py --app /path/to/veadotube-mini --list-instances
python3 tools/maple_statectl.py states --app /path/to/veadotube-mini --instance YOUR_INSTANCE_ID
python3 tools/maple_statectl.py speaking --app /path/to/veadotube-mini --instance YOUR_INSTANCE_ID --dry-run
python3 tools/maple_statectl.py demo --app /path/to/veadotube-mini --instance YOUR_INSTANCE_ID --seconds 3
```

Replace the executable path and instance placeholder with your own values. The controller never selects the first instance automatically. Use `--dry-run` to inspect commands without invoking the app. The demo attempts to restore Idle in a `finally` block; if the native connection is broken, restoration can still fail. A controller failure is not proof that the avatar returned to neutral.

This is a small CLI helper with offline/mock tests. An original-only import into the native app was verified, but the final four-state import and live state API have not been verified. Test locally before relying on it in a stream. No automatic TTS bridge, audio routing, microphone permission or public broadcast is configured.

[Official API documentation](https://veado.tube/docs/tech/api/) · [State event/node commands](https://veado.tube/docs/tech/api/nodes/)

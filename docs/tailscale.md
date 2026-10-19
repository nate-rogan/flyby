# Tailscale (stub — disabled)

flyby does **not** join a tailnet. The image contains no Tailscale binaries, and
the code to start it is commented out in `start.sh` and the `Dockerfile`. This page
explains how you *could* enable it to reach a private service, such as Ollama on
another machine, and why each safeguard matters.

## Why it's off

This app is public on the internet. As soon as its machine joins your tailnet,
Tailscale treats it like any other device you own. With the default access policy
("everyone can reach everything"), anyone who broke into the app could reach every
port on every device, plus any private LAN that a device shares as a subnet route.

## If you enable it, lock it down first

1. **Tag the machine instead of logging it in as you.** In the Tailscale access
   controls, add a tag owner and a single narrow rule:

   ```jsonc
   {
     "tagOwners": { "tag:fly": ["autogroup:admin"] },
     "grants": [
       // fly machines may reach ONLY Ollama on one PC — nothing else
       { "src": ["tag:fly"], "dst": ["<your-device>"], "ip": ["tcp:11434"] }
     ]
   }
   ```

   Tagged devices don't get your user's access, so this is the only path they
   have. Also check that no existing `"*" → "*"` rule still lets everything through.

2. **Use a tagged, ephemeral, reusable auth key** (Settings → Keys, with tag
   `tag:fly`). State is kept in memory (`--state=mem:`), so ephemeral keys stop old
   machines piling up in the admin console.

3. **`--shields-up`** stops tailnet devices from connecting *into* the Fly machine.

4. **No `--accept-routes`**, so the Fly machine never picks up routes to your private LAN.

5. **Keep the public endpoint narrow.** `/api/v1/ollama/models` only calls Ollama's
   read-only `/api/tags` endpoint. Never add a general proxy route, or anyone on the
   internet could run prompts on your GPU.

6. **Bind Ollama to the PC's Tailscale IP** (`OLLAMA_HOST=<device-tailscale-ip>`), not `0.0.0.0`.

## Turning it on

1. Uncomment the Tailscale lines in the `Dockerfile` and the block in `start.sh`.
2. Set the secrets:
   ```bash
   fly secrets set TS_AUTHKEY=tskey-auth-... OLLAMA_BASE_URL=http://<device-tailscale-ip>:11434
   ```
3. Run `fly deploy`. The page should then show `Tailscale: connected` and
   **List models** should return your models.

# Free auto-updates: Tesla Fleet API on an Oracle Always Free VM

This is the free, hands-off setup: an Oracle **Always Free** VM hosts the
public-key file the Fleet API requires *and* runs the daily data pull, which
commits the new numbers back to this repo. No subscriptions.

There are four one-time stages. Budget ~30–45 minutes the first time.

---

## 0. What you need

- A 2019 Model 3 already in your Tesla account.
- A domain name you control (any cheap one works; you only need to point a
  subdomain at the VM).
- An Oracle Cloud account (the Always Free tier is enough — one small
  `VM.Standard.A1.Flex` or `E2.1.Micro` instance).

---

## 1. Oracle Always Free VM

1. Create an **Always Free** compute instance (Ubuntu image is easiest).
2. In the instance's **VCN security list**, allow inbound **TCP 80 and 443**.
3. SSH in and open the host firewall too:
   ```bash
   sudo iptables -I INPUT -p tcp --dport 80 -j ACCEPT
   sudo iptables -I INPUT -p tcp --dport 443 -j ACCEPT
   sudo netfilter-persistent save     # Ubuntu; persists the rules
   ```
4. Point a DNS **A record** (e.g. `tesla.yourdomain.com`) at the VM's public IP.
5. Install basics:
   ```bash
   sudo apt update && sudo apt install -y git python3 openssl caddy
   git clone <this-repo-url> ~/hello-world && cd ~/hello-world
   ```

## 2. Host the Fleet API public key

```bash
sudo WELL_KNOWN=/var/www/tesla/.well-known/appspecific bash deploy/gen-keys.sh
sudo cp deploy/Caddyfile /etc/caddy/Caddyfile
sudo sed -i 's/tesla.example.com/tesla.yourdomain.com/' /etc/caddy/Caddyfile
sudo systemctl restart caddy
```

Verify (should return your PEM):
```bash
curl https://tesla.yourdomain.com/.well-known/appspecific/com.tesla.3p.public-key.pem
```

## 3. Register a Tesla developer app

1. Go to <https://developer.tesla.com> → create an app.
2. Set:
   - **Allowed origin / domain:** `tesla.yourdomain.com`
   - **Redirect URI:** `https://tesla.yourdomain.com/callback`
   - **Scopes:** `vehicle_device_data` (read-only is all we need) + `offline_access`
3. Copy the **Client ID** and **Client Secret**.

Create `tesla_config.json` on the VM (it's git-ignored — never committed):
```json
{
  "TESLA_CLIENT_ID": "xxxxxxxx",
  "TESLA_CLIENT_SECRET": "xxxxxxxx",
  "TESLA_DOMAIN": "tesla.yourdomain.com",
  "TESLA_REDIRECT_URI": "https://tesla.yourdomain.com/callback",
  "TESLA_VIN": "5YJ3E1EA0KF000000"
}
```

Then register your domain with Tesla and complete the OAuth login:
```bash
python3 tesla_auth.py partner     # one-time: Tesla fetches your public key
python3 tesla_auth.py login       # open the URL, approve, paste the redirected URL back
```
`login` saves your **refresh token** into `tesla_config.json`. Test it:
```bash
python3 fetch_tesla.py fleet --dry-run
```

> Note: read-only `vehicle_device_data` does **not** require pairing a virtual
> key with the car — that's only for sending commands. Hosting the public key
> is still required for partner registration, which is why step 2 exists.

## 4. Schedule the daily pull

Give the VM push access to the repo (a GitHub **deploy key** with write access
is simplest), set `git config user.name/email`, then install the timer:

```bash
# edit User= and the paths in the unit if you're not the 'ubuntu' user
sudo cp deploy/tesla-fetch.service /etc/systemd/system/
sudo cp deploy/tesla-fetch.timer   /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now tesla-fetch.timer

systemctl list-timers tesla-fetch.timer   # confirm next run
sudo systemctl start tesla-fetch.service   # run once now to test
journalctl -u tesla-fetch.service -n 30    # see the result
```

`deploy/run_fetch.sh` pulls the latest branch, runs `fetch_tesla.py fleet`,
and commits + pushes `data.js` only when something changed. One reading is kept
per day, so a re-run just updates today's entry.

---

## Free-tier reality check

The Fleet API is free for personal use within a monthly request allowance.
One car polled once a day (≈30 requests/month) is far under it. If you ever
poll aggressively you could hit the free cap — the daily timer keeps you safe.

## Do I need an Oracle database?

No. The dashboard is file-based (`data.js` in git), which is why this is so
simple. The Oracle VM is used purely as an always-on host. If you later want a
queryable history (e.g. SQL over years of readings), an Oracle Autonomous DB
could back the data instead — ask and I'll add a DB-backed store, but it isn't
needed for the dashboard to work.

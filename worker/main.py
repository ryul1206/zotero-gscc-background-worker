import yaml
import gscc
import webhook
import datetime
import pause


# Parse secret_cfg.yaml
def parse_secret_cfg(secret_cfg_fname):
    with open(secret_cfg_fname) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    g = gscc.GSCC(cfg['user_id'], cfg['api_key'])
    wh = webhook.Webhook(cfg['webhook_url'], cfg['webhook_style'])
    sleep_range = (cfg['min_sleep_sec'], cfg['max_sleep_sec'])
    return g, wh, sleep_range


def main(secret_cfg_fname):
    g, wh, sleep_range = parse_secret_cfg(secret_cfg_fname)

    while True:
        # Get next time to run
        next_dt = datetime.datetime.now() + datetime.timedelta(days=1)
        # Fetch all GSCC
        g.fetch_all()
        wh.send(f"Finished fetching all GSCC items.")
        # Pause until next update
        pause.until(time=next_dt)


if __name__=="__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else '../secret_cfg.yml')
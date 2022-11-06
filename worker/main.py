import yaml
import gscc
import webhook
import datetime
import pause


# Parse secret_cfg.yaml
def parse_secret_cfg(secret_cfg_fname):
    with open(secret_cfg_fname) as f:
        cfg = yaml.load(f, Loader=yaml.FullLoader)
    gs = gscc.GSCC(cfg['user_id'], cfg['api_key'])
    gs.set_sleep_range(cfg['min_sleep_sec'], cfg['max_sleep_sec'])
    wh = webhook.Webhook(cfg['webhook_url'], cfg['webhook_style'])
    sleep_range = (cfg['min_sleep_sec'], cfg['max_sleep_sec'])
    day_cycle = cfg['day_cycle']
    return gs, wh, sleep_range, day_cycle


def main(secret_cfg_fname):
    gs, wh, sleep_range, day_cycle = parse_secret_cfg(secret_cfg_fname)

    while True:
        # Start message
        initial_count = gs.get_current_num_items()
        estimated_hours = gs.get_estimated_fetch_time()
        estimated_date = datetime.datetime.now() + datetime.timedelta(hours=estimated_hours)
        wh.send(f"Starting to fetch {initial_count} items.\nEstimated time: {estimated_hours:0.2f} hours (to be completed at {estimated_date:%Y-%m-%d %H:%M})")

        # Get next time to run
        next_dt = datetime.datetime.now() + datetime.timedelta(days=day_cycle)

        # Fetch all GSCC
        gs.fetch_all(wh)

        # Finish message
        wh.send(f"Finished fetching all GSCC items. The next run will be started at {next_dt:%Y-%m-%d %H:%M}.")

        # Pause until next update
        pause.until(time=next_dt)


if __name__=="__main__":
    import sys
    main(sys.argv[1] if len(sys.argv) > 1 else '../secret_cfg.yml')
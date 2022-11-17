import yaml
import webhook
import recaptcha
import gscc


def _parse_cfg() -> gscc.GSCC:
    # Open config file
    try:
        import sys
        cfg_fname = sys.argv[1] if len(sys.argv) > 1 else '../secret_cfg.yml'
        with open(cfg_fname) as f:
            cfg = yaml.load(f, Loader=yaml.FullLoader)
    except FileNotFoundError:
        print(f"Could not find the config file: {cfg_fname}")
        sys.exit(1)

    # Webhook (Optional)
    try:
        wh = webhook.Webhook()
        if 'webhook' in cfg:
            wh.config_all(cfg['webhook'])
    except KeyError as e:
        print(f"[Webhook config] Could not find the key: {e}")
        sys.exit(1)

    # ReCaptcha (Required)
    try:
        rc = recaptcha.ReCaptcha(cfg['captcha'])
    except Exception as e:
        print(f"[ReCaptcha config] {e}")
        sys.exit(1)

    # GSCC (Required)
    try:
        gs = gscc.GSCC(cfg['zotero'], cfg['update'], rc, wh)
    except Exception as e:
        print(f"[GSCC config] {e=}")
        sys.exit(1)
    return gs


if __name__ == "__main__":
    gs = _parse_cfg()
    gs.run()
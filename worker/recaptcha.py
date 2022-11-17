import requests
import re
from twocaptcha import TwoCaptcha


class ReCaptcha:
    def __init__(self, captcha_cfg):
        self._captcha_solver = TwoCaptcha(**captcha_cfg)

    @property
    def balance(self):
        """
        * Docs: https://2captcha.com/lang/python
        * Returns: float in USD
        """
        return self._captcha_solver.balance()

    def solve(self, response: HTMLResponse, url: str) -> bool:
        """
        * Testing: "https://www.google.com/recaptcha/api2/demo"
        * Docs:    https://2captcha.com/2captcha-api#solving_recaptchav2_new
        * Github:  https://github.com/2captcha/2captcha-python
        """
        # Extract the sitekey
        # TODO
        html = response.text
        site_key = re.search(r'data-sitekey="(.+?)"', html)
        if not site_key:
            raise Exception("Could not find sitekey")
        site_key = site_key.group(1)

        # Solve the captcha (reCAPTCHA v2)
        try:
            result = self._captcha_solver.recaptcha(sitekey=site_key, url=url)
        except Exception as e:
            raise Exception(f"Failed to solve captcha: {e=}")
        else:
            result_id = result["captchaId"]
            result_token = result["code"]

        # Submit the captcha token
        try:
            # TODO
            response = requests.post(
                url,
                data={
                    "g-recaptcha-response": result_token,
                    "captchaId": result_id,
                },
            )
        except Exception as e:
            raise Exception(f"Failed to submit captcha: {e=}")

        # Check the response is valid
        # TODO
        return response.status_code == 200

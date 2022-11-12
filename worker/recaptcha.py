import requests
import re
from twocaptcha import TwoCaptcha


class ReCaptcha:
    def __init__(self, captcha_cfg):
        self._captcha_solver = TwoCaptcha(**captcha_cfg)

    def solve(self, response: requests.Response, url: str) -> bool:
        """
        * Testing: "https://www.google.com/recaptcha/api2/demo"
        * Docs:    https://2captcha.com/2captcha-api#solving_recaptchav2_new
        * Github:  https://github.com/2captcha/2captcha-python
        """
        # Extract the sitekey
        html = response.text
        site_key = re.search(r'data-sitekey="(.+?)"', html).group(1)

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
        return response.status_code == 200


# if __name__ == "__main__":
#     g = ReCaptcha(API_KEY)

#     url = "https://www.google.com/recaptcha/api2/demo"
#     response = requests.get(url)

#     # Check if the captcha exists
#     if "g-recaptcha" in response.text:
#         print("Solve the captcha")
#         result = g._solve_captcha(response, url)
#         print(f"Result: {result=}")
#     else:
#         print("No captcha found")

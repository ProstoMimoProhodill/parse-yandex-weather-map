def timer(fun):
    import time

    def f(*args, **kwargs):
        start = time.time()
        res = fun(*args, **kwargs)
        print(f'[UTIL][{fun.__name__}] Time: {time.time() - start}')
        return res

    return f


def chrome_dev_tools_network(url, headless=True, filter=None):
    from selenium import webdriver
    from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
    from selenium.webdriver.chrome.options import Options
    from config import webdriver_path

    options = Options()
    options.headless = headless
    cap = DesiredCapabilities.CHROME
    cap['goog:loggingPrefs'] = {'performance': 'ALL'}
    driver = webdriver.Chrome(webdriver_path, desired_capabilities=cap, options=options)

    driver.get(url)
    if filter:
        log = [item for item in driver.get_log('performance') if filter in str(item)]
    else:
        log = driver.get_log('performance')
    driver.close()

    return log


def extract_token(logs):
    import json

    for log in logs:
        j = json.loads(log['message'])
        try:
            params = j['message']['params']
            if params['type'] == 'Image':
                url = params['request']['url']
                if url[-4:] == 'jpeg':
                    token = "/" + "/".join(url.split('/')[-4:-2])
                    return token
        except Exception:
            pass
    return None



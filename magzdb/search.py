import re
import requests
import time
from loguru import logger

MAX_TIMEOUTS=10
TIMEOUT_DURATION=1
SLEEP_TIME=1

def search(search_term: str, retry=0):
  search_url="https://magzdb.org/makeqlist"
  result_re = re.compile(r"""<td><a\s*href=(?P<url>\/j\/(?P<id>\d+))>(?P<text>.*)</td>""", flags=re.IGNORECASE | re.MULTILINE)
  tag_re = re.compile(r"(<.*?>)", flags=re.IGNORECASE)
  try:
    search_res = requests.post(search_url, params={"t": search_term}, timeout=TIMEOUT_DURATION).text
    matches = []
    for m in re.finditer(result_re,search_res):
      mg = m.groupdict()
      mg['text'] = re.sub(tag_re,"",mg['text']) # someone with better re skills could avoid this
      matches.append(mg)
    print_results(matches)
  except re.error as e:
    logger.error(e)
    raise Exception("REGEX error.")
  except requests.ConnectTimeout as e:
    if(retry < MAX_TIMEOUTS):
      logger.debug("timeout - %d/%d" % (retry,MAX_TIMEOUTS))
      time.sleep(SLEEP_TIME)
      search(search_term, retry+1)
    else:
      logger.error(e)
      raise Exception("Connection timeout.")
  except requests.ConnectionError as e:
    logger.error(e)
    raise Exception("Connection error encountered.")
  except requests.HTTPError as e:
    logger.error(e)
    raise Exception("HTTP Error encountered.")

def print_results(results: list):
  for result in results:
    print("%-6s - %-32s - %s" % (result['id'], result['text'], ("https://magzdb.org%s" % result['url'])))

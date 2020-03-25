import gspread
from oauth2client.service_account import ServiceAccountCredentials

_scope = ["https://www.googleapis.com/auth/drive", "https://spreadsheets.google.com/feeds", ]
_credentials = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", _scope)
_gc = gspread.authorize(_credentials)

def forceOpenSS(title: str):
  try:
    ss = _gc.open(title)
    print(f"Spreadsheet '{title}' was opened.")
  except:
    ss = _gc.create(title)
    ss.share('dennispaust@gmail.com', perm_type="user", role="owner", notify=False, email_message=None, with_link=False)
    print(f"Spreadsheet '{title}' was created.")
  return ss


def forceCreateWS(_ss, title: str, rows: int, cols: int):
  try:
    ws = _ss.add_worksheet(title=title, rows=str(rows), cols=str(cols))
    print("Worksheet '" + title + "' was created.")
  except:
    removeWS(_ss, title)
    ws = _ss.add_worksheet(title=title, rows=str(rows), cols=str(cols))
    print("Worksheet '" + title + "' was overwritten.")

  return ws

removeWS = lambda _ss, title: _ss.del_worksheet(_ss.worksheet(title))

# from time import sleep, 
# def delay(secs: float):
#   print(f"waiting {str(secs)} seconds for writing limit to cool down...", end="", flush=True)
#   sleep(secs)
#   print("continuing now.")

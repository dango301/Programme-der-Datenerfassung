# USER VARIABLES
docTitle = "Arduino Standard LED"  # TC LED Blue
port = "COM8"
T = 80 #angestrebte Periodenlänge in ms



import serial
from time import time
from bisect import bisect_left
from math import floor


# region Serial Communication
ser = serial.Serial(port=port, baudrate=9600)
startTime = time()
print(f"\nConnection with Port '{ser.portstr}' successfully established.")

raw = ""
while not "DATA_END" in raw:
  for c in ser.read():
    raw += chr(c)  # convert from ASCII
ser.close()

print(f"DATA RECEIVED after {str(int(time() - startTime) / 60)} minutes.", end="\n")
# endregion



# region Data Extraction & Evaluation
raw = "".join([s for s in raw.splitlines(True) if s.strip("\r\n")])
lines = [l for l in raw.splitlines()]


class Measurement:
  def __init__(self, dur: float, data: dict):
    self.dur = dur
    self.data = data

  def __str__(self):
    return str(self.__class__) + ": " + str(self.__dict__)

class DataAverage:
  def __init__(self, dur: float, max1: float, min1: float, max2: float, min2: float):
    self.dur = dur
    self.max1 = max1
    self.min1 = min1
    self.max2 = max2
    self.min2 = min2
    # Reihenfolge ist extrem wichtig für Tabellenzuweisung!!!
  
  def __str__(self):
    return str(self.__class__) + ": " + str(self.__dict__)

def take_closest(myList, myNumber):
  """
  Assumes myList is sorted. Returns closest value to myNumber.

  If two numbers are equally close, return the smallest number.
  """
  pos = bisect_left(myList, myNumber)
  if pos == 0:
    return myList[0]
  if pos == len(myList):
    return myList[-1]
  before = myList[pos - 1]
  after = myList[pos]
  if after - myNumber < myNumber - before:
    return after
  else:
    return before

getAvg = lambda l: sum(l) / len(l)


indeces = [i for i in range(len(lines)) if "MEASUREMENT_DURATION: " in lines[i]] + [len(lines) - 2]
measurements = []

for n in range(len(indeces) - 1):
  dur = float(lines[indeces[n]].split("MEASUREMENT_DURATION: ")[1])
  data = {}
  for l in lines[indeces[n] + 1 : indeces[n + 1] - 1]:
    pair = [int(v) for v in l.split(":")]
    data[pair[0]] = pair[1]

  measurements.append(Measurement(dur, data))


byDur = {}
for d in tuple([m.dur for m in measurements]):
  byDur[d] = [m.data for m in measurements if m.dur == d]


averages = []
for dur in list(byDur.keys()):
  allData = byDur[dur]
  allMax1, allMax2, allMin1, allMin2 = [], [], [], []

  for data in allData:

    ts = list(data.keys())
    vals = list(data.values())

    t_max1 = take_closest(ts, dur)
    t_min1 = take_closest(ts, dur + T)
    t_max2 = take_closest(ts, 2 * dur + T)
    t_min2 = take_closest(ts, 2 * (dur + T))
    
    allMax1.append(data[t_max1])
    allMax2.append(data[t_max2])
    allMin1.append(data[t_min1])
    allMin2.append(data[t_min2])

  averages.append(DataAverage(dur, getAvg(allMax1), getAvg(allMin1), getAvg(allMax2), getAvg(allMin2)))


print("DATA PROCESSED", end="\n\n")
# endregion



# region Google Sheets Upload

from gTools import *
if input(f"Do you want to proceed with the title '{docTitle}'? (y/n)  ") != "y":
  docTitle = input("Enter your new Title for the Document:  ")
ss = forceOpenSS(docTitle)
print("\nDATA UPLOAD STARTED")


#region Data Averages Upload
title = "Data Averages"
try:
  ws = ss.worksheet(title)
  existing = [float(v) for v in ws.col_values(1)[1:]]

  for avg in averages:
    if avg.dur in existing:
      rowIndex = existing.index(avg.dur) + 2
      cellList = ws.range(rowIndex, 1, rowIndex, 4)
      for cell, info in zip(cellList, list(vars(avg).values())):
        cell.value = info
      ws.update_cells(cellList)
      print(f"Row for Duration {str(avg.dur)} was overwritten in Worksheet '{title}'.")
    else:
      ws.append_row(list(vars(avg).values()))
      print(f"Row for Duration {str(avg.dur)} was added to Worksheet '{title}'.")
except:
  ws = forceCreateWS(ss, title, len(averages) + 1, 5)
  cellList = ws.range(1, 1, len(averages) + 1, 5)
  labels = ["Duration", "Max. 1", "Min. 1", "Max. 2", "Min. 2"]
  data = []
  for avg in averages:
    for v in list(vars(avg).values()):
      data.append(v)
  for cell, info in zip(cellList, labels + data):
    cell.value = info
  ws.update_cells(cellList)

print(f"Worksheet '{title}' was updated.", end="\n\n")
#endregion


#region Measurements Upload
for dur, allData in byDur.items():

  dataLenghts = [len(d) for d in allData]
  nRows = len(allData) + 1
  nCols = sum(dataLenghts) + 1
  title = "Leuchtdauer: " + str(dur) + "ms"
  ws = forceCreateWS(ss, title, nRows, nCols)

  cellList = ws.range(1, 1, nRows, nCols)
  r1 = ["Time in ms"]
  for data in allData:
    for x in list(data.keys()):
      r1.append(x)
  for cell, v in zip(cellList, r1): cell.value = v
  
  inRowIndex = 1
  for iRow, data in enumerate(allData, 1):
    rowStart = iRow * nCols
    
    cellList[rowStart].value = f"SW {str(iRow)}"
    for cell, info in zip(cellList[rowStart + inRowIndex: rowStart + rowStart + len(data)], [v for v in list(data.values())]):
      cell.value = info
    inRowIndex += len(data)

  ws.update_cells(cellList)
  
  print(f"Worksheet '{title}' was updated.", end="\n\n")
#endregion

# endregion

if ss.sheet1.title == "Sheet1": removeWS(ss, "Sheet1")
print(f"\nPROGRAM FULLY EXECUTED after {str(int(time() - startTime) / 60)} minutes.")

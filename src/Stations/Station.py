class Station:
  def __init__(self, arr):
    self.name = str(arr[0])
    self.longName = arr[1]
    self.alpha3 = arr[2]
    self.tiploc = arr[3]
    self.tpl = arr[4]

  def __str__(self):
    return self.name + "; " + self.longName + "; " + self.alpha3 + "; " + self.tiploc + "; " + self.tpl + ";"

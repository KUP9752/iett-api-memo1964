############ Do not change the assignment code value ############
assignment_code = 140110201
name = "Baha"
surname = "Blast"
student_id = "1964"
### Do not change the variable names above, just fill them in ###

from enum import Enum
from typing import Literal, Optional, Any
from zeep import Client
import json
from pydantic import BaseModel  
import lxml

### ================= Types
class Duyuru(BaseModel): 
  HATKODU: str
  HAT: str
  TIP: str 
  GUNCELLEME_SAATI: str
  MESAJ: str
  
class FiloArac(BaseModel):
  Operator: str
  Garaj: Optional[str]
  KapiNo: str
  Saat: str #FIXME: make DateTime??
  Boylam: float
  Enlem: float
  Hiz: int # float??
  Plaka: Optional[str] #TODO: plaka class??
  
class HatAracKonum(BaseModel):
  kapino: str
  boylam: float
  enlem: float  
  hatkodu: str
  guzergahkodu: str
  hatad: str
  yon: str #Literal["G", "D"]
  son_konum_zamani: str #FIXME time??
  yakinDurakKodu: str
    
class DurakTipi(Enum):
  CCMODERN, \
  İETTBAYRAK, \
  DİĞER, \
  CCMODERNDR, \
  WALLMODERN, \
  İSTON_PERON, \
  İSTON_DAR, \
  İSTON_GENİŞ, \
  İETTÜÇGEN, \
  AÇIK_DURAK, \
  İETTCAMLI, \
  İSTON_GENİŞ_İBB, \
  İSTON_DAR_İBB = range(13)
  
class HatInfo(BaseModel):
  HATKODU: str
  YON: Literal["G", "D"]
  SIRANO: int
  DURAKKODU: int
  DURAKADI: str
  XKOORDINATI: float # maybe coord class??
  YKOORDINATI: float # coord??
  DURAKTIPI: DurakTipi
  ISLETMEBOLGE: str
  ISLETMEALTBOLGE: str
  ILCEADI:str 

### ========================= URLS
duyuruUrl = "https://api.ibb.gov.tr/iett/UlasimDinamikVeri/Duyurular.asmx?wsdl"
fleetUrl = "https://api.ibb.gov.tr/iett/FiloDurum/SeferGerceklesme.asmx?wsdl"
fleetUrl = "https://api.ibb.gov.tr/iett/FiloDurum/SeferGerceklesme.asmx?wsdl"
hatUrl = "https://api.ibb.gov.tr/iett/ibb/ibb.asmx?wsdl"
busUrl = "https://api.ibb.gov.tr/iett/FiloDurum/SeferGerceklesme.asmx?wsdl"

def getResp(url: str, api: str, **kwargs: dict[str, str]):
  """
  Helper that does the SOAP API request

  Args:
      url (str): wsdl URL to use 
      api (str): endpoint to reach on the above url

  Returns:
      JSON | XML : Returns the raw data returned 
  """
  client = Client(wsdl = url)
  return client.service[f"{api}"](**kwargs)
  
### ========================= TASKS
def announcements(line_code: str) -> tuple[int, list[str]]:
  """
  Function that takes the line code, calculates how many announcements there are on the line, and returns the announcements as a list.

  Args:
      line_code (str): Code of the bus line

  Returns:
      tuple[int, list[str]]: (Number of messages, list of messages)
  """
  announcements = getResp(url = duyuruUrl, api = "GetDuyurular_json")
  announcements: list[Duyuru] = [Duyuru.model_validate(d) for d in json.loads(announcements)]
  
  mesajs = [duyuru.MESAJ for duyuru in filter(lambda duyuru: duyuru.HATKODU == line_code, announcements)]
  return len(mesajs), mesajs
    
def stopping_buses() -> list[str]:
  """
  Function function that returns the door numbers of all currently stopping buses as a list.

  Returns:
      list[str]: List of Bus Door Numbers
  """
  fleetData = getResp(url = fleetUrl, api = "GetFiloAracKonum_json")
  fleetData: list[FiloArac] = [FiloArac.model_validate(fd) for fd in json.loads(fleetData)]
  
  ## assumption: find stopping from speed? if hiz == 0 => stopping
  return [arac.KapiNo for arac in filter(lambda arac: arac.Hiz == 0, fleetData)]
  
def max_speeds() -> list[FiloArac]: # !! in json format
  """
  Function that returns information about the top 3 buses with the highest speed at 
  the moment

  Returns:
      list[FiloArac]: 3 buses with the highest speeds
  """
  fleetData = getResp(url = fleetUrl, api = "GetFiloAracKonum_json")
  fleetData: list[FiloArac] = [FiloArac.model_validate(fd) for fd in json.loads(fleetData)]
  
  return [arac.model_dump() for arac in sorted(fleetData, key = lambda fa: fa.Hiz, reverse = True)[:2]]
    
def show_line_stops(line_code: str, direction: Literal["D", "G"]) -> list[str]:
  """
  Function that takes the line code and direction parameters and returns the list of 
  the stops of that line in that direction respectively. 

  Args:
      line_code (str): Code of the Bus Line
      direction ("D" | "G"): 'D' for arrival (dönüş) and 'G' for departure (gidiş)

  Returns:
      list[str]: List of stop names
  """
  hatXML: lxml.etree.Element = getResp(url = hatUrl, api = "DurakDetay_GYY", hat_kodu = line_code)
  
  ## if YON == direction => return DURAKADI
  matches = hatXML.xpath(f'.//Table[YON = "{direction}"]/DURAKADI') if direction in ["G", "D"] else []
  ##FIXME error if the direction param is incorrect??
  
  return [m.text for m in matches]
      
def live_tracking(line_code: str, direction: Literal["G", "D"]) \
  -> tuple[list[tuple[str, float, float]], tuple[str, float, float]]:
  """ 
  Function that saves the stops of the selected line and direction and the data of 
  the  buses  currently  operating  on  that  line  to  the  where.js  file 
  
  Args:
      line_code (str): Code of the Bus Line
      direction ("D" | "G"): 'D' for arrival (dönüş) and 'G' for departure (gidiş)

  Returns:
      (list[T], list[T]): list of stops and list of buses Door Numbers with their locations
      where T = tuple(str, float, float) -> (name, ycoord, xcoord)
      
  """
  ## Stops: 
  hatXML: lxml.etree.Element = getResp(url = hatUrl, api = "DurakDetay_GYY", hat_kodu = line_code)
  stopMatches = hatXML.xpath(f'.//Table[YON = "{direction}"]') if direction in ["G", "D"] else []
  
  ## Buses: 
  busData = getResp(url = busUrl, api = "GetHatOtoKonum_json", HatKodu = line_code)
  busMatches = [HatAracKonum.model_validate(bus) for bus in json.loads(busData)]
  
  def extract(root, items: dict[str, type]) -> tuple[Any, Any, Any]:
    ## ty used to cast the types (mainly for float as  text is always str)
    return [ty(root.find(item).text) for item, ty in items.items()]
  
  stops = [extract(match, {"DURAKADI": str, "YKOORDINATI": float, "XKOORDINATI": float}) for match in stopMatches]
  buses = [[bus.kapino, bus.enlem, bus.boylam] for bus in busMatches]
  
  with open("where.js", "w") as f:
    f.write(f"{stops = }\n")
    f.write(f"{buses = }\n")
    
  return stops, buses

with open("out2.txt", "w") as f:
  f.write(f"(1) \n\t{announcements("10") = }\n")
  f.write(f"(2) \n\t{stopping_buses() = }\n")
  f.write(f"(3) \n\t{ max_speeds() = }\n")
  f.write(f"(4) \n\t{show_line_stops("19T", "G")}\n")
  f.write(f"(4) \n\t{show_line_stops("122C", "D")}\n")
  f.write(f"(5) \n\t{live_tracking("122C", "D")}\n")

# print(f"(1) \n\t{announcements("10") = }\n")
# print(f"(2) \n\t{stopping_buses() = }\n")
# print(f"(3) \n\t{ max_speeds() = }\n")
# print(f"(4) \n\t{show_line_stops("19T", "G")}\n")
# print(f"(4) \n\t{show_line_stops("122C", "D")}\n")
# print(f"(5) \n\t{live_tracking("122C", "D")}\n")


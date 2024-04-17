############ Do not change the assignment code value ############
assignment_code = 140110201
name = "Baha"
surname = "Blast"
student_id = "1964"
### Do not change the variable names above, just fill them in ###

from dataclasses import dataclass
from enum import Enum
from typing import Literal, Optional, TypeAlias, Any
from zeep import Client
import json
from pydantic import BaseModel  
import xml.etree.ElementTree as ET
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
  
### ========================= TASKS
def announcements(line_code: str) -> tuple[int, list[str]]:
    duyuruUrl = "https://api.ibb.gov.tr/iett/UlasimDinamikVeri/Duyurular.asmx?wsdl"
    duyuruClient = Client(wsdl = duyuruUrl)
    announcements = duyuruClient.service.GetDuyurular_json()
    duyuruClient = Client(wsdl = duyuruUrl)
    announcements = duyuruClient.service.GetDuyurular_json()
    announcements: list[Duyuru] = [Duyuru.model_validate(d) for d in json.loads(announcements)]
    
    mesajs = [duyuru.MESAJ for duyuru in filter(lambda duyuru: duyuru.HATKODU == line_code, announcements)]
    return len(mesajs), mesajs
    
    
def stopping_buses() -> list[str]:
  fleetUrl = "https://api.ibb.gov.tr/iett/FiloDurum/SeferGerceklesme.asmx?wsdl"
  fleetClient = Client(wsdl = fleetUrl)
  fleetData = fleetClient.service.GetFiloAracKonum_json()
  fleetData: list[FiloArac] = [FiloArac.model_validate(fd) for fd in json.loads(fleetData)]
  
  ## assumption: find stopping from speed? if hiz == 0 => stopping
  return [arac.KapiNo for arac in filter(lambda arac: arac.Hiz == 0, fleetData)]
  
def max_speeds() -> list[FiloArac]: # !! in json format
    fleetUrl = "https://api.ibb.gov.tr/iett/FiloDurum/SeferGerceklesme.asmx?wsdl"
    fleetClient = Client(wsdl = fleetUrl)
    fleetData = fleetClient.service.GetFiloAracKonum_json()
    fleetData: list[FiloArac] = [FiloArac.model_validate(fd) for fd in json.loads(fleetData)]
    print(f"{ fleetData[0] =}")
    
    return [arac.model_dump() for arac in sorted(fleetData, key = lambda fa: fa.Hiz, reverse = True)[:2]]
    
def show_line_stops(line_code: str, direction: Literal["D", "G"]) -> list[str]:
    hatUrl = "https://api.ibb.gov.tr/iett/ibb/ibb.asmx?wsdl"
    hatClient = Client(wsdl = hatUrl)
    hatXML:lxml.etree.Element = hatClient.service.DurakDetay_GYY(hat_kodu = line_code)
    
    ## if YON == direction return DURAKADI
    matches = hatXML.xpath(f'.//Table[YON = "{direction}"]/DURAKADI') if direction in ["G", "D"] else []
    ##FIXME error if the direction param is incorrect??
    
    return [m.text for m in matches]
      
def live_tracking(line_code: str, direction: Literal["G", "D"]) \
  -> tuple[list[tuple[str, float, float]], tuple[str, float, float]]:
    pass

# print(f"{announcements("10") = }")
# print()
# # print(f"{stopping_buses() = }")
# print()
# print(f"{ max_speeds() = }")
# print()
print(f"{show_line_stops("19T", "G")}")
print("-----")
print(f"{show_line_stops("122C", "D")}")
print()



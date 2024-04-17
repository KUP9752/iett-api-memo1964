############ Do not change the assignment code value ############
assignment_code = 140110201
name = "Baha"
surname = "Blast"
student_id = "1964"
### Do not change the variable names above, just fill them in ###

from dataclasses import dataclass
from typing import Literal, Optional, TypeAlias, Any
from zeep import Client
import json
from pydantic import BaseModel  

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
  Saat: str ## make DateTime??
  Boylam: float
  Enlem: float
  Hiz: int ## float??
  Plaka: Optional[str] ## plaka class??

def announcements(line_code: str) -> tuple[int, list[str]]:
    duyuruUrl = "https://api.ibb.gov.tr/iett/UlasimDinamikVeri/Duyurular.asmx?wsdl"
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
  
def max_speeds() -> list[FiloArac.json]: ## in json format
    fleetUrl = "https://api.ibb.gov.tr/iett/FiloDurum/SeferGerceklesme.asmx?wsdl"
    fleetClient = Client(wsdl = fleetUrl)
    fleetData = fleetClient.service.GetFiloAracKonum_json()
    fleetData: list[FiloArac] = [FiloArac.model_validate(fd) for fd in json.loads(fleetData)]
    print(f"{ fleetData[0] =}")
    
    return [arac.model_dump() for arac in sorted(fleetData, key = lambda fa: fa.Hiz, reverse = True)[:2]]
    
def show_line_stops(line_code: str, direction: Literal["D", "G"]) -> list[str]:
    
def live_tracking(line_code, direction):
    pass

print(f"{announcements("10") = }")
print()
# print(f"{stopping_buses() = }")
print()
print(f"{ max_speeds() = }")
print()


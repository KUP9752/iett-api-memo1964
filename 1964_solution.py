############ Do not change the assignment code value ############
assignment_code = 140110201
name = "Baha"
surname = "Blast"
student_id = "1964"
### Do not change the variable names above, just fill them in ###cd 
############ Do not change the assignment code value ############
assignment_code = 140110201
name = "Baha"
surname = "Blast"
student_id = "1964"
### Do not change the variable names above, just fill them in ###

from dataclasses import dataclass
from typing import Optional, TypeAlias, Any
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

def announcements(line_code: str) -> tuple[int, list[str]]:
    duyuruUrl = "https://api.ibb.gov.tr/iett/UlasimDinamikVeri/Duyurular.asmx?wsdl"
    DuyuruClient = Client(wsdl = duyuruUrl)
    announcements = DuyuruClient.service["GetDuyurular_json"]()
    
    announcements: list[Duyuru] = [Duyuru.model_validate(d) for d in json.loads(announcements)]
    
    thisLine = filter(lambda a: a.HATKODU == line_code, announcements)
    mesajs = [duyuru.MESAJ for duyuru in thisLine]
    
    return len(mesajs), mesajs
    
    
def stopping_buses():
    pass
    
def max_speeds():
    pass
    
def show_line_stops(line_code, direction):
    pass
    
def live_tracking(line_code, direction):
    pass

print(f"{announcements("10") = }")


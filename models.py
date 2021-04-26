from pydantic import BaseModel
from typing import List


class WiFinetwork(BaseModel):
    SSID: str
    RSSI: int
    MAC: str
    Encryptiontype: str


class WiFiscan(BaseModel):
    wifilist: List[WiFinetwork]


class Probeinfo(BaseModel):
    SSID: str
    MAC: str
class ProbeData(BaseModel):
    ProbeList: List[Probeinfo]
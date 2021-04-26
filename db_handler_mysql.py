import os
import json
from sqlalchemy import *
from sqlalchemy.exc import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
from sqlalchemy_utils import database_exists, create_database
from logger import setup_logging
dotenv_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), '.env')
load_dotenv(dotenv_path)

database = os.environ.get('fastapi_db')
user = os.environ.get('fastapi_db_user')
passwd = os.environ.get('fastapi_db_user_pass')
host = os.environ.get('fastapi_db_host')
port = os.environ.get('fastapi_db_port')

Base = declarative_base()


class ProbeData(Base):
    __tablename__ = 'ProbeData'

    SSID = Column('SSID', VARCHAR(length=255), primary_key=True, unique=False)
    MAC = Column('MAC', VARCHAR(length=255), unique=False)

    def __repr__(self):
        return f"<ProbeData(SSID={self.SSID}, MAC={self.MAC})>"


class WiFiData(Base):
    __tablename__ = 'WiFiData'

    SSID = Column('SSID', VARCHAR(length=255), primary_key=True)
    RSSI = Column('RSSI', INTEGER, nullable=True, unique=False)
    MAC = Column('MAC', VARCHAR(length=255), nullable=False, unique=False)
    Encryptiontype = Column('Encryptiontype', VARCHAR(
        length=255), nullable=True, unique=False)
    __table_args__ = (UniqueConstraint('SSID'),)

    def __repr__(self):
        return f"<WiFiData(SSID={self.SSID}, RSSI={self.RSSI}, MAC={self.MAC}, Encryptiontype={self.Encryptiontype})>"


class database_handler():

    def __init__(self):
        self.config = {
            'user': user,
            'passwd': passwd,
            'host': host,
            'port': port
        }
        self.db = database
        self.engine = create_engine(
            f"mysql+pymysql://{self.config['user']}:{self.config['passwd']}@{self.config['host']}:{self.config['port']}/{self.db}"
        )
        self.sqlsession = sessionmaker(bind=self.engine)
        self.logger = setup_logging("db_handler")
        self.create_database()

    def return_url(self):
        return f"mysql+pymysql://{self.config['user']}:{self.config['passwd']}@{self.config['host']}:{self.config['port']}/{self.db}"

    def return_metadata(self):
        return Base.metadata

    def create_database(self):
        if not database_exists(self.engine.url):
            self.logger.log("creating database")
            create_database(self.engine.url)

    def search_wifi(self, ssid: str):
        session = self.sqlsession()
        result = session.query(WiFiData).filter_by(SSID=ssid).first()
        self.logger.debug(f"Fetching this WiFiData from database: {id}")
        if not result:
            return False
        else:
            return {"SSID": result.SSID, "RSSI": result.RSSI, "MAC": result.MAC, "Encryptiontype": result.Encryptiontype}

    def get_wifi_data(self):
        data_dict = {}
        session = self.sqlsession()
        result = session.execute(select([WiFiData]))
        for row in result:
            self.logger.debug(
                f"Fetched this WiFiData: {row.SSID} with this mac: {row.MAC}")
            data_dict[row.SSID] = {
                "RSSI": row.RSSI, "MAC": row.MAC, "Encryptiontype": row.Encryptiontype}
        return data_dict

    def add_WiFiData(self, scanData):
        session = self.sqlsession()
        try:
            for data in scanData["wifilist"]:
                new_WiFiData = WiFiData(SSID=data["SSID"],
                                        RSSI=data["RSSI"], MAC=data["MAC"], Encryptiontype=data["Encryptiontype"])
                session.add(new_WiFiData)
                session.commit()
        except IntegrityError as e:
            self.logger.exception(f"Duplicate keys provided: {e}")
            return False, "Duplicate keys provided"
        return True, None

    def get_probe_data(self):
        data_dict = {}
        session = self.sqlsession()
        result = session.execute(select([ProbeData]))
        for row in result:
            if row.MAC not in data_dict:
                data_dict[row.SSID] = []
            self.logger.debug(
                f"Fetched this probedata: {row.SSID} with this mac: {row.MAC}"
            )
            data_dict[row.MAC].append(row.SSID)
        return data_dict

    def add_ProbeData(self, probeddata):
        session = self.sqlsession()
        try:
            for data in probeddata["ProbeList"]:
                if data["SSID"] != "":
                    new_probedata = ProbeData(
                        SSID=data["SSID"], MAC=data["MAC"])
        except IntegrityError as e:
            self.logger.exception(f"Duplicate somethin, this shouldn't occurr")
        return True, None

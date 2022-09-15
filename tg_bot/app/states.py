from enum import Enum

class States(Enum):
    S_START = "0"
    S_ENTER_DEVICE_ID = "1"
    S_ENTER_ACCOUNT_ID = "2"
    S_ENTER_PHONE_DEVICE = "3"
    S_GET_CONTACT = "4"
    S_GET_PHOTO = "5"

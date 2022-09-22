from enum import Enum

class States(Enum):
    S_START = "0"
    S_ENTER_DEVICE_ID = "1"
    S_GET_ANSWER_FOR_CREATE_OBJECT = "2"
    S_ENTER_ACCOUNT_ID = "3"
    S_ENTER_PHONE_DEVICE = "4"
    S_GET_CONTACT = "5"
    S_GET_PHOTO = "6"


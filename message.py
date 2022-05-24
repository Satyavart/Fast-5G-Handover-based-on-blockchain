import json

def registration_message(id):
    message = {
        "Type": "Registration",
        "Count": 1,
        "ID" : id,
        "TID": None,
        "r": None,
        "Path": [id],
        "Result": None
    }
    return message

def HSS_auth_response_message(tid,r,v,t,hk,path):
    msg = {
        "Type": "HSS_auth_response",
        "Count": 4,
        "ETID": tid,
        "ER": r,
        "Vi": v,
        "T_new": t,
        "HK": hk,
        "Path": path,
        "Result": "success"
    }
    return msg

def broadcast_key(id,hk):
    msg = {
        "Type": "Key_Broadcast",
        "id": id,
        "hk": hk,
        "PID": None
    }
    return msg

def HSS_auth_request_message(id,tid,r,v,t):
    msg = {
        "Type": "HSS_auth_request",
        "Count": 1,
        "TID": tid,
        "R0": json.dumps(r),
        "V0": v,
        "Tu": t,
        "Path": [id],
        "Result": None
    }
    return msg

def eNB_auth_message(r,v,h):
    msg = {
        "Type": "eNB_auth_request",
        "R2": r,
        "V2": v,
        "H_req": h
    }
    return msg

def eNB_auth_response_message(r,h):
    msg = {
        "Type": "eNB_auth_response",
        "R3": r,
        "H_res": h
    }
    return msg
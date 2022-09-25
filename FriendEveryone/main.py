## This does not work anymore due to the relationship api being ratelimited!
import json
import threading
import requests

def Request(ReqData, Data = None, Headers = None, Cookies = None):
    Method = ReqData.get("Method")
    Url = ReqData.get("Url")
    DecodeJSON = ReqData.get("DecodeJSON")
    OnlyBody = ReqData.get("OnlyBody")

    if Method:
        Method = Method.lower()
    else:
        Method = "get"

    Response = getattr(requests, Method)(Url, data=Data, headers=Headers, cookies=Cookies)
    Response.close()
    
    Success, StatusCode, Headers, Cookies, Body = Response.ok, Response.status_code, Response.headers, Response.cookies, Response.text

    if DecodeJSON:
        Body = Response.json()
    
    if OnlyBody:
        return Body

    return {
        'Success': Success, 
        'StatusCode': StatusCode, 
        'Headers': Headers, 
        'Cookies': Cookies, 
        'Body': Body
    }

API = "https://api.cubash.com"
API_Endpoints = {
    'AUTHENTHICATION_FETCH_USER': API + "/authentication/login/fetch-user?value={}",
    'AUTHORIZATION_SESSION': API + "/authorization/session",
    'AUTHENTHICATION_LOGIN': API + "/authentication/login",
    'RELATIONSHIPS_FETCH': API + "/relationships/fetch/list?username={}&page={}",
    'DASHBOARD_MESSAGES': API + "/dashboard/messages",
    'LOGIN_FETCH_USER': API + "/authentication/login/fetch-user?value={}",
    'SETTINGS_ABOUTME': API + "/settings/account/profile/about-me",
    'CHARACTER_COLOR': API + "/character/color",
    'RELATIONSHIPS': API + "/relationships",
    'REQUEST_GAME': API + "/games/request-game",
    'GAMES_LEVELS': API + "/games/levels/all?page{}&view=regular",
    'FORUM_POSTS': API + "/forum/posts?id={}&page={}",
    'STORE_ITEMS': API + "/store/items?type={}&page={}",
    'STORE_ITEM': API + "/store/item?id={}",
    'PROFILE': API + "/profile?username={}",
} 

UserDump = json.loads(Request({ "Url": "https://raw.githubusercontent.com/NougatBitz/Cubash/main/UserDump/allUsers.json", "OnlyBody": True }))

def LoginAccount(Username: str, Password: str):
    SessionData = Request({
        "Url": API_Endpoints["AUTHORIZATION_SESSION"], 
        "DecodeJSON": True 
    })

    if not (SessionData.get("StatusCode") == 200):
        return "Session authorization failed.", False

    Body, Cookies = SessionData.get("Body"), SessionData.get("Cookies")

    XCSRF, _CSRF, CGuard = Body.get("csrf"), Cookies.get("_csrf"), ""

    LoginRequest = Request({
        "Method": "POST",
        "Url": API_Endpoints["AUTHENTHICATION_LOGIN"]
    }, {
        "username": Username,
        "password": Password
    }, { 
        "X-CSRF-TOKEN": XCSRF 
    }, { 
        "_csrf": _CSRF 
    })

    if not (LoginRequest.get("StatusCode") == 201):
        return f"Login request failed. | { LoginRequest.get('StatusCode') }", False
    else:
        CGuard = requests.utils.unquote(LoginRequest.get("Cookies").get("cubash_guard"))

    return {
        "Cookies": {
            "cubash_guard": CGuard,
            "_csrf": _CSRF
        },
        "Headers": {
            "X-CSRF-TOKEN": XCSRF
        }
    }, True

#### YOU HAVE TO CHANGE THE USERNAME & PASSWORD
Authentication, Success = LoginAccount("Username", "Password")
if not Success:
    print("Login was unsuccessful.")
    exit()
else:
    print("Login was successful!")

def FriendUser(Username: str):
    Request({
        "Method": "PUT",
        "Url": str.format(API_Endpoints["RELATIONSHIPS"])
    }, {
        "username": Username
    }, Authentication["Headers"], Authentication["Cookies"])

print("Attempting to friend everyone.")

for Index, Data in enumerate(UserDump.items()):
    UID, Username = Data[0], Data[1]
    
    threading.Thread( target = FriendUser, args = { Username } ).start()

print("Done.")

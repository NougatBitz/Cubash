import json
import threading
import time
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

UsersAPI = "https://api.cubash.com/users?page={}&mode=all"
ProfileAPI = "https://api.cubash.com/profile?username={}"

# This function is most likely really slow and ineffecient cuz im bad at python wow!!
def FetchAllUsers():
    global Finished, UserList, Users
    UserList, Users, Finished = [], {}, 0

    ## Fetch UserList
    def FetchUsers(PageNumber):
        global Finished
        PageResult = Request({
            "Url": str.format(UsersAPI, PageNumber), 
            "DecodeJSON": True, 
            "OnlyBody": True
        })

        for _, Player in enumerate( PageResult.get("result") ): UserList.append( Player.get("username") )

        Finished += 1

        return PageResult.get("pages"), PageResult.get("total")
    
    PageCount, TotalUsers = FetchUsers(1)
    
    for CurrentPage in range(2, PageCount + 1):
        threading.Thread( target = FetchUsers, args = { CurrentPage } ).start()

    while Finished < PageCount: time.sleep(0)

    Finished = 0

    ## Fetch UserIDs
    def FetchUser(Username):
        global Finished
        Profile = Request({
            "Url": str.format(ProfileAPI, Username), 
            "DecodeJSON": True, 
            "OnlyBody": True
        })
        Users[ Profile.get("user").get("id") ] = Username

        Finished += 1
            
    UserCount = len(UserList)

    for Username in UserList:
        threading.Thread( target = FetchUser, args = { Username } ).start()
    
    while Finished < UserCount: 
        time.sleep(0)

    SortedUsers = {}
    
    for Index in Users:
        print(int(Index))
        SortedUsers[ int(Index) ] = Users.get(Index)
    
    for CurrentId in range(0, TotalUsers):
        if not SortedUsers.get(CurrentId):
            SortedUsers[CurrentId] = "BANNED_OR_UNKNOWN"

    SortedUsers = dict(sorted(SortedUsers.items()))
    return SortedUsers

# Dump all users into a "allUsers.json" file
json.dump(FetchAllUsers(), open("allUsers.json", "w"))
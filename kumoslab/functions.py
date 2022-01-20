import discord
from Systems.Economy import economy

async def getmoney(guildid=None, userid=None):
    if userid is None:
        print("Error: User ID is none when trying to use *getmoney*")
        return
    try:
        stats = economy.find_one({"guildid": int(guildid), "id": int(userid)})
        money = stats["money"]
        return money
    except:
        print("Error: User ID is not in the database when trying to use *getmoney*")
        return


async def addmoney(guildid=None, userid=None, amount: int=None):
    if userid is None:
        print("Error: User ID is none when trying to use *addmoney*")
        return
    if amount <= 0:
        print("Error: Amount is less than or equal to 0 when trying to use *addmoney*")
        return
    if amount is None:
        print("Error: Amount is none when trying to use *addmoney*")
        return
    try:
        stats = economy.find_one({"guildid": guildid, "id": userid})
        money = stats["money"]
        updated_money = economy.update_one(
            {"guildid": guildid, "id": userid},
            {"$inc": {"money": amount}},)
        return updated_money
    except:
        print("Error: User ID is not in the database when trying to use *addmoney*")
        return

async def pay(guildid=None, senderid=None, recieverid=None, amount: int = None):
    if guildid is None:
        print("Error: Guild ID is none when trying to use *pay*")
        return
    if senderid is None:
        print("Error: Sender ID is none when trying to use *pay*")
        return
    if recieverid is None:
        print("Error: Reciever ID is none when trying to use *pay*")
        return
    if amount <= 0:
        print("Error: Amount is less than or equal to 0 when trying to use *pay*")
        return
    if amount is None:
        print("Error: Amount is none when trying to use *pay*")
        return
    try:
        sender_stats = economy.find_one({"guildid": guildid, "id": senderid})
        sender_money = sender_stats["money"]
        if sender_money < amount:
            return str("Insufficient Funds!")
        else:
            economy.update_one(
                {"guildid": guildid, "id": senderid},
                {"$inc": {"money": -amount}},)
            reciever_stats = economy.find_one({"guildid": guildid, "id": recieverid})
            reciever_money = reciever_stats["money"]
            economy.update_one(
                {"guildid": guildid, "id": recieverid},
                {"$inc": {"money": + amount}},)
            return
    except:
        print("Error: User ID is not in the database when trying to use *pay*")
        return

async def setmoney(guildid=None, userid=None, amount: int = None):
    if userid is None:
        print("Error: User ID is none when trying to use *setmoney*")
        return
    if amount <= 0:
        print("Error: Amount is less than or equal to 0 when trying to use *setmoney*")
        return
    if amount is None:
        print("Error: Amount is none when trying to use *setmoney*")
        return
    try:
        stats = economy.find_one({"guildid": guildid, "id": userid})
        economy.update_one(
            {"guildid": guildid, "id": userid},
            {"$set": {"money": amount}},)
        return
    except:
        print("Error: User ID is not in the database when trying to use *setmoney*")
        return

async def removeMoney(guildid=None, userid=None, amount: int = None):
    if userid is None:
        print("Error: User ID is none when trying to use *removeMoney*")
        return
    if amount <= 0:
        print("Error: Amount is less than or equal to 0 when trying to use *removeMoney*")
        return
    if amount is None:
        print("Error: Amount is none when trying to use *removeMoney*")
        return
    try:
        stats = economy.find_one({"guildid": guildid, "id": userid})
        money = stats["money"]
        if money < amount:
            return str("Insufficient Funds!")
        else:
            economy.update_one(
                {"guildid": guildid, "id": userid},
                {"$inc": {"money": -amount}},)
            return
    except:
        print("Error: User ID is not in the database when trying to use *removeMoney*")
        return









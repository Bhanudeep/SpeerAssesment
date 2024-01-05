
import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
def dbforusr(usrnm,note):
    mydb = myclient[usrnm]
    mynote = mydb["notes"]
    content={"Note":note}
    mynote.insert_one(content)

def dbforshr(usrnm,note):
    mydb = myclient[usrnm]
    mynote = mydb["shrdnotes"]
    content={"Note":note}
    mynote.insert_one(content)


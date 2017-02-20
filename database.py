import traceback
import threading
import MySQLdb
import datetime

class dataBase:
    def __init__(self, host, uname, pw, dbname, rdr):
        self.conn = MySQLdb.connect(host, uname, pw, dbname, charset='utf8')
        self.rdr = rdr
        self.lock = threading.Lock()

    def close(self):
        self.conn.close()

    def ping(self):
        self.conn.ping()

    def registerUser(self, uid, cid, uname):
        sql = "INSERT INTO `users` (uid, cid, uname) VALUES (%s,%s,%s)"
        self.lock.acquire()
        cur = self.conn.cursor()
        res = 0
        try:
            cur.execute(sql, (uid, cid, uname,))
        except MySQLdb.IntegrityError:
            res = 1
        except Exception as e:
            print(e, datetime.datetime.now())
            traceback.print_exc()
            res = 2
            self.conn.commit()
        cur.close()
        self.lock.release()
        return res

    def addTopic(self, cid, topic):
        if not self.rdr.validTopic(topic):
            topic = self.rdr.closest(topic)
            if topic==None:
                return 2
        sql = "INSERT INTO `topics` (cid, topic) VALUES (%s, %s)"
        self.lock.acquire()
        cur = self.conn.cursor()
        res = 0
        try:
            cur.execute(sql, (cid, topic,))
        except MySQLdb.IntegrityError:
            res = 1
        except Exception as e:
            print(e, datetime.datetime.now())
            traceback.print_exc()
            res = 3
            self.conn.commit()
        cur.close()
        self.lock.release()
        return res

    def deleteTopic(self, cid, topic):
        if not self.rdr.validTopic(topic):
            return 2
        sql = "DELETE FROM `topics` WHERE cid=%s AND topic=%s"
        self.lock.acquire()
        cur = self.conn.cursor()
        res = 0
        try:
            cnt=cur.execute(sql, (cid, topic,))
            if cnt==0:
                res = 1
        except Exception as e:
            print(e, datetime.datetime.now())
            traceback.print_exc()
            res = 3
            self.conn.commit()
        cur.close()
        self.lock.release()
        return res

    def getTopicsByCid(self, cid):
        sql = "SELECT topic FROM `topics` WHERE cid=%s"
        self.lock.acquire()
        cur = self.conn.cursor()
        res = []
        try:
            cur.execute(sql, (cid,))
            for row in cur:
                res.append(row[0])
        except Exception as e:
            print(e, datetime.datetime.now())
            traceback.print_exc()
            res = None
            self.conn.commit()
        cur.close()
        self.lock.release()
        return res

    def getTopics(self):
        sql = "SELECT topic FROM `topics` GROUP BY topic"
        sql2 = "SELECT cid FROM `topics` WHERE topic=%s"
        self.lock.acquire()
        cur = self.conn.cursor()
        cur2 = self.conn.cursor()
        res = []
        try:
            cur.execute(sql)
            for row in cur:
                cur2.execute(sql2, (row[0],))
                cids = []
                for cid in cur2:
                    cids.append(cid[0])
                res.append([row[0],cids])
        except Exception as e:
            print(e, datetime.datetime.now())
            traceback.print_exc()
            res = None
            self.conn.commit()
        cur.close()
        self.lock.release()
        return res


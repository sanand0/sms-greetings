import web

db = web.database(dbn='mysql', db='sanand_greeting', user='sanand_gr', pw='sanand')
store = web.session.DBStore(db, 'sessions')

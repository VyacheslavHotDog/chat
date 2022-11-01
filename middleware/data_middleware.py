from middleware.base import BaseMiddleware


class DataMiddleware(BaseMiddleware):

    def preProcess(self, clas):
        clas.message_json['middlewwareField'] = 'test data'
        print(clas.message_json)
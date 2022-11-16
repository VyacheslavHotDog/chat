from middleware.base import BaseMiddleware


class DataMiddleware(BaseMiddleware):

    def preProcess(self, clas):
        pass
        # clas.message_json['middlewwareField'] = 'test data'
        # print(clas.message_json)
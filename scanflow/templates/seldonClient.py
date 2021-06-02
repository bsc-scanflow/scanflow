#from seldon_core.seldon_client import SeldonClient

class SeldonClient:
    def __init__(self,
                 gateway,
                 transport,
                 namespace,
                 deployment_name,
                 payload_type,
                 gateway_endpoint,
                 microservice_endpoint,
                 grpc_max_send_message_length,
                 grpc_max_receive_message_length,
                 channel_credentials,
                 call_credentials,
                 debug,
                 client_return_type,
                 ssl):
        pass
        #self.sc = SeldonClient(gateway,transport,namespace,deployment_name,payload_type,gateway_endpoint,microservice_endpoint,grpc_max_send_message_length, grpc_max_receive_message_length, channel_credentials, call_credentials, debug, client_return_type, ssl)
    
    def predict(self, data):
        pass
        #r = self.sc.predict(data=data)
        #log.info("response: {}".format(r))
        #return r



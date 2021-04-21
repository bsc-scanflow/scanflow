import logging

class Node(object):
    """
        Abstract base Node class.

    """
    def __init__(self, name: str):
        self.name = name

class Improver(Node):

    def __init__(self,
                 name:str = None,
                 mode='online',
                 port:int = 8006):

        super(Improver, self).__init__(name=name)
        self.mode = mode
        self.port = self.choose_port(port)
        self._to_dict = locals()

    def check_port_in_use(self, port: int):
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0

    def choose_port(self, port: int):
        chosen_port = port
        if self.check_port_in_use(chosen_port):
            logging.info(f"[Improver] Port {chosen_port} is in use by Improver.")
        else:
            logging.info(f"[Improver] Port {chosen_port} is set successfully.")

        return chosen_port

    @property
    def to_dict(self):
        tmp_dict = self._to_dict
        tmp_dict.pop('self', None)
        tmp_dict.pop('__class__', None)
        tmp_dict = {k: v for k, v in tmp_dict.items() if v is not None}
        return tmp_dict

import logging
# from scanflow.setup import Node

class Node(object):
    """
        Abstract base Node class.

    """
    def __init__(self, name: str):
        self.name = name

class Tracker(Node):

    def __init__(self,
                 name:str = None,
                 mode='offline',
                 port:int = 8002):

        super(Tracker, self).__init__(name=name)
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
            logging.info(f"[Tracker] Port {chosen_port} is in use by Tracker.")
        else:
            logging.info(f"[Tracker] Port {chosen_port} is set successfully.")

        return chosen_port

    # def choose_port(self, port: int):
    #     n_trials = 3
    #     for i in range(n_trials+1):
    #         chosen_port = port+i
    #         if self.check_port_in_use(chosen_port):
    #             logging.info(f"[Tracker] Port {chosen_port} is in use. Trying next port.")
    #             continue
    #         else:
    #             logging.info(f"[Tracker] Port {chosen_port} is set successfully.")
    #             return chosen_port
    #
    #     raise ValueError(f'[+] {n_trials} additional ports are in use. Please select another one.')

    @property
    def to_dict(self):
        tmp_dict = self._to_dict
        tmp_dict.pop('self', None)
        tmp_dict.pop('__class__', None)
        tmp_dict = {k: v for k, v in tmp_dict.items() if v is not None}
        return tmp_dict



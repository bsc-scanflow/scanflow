import logging
import subprocess
import os
import docker
import requests
import datetime

from shutil import copy2
from textwrap import dedent
from multiprocessing import Pool

import scanflow.deployer.deployer as deployer
from scanflow.templates import Kubernetes

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)



class SeldonDeployer(deployer.Deployer):
    def __init__(self,
                 k8s_config_file=True):
        super(SeldonDeployer, self).__init__(k8s_config_file)

        #self.seldonclient = SeldonServices(k8s_config_file=k8s_config_file)

        logging.info("seldon backend is not ready!")
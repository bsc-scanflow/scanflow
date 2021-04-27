import logging
import os
import docker
import json
from textwrap import dedent

import scanflow.builder.builder as builder

from scanflow.app import Application, Executor, Workflow
from scanflow.agent import Agent

from typing import List, Dict

from scanflow.tools.scanflowtools import get_scanflow_paths

logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


class DockerBuilder(builder.Builder):
    def __init__(self,
                 registry: str):
        super(DockerBuilder, self).__init__(registry)
        self.client = docker.from_env()

    def build_ScanflowApplication(self, app: Application):
        self.paths = get_scanflow_paths(app.app_dir)
        if app.agents is not None:
            self.build_ScanflowAgents(app.agents)
        if app.workflows is not None:
            self.build_ScanflowWorkflows(app.workflows)
        return app

    def build_ScanflowAgents(self, agents: List[Agent]):
        for agent in agents:
            self.build_ScanflowAgent(agent)

    def build_ScanflowAgent(self, agent: Agent):
        agent.image = self.__build_image_to_registry(agent)

    def build_ScanflowWorkflows(self, workflows: List[Workflow]):
        for workflow in workflows:
            self.build_ScanflowWorkflow(workflow)

    def build_ScanflowWorkflow(self, workflow: Workflow):
        self.build_ScanflowExecutors(workflow.executors)

    def build_ScanflowExecutors(self, executors: List[Executor]):
        for executor in executors:
            self.build_ScanflowExecutor(executor)

    def build_ScanflowExecutor(self, executor: Executor):
        executor.image = self.__build_image_to_registry(executor)

    def __build_image_to_registry(self, source):

        image_name = f"{self.registry}/{source.name}"
        logging.info(f"Building image {image_name}")
        try:
            image = self.client.images.get(image_name)
            return image.tags[0]
    
        except docker.api.client.DockerException as e:
            logging.info(f"[+] Image [{image_name}] not found in repository. Building a new one.")

            build_path = ""
            if source.dockerfile is None:
                dockerfile, build_path = self.__generate_dockerfile(source)
            else:
                if isinstance(source, Executor):
                    build_path = f"{self.paths['workflows_dir']}"
                    dockerfile = f"{self.paths['workflows_dir']}/{source.name}/{source.dockerfile}"
                elif isinstance(source, Agent):
                    build_path = f"{self.paths['agents_dir']}"
                    dockerfile = f"{self.paths['agents_dir']}/{source.name}/{source.dockerfile}"
                else:
                    logging.info(f"unknown source to build the image {source}")

            logging.info(f"dockerfile for using {dockerfile} from {build_path}")
            
            try:    
                image, stat = self.client.images.build(path=build_path,
                                      dockerfile=dockerfile,
                                    tag=image_name)
                logging.info(f'[+] Image [{source.name}] was built successfully. image_tag {image.tags}')
                self.client.images.push(image_name)
                logging.info(f'[+] Image [{source.name}] was pushed to registry successfully.')

                return image.tags[0]
            except docker.api.client.DockerException as e:
                logging.error(f"{e}")
                logging.error(f"[-] Image building failed.", exc_info=True)

            

    def __generate_dockerfile(self, source):
        dockerfile_content = None
        dockerfile = ""
        build_path = ""
        if isinstance(source, Executor):
            dockerfile_content = self.__dockerfile_template_executor(source)
            filename = "Dockerfile_scanflow_executor"
            dockerfile = f"{self.paths['workflows_dir']}/{source.name}/{filename}"
            build_path = f"{self.paths['workflows_dir']}"
        elif isinstance(source, Agent):
            dockerfile_content = self.__dockerfile_template_agent(source)
            filename = "Dockerfile_scanflow_agent"
            dockerfile = f"{self.paths['agents_dir']}/{source.name}/{filename}"
            build_path = f"{self.paths['agents_dir']}"
        else:
            logging.error(f"unknown source {source}")
            
        with open(dockerfile, 'w') as f:
            f.writelines(dockerfile_content)

        logging.info(f'[+] Dockerfile: [{filename}] was created successfully.')

        return dockerfile, build_path
    

    def __dockerfile_template_executor(self, executor):
        template = dedent(f'''
                    FROM 172.30.0.49:5000/scanflow-executor
    
                    COPY {executor.name} /app/{executor.name}
        ''')
        if executor.requirements is not None:
            req_template = dedent(f'''
                    RUN pip install -r /app/{executor.name}/{executor.requirements}
            ''')
            template  += req_template
        if executor.mainfile is not None:
            exec_template = dedent(f''' 
                    CMD ["python", "/app/{executor.name}/{executor.mainfile}"]
            ''')
            template += exec_template
        logging.info(f"{executor.name} 's Dockerfile {template}")
        return template
 
    def __dockerfile_template_agent(self, agent):
        template = dedent(f'''
                    FROM 172.30.0.49:5000/scanflow-agent
    
                    COPY {agent.name} /agent/{agent.name}
    
                    CMD uvicorn /agent/{agent.name}/{agent.mainfile}:agent --reload --host 0.0.0.0 --port 8080
        ''')
        logging.info(f"{agent.name} 's Dockerfile {template}")
        return template
    
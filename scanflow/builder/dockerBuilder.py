import logging
import os
import docker
import json
from textwrap import dedent

import scanflow.builder.builder as builder

from scanflow.app import Application, Executor, Service, Node, Workflow, Tracker, Agent, Sensor, IntervalTrigger, DateTrigger, CronTrigger, BaseTrigger
from datetime import datetime

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

    def build_ScanflowApplication(self, app: Application, trackerPort: int):
        self.paths = get_scanflow_paths(app.app_dir)
        if app.agents is not None:
            self.build_ScanflowAgents(app.agents)
        if app.workflows is not None:
            self.build_ScanflowWorkflows(app.workflows)
        if app.tracker is None:
            app.tracker = self.build_ScanflowTracker(nodePort=trackerPort)
        return app
    
    def build_ScanflowTracker(self, nodePort: int):
        return Tracker(nodePort)

    def build_ScanflowAgents(self, agents: List[Agent]):
        for agent in agents:
            self.build_ScanflowAgent(agent)

    def build_ScanflowAgent(self, agent: Agent):
        agent.image = self.__build_image_to_registry(agent)

    def build_ScanflowWorkflows(self, workflows: List[Workflow]):
        for workflow in workflows:
            self.build_ScanflowWorkflow(workflow)

    def build_ScanflowWorkflow(self, workflow: Workflow):
        self.build_ScanflowNodes(workflow.nodes)

    def build_ScanflowNodes(self, nodes: List[Node]):
        for node in nodes:
            self.build_ScanflowNode(node)

    def build_ScanflowNode(self, node: Node):
        node.image = self.__build_image_to_registry(node)


    def __build_image_to_registry(self, source):

        image_name = f"{self.registry}/{source.name}"
        if isinstance(source, Agent):
            image_name = f"{self.registry}/{source.name}-agent"
        logging.info(f"Building image {image_name}")

        try:
            image = self.client.images.get(image_name)
            logging.info(f"[+] Image [{image_name}] has been found in repository. {image.tags[0]}.")
            return image.tags[0]
    
        except docker.api.client.DockerException as e:
            logging.info(f"[+] Image [{image_name}] not found in repository. Building a new one.")

            build_path = ""
            if source.dockerfile is None:
                dockerfile, build_path = self.__generate_dockerfile(source)
            else:
                if isinstance(source, Node):
                    build_path = f"{self.paths['workflows_dir']}"
                    dockerfile = f"{self.paths['workflows_dir']}/{source.name}/{source.dockerfile}"
                elif isinstance(source, Agent):
                    build_path = f"{self.paths['agents_dir']}"
                    dockerfile = f"{self.paths['agents_dir']}/{source.name}/{source.dockerfile}"
                else:
                    logging.info(f"unknown source to build the image {source}")

            logging.info(f"dockerfile for using {dockerfile} from {build_path}")
            
            try:
                if dockerfile is not None:    
                    image, stat = self.client.images.build(path=build_path,
                                          dockerfile=dockerfile,
                                        tag=image_name)
                    logging.info(f'[+] Image [{source.name}] was built successfully. image_tag {image.tags}')

                    try:
                        # self.client.images.push(image_name)
                        self.client.images.push(repository=f"{self.registry}/{image_name}", 
                                                tag=image.tags, 
                                                auth_config={'username': 'cloudskin-ncloud2', 'password': 'Y2xvdWRza2luLW5jbG91ZDI6cE54emZQNm5TWWJMeEJWM1lHaGk='})
                        logging.info(f'[+] Image [{source.name}] was pushed to registry successfully.')
                    except docker.api.client.DockerException as e:
                        logging.info(f'[+] Image [{source.name}] push failed.')

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
        elif isinstance(source, Service):
            dockerfile_content = self.__dockerfile_template_service(source)
            filename = "Dockerfile_scanflow_service"
            dockerfile = f"{self.paths['workflows_dir']}/{source.name}/{filename}"
            build_path = f"{self.paths['workflows_dir']}"
        elif isinstance(source, Agent):
            dockerfile_content = self.__dockerfile_template_agent(source)
            filename = "Dockerfile_scanflow_agent"
            dockerfile = f"{self.paths['agents_dir']}/{source.name}/{filename}"
            build_path = f"{self.paths['agents_dir']}"
        else:
            logging.error(f"unknown source {source}")
            
        if dockerfile_content is not None:
            with open(dockerfile, 'w') as f:
                f.writelines(dockerfile_content)
    
            logging.info(f'[+] Dockerfile: [{filename}] was created successfully.')
    
            return dockerfile, build_path
        else:
            logging.info(f'[+] Dockerfile: [{filename}] was not created.')
             
            return None, build_path
    

    def __dockerfile_template_executor(self, executor):
        template = dedent(f'''
        ''')

        #baseimage
        if executor.base_image is not None:
            image_name = f"{self.registry}/{executor.base_image}"
            try:
                image = self.client.images.get(image_name)    
            except docker.api.client.DockerException as e:
                raise EnvironmentError(f"[+] Base Image [{image_name}] not found in repository.")
            base_image_template = dedent(f'''
                    FROM {image.tags[0]}
            ''')
            template += base_image_template
        else:
            base_image_template = dedent(f'''
                    FROM {self.registry}/scanflow-executor
            ''')
            template += base_image_template

        #code
        code_template = dedent(f'''
                    COPY {executor.name} /app/{executor.name}
        ''')
        template += code_template

        #requirements
        if executor.requirements is not None:
            req_template = dedent(f'''
                    RUN pip install -r /app/{executor.name}/{executor.requirements}
            ''')
            template  += req_template
        
        #mainfile
        if executor.mainfile is not None:
            if executor.mainfile.endswith('.py'):
                if os.path.isabs(executor.mainfile):
                    exec_template = dedent(f''' 
                        ENTRYPOINT ["python", "{executor.mainfile}"]
                    ''')
                else:
                    exec_template = dedent(f''' 
                        ENTRYPOINT ["python", "/app/{executor.name}/{executor.mainfile}"]
                    ''')
            elif executor.mainfile.endswith('.sh'):
	            exec_template = dedent(f''' 
                    ENTRYPOINT ["/bin/bash", "-c", "/app/{executor.name}/{executor.mainfile}"]
                ''')
            template += exec_template

        logging.info(f"{executor.name} 's Dockerfile {template}")
        return template

    def __dockerfile_template_service(self, service):
        template = dedent(f'''
        ''')
        if service.service_type is not None:
            #baseimage
            if service.base_image is not None:
                image_name = f"{self.registry}/{service.base_image}"
                try:
                    image = self.client.images.get(image_name)    
                except docker.api.client.DockerException as e:
                    raise EnvironmentError(f"[+] Base Image [{image_name}] not found in repository.")
                base_image_template = dedent(f'''
                        FROM {image.tags[0]}
                ''')
                template += base_image_template
            else:
                base_image_template = dedent(f'''
                        FROM python:3.7-slim 
                ''')
                template += base_image_template

            #code
            code_template = dedent(f'''
                        COPY {service.name} /app
                        WORKDIR /app
                        EXPOSE 5000
            ''')
            template += code_template

            #requirements
            if service.requirements is not None:
                req_template = dedent(f'''
                        RUN pip install -r /app/{service.requirements}
                ''')
                template  += req_template

            #mainfile
            if service.mainfile is not None:
                (filename, extension) = os.path.splitext(service.mainfile)
                if extension == '.py':
                    exec_template = dedent(f'''
                        ENV MODEL_NAME {filename}
                        ENV SERVICE_TYPE {service.service_type}

                        CMD exec seldon-core-microservice $MODEL_NAME --service-type $SERVICE_TYPE
                    ''')
                template += exec_template
        
            logging.info(f"{service.name} 's Dockerfile {template}")
            return template
        else:
            return None
 
    def __dockerfile_template_agent(self, agent):
        template = dedent(f'''
                    FROM {self.registry}/scanflow-agent

                    ENV AGENT_NAME {agent.name}
                    ENV AGENT_TYPE {agent.template}

                    RUN mkdir /agent
                    COPY {agent.name} /agent
        ''')
        #sensors injection
        if agent.sensors is not None:
            #copy custom file
            #sensors_template = dedent(f'''
            #        
            #''')
            #template += sensors_template
            #injection
            sensors = {}
            for sensor in agent.sensors:
                #sensor_trigger_dict
                sensor_conf = {}
                sensor_conf.update(name=sensor.name)
                if sensor.isCustom:
                    sensor_conf.update(func=f"scanflow.agent.template.{agent.template}.custom_sensors.{sensor.name}")
                else:
                    sensor_conf.update(func=f"scanflow.agent.template.{agent.template}.sensors.{sensor.name}")
                if isinstance(sensor.trigger, IntervalTrigger):
                    trigger = {"type": "interval"}
                    trigger.update(sensor.trigger.__dict__)
                    sensor_conf.update(trigger=trigger)
                elif isinstance(sensor.trigger, DateTrigger):
                    trigger = {"type": "date"}
                    trigger.update(sensor.trigger.__dict__)
                    sensor_conf.update(trigger=trigger)
                elif isinstance(sensor.trigger, CronTrigger):
                    trigger = {"type": "cron"}
                    trigger.update(sensor.trigger.__dict__)
                    sensor_conf.update(trigger=trigger)
                if sensor.args is not None:
                    sensor_conf.update(args=sensor.args)
                if sensor.kwargs is not None:
                    sensor_conf.update(kwargs=sensor.kwargs)
                if sensor.next_run_time is not None:
                    sensor_conf.update(next_run_time=sensor.next_run_time.isoformat())
                #sensor
                sensor_dict = {f"{sensor.name}":sensor_conf}
                sensors.update(sensor_dict)
            #sensors
            sensors = json.dumps(sensors)
            logging.info(f"sensor configuration registered:{sensors}")
            sensors_env_template = dedent(f'''
                   ENV sensors '{sensors}' 
            ''')
            template += sensors_env_template

        #start
        template += dedent(f'''
             CMD [ "cp /agent/* /scanflow/scanflow/scanflow/agent/template/{agent.template} && uvicorn main:agent --reload --host 0.0.0.0 --port 8080" ]
        ''')

        logging.info(f"{agent.name} 's Dockerfile {template}")
        return template
        
    
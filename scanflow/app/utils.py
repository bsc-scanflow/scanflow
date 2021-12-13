from . import Application, Workflow, Executor, Service, Dependency, Agent, Tracker

def dict_to_app(dictionary):
    app = Application(dictionary['app_name'], dictionary['app_dir'], dictionary['team_name'])
    if dictionary['workflows']:
        workflows = []
        for workflow_dict in dictionary['workflows']:
            workflows.append(dict_to_workflow(workflow_dict))
        app.workflows = workflows
    if dictionary['agents']:
        agents = []
        for agent_dict in dictionary['agents']:
            agents.append(dict_to_agent(agent_dict))
        app.agents = agents
    if dictionary['tracker']:
        app.tracker = Tracker(dictionary['tracker']['nodePort'], dictionary['tracker']['image'])
    return app

def dict_to_workflow(dictionary):
    name = dictionary['name']
    nodes = []
    for node_dict in dictionary['nodes']:
        if node_dict['node_type'] == 'executor':
            nodes.append(dict_to_executor(node_dict))
        elif node_dict['node_type'] == 'service':
            nodes.append(dict_to_service(node_dict))
    workflow = Workflow(name, nodes)
    if dictionary['edges']:
        edges = []
        for edge_dict in dictionary['edges']:
            if edge_dict['edge_type'] == 'dependency':
                edges.append(Dependency(edge_dict['dependee'], edge_dict['depender'], int(edge_dict['priority'])))
        workflow.edges = edges
    if dictionary['type']:
        type = dictionary['type']
        workflow.type = type
    if dictionary['resources']:
        resources = dict_to_resources(dictionary['resources'])
        workflow.resources = resources
    if dictionary['affinity']:
        affinity = dict_to_affinity(dictionary['affinity'])
        workflow.affinity = affinity
    if dictionary['kedaSpec']:
        kedaSpec = dict_to_kedaSpec(dictionary['kedaSpec'])
        workflow.kedaSpec = kedaSpec
    if dictionary['hpaSpec']:
        hpaSpec = dict_to_hpaSpec(dictionary['hpaSpec'])
        workflow.hpaSpec = hpaSpec
    if dictionary['output_dir']:
        output_dir = dictionary['output_dir']
        workflow.output_dir = output_dir
    
    return workflow

def dict_to_affinity(dictionary):
    return dictionary

def dict_to_kedaSpec(dictionary):
    return dictionary

def dict_to_hpaSpec(dictionary):
    return dictionary

def dict_to_executor(dictionary):
    name = dictionary['name']
    mainfile = dictionary['mainfile']
    executor = Executor(name, mainfile)
    if dictionary['parameters']:
        executor.parameters = dictionary['parameters']
    if dictionary['requirements']:
        executor.requirements = dictionary['requirements']
    if dictionary['dockerfile']:
        executor.dockerfile = dictionary['dockerfile']
    if dictionary['base_image']:
        executor.base_image = dictionary['base_image']
    if dictionary['env']:
        executor.env = dictionary['env']
    if dictionary['image']:
        executor.image = dictionary['image']
    if dictionary['timeout']:
        executor.timeout = dictionary['timeout']
    if dictionary['resources']:
        executor.resources = dict_to_resources(dictionary['resources'])
    if dictionary['affinity']:
        executor.affinity = dict_to_affinity(dictionary['affinity'])
    return executor

def dict_to_resources(dictionary):
    return dictionary

def dict_to_service(dictionary):
    name = dictionary['name']
    service = Service(name)
    if dictionary['mainfile']:
        service.mainfile = dictionary['mainfile']
    if dictionary['image']:
        service.image = dictionary['image']
    if dictionary['env']:
        service.env = dictionary['env']
    if dictionary['envfrom']:
        service.env = dictionary['envfrom']
    if dictionary['requirements']:
        service.requirements = dictionary['requirements']
    if dictionary['dockerfile']:
        service.dockerfile = dictionary['dockerfile']
    if dictionary['base_image']:
        service.base_image = dictionary['base_image']
    if dictionary['service_type']:
        service.service_type = dictionary['service_type']
    if dictionary['implementation_type']:
        service.implementation_type = dictionary['implementation_type']
    if dictionary['modelUri']:
        service.modelUri = dictionary['modelUri']
    if dictionary['envSecretRefName']:
        service.envSecretRefName = dictionary['envSecretRefName']
    if dictionary['endpoint']:
        service.endpoint = dictionary['endpoint']
    if dictionary['parameters']:
        service.parameters = dictionary['parameters']
    if dictionary['resources']:
        service.resources = dict_to_resources(dictionary['resources'])
    if dictionary['affinity']:
        service.affinity = dict_to_affinity(dictionary['affinity'])
    
    
def dict_to_agent(dictionary):
    agent = Agent(name)
    return agent
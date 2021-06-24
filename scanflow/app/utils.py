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
    if dictionary['affinity']:
        affinity = dict_to_affinity(dictionary['affinity'])
        workflow.affinity = affinity
    if dictionary['kedaSpec']:
        kedaSpec = dict_to_kedaSpec(dictionary['kedaSpec'])
        workflow.kedaSpec = kedaSpec
    if dictionary['output_dir']:
        output_dir = dictionary['output_dir']
        workflow.output_dir = output_dir
    
    return workflow

def dict_to_affinity(dictionary):
    pass

def dict_to_kedaSpec(dictionary):
    pass

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
    if dictionary['resources']:
        executor.resources = dict_to_resources(dictionary['resources'])
    return executor

def dict_to_resources(dictionary):
    pass

def dict_to_service(dictionary):
    pass

def dict_to_agent(dictionary):
    agent = Agent(name)
    return agent
from . import Application, Workflow, Executor, Dependency, Agent, Tracker

def dict_to_app(dictionary):
    app = Application(dictdictionary['app_name'], dictionary['app_dir'], dictionary['team_name'])
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
    executors = []
    for executor_dict in dictionary['executors']:
        executors.append(dict_to_executor(executor_dict))
    dependencies = []
    for dependency_dict in dictionary['dependencies']:
        dependencies.append(Dependency(dependency_dict['dependee'], dependency_dict['depender'], int(dependency_dict['priority'])))
    output_dir = dictionary['output_dir']
    workflow = Workflow(name, executors, dependencies, output_dir)
    return workflow

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
    return executor

def dict_to_agent(dictionary):
    agent = Agent(name)
    return agent
docker build -f server/Dockerfile -t scanflow-server .

docker build -f tracker/Dockerfile -t scanflow-tracker .

docker build -f agentbase/Dockerfile -t scanflow-agent .

docker build -f executorbase/Dockerfile -t scanflow-executor .

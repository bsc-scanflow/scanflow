#general
from typing import List
import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)


#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException



#queue
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
schedule = AsyncIOScheduler(
    jobstores={
        'default': SQLAlchemyJobStore(url='sqlite:///monitor.sqlite')
    },
    #executors = {
    #    'default': ThreadPoolExecutor(20),
    #    'processpool': ProcessPoolExecutor(5)
    #}
)
from datetime import datetime

#scanflow
from scanflow.agent.config.settings import settings
from scanflow.agent.template.monitor import custom_sensors
from scanflow.agent.schemas.sensor import Sensor, SensorOutput, CronTrigger, IntervalTrigger, DateTrigger

from scanflow.client import ScanflowTrackerClient
import mlflow
client = ScanflowTrackerClient(verbose=True)
mlflow.set_tracking_uri(client.get_tracker_uri(False))


monitor_sensors_router = APIRouter()

try:
    monitor_sensors_router.include_router(custom_sensors.custom_sensor_router)
except:
    logging.info("custom_sensors function does not provide a router.")

async def tick():
    print('Tick! The time is: %s' %  time.strftime("'%Y-%m-%d %H:%M:%S'"))

@monitor_sensors_router.on_event("startup")
async def sensors_startup():
    logging.info(f"{settings.AGENT_NAME} monitor sensors startup")
    schedule.start()
    print(settings.functions[1].path())
    schedule.add_job(settings.functions[1].path, 'interval', seconds=30, next_run_time=datetime.fromtimestamp(time.time()))

@monitor_sensors_router.on_event("shutdown")
async def sensors_shutdown():
    logging.info(f"{settings.AGENT_NAME} monitor sensors shutdown")
    scheduler.shutdown()

@monitor_sensors_router.get("/",
                            status_code= status.HTTP_200_OK)
async def sensors_root():
    try:
        for function in settings.functions:
            if function.name == "sensor_root":
                return function.path()
    except:
        return {"Hello": "monitor sensors"}

@monitor_sensors_router.get("/get/all", 
                            summary="get all sensors' information",
                            status_code = status.HTTP_200_OK,
                            response_model = List[SensorOutput])
async def get_all_sensors():
    """
    get all sensors' information
    :return:
    """
    jobs = []
    for job in schedule.get_jobs():
        jobs.append( 
            SensorOutput(
                id=job.id, name=job.name, func_name=job.func_ref, trigger=str(job.trigger), next_run_time=str(job.next_run_time)
            )
        )
    return jobs

@monitor_sensors_router.get("/get", 
                            summary="get specific sensor's information",
                            status_code = status.HTTP_200_OK,
                            response_model= SensorOutput)
async def get_sensor(sensor_id: str):
    job = schedule.get_job(job_id=sensor_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="sensor is not found")
    return  SensorOutput(
                id=job.id, name=job.name, func_name=job.func_ref, trigger=str(job.trigger), next_run_time=str(job.next_run_time)
            )

# interval 固定间隔时间调度
@monitor_sensors_router.post("/add/interval",
                             summary="start an interval sensor: sensor will run at every interval seconds",
                             status_code = status.HTTP_200_OK)
async def add_sensor_interval( sensor: Sensor, intervalTrigger: IntervalTrigger ):
    schedule_job = schedule.add_job(sensor.func,
                                    'interval',
                                    weeks = intervalTrigger.weeks,
                                    days = intervalTrigger.days,
                                    hours = intervalTrigger.hours,
                                    minutes = intervalTrigger.minutes,
                                    seconds = intervalTrigger.seconds,
                                    start_date = intervalTrigger.start_date,
                                    end_date = intervalTrigger.end_date,
                                    timezone = intervalTrigger.timezone,
                                    jitter = intervalTrigger.jitter,

                                    args=sensor.args,
                                    kwargs=sensor.kwargs,
                                    name=sensor.name,
                                    next_run_time=datetime.fromtimestamp(sensor.next_run_time)
                                    )
    return {"detail": f"{sensor.name} has been added. first run will start at {sensor.next_run_time}"}


# date 某个特定时间点只运行一次
@monitor_sensors_router.post("/add/date", 
                             summary="start a date sensor: sensor only run once at the specific date time",
                             status_code = status.HTTP_200_OK)
async def add_sensor_date(sensor: Sensor, dataTrigger: DateTrigger):
    schedule_job = schedule.add_job(sensor.func,
                                    'date',
                                    run_date = dataTrigger.run_date,
                                    timezone = dataTrigger.timezone,

                                    args=sensor.args,
                                    kwargs=sensor.kwargs,
                                    name=sensor.name
                                    )
    return {"detail": f"{sensor.name} has been added. sensor will run start at {sensor.run_date}"}


# cron 更灵活的定时任务 可以使用crontab表达式
@monitor_sensors_router.post("/add/cron",  
                             summary="start a flexible sensor with crontab expression",
                             status_code = status.HTTP_200_OK)
async def add_sensor_cron(sensor: Sensor, cronTrigger: CronTrigger):
    schedule_job = schedule.add_job(sensor.func,
                                    CronTrigger.from_crontab(cronTrigger.crontab),

                                    args=sensor.args,
                                    kwargs=sensor.kwargs,
                                    name=sensor.name
                                    )
    return {"detail": f"{sensor.name} has been added. sensor will run at {cronTrigger.crontab}"}

@monitor_sensors_router.delete("/remove", 
                              summary="delete a sensor",
                              status_code = status.HTTP_200_OK)
async def remove_sensor(sensor_id: str):
    job = schedule.get_job(job_id=sensor_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="sensor is not found")
    schedule.remove_job(job_id)
    return {"detail": f"{sensor_id} has been removed."}




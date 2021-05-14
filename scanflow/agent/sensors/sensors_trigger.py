#general
from typing import List
import logging
logging.basicConfig(format='%(asctime)s -  %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')
logging.getLogger().setLevel(logging.INFO)

#fastapi
from fastapi import FastAPI, APIRouter
from fastapi import Response, status, HTTPException


#scanflow
from scanflow.agent.config.settings import settings
from scanflow.agent.schemas.sensor import Sensor, SensorOutput, Trigger

#queue
import asyncio
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from apscheduler.triggers.cron import CronTrigger
schedule = AsyncIOScheduler(
    jobstores={
        'default': SQLAlchemyJobStore(url=f"sqlite:///{settings.AGENT_NAME}.sqlite")
    },
    #executors = {
    #    'default': ThreadPoolExecutor(20),
    #    'processpool': ProcessPoolExecutor(5)
    #}
)
from datetime import datetime
import time

sensors_trigger_router = APIRouter()

@sensors_trigger_router.on_event("startup")
async def sensors_startup():
    logging.info(f"{settings.AGENT_NAME} monitor sensors startup")
    await sensors_root()
    schedule.start()
    if settings.sensors is not None:
        for k,v in settings.sensors.items():
            if v.trigger.type == 'interval':
                await add_sensor_interval(v.name)
            elif v.trigger.type == 'date':
                await add_sensor_date(v.name)
            elif v.trigger.type == 'cron':
                await add_sensor_cron(v.name)

@sensors_trigger_router.on_event("shutdown")
async def sensors_shutdown():
    logging.info(f"{settings.AGENT_NAME} monitor sensors shutdown")
    await remove_all_sensors()
    scheduler.shutdown()

@sensors_trigger_router.get("/",
                            status_code= status.HTTP_200_OK)
async def sensors_root():
    print(f"Hello! monitor trigger sensors")
    return {"Hello": "monitor trigger sensors"}

@sensors_trigger_router.get("/get/all", 
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
                id=job.id, name=job.name, func_name=job.func_ref, trigger_str=str(job.trigger), next_run_time=str(job.next_run_time)
            )
        )
    return jobs

@sensors_trigger_router.get("/get", 
                            summary="get specific sensor's information",
                            status_code = status.HTTP_200_OK,
                            response_model= SensorOutput)
async def get_sensor(sensor_id: str):
    job = schedule.get_job(job_id=sensor_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="sensor is not found")
    return  SensorOutput(
                id=job.id, name=job.name, func_name=job.func_ref, trigger_str=str(job.trigger), next_run_time=str(job.next_run_time)
            )

# interval 固定间隔时间调度
@sensors_trigger_router.post("/add/interval",
                             summary="start an interval sensor: sensor will run at every interval seconds",
                             status_code = status.HTTP_200_OK)
async def add_sensor_interval( sensor_name: str ):
    sensor = settings.sensors[f"{sensor_name}"]
    print(sensor.dict())

    if sensor.next_run_time is None:
        #default start right now
        next_run_time = datetime.fromtimestamp(time.time())
    else:
        next_run_time = sensor.next_run_time

    if sensor.trigger.type == 'interval': 
        schedule_job = schedule.add_job(sensor.func,
                                    'interval',
                                    weeks = sensor.trigger.weeks,
                                    days = sensor.trigger.days,
                                    hours = sensor.trigger.hours,
                                    minutes = sensor.trigger.minutes,
                                    seconds = sensor.trigger.seconds,
                                    start_date = sensor.trigger.start_date,
                                    end_date = sensor.trigger.end_date,
                                    timezone = sensor.trigger.timezone,
                                    jitter = sensor.trigger.jitter,

                                    args=sensor.args,
                                    kwargs=sensor.kwargs,
                                    name=sensor.name,
                                    next_run_time=next_run_time
                                    )
        logging.info(f"{sensor.name} has been added. first run will start at {next_run_time}")
        return {"detail": f"{sensor.name} has been added. first run will start at {next_run_time}"}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="trigger is not allowed")


# date 某个特定时间点只运行一次
@sensors_trigger_router.post("/add/date", 
                             summary="start a date sensor: sensor only run once at the specific date time",
                             status_code = status.HTTP_200_OK)
async def add_sensor_date(sensor_name: str):
    sensor = settings.sensors[f"{sensor_name}"]

    if sensor.trigger.type == 'date': 
        schedule_job = schedule.add_job(sensor.func,
                                    'date',
                                    run_date = sensor.trigger.run_date,
                                    timezone = sensor.trigger.timezone,

                                    args=sensor.args,
                                    kwargs=sensor.kwargs,
                                    name=sensor.name
                                    )
        logging.info(f"{sensor.name} has been added. sensor will run start at {sensor.run_date}")
        return {"detail": f"{sensor.name} has been added. sensor will run start at {sensor.run_date}"}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="trigger is not allowed")


# cron 更灵活的定时任务 可以使用crontab表达式
@sensors_trigger_router.post("/add/cron",  
                             summary="start a flexible sensor with crontab expression",
                             status_code = status.HTTP_200_OK)
async def add_sensor_cron(sensor_name: str):
    sensor = settings.sensors[f"{sensor_name}"]

    if sensor.trigger.type == 'cron': 
        schedule_job = schedule.add_job(sensor.func,
                                    CronTrigger.from_crontab(sensor.trigger.crontab),

                                    args=sensor.args,
                                    kwargs=sensor.kwargs,
                                    name=sensor.name
                                    )
        logging.info(f"{sensor.name} has been added. sensor will run at {cronTrigger.crontab}")
        return {"detail": f"{sensor.name} has been added. sensor will run at {cronTrigger.crontab}"}
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="trigger is not allowed")

@sensors_trigger_router.delete("/remove", 
                              summary="delete a sensor",
                              status_code = status.HTTP_200_OK)
async def remove_sensor(sensor_id: str):
    job = schedule.get_job(job_id=sensor_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="sensor is not found")
    schedule.remove_job(job_id)
    return {"detail": f"{sensor_id} has been removed."}

@sensors_trigger_router.delete("/remove/all", 
                              summary="delete all sensors",
                              status_code = status.HTTP_200_OK)
async def remove_all_sensors():
    schedule.remove_all_jobs()
    logging.info("all jobs has been removed.")
    return {"detail": f"all jobs has been removed."}




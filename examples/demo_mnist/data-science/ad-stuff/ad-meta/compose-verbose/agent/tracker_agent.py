import uvicorn
import os
import track

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

if 'AGENT_PORT' in os.environ:
    port = int(os.environ['AGENT_PORT'])
else:
    port = int(os.environ['MLFLOW_PORT'])+1

print(track.list_artifacts())


@app.get("/artifacts/last")
async def root():
    msg = f"""
    The last artifact is:

        {track.list_artifacts()}

    """
    return {"[Tracker]": msg}

@app.get("/interpretation/{feedback_id}")
async def root(feedback_id: int):
    msg = f"""
    The interpretation for feedback={feedback_id} is:

        Explanation 1.
        Explanation 2.

    """
    return {"[Checker]": msg}
    
if __name__ == '__main__':
     uvicorn.run(app, port=port, host='0.0.0.0')

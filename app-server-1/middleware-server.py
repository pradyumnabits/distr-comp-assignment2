# Server application
from fastapi import FastAPI
from pydantic import BaseModel
import requests
import socket
import time
import random
import asyncio  # Import the asyncio library


# Set the server port (use the correct port)
local_server_port = 8001

# Define the URL of the remote process's FastAPI application
REMOTE_API_URL = "http://localhost:8002"  # Replace with the correct URL

app = FastAPI()

class RequestMessage(BaseModel):
    sender_process_id: int
    sender_clock: int

class ReplyMessage(BaseModel):
    sender_process_id: int
    sender_clock: int

# Get the system's hostname
system_name = socket.gethostname()


# Combine the system name and port to create the process_id
#process_id = f"{system_name}:{local_server_port}"
current_timestamp = int(time.time() * 1000)
# Generate a random number
random_number = random.randint(1, 1000)
process_id = current_timestamp + random_number


clock = 0
requesting = False
accessing_shared_resource = False
num_replies_received = 0
queued_requests = []


@app.post("/request_access")
async def request_access(request_data: RequestMessage):
    global process_id, clock, requesting, num_replies_received, queued_requests

    # Receive a request message from another process
    sender_process_id = request_data.sender_process_id
    sender_clock = request_data.sender_clock
    clock = max(clock, sender_clock) + 1

    if not requesting or (sender_clock <  clock):
        # Send a reply message to the sender
        reply_message = ReplyMessage(sender_process_id=process_id, sender_clock=clock)
        queued_requests.append((sender_clock, sender_process_id))

    elif requesting and (clock == sender_clock):

        # Check if the local process is already requesting access
        # and if its clock is equal to the sender's clock

        # In Lamport's DME algorithm, the process with the lower
        # timestamp has higher priority. If the local process's
        # timestamp (clock) is equal to the sender's timestamp
        # (sender_clock), then we compare the process IDs to
        # determine priority.

        if sender_process_id < process_id:
            # The sender process has a lower process ID, so it has
            # higher priority. Send a reply message to the sender.
            reply_message = ReplyMessage(sender_process_id=process_id, sender_clock=clock)
            queued_requests.append((sender_clock, sender_process_id))

        else:
            # The local process has a lower process ID, so it has
            # higher priority. Wait for requesting == False to send the reply
            await wait_for_requesting()
            reply_message = ReplyMessage(sender_process_id=process_id, sender_clock=clock)
            queued_requests.append((sender_clock, sender_process_id))

    print(f"request_access  - Process ID: {process_id}, Clock: {clock}, Queued Requests: {queued_requests}")


    return reply_message

async def wait_for_requesting():
    interval = 0.5  # 500 milliseconds (0.5 seconds)
    while requesting:
        await asyncio.sleep(interval)

@app.post("/release_access")
async def release_access(request_data: RequestMessage):
    global process_id, clock, requesting, num_replies_received, queued_requests

    sender_process_id = request_data.sender_process_id
    sender_clock = request_data.sender_clock

    # Find and remove the first entry from queued_requests if it matches
    if queued_requests[0] == (sender_clock, sender_process_id):
        
        queued_requests.pop(0)

        print(f"release_access  - Process ID: {process_id}, Clock: {clock}, Queued Requests: {queued_requests}")

        return {"message": "DME_LOCK_RELEASED"}
    else:
        return {"message": "DME_LOCK_NOT_AVAILABLE"}


@app.post("/local_request_access")
async def local_request_access():
    global process_id, clock, requesting, num_replies_received, queued_requests , accessing_shared_resource

        # Print the state before processing
    print(f"local_request_access: start - Process ID: {process_id}, Clock: {clock}, Requesting: {requesting}, Queued Requests: {queued_requests}")



    clock += 1  # Increment the local clock
    #clock = int(time.time() * 1000)


    requesting = True


    queued_requests.append((clock, process_id))
    
    # Construct the request data
    request_data = RequestMessage(sender_process_id=process_id, sender_clock=clock)

    # Make a POST request to the remote /request_access endpoint
    #response = requests.post(f"{REMOTE_API_URL}/request_access", json=request_data.json())
    response = requests.post(f"{REMOTE_API_URL}/request_access", data=request_data.model_dump_json())


    # If reposnse is successful & the top process_id is the local server id then accquire the lock
    if response.status_code == 200:
        # Parse and return the response
        response_data = response.json()
        # If the top process_id is the local server id then accquire the lock
        if queued_requests and queued_requests[0] == (clock, process_id):

            accessing_shared_resource = True



    # Print the state after processing
    print(f"local_request_access: end - Process ID: {process_id}, Clock: {clock}, Requesting: {requesting}, Queued Requests: {queued_requests}")


    return accessing_shared_resource
    

@app.post("/local_release_access")
async def local_release_access():
    global process_id, clock, requesting, num_replies_received, queued_requests


    # Print the state before processing
    print(f"local_release_access: start - Process ID: {process_id}, Clock: {clock}, Requesting: {requesting}, Queued Requests: {queued_requests}")


    queued_requests.pop(0);


    # Construct the request data
    request_data = RequestMessage(sender_process_id=process_id, sender_clock=clock)
    
    # Make a POST request to the remote /release_access endpoint
    #response = requests.post(f"{REMOTE_API_URL}/release_access", json=request_data.json())
    response = requests.post(f"{REMOTE_API_URL}/release_access", data=request_data.model_dump_json())


    if response.status_code == 200:
        # Parse and return the response
        response_data = response.json()

        # Release the shared resource
        accessing_shared_resource = False

        # The process has released the shared resource
        requesting = False

        clock += 1

        # Print the state after processing
        print(f"local_release_access: end - Process ID: {process_id}, Clock: {clock}, Requesting: {requesting}, Queued Requests: {queued_requests}")

        return True

    else:
        # Handle the case where the remote request was unsuccessful
        return False


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=local_server_port)


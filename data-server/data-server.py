# from fastapi import FastAPI
# from pydantic import BaseModel
# from datetime import datetime
# import logging
# from queue import Queue  # Import the Queue class

# app = FastAPI()

# # Set the maximum size for the queue to store the latest messages
# max_messages = 100
# shared_file = Queue(max_messages)  # Use a Queue instead of a deque

# class Message(BaseModel):
#     text: str

# # Configure logging
# logging.basicConfig(filename='server.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# @app.get("/view")
# async def view_messages():
#     return list(shared_file.queue)  # Access the queue using the .queue attribute

# @app.post("/post", response_model=Message)
# async def post_message(message: Message):
#     print(message) 
#     shared_file.put(message)  # Use .put() to add messages to the queue
#     return {"text": message}


import os
from fastapi import FastAPI
from pydantic import BaseModel
from queue import Queue

app = FastAPI()

# Set the maximum size for the queue to store the latest messages
max_messages = 100

# Check if the data-file exists and load it into the Queue if it does
data_file_path = "chat-data.txt"
shared_file = Queue(max_messages)
if os.path.exists(data_file_path):
    with open(data_file_path, "r") as file:
        for line in file:
            shared_file.put(line.strip())  # Load each line from the file into the Queue

class Message(BaseModel):
    text: str

@app.on_event("shutdown")
def save_messages_to_file():
    with open(data_file_path, "w") as file:
        while not shared_file.empty():
            message = shared_file.get()
            file.write(f"{message}\n")

@app.get("/view")
async def view_messages():
    return list(shared_file.queue)

@app.post("/post", response_model=Message)
async def post_message(message: Message):
    shared_file.put(message.text)  # Use .put() to add messages to the queue
    with open(data_file_path, "a") as file:
        file.write(f"{message.text}\n")
    return {"text": message.text}

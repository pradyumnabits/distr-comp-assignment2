from pydantic import BaseModel
import getpass
import socket
import requests
from datetime import datetime
import logging

# Get the system's username
user_name = getpass.getuser()

# Get the machine name
machine_name = socket.gethostname()

# URL of the FastAPI server
data_server_url = "http://127.0.0.1:8000"  # Replace with the actual server URL

# Define the URL of the local process's FastAPI application
LOCAL_API_URL = "http://localhost:8001"  # Replace with the correct URL

# Constants
NUM_PROCESSES = 2  # Replace with the actual number of processes

class RequestMessage(BaseModel):
    sender_process_id: int
    sender_clock: int

class ReplyMessage(BaseModel):
    sender_process_id: int
    sender_clock: int

def requestCriticalSection():
    
    requests.post(f"{LOCAL_API_URL}/local_request_access")


def releaseCriticalSection():
    
    requests.post(f"{LOCAL_API_URL}/local_release_access")


def make_post_request_synchronized(data_server_url, message_content):
    requestCriticalSection()
    make_post_request(data_server_url, message_content)
    releaseCriticalSection()

def make_post_request(data_server_url, message_content):
    message_to_post = f"{user_name}: {message_content}"
    timestamp = datetime.now().strftime("%d %b %I:%M%p")
    message_with_timestamp = f"{timestamp} {message_to_post}"
    print(message_with_timestamp) 
    response = requests.post(f"{data_server_url}/post", json={"text": message_with_timestamp})
    if response.status_code == 200:
        print("Message posted.")
    else:
        print("Failed to post message.")

# Function to change the user name if input is provided
def change_user_name():
    global user_name
    new_user_name = input("Enter your name (Press Enter to keep the current name): ")
    if new_user_name:
        user_name = new_user_name
        print(f"User name updated to: {user_name}")



while True:
    change_user_name()  # Prompt for user name input
    print("Options: [ view , post ]")
    print("view : View Messages")
    print("post : Post Message")
    print("exit: Exit Application")

    option = input(f"{user_name}@{machine_name} > ").lower()

    if option == "view":
        response = requests.get(f"{data_server_url}/view")
        if response.status_code == 200:
            messages = response.json()
            if messages:
                print("Messages:")
                for index, message in enumerate(messages, 1):
                    print(f"{message}")
            else:
                print("No messages available.")
        else:
            print("Failed to view messages.")
    
    elif option == "post":
        # Post Message
        message_content = input("Enter your message: ")
        message_to_post = f"{user_name}: {message_content}"
        make_post_request_synchronized(data_server_url, message_content)

    elif option == "exit":
        print("Exiting the application.")
        break  # Exit the loop and application
    
    else:
        print("Invalid option.")


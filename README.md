# distr-comp-assignment2

This example demonstrates a simple chat console application which uses Distributed Mutual exclusion(DME) for posting messages.
This application is written in Python langauge.

## Set the environment 
1. Open a terminal.
2. Install the required dependencies i.e. pip, FastAPI, uvicorn if not yet available on server


## Note : Following are the sequencees for starting the application

 1. Start data-server.py on the server (Server 3)
 2. Start middleware-server.py on both the servers (Server 1, Server2)
 3. Start chat-app.py in both the servers (Sever 1 , Server2)

## Server 1

Server 1 serves files from its local directory and can communicate with Server 2 to retrieve files.

Server 1:
1. Open a terminal , navigate to distr-comp-assignment2
2. Navigate to the `app-server-1` directory.
3. Update the following  in chat-app.py

    # URL of the FastAPI server
    data_server_url = "http://127.0.0.1:8000"  # Replace with the actual server URL of Server 3

	# Define the URL of the local process's FastAPI application
	LOCAL_API_URL = "http://localhost:8002"  # Replace with the correct local middleware port

4. Update the following  in middleware-server.py
   
    # Set the server port (use the correct port)
	local_server_port = 8002 # Replace with the correct local port

	# Define the URL of the remote process's FastAPI application
	REMOTE_API_URL = "http://localhost:8001"  # Replace with the correct URL of Server 2

3. Start middleware-server.py 
   ./start-middleware.sh

4. Start chat-app.py 
   ./start.sh
   

## Server 2
Server 1:
1. Open a terminal , navigate to distr-comp-assignment2
2. Navigate to the `app-server-1` directory.
3. Update the following  in chat-app.py

    # URL of the FastAPI server
    data_server_url = "http://127.0.0.1:8000"  # Replace with the actual server URL of Server 3 

	# Define the URL of the local process's FastAPI application
	LOCAL_API_URL = "http://localhost:8002"   # Replace with the correct local middleware port

4. Update the following  in middleware-server.py
   
    # Set the server port (use the correct port)
	local_server_port = 8002 # Replace with the correct local port

	# Define the URL of the remote process's FastAPI application
	REMOTE_API_URL = "http://localhost:8001"  # Replace with the correct URL of Server 1

3. Start middleware-server.py 
   ./start-middleware.sh

4. Start chat-app.py 
   ./start.sh

## Server 3

To start the data-server:

1. Open a terminal.
2. Navigate to the data-server directory.
3. Update the local port , default 8000
4. Start the server 
   ./start.sh

# Running Your Flask Application in the Background

This guide explains how to keep your Flask application running continuously, even after closing Visual Studio.

## Starting the Application in Background Mode

To start your application in the background:

1. Open a terminal in your project directory
2. Run the following command:
   ```
   ./run_in_background.sh
   ```
3. You should see a message confirming that the application has started in the background with a PID (Process ID)
4. You can now close Visual Studio, and the application will continue running

## Stopping the Background Application

To stop the application when needed:

1. Open a terminal in your project directory
2. Run the following command:
   ```
   ./stop_background_app.sh
   ```
3. You should see a message confirming that the application has been stopped

## How It Works

The `run_in_background.sh` script:
- Checks for and kills any existing process using port 5000
- Starts your Flask application with Gunicorn in the background using `nohup`
- Saves the process ID to a file (`gunicorn.pid`) for easy management
- Redirects output to a log file (`gunicorn.log`)

The `stop_background_app.sh` script:
- Reads the process ID from the `gunicorn.pid` file
- Stops the application process
- Removes the PID file

## Checking If Your Application Is Running

To check if your application is still running:

```
ps -p $(cat gunicorn.pid)
```

You can also check the application's health endpoint:

```
curl http://localhost:5000/health
```

## Viewing Application Logs

To view the application logs:

```
cat gunicorn.log
```

Or to follow the logs in real-time:

```
tail -f gunicorn.log
# Station API Simulator

A Flask-based web application that simulates multiple stations sending mock data to an API endpoint. This tool is designed to help developers test their API endpoints with realistic station data streams.

## Features

- **Web Interface**: Easy-to-use control panel for managing data simulation
- **Multiple Station Support**: Simultaneously manage up to 6 different stations
- **Configurable Parameters**:
  - Custom API endpoint
  - Adjustable sending intervals
  - Configurable starting indices for each station
- **Real-time Control**: Start/stop individual station data streams
- **Background Processing**: Uses APScheduler for reliable data transmission
- **Error Handling**: Robust error management for API calls and file operations
- **Timezone Support**: Configured for Asia/Ho_Chi_Minh timezone

## Prerequisites

- Python 3.x
- Flask
- APScheduler
- Requests
- pytz

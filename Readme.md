<p align="center">
  <img src="assets/logo.png" alt="Capital Quest Logo" width="200">
</p>

<h1 align="center">Capital Quest</h1>

<p align="center">
  Test your knowledge of world capitals with this interactive quiz game! 🌍🏙️
</p>

<p align="center">
  <a href="#play-the-game-">Play the Game</a> •
  <a href="#installation-for-developers-">Installation for Developers</a>
</p>

<br>

## Play the Game 🎮

Ready to challenge your knowledge of world capitals? 

[Click here to play Capital Quest!](https://capital-quest.example.com) 🚀

## Installation for Developers 🛠️

If you want to run Capital Quest locally, follow these steps:

### Prerequisites

- Python 3.9 or higher
- Git

### Option 1: Git Clone 🐙

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/capitalquest.git
   cd capitalquest
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the application:
   ```bash
   python launch.py
   ```

   This will start both the API and front-end components in development mode.

   Customize with options:
   - `--env`: Choose between `dev` (default) or `prod` environments
   - `--component`: Run `api`, `front`, or `both` (default) components
   - `--api-host`, `--api-port`: Set custom API host/port (default: localhost:8000)
   - `--front-host`, `--front-port`: Set custom front-end host/port (default: localhost:8051)

   Example:
   ```bash
   python launch.py --env prod --component api --api-port 8080
   ```

   Note: You can also set these options using environment variables or a .env file:
   ```bash
   export api_host=localhost
   export api_port=8000
   export front_host=localhost
   export front_port=8051
   export environment=dev
   ```

4. Open your browser and navigate to `http://localhost:8051` (or your custom front-end port)

### Option 2: Docker 🐳

A Docker image is available for easy setup:

1. Pull the Docker image:
   ```bash
   docker pull yourdockerhub/capitalquest:latest
   ```

2. Run the container:
   ```bash
   docker run -p 8051:8051 yourdockerhub/capitalquest:latest
   ```

3. Access the game at `http://localhost:8051`

---

Enjoy testing your knowledge of world capitals with Capital Quest! 🌎🏆

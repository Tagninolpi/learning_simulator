# Mating Game - LEHNA

## Context

According to evolutionary theory, individuals seek to reproduce with high-quality partners in order to increase the chances of survival and reproduction of their offspring. It is now known that animals are able to assess the quality of a potential partner and make choices that maximize their reproductive success.

However, the choices made by individuals are not always strictly rational. Studies have shown that, in certain situations, an individual may refuse a higher-quality partner than the one they are already paired with, or conversely choose a new partner of lower quality. This seemingly “irrational” behavior actually constitutes an adaptive response: it can promote pair stability and, in the long term, improve reproductive success. In other words, what is called a behavioral bias is not necessarily an error in judgment, but may be an advantageous evolutionary adaptation with a major evolutionary impact.

Researchers at LEHNA wanted to create an experimental situation making it possible to highlight this adaptive bias, using an interactive game reproducing the mechanisms of the model, in order to observe the existence of this bias in humans and analyze their behavior over the course of the simulated breeding season.

## Usefulness of the game compared to the existing model

The objective of this project is to design an interactive game simulating a breeding season, during which each player must choose partners over time. The game is based on a biological model inspired by the work of LEHNA, in which individuals must decide whether to keep their current partner or switch to a new candidate.

A population composed of several players interacts during the simulation. Individuals are randomly paired to form couples. At each round, the player must decide whether to keep their current partner or change. In other words, the player must develop a strategy in order to maximize the quality of the partner with whom they reproduce (mate) before the end of the season.

This game pursues two main objectives:

1. **A pedagogical and experimental objective**: The game must allow students and players to understand how decision biases influence behavior. It leads to questioning how these biases can be modeled, and the fact that an optimal bias is not always intuitive. By manipulating the game parameters (time remaining in the season, duration of courtship, etc.), the player discovers that the most rational strategy is not always the most effective in the long term.

2. **A science communication objective**: In a popularization context (forum, exhibition, or public presentation), the game illustrates the fact that a human bias, often perceived as irrational, can in reality have adaptive value.

### Description of the existing model

LEHNA researchers have built a frequency-dependent model making it possible to estimate the expected adaptive emotional biases as a function of individual quality, time remaining in the season, and time already spent in courtship.

In the model, each individual can occupy three states:
- **Single**: without a partner;
- **Courtship**: in the partner evaluation phase;
- **Mate**: partner accepted, successful reproduction.

This model is based on a theoretical infinite population whose quality values follow a distribution between 0 and 1, called the beta distribution. Classes of values have been defined in order to limit heterogeneity and better represent interactions between individuals of similar quality levels.

The probability of “mating” (reproduction) between two individuals in the “courtship” phase (interaction prior to mating) is modeled by a sigmoid function. The x-axis represents the number of time steps spent in courtship, and the y-axis the probability of transition to “mate”. This probability gradually increases with the duration of courtship, up to an inflection point beyond which the probability of reproduction quickly becomes maximal.

It should be understood that this bias is not an error in judgment, but an evolutionary adaptation. In other words, what is referred to as an “emotional bias” corresponds to an adaptive strategy that promotes pair stability and increases the probability of reproduction in the long term. Emotion, far from being an irrational deviation, is therefore a functional mechanism that supports the evolutionary success of individuals.

## Game description

The interactive game simulates a breeding season during which players must mutually choose their partners. The main mechanisms are as follows:

### Game start logic
1. **Lobby creation**: The administrator creates a game (the “lobby”) from the interface by establishing a WebSocket connection with the server. Through this connection, the admin sends the game parameters to the server. The server creates a unique lobby instance containing these parameters.
2. **Player connection**: When loading the page, the WebSocket checks the lobby status. If a lobby exists, players can join it. The server notifies the admin of the number of connected players.
3. **Game launch**: The administrator can start the game once enough players are connected. The server assigns a value to each player (drawn from a distribution) and starts the main game loop (asynchronous task). The administrator then accesses the live visualization page, while players are redirected to the game page.

### Logic during the game
The core of the game runs in an asynchronous main loop on the server side. WebSockets ensure real-time bidirectional communication.

1. **Pair formation**: The server randomly selects pairs among active players (not yet in “mating”). Each player receives via WebSocket the value of their partner and the visible information.
2. **Choice phase**: An internal timer starts (e.g., 60 seconds). Each player can click on “accept”. The click sends a message to the server via WebSocket.
3. **End of timer and evaluation**: At the end of the timer, if both players have mutually accepted, a courtship is created. For each couple in courtship, the server calculates a probability of transition to mating (sigmoid function). If reached, the couple enters mating and is removed from the active pool.

### End of the game
The loop stops when there are no more active players or at the end of the season. The server sends the final results via WebSocket. Each player views their statistics, and the admin can download a summary CSV of the choices made by players.

### Game parameterization
The administrator can configure:
- Number of time steps (npt) of a season
- Courtship npt (sigmoid inflection)
- Time to make a choice
- Other default parameters.

Each parameter can be made visible or not to the players.

## How to use

### Prerequisites
- Python 3.8 or higher
- A modern web browser (Chrome, Firefox, Safari, etc.)
- Internet connection for WebSockets

### 1) Locally with a virtual environment
1. Clone or download the project into a local directory.
2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Start the server:
   ```
   uvicorn app:app --host 0.0.0.0 --port 8000 --reload
   ```
5. Open your browser and go to `http://localhost:8000`.
6. The administrator can then create a lobby and join the game from other tabs.

### 2) Online with Render
The project is configured for deployment on Render (see `render.yaml`).
1. Create an account on Render and link your GitLab repository.
2. Deploy the application using the default settings (port via `$PORT`).
3. Once deployed, obtain the public URL (e.g., `https://your-app.onrender.com`).
4. Share the URL: users access it directly via their browser to play.
5. The server remains online continuously (use Uptimerobot to avoid interruptions).

## Technical architecture

### Backend (Python/FastAPI)
- **app.py**: FastAPI entry point, route and WebSocket management.
- **server_class.py**: Server logic, message handling, lobby, admin.
- **game_class.py**: Core game logic, rounds, pairings, probabilities.
- **player_class.py**: Player model, value/class calculations.
- **connections_class.py**: WebSocket connection management, UI updates.
- **observer_class.py**: Asynchronous listener for queued messages.

### Frontend (HTML/JS/CSS)
- **index.html**: Main container, loads styles and scripts.
- **main.js**: JavaScript logic for WebSockets, dynamic loading of HTML fragments.
- **HTML Fragments** (in `static/fragments/`): Pages for menu, lobby, results.
- **Styles**: `tokens.css` (variables), `components.css` (UI), `hidden.css` (utilities).
- **Sounds**: Audio effects in `static/sounds/`.

### Technologies
- **FastAPI**: Asynchronous web framework for APIs and WebSockets.
- **Uvicorn**: ASGI server.
- **NumPy**: Mathematical computations.
- **WebSockets**: Real-time communication.
- **Vanilla JavaScript**: Front-end management.

### Security
- WebSocket message validation.
- Data anonymization (no GDPR applicable).

## Development and contribution

### Project structure
```
/
├── app.py                 # Main server
├── game_class.py          # Game logic
├── player_class.py        # Player model
├── server_class.py        # Server management
├── connections_class.py   # WebSocket connections
├── observer_class.py      # Message processing
├── file_management.py     # File management
├── requirements.txt       # Dependencies
├── render.yaml            # Deployment
└── static/
    ├── index.html
    ├── main.js
    ├── fragments/         # HTML pages
    ├── styles/            # CSS
    └── sounds/            # Audio
```


### Testing and debugging
- Run in `--reload` mode for development.
- Use browser debugging tools for WebSockets.
- Manual testing for each feature.

### Contribution
- Fork the GitLab repository, create a branch for modifications.
- Respect code style (PEP 8 for Python, JS conventions).
- Test locally before submitting a PR.

### FAQ
- **The game does not start?** Check that port 8000 is free and dependencies are installed.
- **WebSocket issues?** Browser support, no firewall blocking.
- **How to add sounds?** Place them in `static/sounds/` and reference them in JS.
- **Empty CSV data?** Ensure the game was played and the admin downloads after the end.
- **Browser does not refresh my changes?** During development on HTML and JavaScript files, the browser may cache resources. Open the page inspector, go to the "Network" tab, check "Disable cache", and keep the inspector open while making changes.

For technical details, see comments in the source code.

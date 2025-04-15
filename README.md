# general-i-a

El juego de la generala jugado por IA, Generalia

## Overview
This project implements the classic dice game Generala, playable via a command-line interface (CLI). The game logic and scoring are handled in Python, and the project is structured for easy extension and testing.

## Features
- Play Generala against another player via the CLI
- Scoreboard display
- Category selection and scoring logic
- Easily extensible for AI or additional features

## Requirements
- Python 3.11+
- [Poetry](https://python-poetry.org/) for dependency management

## Setup
1. Clone the repository:
   ```sh
   git clone <repo-url>
   cd general-i-a
   ```
2. Install dependencies:
   ```sh
   poetry install
   ```

## Usage
To start the CLI game, run:
```sh
poetry run python src/cli.py
```

## Project Structure
- `src/cli.py`: Main CLI interface for playing Generala
- `src/generala.py`: Game logic, rules, and scoring
- `notebook/`: Example Jupyter notebooks for experimentation

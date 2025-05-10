 ##  Snake Game with AI (Greedy & A*) - Pygame

This is a feature-rich version of the classic Snake Game developed using **Python** and **Pygame**. It includes both **manual** and **AI-controlled** gameplay modes, with two types of AI:
- **Greedy Algorithm**
- **A\* (A-Star) Pathfinding Algorithm**

##  Features

- Manual gameplay mode using arrow keys.
- AI modes using either Greedy or A* algorithms.
- Dynamic speed increase as the score rises.
- Score display during gameplay.
- Game Over screen with buttons to restart or exit.
- Background, sound effects, and custom assets (apple image, background, etc.).
- Smart collision detection with self and walls.
-------------------------------


##  AI Modes

- **Greedy Algorithm:** Chooses the next move based on the shortest distance to the food, avoiding immediate collisions.
- **A\* Algorithm:** Uses pathfinding to find an optimal path to the food, considering obstacles (snake body and walls).

##  How to Run

1. Make sure Python 3 is installed on your system.
2. Install required packages (mainly `pygame` and `numpy`):

   ```bash
   pip install pygame numpy
How to run 
   ```bash
   python both.py

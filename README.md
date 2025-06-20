# Euroleague Team Optimizer

This project uses Linear Programming (LP) to optimize Euroleague basketball team selection. The application allows users to build a 14-player roster while considering constraints like playstyle preferences, salary cap, positional requirements, and nationality filters.

## Features:
- **Playstyle Selection**: Choose between Aggressive, Defensive, or Balanced.
- **Salary Cap**: Set a budget constraint to manage costs.
- **Positional Constraints**: Ensure a minimum number of players per position.
- **Nationality Filter**: Include at least 4 players from a specific country.
- **Downloadable Results**: Export the optimized team as a CSV file.

## How to Use Locally:
- Clone this repository and install the required dependencies.
- Run the application using Streamlit ```streamlit run lp_euroleague_project.py```
- Access the app in your browser and input your preferences to generate the optimal team.

## Try the App Online: 
Click the URL to try the app online using Streamlit:
https://euroleague-team-optimizer.streamlit.app

## Inspiration: 
This project was inspired by the article "Playing Moneyball: Creating an Efficient NBA Team with Linear Programming" by 
Nicolás García Aramouni. Special thanks to him for sharing his work and methodology.

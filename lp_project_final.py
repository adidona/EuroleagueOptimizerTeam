# -*- coding: utf-8 -*-
"""LP_Project_Final.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1qNDFOERlnfbAgq48pFRvmqxrjpYUVgjB

# Euroleague team optimizer using linear programming
**Authors**:


*   **Antonios Didonakis**
*   **Stathis Pantos**

**Institution**: **University of Thessaly**

This project aims to demonstrate how to create an interactive application for optimizing basketball team selection.
Users can choose their preferred playstyle (Aggressive, Defensive, or Balanced) and set a salary cap.
The program  uses linear programming to select 14 players that best fit the chosen playstyle while adhering to the constraints.

**Data Preparation**
"""

import streamlit as st
import pandas as pd
from ortools.linear_solver import pywraplp

# Load datasets
@st.cache
def load_stats():
    """
    Load stats dataset from a local CSV file.
    """
    return pd.read_csv('euroleague23-24_stats.csv')

@st.cache
def load_salaries():
    """
    Load salaries dataset from a local CSV file.
    """
    return pd.read_csv('euroleague_2024_salaries.csv').rename(columns={"2023-24": "Salary"})

@st.cache
def merge_datasets(stats_df, salaries_df):
    """
    Merge the stats and salaries datasets into a final DataFrame.
    """
    merged_df = pd.merge(stats_df, salaries_df, how="inner", on="Player")
    return merged_df

# Load data
df_stats = load_stats()
df_salaries = load_salaries()
df = merge_datasets(df_stats, df_salaries)

# Efficiency (EFF)
df['EFF'] = (
    df['PTS'] +
    df['TRB'] +
    df['AST'] +
    df['STL'] +
    df['BLK'] +
    (df['3P'] * 1.5) -
    (df['FGA'] - df['FG']) -
    (df['FTA'] - df['FT']) -
    df['TOV'] -
    df['PF']
)

# Aggressive Score
df["Agg_Score"] = (
    (0.5 * df["PTS"]) +
    (0.3 * df["3P"]) +
    (0.1 * df["AST"]) +
    (0.05 * df["STL"]) +
    (0.05 * df["BLK"])
)

# Defensive Score
df["Def_Score"] = (
    (0.4 * df["TRB"]) +
    (0.35 * df["STL"]) +
    (0.2 * df["BLK"]) +
    (0.025 * df["PTS"]) +
    (0.025 * df["AST"])
)

# Balanced Score
df["Bal_Score"] = (
    (0.25 * df["PTS"]) +
    (0.2 * df["TRB"]) +
    (0.2 * df["AST"]) +
    (0.2 * df["3P"]) +
    (0.075 * df["STL"]) +
    (0.075 * df["BLK"])
)

# User input
st.title("Euroleague Team Optimizer")
st.sidebar.header("User Inputs")
st.markdown("""
Welcome to the **Euroleague Team Optimizer**! 🎮🏀

This application uses **linear programming** to help you build an optimized basketball team based on:
- **Playstyle** preferences (Aggressive, Defensive, or Balanced)
- A **Salary Cap** to manage costs effectively

### How it works:
1. **Select a playstyle** from the dropdown menu on the left:
   - **Aggressive**: Focus on high-scoring and offensive plays.
   - **Defensive**: Emphasize defensive strength and teamwork.
   - **Balanced**: A mix of both offensive and defensive strategies.
2. **Set your salary cap** using the slider.
3. Click **Run Optimization** to generate the best possible team of 14 players while adhering to the constraints.

Build your dream Euroleague team today and see how strategic constraints shape your roster! 🏆
        """)

playstyle = st.sidebar.selectbox(
    "Select Playstyle:",
    options=["Aggressive", "Defensive", "Balanced"]
)

salary_cap = st.sidebar.slider(
    "Set Salary Cap (€):",
    min_value=5_000_000,
    max_value=30_000_000,
    step=1_000_000,
    value=20_000_000
)

# Map playstyle to score column
playstyle_map = {
    "Aggressive": "Agg_Score",
    "Defensive": "Def_Score",
    "Balanced": "Bal_Score"
}
score_column = playstyle_map[playstyle]

df["Score"] = df[score_column]

# OR-Tools Optimization
def optimize_team(df, salary_cap):
    solver = pywraplp.Solver.CreateSolver('SCIP')
    if not solver:
        st.error("Solver Initialization Failed!")
        return None

    # Create Variables
    x = {i: solver.BoolVar(name=f"x_{i}") for i in df.index}

    # Add Constraints
    solver.Add(solver.Sum(x[i] for i in df.index) == 14)  # Team size: 14 players
    solver.Add(solver.Sum(x[i] * df.loc[i, "Salary"] for i in df.index) <= salary_cap)  # Salary cap

    # Minimum players per position
    for pos in df["Pos"].unique():
        indices = df[df["Pos"] == pos].index
        solver.Add(solver.Sum(x[i] for i in indices) >= 3)

    # Guards constraint
    guard_indices = df[df["Pos"] == "G"].index
    solver.Add(solver.Sum(x[i] for i in guard_indices) >= 5)  # Min 5 guards
    solver.Add(solver.Sum(x[i] for i in guard_indices) <= 7)  # Max 7 guards

    # Objective Function
    objective = solver.Objective()
    for i in df.index:
        objective.SetCoefficient(x[i], df.loc[i, "Score"])
    objective.SetMaximization()

    # Solve
    status = solver.Solve()
    if status == pywraplp.Solver.OPTIMAL:
        selected_indices = [i for i in df.index if x[i].solution_value() > 0.5]
        return df.loc[selected_indices].sort_values(by="Salary", ascending=False)
    else:
        st.warning("No optimal solution found!")
        return None

# Perform optimization
optimized_team = optimize_team(df, salary_cap)

# Display results
if optimized_team is not None:
    optimized_team.insert(0, 'Rank', range(1, len(optimized_team) + 1))
    optimized_team = optimized_team.sort_values(by="Salary", ascending=False).reset_index(drop=True)
    st.subheader(f"Optimized Team ({playstyle}, Salary Cap: €{salary_cap:,})")
    st.table(optimized_team[["Rank", "Player", "Pos", "Score", "Salary"]])
else:
    st.info("Select your preferences to see the results!")
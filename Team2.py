import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt

class EuropeanFootballAnalysis:
    def __init__(self, filename = None):
        self.file = filename
        
        # Container for Raw data
        self.raw_data = None 
        
        # Container for cleaned data
        self.cleaned_data = None
        
        
        # Mapping dictionaries      
        self.position_map = {
            'GK': 'Goalkeeper',
            'DF': 'Defender', 
            'MF': 'Midfielder',
            'FW': 'Forward'
        }
        
        self.colors = {
            'Premier League': '#38003c',
            'La Liga': '#eda132',
            'Bundesliga': '#d3010c',
            'Serie A': '#008fd8',
            'Ligue 1': '#091c3e'
        }

        self.team_colors = {
          # Premier League
          'Manchester City': '#6CABDD',
          'Arsenal': '#EF0107',
          'Liverpool': '#C8102E',
          'Manchester United': '#DA291C',
          'Tottenham': '#FFFFFF',
          'Chelsea': '#034694',
          'Newcastle United': '#241F20',
          'Brighton': '#0057B8',
          'Aston Villa': '#95BFE5',
          'West Ham': '#7A263A',
          
          # La Liga  
          'Real Madrid': '#FEBE10',
          'Barcelona': '#A50044',
          'Atletico Madrid': '#CB3524',
          'Sevilla': '#FFFFFF',
          'Real Betis': '#00954C',
          'Villarreal': '#FFE667',
          'Real Sociedad': '#00529F',
          'Athletic Club': '#EE2523',
          
          # Serie A
          'Inter': '#010E80',
          'Milan': '#FB090B',
          'Juventus': '#000000',
          'Napoli': '#12A0D7',
          'Roma': '#8E1F2F',
          'Lazio': '#FFFFFF',
          'Atalanta': '#1D5EA8',
          'Fiorentina': '#482E92',
          
          # Bundesliga
          'Bayern Munich': '#0066B3',
          'Dortmund': '#FDE100',
          'RB Leipzig': '#DD0741',
          'Leverkusen': '#E32219',
          'Eintracht Frankfurt': '#E21A23',
          'Wolfsburg': '#65FF00',
          'Freiburg': '#E30613',
          "M'Gladbach": '#000000',
          
          # Ligue 1
          'Paris S-G': '#004170',
          'Marseille': '#00B9F1',
          'Lyon': '#D61C28',
          'Monaco': '#E30613',
          'Lille': '#E21A23',
          'Rennes': '#E21A23',
          'Lens': '#FFDC00',
          'Nice': '#000000'
      }

    def scrape(self):
        """
        Task 1: Read data from the html file and extraction table.
        populates self.raw_data as a pandas DataFrame.
        """
        # Replace with your code
        # Task Number 1
    

        with open(self.file, "r", encoding="utf-8") as football_file:
            html_content = football_file.read()
        soup = BeautifulSoup(html_content, "html.parser")
        table = soup.find("table", id="stats_standard")
        header_rows = table.find("thead").find_all("tr")
    
        columns = []
        last_header_row = header_rows[-1]
        for th in last_header_row.find_all("th"):
            text = th.get_text(strip=True)
            columns.append(text)

        start = columns.index("CrdR") + 1
        for i in range(start, len(columns)-1):
            columns[i] = columns[i] + "/90"

        rows = []
        for tr in table.find("tbody").find_all("tr"):
            row_values = []
            for cell in tr.find_all(["th", "td"]):
                row_values.append(cell.get_text(strip=True))
            rows.append(row_values)
        
        self.raw_data = pd.DataFrame(rows, columns=columns)
        return self.raw_data

        

    def clean_data(self):
        """
        Task 2 & 3: Clean data.
        - Remove special characters from data
        - Convert columns with commas to numeric data
        - Parse Nation: extract 3-letter code from flag images or text
        - Parse Position: extract primary position and add a new column to data
        - Convert Columns to numbers based on the type of data
        - Populates self.cleaned_data as a pandas DataFrame.
        """
        # Task Number 2 and 3
        df = self.raw_data.copy()


        df = df[df["Rk"] !="Rk"]
        for column in df.columns:
            df[column] = df[column].str.replace("*","")
            df[column] = df[column].str.strip()

        df["Min"] = df["Min"].str.replace(",","")

        df = df.replace("", np.nan)

        number_columns = ["Rk", "Age", "Born", "MP", "Starts", "Min", "90s",
                          "Gls", "Ast", "G+A", "G-PK", "PK", "PKatt", "CrdY", "CrdR",
                          "Gls/90", "Ast/90", "G+A/90", "G-PK/90", "G+A-PK/90"]
        for column in number_columns:
            df[column] = pd.to_numeric(df[column], errors="coerce")
            df[column] = df[column].fillna(0)
        df["Min"] = df["Min"].astype(int)
        df = df.fillna("Unknown")

        df["Nations"] = df["Nation"].str[-3:]

        df["League"] = df["Comp"].str.lstrip("abcdefghijklmnopqrstuvwxyz")

        df["Primary_Position"] = df["Pos"].apply(self._extract_primary_position)

        self.cleaned_data = df
        return self.cleaned_data        

        


    def _extract_primary_position(self, pos_str):
        """
        Helper for Task 3: Extract primary position from codes like 'FWMF' or 'DF,MF'
        """
        # Task Number 3
        if type(pos_str) != str:
            return "unknown"

        if "," in pos_str:
            first = pos_str.split(",")[0].strip()
        else:
            first = pos_str[:2]
        if first in ["GK", "DF", "MF", "FW"]:
            return first
        return "Unknown"

        
        

    def add_derived_metrics(self):
        """
        Task 4: Add Minutes_per_Game, and Goal_Contribution_Rate. The derived metrics should be added as new columns to self.cleaned_data.
        """
        # Task Number 4
        df = self.cleaned_data
        df["Mins_Per_Game"] = df["Min"]/df["MP"]
        df["Goal_Contr_Rate"] = df["G+A"] / df["90s"]
        df = df.replace([np.inf, -np.inf], np.nan)
        df['Mins_Per_Game'] = df['Mins_Per_Game'].fillna(0)
        df["Goal_Contr_Rate"]= df["Goal_Contr_Rate"].fillna(0)

        self.cleaned_data = df
        return self.cleaned_data

    def find_top_scorer(self):
        """
        Task 5: Find the player(s) with the highest number of goals. Return player name, team, goals, league.
        """
        
        df = self.cleaned_data
        # Highest goal total in the whole dataset (a single number)
        max_goals = df["Gls"].max()
        # Boolean filter: keeps every row where Gls equals the maximum.
        # Using == instead of idxmax() means tied players will be included.
        top_scorer = df[df["Gls"] == max_goals]
        # Double brackets select several columns; reset_index renumbers the rows from 0. 
        return top_scorer[["Player", "Squad", "Gls", "League"]].reset_index(drop=True)
        

    def find_playmaker(self):
        """
        Task 6: Find the player(s) with the highest number of assists. Return player name, team, assists, league.
        """
        df = self.cleaned_data
        # Highest assist total in the whole dataset (a single number)
        max_assists = df["Ast"].max()
        # Keep all players who reached that total (ties included)
        top_playmakers = df[df["Ast"] == max_assists]
        return top_playmakers[["Player", "Squad", "Ast", "League"]].reset_index(drop=True)
    

    def find_ironman(self):
        """
        Task 7: Find the player(s) with the highest number of minutes played. Return player name, team, minutes played, matches played.
        """
        df = self.cleaned_data
        # Most minutes played by any player in the dataset (a single number)
        max_minutes = df["Min"].max()
        # Several players can play every minute of a 38-game season, so we keep all players who reached that total (ties included)
        ironmen = df[df["Min"] == max_minutes]
        return ironmen[["Player", "Squad", "Min", "MP"]].reset_index(drop=True)
    

    def find_efficient_striker(self):
        """
        Task 8: Find the forward(s) who is most efficent (most goals per minutes played) and has played more than 1000 minutes. Return player name, team, goals, minutes played, goals per minute.
        """
        df = self.cleaned_data
        # Filter for forwards with more than 1000 minutes played 
        # .copy() is used to avoid SettingWithCopyWarning when creating new columns in the filtered DataFrame
        forwards = df[(df["Primary_Position"] == "FW") & (df["Min"] > 1000)].copy()
        # Calculate goals per minute for each forward
        forwards["Goals_per_Minute"] = forwards["Gls"] / forwards["Min"]
        # Find the forward(s) with the highest goals per minute
        max_efficiency = forwards["Goals_per_Minute"].max()
        efficient_forwards = forwards[forwards["Goals_per_Minute"] == max_efficiency]
        return efficient_forwards[["Player", "Squad", "Gls", "Min", "Goals_per_Minute"]].reset_index(drop=True)


    def find_most_disciplined(self):
        """
        Task 9: Find the player(s) with the lowest number of yellow cards and red cards after playing for 90 minutes. The total minutes played should be more than 1000 minutes. Return player name, team, yellow cards, red cards, discipline score (cards per 90), position.
        """
        df = self.cleaned_data
        # Filter for players with more than 1000 minutes played
        players = df[df["Min"] > 1000].copy()
        # Calculate discipline score (cards per 90 minutes)
        players["Discipline_Score"] = (players["CrdR"] + players["CrdY"] * 0.5) / players["90s"]
        # Find the player(s) with the lowest discipline score
        best = players[players["Discipline_Score"] == players["Discipline_Score"].min()]
        # Sort the tied players by minutes, so those with the largest come first
        best = best.sort_values(by="Min", ascending=False)
        return best[["Player", "Squad", "CrdY", "CrdR", "Discipline_Score", "Primary_Position"]].reset_index(drop=True)

    def compare_leagues_attack(self):
        """
        Task 10: Compare the average number of goals scored by each league. Return a bar chart visualization and the average goals per 90 for each league.
        """
        df = self.cleaned_data
        df = df[df["Min"] > 90] #Only keeps rows with at least 90 mins

        avg_goals = df.groupby("League")["Gls/90"].mean().sort_values(ascending=False)

        
        grouped = df.groupby("League")
        weighted = (grouped["Gls"].sum() / grouped["90s"].sum()).reindex(avg_goals.index) #Weighted check + total goals / totals 90s per league

        fig, ax = plt.subplots(figsize=(9, 6))
        bar_colors = [self.colors.get(league, "gray") for league in avg_goals.index] #Creating bar colors, default = gray

        bars = ax.bar(avg_goals.index, avg_goals.values, color=bar_colors)
        ax.bar_label(bars, fmt = "%.3f") #Print each bar's values on top
        ax.set_title("Average Goals per 90 Minutes by League")
        ax.set_xlabel("League")
        ax.set_ylabel("Average Goals per 90")

        plt.tight_layout()

        data = {
            "avg_goals_per_90": avg_goals.round(3).to_dict(),
            "weighted_avg_goals_per_90": weighted.round(3).to_dict(),
            "players_counted": grouped.size().reindex(avg_goals.index).to_dict() #Counts players per league, reindex keeps the same league order
        }

        return fig, data #Returned for driver can show

    def compare_position_productivity(self):
        """
        Task 11: Compare the average number of goals scored and assists by each position.
        Return a plot with two subplots and the data dictionary for the plots:
          (1) Average G+A by Primary Position
          (2) Average G+A by Primary Position per League
        """

        df = self.cleaned_data
        df = df[(df["Min"] >= 90) & (df["Primary_Position"] != "Unknown")] #Only keep rows with at least 90 mins and known positions

        order = ["GK", "DF", "MF", "FW"] #Defense to attack order for plotting

        overall = df.groupby("Primary_Position")["G+A"].mean().reindex(order)
        by_league = (df.groupby(["Primary_Position", "League"])["G+A"].mean().unstack().reindex(order)) #Unstacks league to columns, reindex keeps the same position order

        labels = [self.position_map[p] for p in order] #Sets labels to be in order of defense to attack

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6)) #Sets 1 row with 2 sets of axes

        bars = ax1.bar(labels, overall.values, color = "gray")
        ax1.bar_label(bars, fmt = "%.2f")
        ax1.set_title("Average G+A by position")
        ax1.set_xlabel("Position")
        ax1.set_ylabel("Average G+A")

        by_league.plot(kind="bar", ax=ax2, color=[self.colors.get(l, "gray") for l in by_league.columns])

        ax2.set_xticklabels(labels, rotation = 0) #Swaps code for full names
        ax2.set_title("Average G+A by position per league")
        ax2.set_xlabel("Position")
        ax2.set_ylabel("Average G+A")
        ax2.legend(title="League")

        plt.tight_layout()

        data = {
            "overall": overall.round(2).to_dict(),
            "by_league": by_league.round(2).to_dict()
        }

        return fig, data #Returns for driver to show

    def age_curve_analysis(self):
        """
        Task 12: Compare the player age vs Goal Contribution Rate. Return a scatter plot visualization with a trend line and data.
        """
        df = self.cleaned_data
        df = df[(df["Age"] > 0) & (df["Min"] >= 450)] #drop if age is not positive or minutes played is less than 450

        x = df["Age"].to_numpy()
        y = df["Goal_Contr_Rate"].to_numpy()

        corr = np.corrcoef(x, y)[0, 1] #correlation coefficient returns a 2x2 matrix for x-y entry
        slope, intercept = np.polyfit(x, y, 1) #y = mx + b
        a, b, c = np.polyfit(x, y, 2) #y = ax^2 + bx + c
        peak_age = -b / (2 * a) if a < 0 else None # Only exists if curve is downward facing

        fig, ax = plt.subplots(figsize=(10, 6))
        ax.scatter(x, y, alpha=0.4, color="gray", label="Players") #Shows desity 

        xs = np.linspace(x.min(), x.max(), 100) #Plots 100 points between min and max age for trend lines
        ax.plot(xs, slope * xs + intercept, color="red", linewidth=2, label="Linear Trend")
        ax.plot(xs, a * xs ** 2 + b * xs + c, color="green", linewidth=2, linestyle="--", label="Quadratic Trend")
        
        ax.set_title("Age vs Goal Contribution Rate (G+A per 90)")
        ax.set_xlabel("Age")
        ax.set_ylabel("Goal Contribution Rate (G+A per 90)")
        ax.legend()

        plt.tight_layout()

        data = { #Converts numpy types to python types
            "correlation": round(float(corr), 3),
            "linear_slope": round(float(slope), 4),
            "Linear_intercept": round(float(intercept), 4),
            "peak_age_quadratic": None if peak_age is None else round(float(peak_age), 1),
            "players_used": int(len(df))
        }

        return fig, data #Return for driver to show


    def league_defensive_discipline(self):
        """
        Task 13
        Plan: 
        a. Filter the cleaned dataset for defenders Primary_Position == 'DF' with at > 90 minutes played time.
        b. Group the data by each league and calculate the mean of CrdY (yellow cards) and 'CrdR' (red cards) and per 90 card rates.
        c. Create two subplots, subplot 1 with two grouped bars per league yellow vs red cards and subplot 2 comparing cards per 90 mins.
        d. Return the figure and the dictionary containing the defense statistics.
        """
        df = self.cleaned_data
        defenders = df[(df["Primary_Position"] == "DF") & (df["Min"] >= 90)].copy()

        defenders["CrdY/90"] = defenders["CrdY"] / defenders["90s"]
        defenders["CrdR/90"] = defenders["CrdR"] / defenders["90s"]

        avg_cards = defenders.groupby("League")[["CrdY", "CrdR"]].mean().sort_values(by="CrdY", ascending=False)
        avg_cards_per90 = defenders.groupby("League")[["CrdY/90", "CrdR/90"]].mean().reindex(avg_cards.index)

        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

        x = np.arange(len(avg_cards.index))
        width = 0.35

        # Subplot 1: Two bars per league (Average Yellow Cards and Average Red Cards)
        bars_y1 = ax1.bar(x - width / 2, avg_cards["CrdY"], width, label="Yellow Cards", color="#f1c40f")
        bars_r1 = ax1.bar(x + width / 2, avg_cards["CrdR"], width, label="Red Cards", color="#e74c3c")
        ax1.bar_label(bars_y1, fmt="%.2f", padding=2)
        ax1.bar_label(bars_r1, fmt="%.2f", padding=2)
        ax1.set_title("Average Yellow & Red Cards per Defender by League")
        ax1.set_xlabel("League")
        ax1.set_ylabel("Average Cards")
        ax1.set_xticks(x)
        ax1.set_xticklabels(avg_cards.index)
        ax1.legend()

        # Subplot 2: Two bars per league (Average Yellow & Red Cards per 90 mins)
        bars_y2 = ax2.bar(x - width / 2, avg_cards_per90["CrdY/90"], width, label="Yellow Cards / 90", color="#f1c40f")
        bars_r2 = ax2.bar(x + width / 2, avg_cards_per90["CrdR/90"], width, label="Red Cards / 90", color="#e74c3c")
        ax2.bar_label(bars_y2, fmt="%.3f", padding=2)
        ax2.bar_label(bars_r2, fmt="%.3f", padding=2)
        ax2.set_title("Average Defensive Cards per 90 Minutes by League")
        ax2.set_xlabel("League")
        ax2.set_ylabel("Average Cards per 90")
        ax2.set_xticks(x)
        ax2.set_xticklabels(avg_cards_per90.index)
        ax2.legend()

        plt.tight_layout()

        data = {
            "avg_cards": avg_cards.round(3).to_dict(),
            "avg_cards_per_90": avg_cards_per90.round(3).to_dict()
        }

        return fig, data    

    def youth_vs_veteran(self):
        """
        Task 14

        Plan:
        a. Filter the dataset to ignore goalkeepers 'GK' and 'Unknown' positions and keep players with >= 90 minutes played.
        b. Filter for Youth 0 < Age <= 21 and veteran Age >= 32 players and label them in a new 'Age_Group' column.
        c. Assign a position performance metric. Mins_Per_Game for defense DF, Goal_Contr_Rate for Midfielders MF and Gls/90 for forwards FW.
        d. Group by League and Age_Group for each position and plot a grouped bar chart on each subplot.
        e. Return the figure and the dictionary of the grouped performace for each position.
        """
        df = self.cleaned_data
        df = df[(df["Min"] >= 90) & (df["Primary_Position"].isin(["DF", "MF", "FW"]))].copy()

        youth_mask = (df["Age"] > 0) & (df["Age"] <= 21)
        veteran_mask = df["Age"] >= 32
        df = df[youth_mask | veteran_mask].copy()

        df["Age_Group"] = np.where(df["Age"] <= 21, "Youth (<=21)", "Veteran (>=32)")

        position_configs = [
            ("DF", "Mins_Per_Game", "Defenders: Avg Minutes per Game"),
            ("MF", "Goal_Contr_Rate", "Midfielders: Avg Goal Contr. Rate (G+A/90)"),
            ("FW", "Gls/90", "Forwards: Avg Goals per 90")
        ]

        fig, axes = plt.subplots(1, 3, figsize=(18, 6))
        data = {}

        age_order = ["Youth (<=21)", "Veteran (>=32)"]

        for ax, (pos, metric, title) in zip(axes, position_configs):
            pos_df = df[df["Primary_Position"] == pos]
            grouped = (
                pos_df.groupby(["League", "Age_Group"])[metric]
                .mean()
                .unstack()
                .reindex(columns=age_order)
                .fillna(0)
            )

            grouped.plot(kind="bar", ax=ax, color=["#3498db", "#e67e22"], width=0.7)
            for container in ax.containers:
                ax.bar_label(container, fmt="%.2f", fontsize=8, padding=2)

            ax.set_title(title)
            ax.set_xlabel("League")
            ax.set_ylabel(metric)
            ax.tick_params(axis="x", rotation=30)
            if pos == "DF":
                ax.legend(title="Age Group", fontsize=7.5, title_fontsize=7.5)
            else:
                ax.legend(title="Age Group")

            data[pos] = grouped.round(3).to_dict()

        plt.tight_layout()

        return fig, data

    def data_quality_report(self):
        """
        Task 15: Generate a report on data quality.
        """
        # Replace with your code
        pass

    def handle_transfers(self):
        """
        Task 16: Identify players with multiple entries and aggregate. Strategy: Sum counting stats, weighted average for rate stats.
        """
        # Replace with your code
        pass

    def __drawRadarChart(self, ax, player_data, player_name, color, attributes, all_players_data=None):
        """
        Helper method: Draws a single radar chart polygon on given axes.
        
        Input:
            ax: Matplotlib axes object (polar projection)
            player_data: Dict or Series of attribute values
            player_name: String for legend label
            color: Color string for the polygon
            attributes: List of attribute names (columns) to plot
            all_players_data: DataFrame of all players for normalization context
        """
        # Replace with your code
        pass

    def compare_players_radar(self, player1_name, player2_name, attributes, 
                             normalization='minmax', figsize=(10, 10), save_path=None):
        """
        Task 17: Compare two players using a radar chart across specified attributes.
        
        Input:
            player1_name: String, exact name of first player (e.g., "Erling Haaland")
            player2_name: String, exact name of second player (e.g., "Kylian Mbappé")
            attributes: List of column names to compare (e.g., ['Gls', 'Ast', 'xG', 'xAG', 'Shots'])
            normalization: 'minmax' (0-100 scale), 'raw' (actual values), or 'percentile' (league percentile)
            figsize: Tuple for figure size
            save_path: Optional path to save figure
            
        Output: Displays radar chart (and saves if path provided). Returns comparison DataFrame.
        """
        # Replace with your code
        pass

    def _aggregate_player_stats(self, player_df):
        """Helper to sum stats for players with multiple rows (transfers)"""
        # Replace with your code
        pass


if __name__ == "__main__":
    # Driver code to show output for the questions.
    analysis = EuropeanFootballAnalysis("Player_Stats.html")
    raw = analysis.scrape()
    print("\nTask 1")
    print(raw.head())

    clean = analysis.clean_data()
    print("\nTask 2 & 3")
    print(clean["Primary_Position"].value_counts())
    print(clean.head())
    
    clean = analysis.add_derived_metrics()
    print("\nTask 4")
    print(clean.head())

    print("\nTask 5")
    print(analysis.find_top_scorer())

    print("\nTask 6")
    print(analysis.find_playmaker())

    print("\nTask 7")
    print(analysis.find_ironman())

    print("\nTask 8")
    print(analysis.find_efficient_striker())

    print("\nTask 9")
    print(analysis.find_most_disciplined())

    fig10, task10_data = analysis.compare_leagues_attack()
    fig10.savefig("task10_leagues.png")
    print("\nTask 10 saved as task10_leagues.png")
    print(task10_data)

    fig11, task11_data = analysis.compare_position_productivity()
    fig11.savefig("task11_positions.png")
    print("\nTask 11 saved as task11_positions.png")
    print(task11_data)

    fig12, task12_data = analysis.age_curve_analysis()
    fig12.savefig("task12_age_curve.png")
    print("\nTask 12 saved as task12_age_curve.png")
    print(task12_data)

    fig13, task13_data = analysis.league_defensive_discipline()
    fig13.savefig("task13_defensive_discipline.png")
    print("\nTask 13 saved as task13_defensive_discipline.png")
    print(task13_data)

    fig14, task14_data = analysis.youth_vs_veteran()
    fig14.savefig("task14_youth_vs_veteran.png")
    print("\nTask 14 saved as task14_youth_vs_veteran.png")
    print(task14_data)

    plt.show()

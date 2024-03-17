import plotly
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
import yaml
import json
import config
import os

with open(os.path.join(config.BASE_DIR, 'web/data/teams.yaml'), "r") as f:
    teamnames = yaml.load(f, Loader=yaml.Loader)


def overall_event(df):
    df["teamNumberB"] = df.teamNumber
    avgs = df.groupby(["teamNumber"]).mean().round(2)
    avgs.reset_index(inplace=True)
    print(avgs.head())
    avgs["teamName"] = avgs.teamNumber.apply(lambda x: teamnames[int(x)])
    print(avgs.head())

    fig = px.scatter(
        avgs,
        x="telePoints",
        y="autoPoints",
        hover_data=[
            "teamName",
            "telePoints",
            "autoPoints",
            "climbPoints",
            "rating",
        ],
        size="climbPoints",
        labels={
            "telePoints": "teleop points",
            "autoPoints": "auto points",
            "climbPoints": "climb points",
            "teamName": "team name",
            "rating": "rating",
        },
        color="rating",
        color_continuous_scale=px.colors.sequential.Plotly3,
    )

    fig.update_layout(
        title={
            "text": "Eventwide performance by team",
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        width=1500,
        height=700,
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color="#777"),
        xaxis=dict(linecolor="#777", gridcolor="#777", showgrid=True),
        yaxis=dict(
            linecolor="#777",
            gridcolor="#777",
            showgrid=True,
        ),
    )

    fig.update_traces(marker_sizemin=5)

    fig.update_xaxes(
        showspikes=True,
        spikecolor="#777",
        spikesnap="cursor",
        spikemode="across",
        spikedash="dot",
    )
    fig.update_yaxes(showspikes=True, spikecolor="#777", spikedash="dot")
    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)

    return plot_json


def by_team(df):
    df = df.sort_values("matchNum")

    fig = make_subplots(rows=3, cols=1, shared_xaxes=True, vertical_spacing=0.125)

    fig.add_trace(
        go.Scatter(
            x=list(df["matchNum"]),
            y=list(df["autoPoints"]),
            name="auto points",
            hovertemplate="Match number: %{x}<br>Auto points: %{y}<br>",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=list(df["matchNum"]),
            y=list(df["telePoints"]),
            name="tele points",
            hovertemplate="Match number: %{x}<br>Teleop points: %{y}<br>",
        ),
        row=2,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=list(df["matchNum"]),
            y=list(df["climbPoints"]),
            name="endgame level",
            hovertemplate="Match number: %{x}<br>Climb level=: %{y}<br>",
        ),
        row=3,
        col=1,
    )

    fig.update_layout(
        title={
            "text": "Team performance by each match",
            "y": 0.9,
            "x": 0.5,
            "xanchor": "center",
            "yanchor": "top",
        },
        width=1500,
        height=550,
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color="#777"),
    )
    fig.update_xaxes(
        linecolor="#777",
        gridcolor="#777",
        showspikes=True,
        spikesnap="cursor",
        spikemode="across",
        spikecolor="#777",
        spikedash="dot",
    )
    fig.update_xaxes(title_text="match number", row=3, col=1)

    fig.update_yaxes(
        linecolor="#777",
        gridcolor="#777",
        showspikes=True,
        spikecolor="#777",
        spikedash="dot",
    )
    fig.update_yaxes(title_text="auto cargo", row=1, col=1)
    fig.update_yaxes(title_text="teleop cargo", row=2, col=1)
    fig.update_yaxes(title_text="endgame level", row=3, col=1)

    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return plot_json


def alliance_graph(red_dfs, blue_dfs):
    layout = go.Layout(polar=dict(radialaxis=dict(visible=True, range=[0, 1])))

    fig = make_subplots(
        rows=2,
        cols=4,
        vertical_spacing=0.25,
        specs=[[{"type": "polar"}] * 4] * 2,
        horizontal_spacing=0.05,
    )
    fields = [
        "autoPointsNormalized",
        "telePointsNormalized",
        "climbPointsNormalized",
        "ratingScoreNormalized",
        "cyclesNormalized",
    ]

    labels = ["auto", "teleop", "climb", "rating", "cycles"]
    reds = ["crimson", "orangered", "tomato"]
    blues = ["dodgerblue", "royalblue", "steelblue"]

    col = 2
    color = 0

    fig.add_trace(
        go.Scatterpolar(
            r=[round(red_dfs[0][field].mean()) + round(red_dfs[1][field].mean()) + round(red_dfs[2][field].mean()) for field in fields],
            theta=labels,
            fill="toself",
            name="Red",
            text="Red",
            line=dict(color="crimson"),
            marker=dict(color="crimson")
        ),
        row=1,
        col=1
    )

    for red_df in red_dfs:
        fig.add_trace(
            go.Scatterpolar(
                r=[round(red_df[field].mean(), 2) for field in fields],
                theta=labels,
                fill="toself",
                name=str(round(red_df["teamNumber"].mean())),
                text=str(round(red_df["teamNumber"].mean())),
                line=dict(color=reds[color]),
                marker=dict(color=reds[color])
            ),
            row=1,
            col=col,
        )

        # fig.add_trace(
        #     go.Scatterpolar(
        #         r=[round(red_df[field].mean(), 2) for field in fields],
        #         theta=labels,
        #         fill="toself",
        #         name=str(round(red_df["teamNumber"].mean())),
        #         line=dict(color=reds[color]),
        #         marker=dict(color=reds[color])
        #     ),
        #     row=1,
        #     col=1,
        # )

        col += 1

    col = 2
    color = 0

    fig.add_trace(
        go.Scatterpolar(
            r=[round(blue_dfs[0][field].mean()) + round(blue_dfs[1][field].mean()) + round(blue_dfs[2][field].mean()) for field in fields],
            theta=labels,
            fill="toself",
            name="Blue",
            text="Blue",
            line=dict(color="dodgerblue"),
            marker=dict(color="dodgerblue")
        ),
        row=2,
        col=1
    )

    for blue_df in blue_dfs:
        fig.add_trace(
            go.Scatterpolar(
                r=[round(blue_df[field].mean(), 2) for field in fields],
                theta=labels,
                fill="toself",
                name=str(round(blue_df["teamNumber"].mean())),
                text=str(round(blue_df["teamNumber"].mean())),
                line=dict(color=blues[color]),
                marker=dict(color=blues[color])
            ),
            row=2,
            col=col,
        )

        # fig.add_trace(
        #     go.Scatterpolar(
        #         r=[round(blue_df[field].mean(), 2) for field in fields],
        #         theta=labels,
        #         fill="toself",
        #         name=str(round(blue_df["teamNumber"].mean())),
        #         line=dict(color=blues[color]),
        #         marker=dict(color=blues[color])
        #     ),
        #     row=2,
        #     col=1,
        # )

        col += 1

    polar_layouts = {"polar" + str(i): dict(radialaxis=dict(visible=True, range=[0, 1])) if i%4 != 1 else dict(radialaxis=dict(visible=True, range=[0, 3])) for i in range(1, 9)}

    titles = ["Red", str(round(red_dfs[0]["teamNumber"].mean())), str(round(red_dfs[1]["teamNumber"].mean())), str(round(red_dfs[2]["teamNumber"].mean())), "Blue", str(round(blue_dfs[0]["teamNumber"].mean())), str(round(blue_dfs[1]["teamNumber"].mean())), str(round(blue_dfs[2]["teamNumber"].mean()))]
    title_layouts = {"title" + str(i+1): dict(text=titles[i]) for i in range(len(titles))}

    fig.update_layout(
        width=1500,
        height=650,
        paper_bgcolor="rgba(255,255,255,0)",
        plot_bgcolor="rgba(255,255,255,0)",
        font=dict(color="#777"),
        showlegend=False,
        **polar_layouts
                )

    plot_json = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    return plot_json

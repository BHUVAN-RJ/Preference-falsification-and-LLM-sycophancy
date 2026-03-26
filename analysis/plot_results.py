import pandas as pd
import matplotlib.pyplot as plt
import sys


def plot_falsification_gap(csv_path: str, trigger_round: int = 6):
    df = pd.read_csv(csv_path)

    fig, axes = plt.subplots(2, 2, figsize=(14, 10))

    # Plot 1: Gap per agent over time
    ax = axes[0, 0]
    for agent_id in df["agent_id"].unique():
        agent_data = df[df["agent_id"] == agent_id]
        ax.plot(
            agent_data["round"],
            agent_data["falsification_gap"],
            marker="o",
            label=agent_id,
            markersize=4,
        )
    ax.axvline(x=trigger_round, color="red", linestyle="--", alpha=0.7, label="Trigger")
    ax.set_xlabel("Round")
    ax.set_ylabel("Falsification Gap |private - public|")
    ax.set_title("Falsification Gap Over Time")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Plot 2: Private vs Public (population mean)
    ax = axes[0, 1]
    by_round = (
        df.groupby("round")
        .agg(mean_private=("private_score", "mean"), mean_public=("public_score", "mean"))
        .reset_index()
    )
    ax.plot(by_round["round"], by_round["mean_private"], "b-o", label="Mean Private Belief", markersize=5)
    ax.plot(by_round["round"], by_round["mean_public"], "r-s", label="Mean Public Expression", markersize=5)
    ax.axvline(x=trigger_round, color="gray", linestyle="--", alpha=0.7, label="Trigger")
    ax.fill_between(
        by_round["round"],
        by_round["mean_private"],
        by_round["mean_public"],
        alpha=0.15,
        color="purple",
    )
    ax.set_xlabel("Round")
    ax.set_ylabel("Score (-5 to +5)")
    ax.set_title("Private Belief vs Public Expression (Population Mean)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Plot 3: Scatter final round
    ax = axes[1, 0]
    for agent_id in df["agent_id"].unique():
        agent_data = df[df["agent_id"] == agent_id]
        last = agent_data.iloc[-1]
        ax.scatter(last["private_score"], last["public_score"], s=100, zorder=5)
        ax.annotate(
            agent_id,
            (last["private_score"], last["public_score"]),
            fontsize=8,
            ha="center",
            va="bottom",
        )
    ax.plot([-5, 5], [-5, 5], "k--", alpha=0.3, label="No falsification")
    ax.set_xlabel("Private Score (final round)")
    ax.set_ylabel("Public Score (final round)")
    ax.set_title("Private vs Public (Final Round)")
    ax.set_xlim(-6, 6)
    ax.set_ylim(-6, 6)
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    # Plot 4: Mean gap bar chart
    ax = axes[1, 1]
    gap_by_round = df.groupby("round")["falsification_gap"].mean().reset_index()
    colors = ["steelblue" if r < trigger_round else "coral" for r in gap_by_round["round"]]
    ax.bar(gap_by_round["round"], gap_by_round["falsification_gap"], color=colors, alpha=0.8)
    ax.axvline(x=trigger_round - 0.5, color="red", linestyle="--", alpha=0.7)
    ax.set_xlabel("Round")
    ax.set_ylabel("Mean Falsification Gap")
    ax.set_title("Population Mean Falsification Gap")
    ax.grid(True, alpha=0.3, axis="y")

    plt.tight_layout()
    out_path = csv_path.replace(".csv", "_plots.png")
    plt.savefig(out_path, dpi=150, bbox_inches="tight")
    print(f"Saved plots to {out_path}")
    plt.show()


if __name__ == "__main__":
    csv_path = sys.argv[1] if len(sys.argv) > 1 else "results/run_001.csv"
    trigger = int(sys.argv[2]) if len(sys.argv) > 2 else 6
    plot_falsification_gap(csv_path, trigger)

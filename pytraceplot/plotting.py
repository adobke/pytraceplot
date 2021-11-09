import matplotlib.patches as mpatches
from matplotlib import cm
from matplotlib.transforms import Bbox, TransformedBbox

TRACE_LINE_HEIGHT = 0.6


def traceplot(ax, task_data):
    cpus = {}

    legend_entries = []
    min_time = None
    max_time = None
    for idx, (task_name, task_data) in enumerate(task_data):
        color = cm.tab10(idx)
        legend_entries.append(mpatches.Patch(color=color, label=task_name))
        for cpu, (start, end) in task_data:
            min_time = min(start, start if min_time is None else min_time)
            max_time = max(end, end if max_time is None else max_time)
            if cpu not in cpus:
                cpus[cpu] = []
            cpus[cpu].append((task_name, start, end - start, color))

    for idx, cpu in enumerate(reversed(sorted(cpus.keys()))):
        data = cpus[cpu]
        for (name, start, length, color) in data:
            ax.add_patch(
                mpatches.FancyBboxPatch(
                    (start, idx - TRACE_LINE_HEIGHT / 2),
                    length,
                    TRACE_LINE_HEIGHT,
                    boxstyle="round,pad=0,rounding_size=0.25",
                    ec="none",
                    fc=color,
                    mutation_aspect=0.5,
                )
            )
            box = TransformedBbox(
                Bbox.from_bounds(
                    start, idx - TRACE_LINE_HEIGHT / 2, length, TRACE_LINE_HEIGHT
                ),
                ax.transData,
            )
            ax.annotate(
                name,
                (start + length / 2, idx + 0.01),
                ha="center",
                va="center",
                clip_box=box,
                fontsize=14,
                color="white",
            )

    ax.set_yticks([idx for idx in range(len(cpus))])
    ax.set_yticklabels(list(reversed(sorted(cpus.keys()))))
    ax.set_ylabel("Cpu")
    ax.grid(axis="y", linestyle="-", linewidth="2", color="gray")
    ax.set_axisbelow(True)
    ax.set_ylim(-0.5, len(cpus) - 0.5)
    ax.set_xlim(min_time, max_time)

    ax.xaxis.set_major_formatter(lambda val, pos: val / 1e9)
    return ax


def parse_ftrace(input_text):
    return []

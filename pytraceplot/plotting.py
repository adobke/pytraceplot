from dataclasses import dataclass

import matplotlib.patches as mpatches
from matplotlib import cm
from matplotlib.transforms import Bbox, TransformedBbox

TRACE_LINE_HEIGHT = 0.6


def traceplot(ax, events, plot_duration=None):
    # legend_entries = []
    # for idx, (task_name, task_data) in enumerate(task_data):
    #    color = cm.tab10(idx)
    #    legend_entries.append(mpatches.Patch(color=color, label=task_name))
    #    for cpu, (start, end) in task_data:
    #        min_time = min(start, start if min_time is None else min_time)
    #        max_time = max(end, end if max_time is None else max_time)
    #        if cpu not in cpus:
    #            cpus[cpu] = []
    #        cpus[cpu].append((task_name, start, end - start, color))

    colors = {}
    last_process_event_on_cpu = {}

    min_time = None
    max_time = None

    def add_event(event, end_time):
        start_time = event.timestamp - min_time
        event_length = (end_time - min_time) - start_time
        event_y_position = event.cpu - TRACE_LINE_HEIGHT / 2

        ax.add_patch(
            mpatches.FancyBboxPatch(
                (start_time, event_y_position),
                event_length,
                TRACE_LINE_HEIGHT,
                boxstyle="round,pad=0,rounding_size=0.25",
                ec="none",
                fc=event.color,
                mutation_aspect=0.5,
            )
        )
        box = TransformedBbox(
            Bbox.from_bounds(
                start_time, event_y_position, event_length, TRACE_LINE_HEIGHT
            ),
            ax.transData,
        )
        ax.annotate(
            event.process_name,
            (start_time + event_length / 2, event.cpu),
            ha="center",
            va="center",
            clip_box=box,
            fontsize=14,
            color="white",
        )

    for event in events:
        last_event = last_process_event_on_cpu.get(event.cpu)
        min_time = min(
            event.timestamp, event.timestamp if min_time is None else min_time
        )
        max_time = max(
            event.timestamp, event.timestamp if max_time is None else max_time
        )

        if event.timestamp - min_time > plot_duration * 1e9:
            break

        if last_event:
            add_event(last_event, event.timestamp)

        if event.process_id == 0:
            last_process_event_on_cpu[event.cpu] = None
            continue

        pid_key = f"{event.process_id}__{event.process_name}"
        if pid_key not in colors:
            colors[pid_key] = cm.tab10(len(colors))
        event.color = colors[pid_key]
        last_process_event_on_cpu[event.cpu] = event

    for event in last_process_event_on_cpu.values():
        if event:
            add_event(event, max_time)

    ax.set_yticks([idx for idx in range(len(last_process_event_on_cpu))])
    ax.set_yticklabels(list(sorted(last_process_event_on_cpu.keys())))
    ax.set_ylabel("Cpu")
    ax.grid(axis="y", linestyle="-", linewidth="2", color="gray")
    ax.set_axisbelow(True)
    ax.set_ylim(len(last_process_event_on_cpu) - 0.5, -0.5)
    ax.set_xlim(0, max_time - min_time)

    ax.xaxis.set_major_formatter(lambda val, pos: val / 1e9)
    return ax


@dataclass
class CpuContextSwitchEvent:
    cpu: int
    timestamp: int
    process_id: int
    process_name: str
    color: any = None


def parse_ftrace(input_text):
    for line in input_text.splitlines():
        if line and line[0] != "#" and "sched_switch" in line:
            metadata, event = line.split(": sched_switch: ", 1)
            metadata, tsc = metadata.rsplit(" ", 1)
            cpu = int(metadata[metadata.index(" [") + 2 : metadata.index("] ")])
            tsc = int(float(tsc) * 1000000000)
            before, after = event.split(" ==> ")

            comm_key = "next_comm="
            pid_key = "next_pid="
            prio_key = "next_prio="
            new_proc_name = after[
                after.index(comm_key) + len(comm_key) : after.index(pid_key) - 1
            ].replace("worker_", "")
            new_pid = int(
                after[after.index(pid_key) + len(pid_key) : after.index(prio_key) - 1]
            )

            yield CpuContextSwitchEvent(cpu, tsc, new_pid, new_proc_name)

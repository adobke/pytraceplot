from unittest import TestCase

from pytraceplot import parse_ftrace


class TestBasicParsing(TestCase):
    def test_parse_sched_switch(self):
        test_input = """\
# tracer: nop
#
# entries-in-buffer/entries-written: 1416/1416   #P:12
#
#                              _-----=> irqs-off
#                             / _----=> need-resched
#                            | / _---=> hardirq/softirq
#                            || / _--=> preempt-depth
#                            ||| /     delay
#           TASK-PID   CPU#  ||||    TIMESTAMP  FUNCTION
#              | |       |   ||||       |         |
          <idle>-0     [000] d... 19527.681163: sched_switch: prev_comm=swapper/0 prev_pid=0 prev_prio=120 prev_state=R ==> next_comm=worker_a next_pid=29823 next_prio=79
        worker_a-29823 [000] d... 19527.681230: sched_switch: prev_comm=worker_a prev_pid=29823 prev_prio=79 prev_state=S ==> next_comm=swapper/0 next_pid=0 next_prio=120
"""
        result = parse_ftrace(test_input)
        self.assertEqual(2, len(result))

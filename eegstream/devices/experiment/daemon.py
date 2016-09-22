import tkinter as tk
from collections import namedtuple

from pylsl import StreamInfo, StreamOutlet

Action = namedtuple('Action', ['id', 'length'])
Paradigm = namedtuple('Paradigm', ['actions', 'id2description'])

class ExperimentRecorder:
    def gui_init(self):
        self.root = tk.Tk()

        self.label = tk.Label(self.root, text="Experiment")
        self.label.pack(side=tk.TOP)

        self.currentActionVar = tk.StringVar(self.root, 'Do\n')
        self.currentActionField = tk.Label(self.root,
                                      textvariable=self.currentActionVar)
        self.currentActionField.pack(side=tk.TOP, expand=tk.TRUE, fill=tk.X)

        self.scheduleVar = tk.StringVar(self.root, 'Schedule\n')
        self.schedule = tk.Label(self.root, textvariable=self.scheduleVar)
        self.schedule.pack(side=tk.TOP)

    def __init__(self, paradigm: Paradigm, stream_outlet: *, time_quant):
        self.actions = paradigm.actions
        self.id2description = paradigm.id2description
        self.time_quant = time_quant

        self.gui_init()

        self.next_action(0)
        self.set_timer()

    def set_timer(self):
        self.root.after(self.time_quant, self.loop)

    def next_action(self, action: int):
        self.current_action = action
        self.current_action_id, self.timer =self.actions[self.current_action]

        self.update_action_field()
        self.update_schedule_field()

    def loop(self):
        self.timer -= self.time_quant / 1000
        if self.timer < 0:
            if self.current_action + 1 < len(self.actions):
                self.next_action(self.current_action + 1)
                self.set_timer()
            else:
                self.update_over()
        else:
            self.set_timer()
            self.update_action_field()

    def update_over(self):
        self.currentActionVar.set('Great job!')

    def update_schedule_field(self):
        new_schedule = []
        for action_id, length in self.actions[self.current_action+1:]:
            description = '{} : {}'.format(self.id2description[action_id],
                                           length)
            new_schedule.append(description)
        self.scheduleVar.set('\n'.join(new_schedule))


    def update_action_field(self):
        text = '{}\n{:<.2}'.format(self.id2description[self.current_action_id],
                                   self.timer)
        self.currentActionVar.set(text)

    def start_mainloop(self):
        self.root.geometry("600x600")
        self.root.mainloop()


if __name__ == '__main__':
    paradigm = Paradigm(actions=[(1, 2.0), (0, 3.0), (2, 2.0)],
                        id2description={0: 'Stay idle',
                                        1: 'Dance',
                                        2: 'Sing'})

    experiment_recorder = ExperimentRecorder(paradigm, time_quant=100)
    experiment_recorder.start_mainloop()
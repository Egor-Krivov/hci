from pylsl import StreamOutlet

from eegstream.devices.experiment.daemon import Paradigm, ExperimentRecorder

if __name__ == '__main__':
    from eegstream.devices import make_stream_info, Experiment

    paradigm = Paradigm(
        actions=[(0, 15.0)] + \
            [(1, 6.0),
            (0, 6.0),
            ] * 10,
        id2description=
        {0: 'Stay idle',
         1: 'Show something'})

    stream_info = make_stream_info(Experiment)
    stream_outlet = StreamOutlet(stream_info)

    experiment_recorder = ExperimentRecorder(paradigm, stream_outlet,
                                             time_quant=10)
    experiment_recorder.start_mainloop()

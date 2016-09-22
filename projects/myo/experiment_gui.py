if __name__ == '__main__':
    from eegstream.devices import make_stream_info, Experiment
    paradigm = Paradigm(actions=[(0, 5.0), (1, 2.0), (0, 3.0), (2, 2.0)],
                        id2description={0: 'Stay idle',
                                        1: 'Dance',
                                        2: 'Sing'})

    stream_info = make_stream_info(Experiment)
    stream_outlet = StreamOutlet(stream_info)

    experiment_recorder = ExperimentRecorder(paradigm, stream_outlet,
                                             time_quant=100)
    experiment_recorder.start_mainloop()
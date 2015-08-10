from pointer import Pointer

import struct
import numpy as np
import nengo

import ipdb

class SpaSimilarity(Pointer):

    def __init__(self, obj, **kwargs):
        super(SpaSimilarity, self).__init__(obj, **kwargs)
        # I'll eventually have to learn how to switch from showing pairs
        # Probably by rebuilding the whole graph
        try:
            target_key = kwargs['target']
        except KeyError:
            target_key = kwargs['args']

        self.labels = obj.outputs[target_key][1].keys
        # I'm not clear on why the +1 is required...
        self.struct = struct.Struct('<%df' % (1 + len(self.labels)))

    # Taken from pointer.py, should I add an if-statement
    # or a threshold property so I don't have to copy the whole system?
    # I'm probably going to use the labels later for dynamic legend stuff
    def gather_data(self, t, x):
        vocab = self.vocab_out
        key_similarity = np.dot(vocab.vectors, x)
        if self.config.show_pairs:
            self.vocab_out.include_pairs = True
            pair_similarity = np.dot(vocab.vector_pairs, x)
            # this probably isn't going to work... but I can't figure out how else to add it?
            key_similarity += pair_similarity

        self.data.append(self.struct.pack(t, *list(key_similarity)))

    def update_client(self, client):
        # while there is data that should be sent to the client
        while len(self.data) > 0:
            item = self.data.popleft()
            # send the data to the client
            client.write(item, binary=True)

    def javascript(self):
        """Almost identical to value.py"""
        info = dict(uid=id(self), label=self.label,
                    n_lines=len(self.labels), synapse=0, min_value=-1.5, max_value=1.5, pointer_labels=self.labels)
        json = self.javascript_config(info)
        return 'new Nengo.SpaSimilarity(main, sim, %s);' % json

    def add_nengo_objects(self, page):
        with page.model:
            output = self.obj.outputs[self.target][0]
            self.node = nengo.Node(self.gather_data,
                                   size_in=self.vocab_out.dimensions)
            self.conn = nengo.Connection(output, self.node, synapse=0.01)

    def remove_nengo_objects(self, page):
        """Undo the changes made by add_nengo_objects."""
        page.model.connections.remove(self.conn)
        page.model.nodes.remove(self.node)

    def message(self, msg):
        """This should never be called."""
        raise AttributeError("You can't set the value of a plot!")

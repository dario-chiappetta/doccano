from __future__ import unicode_literals, print_function

import logging
import random
from pathlib import Path
import spacy

logger = logging.getLogger(__name__)

# new entity label
LABEL = 'ANIMAL'

TRAIN_DATA = [
    ("Horses are too tall and they pretend to care about your feelings", {
        'entities': [(0, 6, 'ANIMAL')]
    }),

    ("Do they bite?", {
        'entities': []
    }),

    ("horses are too tall and they pretend to care about your feelings", {
        'entities': [(0, 6, 'ANIMAL')]
    }),

    ("horses pretend to care about your feelings", {
        'entities': [(0, 6, 'ANIMAL')]
    }),

    ("they pretend to care about your feelings, those horses", {
        'entities': [(48, 54, 'ANIMAL')]
    }),

    ("horses?", {
        'entities': [(0, 6, 'ANIMAL')]
    })
]

class DocumentClassificationModel(object):

    def __init__(self, project):
        self.project = project
    
    def train(self):
        """
        Retrain the model using data from the labelling project. Output the f1
        score of the trained model.
        """
        logger.warning("Dummy Document Classification training")
        return 0.5

    def predict(self, text):
        """
        Predict the class of the given text. Return a Label instance
        """
        logger.warning("Dummy Document Classification prediction")
        return random.choice(self.project.labels.all())

class SequenceLabelingModel(object):

    def __init__(self, project):
        self.project = project
    
    def train(self):
        """
        Retrain the model using data from the labeling project. Output the f1
        score of the trained model.
        """
        logger.warning("Dummy Sequence Labeling training")
        return 0.5

    def predict(self, text):
        """
        Predict labeled entities in the given text. Return a Label instance
        """
        logger.warning("Dummy Sequence Labeling prediction")
        dummy_span = min(5, len(text)-1)
        dummy_start = random.randint(0, max(0, len(text)-dummy_span))
        dummy_label = random.choice(self.project.labels.all())
        return [{
            'label': dummy_label,
            'start': dummy_start,
            'end': dummy_start+dummy_span
        }]

class NERModel(object):

    def __init__(self, model=None, lang='en'):
        self.model = model
        if model is not None:
            self.nlp = spacy.load(model)
        else:
            self.nlp = spacy.blank(lang)

        if 'ner' not in self.nlp.pipe_names:
            self.ner = self.nlp.create_pipe('ner')
            self.nlp.add_pipe(self.ner)
        else:
            self.ner = self.nlp.get_pipe('ner')

    def add_label(self, label):
        self.ner.add_label(label)

    def get_optimizer(self):
        if self.model is None:
            optimizer = self.nlp.begin_training()
        else:
            optimizer = self.nlp.entity.create_optimizer()

        return optimizer

    def train(self, train_data, n_iter=20):
        optimizer = self.get_optimizer()
        other_pipes = [pipe for pipe in self.nlp.pipe_names if pipe != 'ner']
        with self.nlp.disable_pipes(*other_pipes):  # only train NER
            for _ in range(n_iter):
                random.shuffle(train_data)
                losses = {}
                for text, annotations in train_data:
                    self.nlp.update([text], [annotations], sgd=optimizer, drop=0.35, losses=losses)
                print(losses)

    def predict(self, text):
        doc = self.nlp(text)
        print("Entities in '%s'" % text)
        for ent in doc.ents:
            print(ent.label_, ent.text)

    def save(self, new_model_name='animal', output_dir=None):
        if output_dir is not None:
            output_dir = Path(output_dir)
            if not output_dir.exists():
                output_dir.mkdir()
            self.nlp.meta['name'] = new_model_name  # rename model
            self.nlp.to_disk(output_dir)
            print("Saved model to", output_dir)


def main():
    model = NERModel()
    model.add_label(LABEL)
    model.train(TRAIN_DATA)
    model.predict(text='Do you like horses?')
    model.save(output_dir='./model')
    model = NERModel(model='./model')
    model.predict(text='Do you like horses?')


if __name__ == '__main__':
    main()

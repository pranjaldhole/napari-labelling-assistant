"""
This module is an example of a barebones QWidget plugin for napari

It implements the ``napari_experimental_provide_dock_widget`` hook specification.
see: https://napari.org/docs/dev/plugins/hook_specifications.html

Replace code below according to your needs.
"""
from napari_plugin_engine import napari_hook_implementation
from qtpy.QtWidgets import QWidget, QHBoxLayout, QPushButton, QCheckBox

import numpy as np
import matplotlib.pyplot as plt

from napari.layers.labels.labels import Labels

class LabellingAssistant(QWidget):
    # your QWidget.__init__ can optionally request the napari viewer instance
    # in one of two ways:
    # 1. use a parameter called `napari_viewer`, as done here
    # 2. use a type annotation of 'napari.viewer.Viewer' for any parameter
    def __init__(self, napari_viewer):
        super().__init__()
        self.viewer = napari_viewer

        # Prints stats as stdout
        btn = QPushButton("Get stats!")
        btn.clicked.connect(self._std_stats)

        # Generates a figure
        bar = QPushButton("View stats!")
        bar.clicked.connect(self._generate_plot)

        # Boolean for excluding unlabelled region
        self.exclude_unlabelled = QCheckBox("Exclude unlabelled data")
        self.exclude_unlabelled.setChecked(False)
        self.exclude_unlabelled.toggled.connect(self.onClicked)

        # Boolean for excluding background labelled region
        self.exclude_bg_label = QCheckBox("Exclude background labels (iff BG ID == 1)")
        self.exclude_bg_label.setChecked(False)
        self.exclude_bg_label.toggled.connect(self.onClicked)

        self.setLayout(QHBoxLayout())
        self.layout().addWidget(btn)
        self.layout().addWidget(bar)
        self.layout().addWidget(self.exclude_unlabelled)
        self.layout().addWidget(self.exclude_bg_label)

    def onClicked(self):
        _ = self.sender()

    def _on_click(self):
        print("napari has", len(self.viewer.layers), "layers")

    def _std_stats(self):
        get_stats(self.viewer.layers)
    
    def _generate_plot(self):
        view_stats(self.viewer.layers,
                   self.exclude_unlabelled.isChecked(),
                   self.exclude_bg_label.isChecked())


@napari_hook_implementation
def napari_experimental_provide_dock_widget():
    # you can return either a single widget, or a sequence of widgets
    return [LabellingAssistant]

def fetch_data(label_layers):
    data = []
    num_labels = 0
    for i, layer in enumerate(label_layers):
        if type(layer) == Labels:
            array = layer.data
            print("array shape: ", array.shape)
            data.append(array)
            num_labels = max(num_labels, array.max())
            #print(f"{layer.name} added!")
        else:
            #print(f"{layer.name} is an Image!")
            continue
    return data, num_labels

def get_counts(label_array, max_labels):
    label_list = list(range(max_labels + 1))

    u, c = np.unique(label_array, return_counts=True)

    count_list = []
    for i in label_list:
        if i not in u:
            #print('missing label: ', i)
            count_list.append(0)
        else:
            count_list.append(c[np.where(i == u)[0][0]])

    return label_list, count_list

def get_counts_from_labels(labels_data, num_labels):
    unique, counts = get_counts(labels_data[0], num_labels)
    for i in range(1, len(labels_data)):
        label_array = labels_data[i]
        u, c = get_counts(label_array, num_labels)
        assert unique == u, 'Number of label IDs mismatched!'
        counts = [a + b for a, b in zip(counts, c)] #element-wise addition

    return unique, counts

def get_stats(label_layers):
    labels_data, num_labels = fetch_data(label_layers)
    unique, counts = get_counts_from_labels(labels_data, num_labels)
    for i, c in zip(unique, counts):
        if i == 0:
            print(f"Label ID: {i} | Count (in Pixels): {c} | unlabelled pixels")
        elif i == 1:
            print(f"Label ID: {i} | Count (in Pixels): {c} | background pixels")
        else:
            print(f"Label ID: {i} | Count (in Pixels): {c}")

def view_stats(label_layers, exclude_unlabelled_pixels, exclude_background_pixels):
    labels_data, num_labels = fetch_data(label_layers)
    unique, counts = get_counts_from_labels(labels_data, num_labels)
    if exclude_unlabelled_pixels:
        start_with = 1
    if exclude_background_pixels: # will also exclude unlabelled pixels
        start_with = 2
    else:
        start_with = 0
    plot_bar(unique[start_with:], counts[start_with:])

def plot_bar(unique, counts):
    _, _ = plt.subplots(figsize=(15,5))
    LABELS = [str(a) for a in unique] 
    plt.bar(unique, counts)
    plt.xticks(unique, LABELS)
    plt.xlabel('Label ID')
    plt.ylabel('Labels count (in Pixels)')
    plt.show()

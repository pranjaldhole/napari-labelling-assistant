from napari_labelling_assistant import LabellingAssistant, fetch_data, get_colors
import numpy as np

# make_napari_viewer is a pytest fixture that returns a napari viewer object
# capsys is a pytest fixture that captures stdout and stderr output streams
def test_example_q_widget(make_napari_viewer, capsys):
    # make viewer and add an image layer using our fixture
    viewer = make_napari_viewer()
    viewer.add_labels(np.random.choice([0,1,2], (100,100), p=[0.6, 0.3, 0.1]))

    # create our widget, passing in the viewer
    my_widget = LabellingAssistant(viewer)

    # call our widget method
    my_widget._on_click()

    # read captured output and check that it's as we expected
    captured = capsys.readouterr()
    assert captured.out == "napari has 1 layers\n"

def get_label_array():
    label_array = np.array([[1, 0, 0, 1, 1, 1, 0, 1, 0, 1],
                            [1, 0, 2, 0, 0, 0, 0, 0, 0, 0],
                            [0, 0, 2, 1, 2, 1, 1, 0, 0, 2],
                            [2, 0, 0, 1, 2, 2, 1, 1, 1, 1],
                            [1, 2, 1, 1, 0, 0, 0, 0, 0, 1],
                            [0, 0, 0, 0, 1, 0, 1, 2, 0, 2],
                            [0, 0, 2, 1, 2, 1, 0, 2, 1, 0],
                            [1, 0, 0, 1, 2, 1, 0, 0, 0, 2],
                            [1, 0, 0, 0, 0, 1, 0, 0, 0, 0],
                            [1, 0, 0, 0, 0, 0, 0, 1, 2, 1]])
    return label_array


def test_data_fetching(make_napari_viewer):
    viewer = make_napari_viewer()
    label_array = get_label_array()
    viewer.add_labels(label_array)

    data, num_labels, num_layers = fetch_data(viewer.layers)
    assert np.array_equal(data[0], label_array)
    assert num_labels == 3
    assert num_layers == 1

def test_label_colors_order(make_napari_viewer):
    viewer = make_napari_viewer()
    label_array = get_label_array()
    viewer.add_labels(label_array)

    default_color_dict = {
        '1': np.array([0.47063142, 0.14611654, 0.02730864]),
        '2': np.array([0.35923997, 0.83787304, 0.97641581]),
        '3': np.array([0.57314003, 0.53869504, 0.91307282]),
        '4': np.array([0.6125465 , 0.37994882, 0.18645138]),
        '5': np.array([0.28053862, 0.22821146, 0.62640917]),
        '6': np.array([0.67241573, 0.92709625, 0.5439105 ]),
        '7': np.array([0.70704526, 0.49094781, 0.74280363]),
        '8': np.array([0.52777791, 0.56721127, 0.60434461]),
        '9': np.array([0.99877518, 0.96869242, 0.10985588]),
    }
    num_labels = 9
    colors_dict = get_colors(num_labels, viewer.layers[0])
    for i in range(1, num_labels+1):
        assert default_color_dict[str(i)] == colors_dict[str(i)]

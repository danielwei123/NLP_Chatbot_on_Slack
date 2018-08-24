from vis.visualization.saliency import visualize_cam
import numpy as np
import cv2
import skimage.io as io
import matplotlib.pyplot as plt
import keras
import skimage

def grad_cam(model, image):
    model.layers[-1].activation = keras.activations.linear
    return visualize_cam(model,
                         layer_idx=len(model.layers) - 1,  # modify this as the network changes, must be the last layer
                         filter_indices=[1],  # index of importance in the layer, change
                         seed_input=image,  # image of interest
                         penultimate_layer_idx=147,  # layer prior to the GLOBAL max pooling layer
                         backprop_modifier=None,  # no need to modify
                         grad_modifier=None)  # no need to modify


def find_fraction_of_importance(heatmap, image):
    red_heatmap = heatmap[:, :, 0]
    ret, thresh = cv2.threshold(red_heatmap, np.max(red_heatmap.flatten()) * .85, 1,
                                cv2.THRESH_BINARY)  # threshold top 15%
    _, contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    # cv2.drawContours(image, contours, -1, (0, 255, 0), 3) #this is here just in case you need to check if any contours existed
    largest_contours = sorted(contours, key = cv2.contourArea)[-2]
    try:
        rect = cv2.boundingRect(largest_contours)
        x, y, w, h = rect
        cropped_img = image[y:y + h, x:x + w]  # this is here in case you need to check the crop of the image
        fraction_of_importance = float(float(x) + w/2.0) / float(heatmap.shape[1])  # expresses the location of the object
        # in terms of the fraction of the total width of the image
        return cropped_img, heatmap, fraction_of_importance
    except IndexError:
        return None, None, None


def create_graph(heatmap, image, cropped_img, cols=1):
    images = [image, heatmap, cropped_img]
    titles = ['Images', 'Heatmap', 'Cropped Images']  # images and titles must have the same size
    assert ((titles is None) or (len(images) == len(titles)))
    n_images = len(images)
    if titles is None: titles = ['Image (%d)' % i for i in range(1, n_images + 1)]
    fig = plt.figure()
    for n, (image, title) in enumerate(zip(images, titles)):
        a = fig.add_subplot(cols, np.ceil(n_images / float(cols)), n + 1)
        if image.ndim == 2:
            plt.gray()
        plt.imshow(image)
        a.set_title(title)
    # fig.set_size_inches(np.array(fig.get_size_inches()) * n_images)
    # plt.savefig(name_of_example,  bbox_inches='tight')
    # plt.close()

    fig.canvas.draw()
    # Now we can save it to a numpy array.
    data = np.fromstring(fig.canvas.tostring_rgb(), dtype=np.uint8, sep='')
    data = data.reshape(fig.canvas.get_width_height()[::-1] + (3,))

    return data


def prediction_graph(model, image):
    image = cv2.resize(image, (224, 224)).astype('float64') / 255.
    prediction = model.predict(np.expand_dims(image, axis=0))
    print(prediction)
    if np.argmax(prediction) == 1:
        heatmap = grad_cam(model, image)
        cropped_img, heatmap, fraction_of_importance = find_fraction_of_importance(heatmap, image)  # find fraction
        graph = create_graph(heatmap, image, cropped_img, cols=1)  # create graph (remove in production)
        return graph
    else:
        return None


def prediction_fraction(model, image):
    image = cv2.resize(image, (224, 224)).astype('float64') / 255.
    prediction = model.predict(np.expand_dims(image, axis=0))
    if np.argmax(prediction) == 1:
        heatmap = grad_cam(model, image)
        cv2.imwrite("heatmap.jpg", heatmap)
        cropped_img, heatmap, fraction_of_importance = find_fraction_of_importance(heatmap, image)  # find fraction
        return fraction_of_importance
    else:
        return None

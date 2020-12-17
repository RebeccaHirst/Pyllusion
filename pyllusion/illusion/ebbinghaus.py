import numpy as np
import PIL.Image, PIL.ImageDraw, PIL.ImageFilter, PIL.ImageFont, PIL.ImageOps
from psychopy import visual, event
from .delboeuf import _delboeuf_parameters_sizeinner, _delboeuf_parameters_sizeouter
from ..image import image_circle
from ..image.utilities import _coord_circle


def ebbinghaus_image(parameters=None, width=800, height=600, background="white",
                     method="pil", full_screen=False, **kwargs):
    """
    Examples
    ---------
    >>> import pyllusion as ill
    >>>
    >>> parameters = ill.ebbinghaus_parameters(difficulty=2, illusion_strength=1)
    >>> ill.ebbinghaus_image(parameters, method="pil")  #doctest: +ELLIPSIS
    <PIL.Image.Image ...>
    >>> ill.ebbinghaus_image(parameters, method="psychopy")  #doctest: +SKIP
    """
    # Create white canvas and get drawing context
    if parameters is None:
        parameters = ebbinghaus_parameters(**kwargs)

    # PIL Image
    if method == "pil":
        # Background
        image  = PIL.Image.new('RGB', (width, height), color=background)
    
        # Outer circles
        for side in ["Left", "Right"]:
            image = _ebbinghaus_image_draw(image,
                                           parameters,
                                           side=side,
                                           color_inner="red",
                                           color_outer="black")

        return image

    # PsychoPy
    elif method == "psychopy":
        win = visual.Window(size=[width, height], fullscr=full_screen,
                            screen=0, winType='pyglet', allowGUI=False,
                            allowStencil=False,
                            monitor='testMonitor', color=background, colorSpace='rgb',
                            blendMode='avg', units='pix')
        for side in ["Left", "Right"]:
            _ebbinghaus_psychopy_draw(win, parameters, side=side, color_inner="red", color_outer="black")

        # Display    
        win.flip()
        event.waitKeys()
        win.close()





def _ebbinghaus_psychopy_draw(window, p, side="Left", color_inner="red", color_outer="black"):

    # Draw inner circle
    size_inner = p["Size_Inner_" + side]
    radius_inner, x_inner, y_inner = _coord_circle(image=window, diameter=size_inner,
                                     x=p["Position_" + side],
                                     y=0, method="psychopy")

    circle_inner = visual.Circle(win=window, units="pix", fillColor=color_inner,
                                 lineColor=color_inner, edges=128,
                                 radius=radius_inner, lineWidth=0.5)
    circle_inner.pos = [x_inner-window.size[0]/2, y_inner-window.size[1]/2]
    circle_inner.draw()

    # outer circle
    ratio = window.size[0] / window.size[1]  # Get width/height ratio to have equidistant circles
    size_outer = p["Size_Outer_" + side]  
    x_outer = p["Position_Outer_x_" + side] / ratio # Adjust for non-squared screen
    x_outer = x_outer + (p["Position_" + side] - np.mean(x_outer))
    for i in range(len(p["Position_Outer_x_" + side])):
        radius_outer, x_out, y_out = _coord_circle(image=window, diameter=size_outer,
                                                   x=x_outer[i],
                                                   y=p["Position_Outer_y_" + side][i],
                                                   method="psychopy")
        circle_outer = visual.Circle(win=window, units="pix",
                                     fillColor=color_outer, lineColor=color_outer,
                                     edges=128, radius=radius_outer, lineWidth=0.5)
        circle_outer.pos = [x_out-window.size[0]/2, y_out-window.size[1]/2]
        circle_outer.draw()



def _ebbinghaus_image_draw(image, p, side="Left", color_inner="red", color_outer="black"):

    # Draw inner circle
    image = image_circle(image=image, size=p["Size_Inner_" + side], x=p["Position_" + side], y=0, color=color_inner)

    # Get width/height ratio to have equidistant circles
    ratio = image.size[0] / image.size[1]

    # Adjust for non-squared screen
    x = p["Position_Outer_x_" + side] / ratio
    x = x + (p["Position_" + side] - np.mean(x))

    # Plot each outer circles
    for i in range(len(p["Position_Outer_x_" + side])):
        image = image_circle(image=image, size=p["Size_Outer_" + side], x=x[i], y=p["Position_Outer_y_" + side][i], color=color_outer)

    return image



# ------------------------------------------
# Parameters
# ------------------------------------------

def ebbinghaus_parameters(difficulty=0, size_min=0.25, illusion_strength=0, distance=1, distance_auto=False):
    # Size inner circles
    parameters = _delboeuf_parameters_sizeinner(difficulty=difficulty, size_min=size_min)
    inner_size_left = parameters["Size_Inner_Left"]
    inner_size_right = parameters["Size_Inner_Right"]

    # Position
    position_left = -0.5
    position_right = 0.5

    # Base size outer circles
    outer_size_left = size_min
    outer_size_right = size_min

    # Actual outer size based on illusion
    outer_size_left, outer_size_right = _delboeuf_parameters_sizeouter(outer_size_left,
                                                                       outer_size_right,
                                                                       difficulty=difficulty,
                                                                       illusion_strength=illusion_strength,
                                                                       both_sizes=True)

    # Location outer circles
    l_outer_x, l_outer_y, l_distance_edges = _ebbinghaus_parameters_outercircles(x=position_left,
                                                            y=0,
                                                            size_inner=inner_size_left,
                                                            size_outer=outer_size_left,
                                                            n="auto")
    r_outer_x, r_outer_y, r_distance_edges = _ebbinghaus_parameters_outercircles(x=position_right,
                                                            y=0,
                                                            size_inner=inner_size_right,
                                                            size_outer=outer_size_right,
                                                            n="auto")

    # Get location and distances
    if distance_auto is False:
        distance_centers = distance
        position_left, position_right = -(distance_centers / 2), (distance_centers / 2)
        distance_edges_inner = distance_centers - (inner_size_left/2 + inner_size_right/2)
        distance_edges_outer = distance_centers - l_distance_edges - (outer_size_left/2) - r_distance_edges - (outer_size_right/2)

    else:
        distance_edges_outer = distance
        distance_centers = distance_edges_outer + l_distance_edges + (outer_size_left/2) + r_distance_edges + (outer_size_right/2)
        distance_edges_inner = distance_centers - (outer_size_left/2 + outer_size_right/2)
        position_left, position_right = -(distance_centers / 2), (distance_centers / 2)

    parameters.update({
        "Illusion": "Ebbinhaus",
        "Illusion_Strength": illusion_strength,
        "Illusion_Type": "Congruent" if illusion_strength > 0 else "Incongruent",

        "Size_Outer_Left": outer_size_left,
        "Size_Outer_Right": outer_size_right,

        "Distance_Centers": distance_centers,
        "Distance_Edges_Inner": distance_edges_inner,
        "Distance_Edges_Outer": distance_edges_outer,

        "Size_Inner_Smaller": np.min([inner_size_left, inner_size_right]),
        "Size_Inner_Larger": np.max([inner_size_left, inner_size_right]),
        "Size_Outer_Smaller": np.min([outer_size_left, outer_size_right]),
        "Size_Outer_Larger": np.max([outer_size_left, outer_size_right]),

        "Position_Outer_x_Left": l_outer_x,
        "Position_Outer_y_Left": l_outer_y,
        "Position_Outer_x_Right": r_outer_x,
        "Position_Outer_y_Right": r_outer_y,

        "Position_Left": position_left,
        "Position_Right": position_right
        })

    return parameters



def _ebbinghaus_parameters_outercircles(x=0, y=0, size_inner=0.25, size_outer=0.3, n="auto"):
    # Find distance between center of inner circle and centers of outer circles
    distance = (size_inner / 2) + (size_outer / 2) + 0.01

    # Find n
    if n == "auto":
        perimeter = 2 * np.pi * distance
        n = np.int(perimeter / size_outer)

    # Get position of outer circles
    angle = np.deg2rad(np.linspace(0, 360, num=n, endpoint=False))
    circle_x = x + (np.cos(angle) * distance)
    circle_y = y + (np.sin(angle) * distance)

    return circle_x, circle_y, distance

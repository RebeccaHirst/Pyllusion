import numpy as np
import PIL.Image, PIL.ImageDraw, PIL.ImageFilter, PIL.ImageFont, PIL.ImageOps
from ..image import image_circle
from ..psychopy.psychopy_circles import psychopy_circle

class Delboeuf():
    """
    A class to generate a Delboeuf illusion.

    """

    def __init__(self,
                 name = "Delboeuf",
                 strength = 0,
                 difference = 0,
                 size_min = 0.25,
                 distance = 1,
                 distance_auto = False,
                 distance_centers= None,
                 inner_sizes = [],
                 both_sizes = False,
                 targetCol = "red"):
        """
        Parameters
        ----------
        strength : float
            The strength of the surrounding context, i.e. outer circles, in biasing perception of unequally sized inner circles.
            Specifically, the size of left outer circle relative to its inner circle (in percentage, e.g, if ``difference=1``,
            it means that the left outer circle will be 100% bigger, i.e., 2 times bigger than the left
            inner circle). A negative sign reflects the size difference of the right circles, i.e.,
            i.e., ``difference=-1`` means the right outer circle will be 100% bigger than the inner right circle.
        difference : float
            The objective size difference of the inner circles.
            Specifically, the size of left inner circle relative to the right inner circle (in percentage, e.g., if ``difference=1``,
            it means that the left circle will be 100% bigger, i.e., 2 times bigger than the right).
            A negative sign reflects the size difference of the right inner circle relative to the left,
            i.e., ``difference=-1`` means the right inner circle will be 100% bigger than the left inner circle.
        size_min : float
            Size of smaller inner circle.
        distance : float
            Distance between circles.
        distance_auto : bool
            If true, distance is between edges (fixed spacing), if false, between centers (fixed location).

        Returns
        -------
        An instance of the Delboeuf class

        Examples
        ---------

        >>> myDelboeuf = delboeuf2.Delboeuf(strength = 3, difference = 2)
        >>> # draw the image as PIL and save it
        >>> myDelboeuf.draw(method = 'image', width = 800, height = 600, outpath = "myDelboeuf.png")
        >>> # draw the image in a PsychoPy window
        >>> # Initiate Window
        >>> window = visual.Window(size=[800, 600], color='white')
        >>> myDelboeuf.draw(method = 'psychopy', window = window)
        >>> window.flip()
        >>> event.waitKeys()
        """
        self.name = name
        self.strength = strength
        self.type = "Congruent" if strength > 0 else "Incongruent"
        self.inner_sizes = inner_sizes
        self.difference = difference
        self.targetCol = targetCol
        self.distance = distance
        print(self.distance)

        size_bigger = np.sqrt(1 + np.abs(difference)) * size_min

        if difference > 0:  # if right is smaller
            self.inner_sizes.extend([size_min, size_bigger])
        else:
            self.inner_sizes.extend([size_bigger, size_min])

        self.size_inner_difference = np.pi *(size_bigger / 2) ** 2 / np.pi * (size_min / 2) ** 2

        self.size_inner_smaller = np.min(inner_sizes)
        self.size_inner_larger = np.max(inner_sizes)
        # Base size outer circles
        self.outer_sizes = [self.inner_sizes[0] + (0.2 * size_min), self.inner_sizes[1] + (0.2 * size_min)]

        # Actual outer size based on illusion
        if both_sizes is True:
            strength = strength / 2

        # Actual outer size based on illusion
        if difference > 0:  # if right is smaller
            if strength > 0:
                self.outer_sizes[0] = np.sqrt(1 + np.abs(strength)) * self.outer_sizes[0]
                if both_sizes is True:
                    self.outer_sizes[1] = self.outer_sizes[1] / np.sqrt(1 + np.abs(strength))
            else:
                self.outer_sizes[1] = np.sqrt(1 + np.abs(strength)) * self.outer_sizes[1]
                if both_sizes is True:
                    self.outer_sizes[0] = self.outer_sizes[0] / np.sqrt(1 + np.abs(strength))

        else:
            if strength > 0:
                self.outer_sizes[1] = np.sqrt(1 + np.abs(strength)) * self.outer_sizes[1]
                if both_sizes is True:
                    self.outer_sizes[0] = self.outer_sizes[0] / np.sqrt(1 + np.abs(strength))
            else:
                self.outer_sizes[0] = np.sqrt(1 + np.abs(strength)) * self.outer_sizes[0]
                if both_sizes is True:
                    self.outer_sizes[1] = self.outer_sizes[1] / np.sqrt(1 + np.abs(strength))

        # Get location and distances
        if distance_auto is False:
            self.distance_centers = distance
            self.positions = -(self.distance_centers / 2), (self.distance_centers / 2)
            self.distance_edges_inner = self.distance_centers - (
                    self.inner_sizes[0] / 2 + self.inner_sizes[1] / 2
            )
            self.distance_edges_outer = self.distance_centers - (
                    self.outer_sizes[0] / 2 + self.outer_sizes[1] / 2
            )
        else:
            self.distance_edges_outer = distance
            self.distance_centers = self.distance_edges_outer + (
                    self.inner_sizes[0] / 2 + self.inner_sizes[1] / 2
            )
            self.distance_edges_inner = self.distance_centers - (
                    self.outer_sizes[0] / 2 + self.outer_sizes[1] / 2
            )
            self.positions= -(self.distance_centers / 2), (self.distance_centers / 2)
        self.size_outer_smaller = np.min(self.outer_sizes)
        self.size_outer_larger = np.max(self.outer_sizes)

    def draw(self, method = 'image', width = None, height = None, window = None, background="white", outline=10, outpath = None):
        """ A method to draw the Delboeuf instance either as PIL or psychopy stimuli
        Input
        -----
        method
            string 'psychopy' or 'image'

            psychopy method will render a psychopy image
            image method will return an image file generated using PIL

        width
            width of the image in pixel units

        height
            height of the image in pixel units

        window
            if method is 'psychopy' what window will the image be drawn in

        background
            color of the background
            """

        if method == 'image':
            # Create white canvas and get drawing context
            self.image = PIL.Image.new('RGB', (width, height), color=background)

            # Loop circles
            for i, pos in enumerate(self.positions):
                # Draw outer circle
                self.image = image_circle(image=self.image,
                             x=pos, y=0,
                             size=self.outer_sizes[i],
                             color=(0, 0, 0, 0), outline=outline)
                print('size_new', self.outer_sizes[i], 'pos: ', pos)
                # Draw inner circle
                self.image = image_circle(image=self.image,
                             x=pos, y=0,
                             size=self.inner_sizes[i],
                             color=self.targetCol)

            if outpath:
                self.image.save(outpath)
        elif method == 'psychopy':
            # Create white canvas and get drawing context
            # Loop circles
            for i, pos in enumerate(self.positions):
                # Draw outer circle
                self.image = psychopy_circle(window, x=pos, y=0, size=self.outer_sizes[i],
                                color="white", outline_color="black", outline=3)

                # Draw inner circle
                self.image = psychopy_circle(window, x=pos, y=0, size=self.inner_sizes[i],
                                color=self.targetCol, outline_color="red", outline=0.5)

        else:
            raise TypeError(
                method,  " is not a method. Use 'psychopy' or 'image'",
            )

    def setStrength(self, strength):
        """ Update the strength of the illusion
             Input
             ----------
             strength : int
                The new strength of the illusion"""
        self.strength = strength
        # reinitialize the object
        self.__init__()

    def setDifference(self, difference):
        """ NOTE: not working as expected??
        Update the difference of the illusion
             Input
             ----------
             difference : float
                The new difference param of the illusion"""
        self.difference = difference
        # reinitialize the object
        self.__init__(difference = difference)

    def setTargetCol(self, color):
        """ Update the color of the targets
             Input
             ----------
             color : str
                The new target color"""
        self.targetCol = color

    def setDistance(self, distance):
        """ Update the distance between the targets
             Input
             ----------
              distance : float
                 New distance between circles.
             Example
             ----------
             myDebeouf.setDistance(2)
             
             """
        self.distance = distance
        # reinitialize the object
        self.__init__(distance = distance)


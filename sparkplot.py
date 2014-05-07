#!/usr/bin/env python
import StringIO

import os, sys, re
from optparse import OptionParser
import matplotlib
# If you want to use a different backend, replace Agg with
# Cairo, PS, SVG, GD, Paint etc.
# Agg stands for "antigrain rendering" and produces PNG files
matplotlib.use('Agg')

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from pylab import *

class Sparkplot:
    """
    Creates sparkline graphics, as described by Edward Tufte. Uses the matplotlib library.

    The 2 styles of plots implemented so far are: 'line' and 'bars'
    """
    def __init__(self, type='line', data=[], input_file="data.txt", output_file="",
                 plot_first=True, plot_last=True,
                 label_first_value=False, label_last_value=False,
                 plot_min=False, plot_max=False,
                 label_min=False, label_max=False,
                 draw_hspan=False, hspan_min=-1, hspan_max=0,
                 label_format="", currency='$', verbose=0):
        self.type = type
        self.data = data
        self.input_file = input_file
        self.output_file = output_file
        self.plot_first = plot_first
        self.plot_last = plot_last
        self.label_first_value = label_first_value
        self.label_last_value = label_last_value
        self.plot_min = plot_min
        self.plot_max = plot_max
        self.label_min = label_min
        self.label_max = label_max
        self.draw_hspan = draw_hspan
        self.hspan_min = hspan_min
        self.hspan_max = hspan_max
        self.label_format = label_format
        self.currency = currency
        self.verbose = verbose

    def process_args(self):
        parser = OptionParser()
        parser.add_option("-m", "--type", dest="type",
                          default="line", help="graphic type (can be 'line' [default], 'bars')")
        parser.add_option("-i", "--input", dest="input_file",
                          default="data.txt", help="input data file (default is data.txt)")
        parser.add_option("-o", "--output", dest="output_file",
                          default="", help="output data file (default is data.png)")
        parser.add_option("--noplot_first", action="store_false", dest="plot_first",
                          default=True, help="do not plot first data point in different color")
        parser.add_option("--noplot_last", action="store_false", dest="plot_last",
                          default=True, help="do not plot last data point in different color")
        parser.add_option("--label_first", action="store_true", dest="label_first_value",
                          default=False, help="label first data value (default=False)")
        parser.add_option("--label_last", action="store_true", dest="label_last_value",
                          default=False, help="label last data value (default=False)")
        parser.add_option("--plot_min", action="store_true", dest="plot_min",
                          default=False, help="plot min data point in different color (default=False)")
        parser.add_option("--plot_max", action="store_true", dest="plot_max",
                          default=False, help="plot max data point in different color (default=False)")
        parser.add_option("--label_min", action="store_true", dest="label_min",
                          default=False, help="label min data value (default=False)")
        parser.add_option("--label_max", action="store_true", dest="label_max",
                          default=False, help="label max data value (default=False)")
        parser.add_option("--draw_hspan", action="store_true", dest="draw_hspan",
                          default=False, help="draw a horizontal band along the x axis (default=False)")
        parser.add_option("--hspan_min", dest="hspan_min", type="int",
                          default=-1, help="specify the min y value for the hspan (default=-1)")
        parser.add_option("--hspan_max", dest="hspan_max", type="int",
                          default=0, help="specify the max y value for the hspan (default=0)")
        parser.add_option("--format", dest="label_format", metavar="FORMAT",
                          default="", help="format for the value labels (can be empty [default], 'comma', 'currency')")
        parser.add_option("--currency", dest="currency",
                          default="$", help="currency symbol (default='$')")
        parser.add_option("--verbose", action="store_true", dest="verbose",
                          default=False, help="show diagnostic messages (default=False)")

        (options, args) = parser.parse_args()

        self.type = options.type
        self.input_file = options.input_file
        self.output_file = options.output_file
        self.plot_first = options.plot_first
        self.plot_last = options.plot_last
        self.label_first_value = options.label_first_value
        self.label_last_value = options.label_last_value
        self.plot_min = options.plot_min
        self.plot_max = options.plot_max
        self.label_min = options.label_min
        self.label_max = options.label_max
        self.draw_hspan = options.draw_hspan
        self.hspan_min = options.hspan_min
        self.hspan_max = options.hspan_max
        self.label_format = options.label_format
        self.verbose = options.verbose
        self.currency = options.currency

    def get_input_data(self):
        """
        Read input file and fill data list.

        Data file is assumed to contain one column of numbers which will
        be plotted as a timeseries.
        """
        try:
            f = open(self.input_file)
        except:
            print "Input file %s could not be opened" % self.input_file
            sys.exit(1)
        data = [float(line.rstrip('\n')) for line in f.readlines() if re.search('\d+', line)]
        f.close()
        return data

    def plot_sparkline(self):
        """
        Plot sparkline graphic by using various matplotlib functions.
        """
        if len(self.data) == 0:
            self.data = self.get_input_data()
        num_points = len(self.data)
        min_data = min(self.data)
        max_data = max(self.data)
        sum_data = sum(self.data)
        avg_data = sum(self.data) / num_points
        min_index = self.data.index(min_data)
        max_index = self.data.index(max_data)
        if self.verbose:
            print "Plotting %d data points" % num_points
            print "Min", min_index, min_data
            print "Max", max_index, max_data
            print "Avg", avg_data
            print "Sum", sum_data

        # last_value_len is used for dynamically adjusting the width of the axes
        # in the axes_position list
        if self.label_last_value:
            last_value_len = len(self.format_text(self.data[num_points-1]))
        elif self.label_max:
            last_value_len = len(self.format_text(max_data))
        else:
            last_value_len = 1

        # delta_height is used for dynamically adjusting the height of the axes
        # in the axes_position list
        if self.plot_max or self.label_max or self.label_last_value:
            delta_height = 0.32
        else:
            delta_height = 0.1

        axes_position = [0.02,0.02,1-0.035*last_value_len,1-delta_height]

        # Width of the figure is dynamically adjusted depending on num_points
        fig_width = min(5, max(1.5, 0.03 * num_points))

        # Height of the figure is set differently depending on plot type
        if self.type.startswith('line'):
            fig_height = 0.3
        elif self.type.startswith('bar'):
            if self.label_max:
                fig_height = 0.5
            else:
                fig_height = 0.1

        if self.verbose:
            print "Figure width:", fig_width
            print "Figure height:", fig_height
            print "Axes position:", axes_position

        # Create a figure with the given width, height and dpi
        fig = figure(1, figsize=(fig_width, fig_height), dpi=150)

        if self.type.startswith('line'):
            # For 'line' plots, simply plot the line
            plot(range(num_points), self.data, color='gray')
        elif self.type.startswith('bar'):
            # For 'bars' plots, simulate bars by plotting vertical lines
            for i in range(num_points):
                if self.data[i] < 0:
                    color = 'r'
                else:
                    color = 'b' # Use color = '#003163' for a dark blue
                plot((i, i), (0, self.data[i]), color=color, linewidth=1.25)


        if self.draw_hspan:
            axhspan(ymin=self.hspan_min, ymax=self.hspan_max, xmin=0, xmax=1, linewidth=0.5, edgecolor='gray', facecolor='gray')

        if self.type == 'line':
            # Plotting the first, last, min and max data points in a different color only makes sense for 'line' plots
            if self.plot_first:
                plot([0,0], [self.data[0], self.data[0]], 'r.')
            if self.plot_last:
                plot([num_points-1, num_points-1], [self.data[num_points-1], self.data[num_points-1]], 'r.')
            if self.plot_min:
                plot([min_index, min_index], [self.data[min_index], self.data[min_index]], 'b.')
            if self.plot_max:
                plot([max_index, max_index], [self.data[max_index], self.data[max_index]], 'b.')

        if self.label_first_value:
            text(0, self.data[0], self.format_text(self.data[0]), size=6)
        if self.label_last_value:
            text(num_points-1, self.data[num_points-1], self.format_text(self.data[num_points-1]), size=6)
        if self.label_min:
            text(min_index, self.data[min_index], self.format_text(min_data), size=6)
        if self.label_max:
            text(max_index, self.data[max_index], self.format_text(max_data), size=6)

        # IMPORTANT: commands affecting the axes need to be issued AFTER the plot commands

        # Set the axis limits instead of letting them be computed automatically by matplotlib
        # We leave some space around the data points so that the plot points for
        # the first/last/min/max points are displayed
        axis([-1, num_points, 0.9*min_data, 1.1*max_data ])

        # Turn off all axis display elements (frame, ticks, tick labels)
        axis('off')
        # Note that these elements can also be turned off via the following calls,
        # but I had problems setting the axis limits AND settings the ticks to empty lists
        #a.set_xticks([])
        #a.set_yticks([])
        #a.set_frame_on(False)

        # Set the position for the current axis so that the data labels fit in the figure
        a = gca()
        a.set_position(axes_position)

        # Save the plotted figure to a data file
        #self.generate_output_file()
        #note: I am subverting the original code here to make this 'Flask' friendly.  see https://gist.github.com/rduplain/1641344
        output = StringIO.StringIO()
        canvas = FigureCanvas( fig  )
        canvas.print_png( output )
        return output

    def generate_output_file(self):
        """
        Save plotted figure to output file.

        The AGG backend will automatically append .PNG to the file name
        """
        if not self.output_file:
            self.output_file = os.path.splitext(self.input_file)[0]
        if self.verbose:
            print "Generating output file " + self.output_file + '.png'
        savefig(self.output_file)

    def format_text(self, data):
        """
        Format text for displaying data values.

        The only 2 formats implemented so far are:
        'currency' (e.g. $12,249)
        'comma' (e.g. 34,256,798)
        """
        if self.label_format == 'currency' or self.label_format == 'comma':
            t = str(int(data))
            text = ""
            if self.label_format == 'currency':
                text += self.currency
            l = len(t)
            if l > 3:
                quot = l / 3
                rem = l % 3
                text += t[:rem]
                for i in range(quot):
                    text += ',' + t[rem:rem+3]
                    rem += 3
            else:
                text += t
        else:
            text = str(data)
        return text

if __name__ == '__main__':
    sparkplot = Sparkplot()
    sparkplot.process_args()
    sparkplot.plot_sparkline()
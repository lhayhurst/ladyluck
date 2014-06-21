import unittest

red_scale    = ['nocolor','red1', 'red2', 'red3', 'red4', 'red5', 'red6', 'red7', 'red8', 'red9']
green_scale  = ['nocolor', 'green1', 'green2', 'green3', 'green4', 'green5', 'green6', 'green7', 'green8', 'green9']

class colorscale:

    def index_calc(self, v):
            v = float('%.1f' % v)
            d = 1 - v
            index = None
            if d < .1:
                index = 0
            if d >= .9:
                index = 9
            index = int(d*10)
            return index

    def index(self, expected, actual):

        diff = actual - expected
        if diff == 0:
            return red_scale[0]
        if diff > 0:
            #greens
            #convert the different to an index from 0-9
            #e:10, a:15, d:5
            v = float(expected / actual)
            return self.index_calc(v)
        elif diff < 0:
            v = float( actual / expected )
            return self.index_calc(v)

    def colormap(self, expected, actual):
        return red_scale[0]
#        index = self.index(expected, actual)
#        if index > 9 or index < 0: #WTF?? :-)
#            return green_scale[0]
#        if actual >= expected:
#            return green_scale[index]
#        return red_scale[index]

class ColorScaleTest(unittest.TestCase):
    def testGreens(self):
        c = colorscale()
        index = c.index(10.0,15.0)
        self.assertEqual( index, 3 )
        self.assertEqual( 0, c.index(10.0, 11.0))
        self.assertEqual( 1, c.index(10.0, 12.0))
        self.assertEqual( 8, c.index(10.0, 50.0))
        self.assertEqual( 9, c.index(10.0, 110.0))

        self.assertEqual( 0, c.index(10.0, 9.0))
        self.assertEqual( 1, c.index(10.0, 8.0))

        self.assertEqual( 'nocolor', c.colormap(10.0, 10.0 ))



if __name__ == "__main__":
    unittest.main()

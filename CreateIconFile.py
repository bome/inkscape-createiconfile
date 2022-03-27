# coding=utf-8

# Copyright 2022 Sven Schork
# Copyright 2022 Florian Bomers

# Permission is hereby granted, free of charge, to any person obtaining a copy of 
# this software and associated documentation files (the "CreateIconFile"), to deal in the 
# Software without restriction, including without limitation the rights to use, 
# copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the 
# Software, and to permit persons to whom the Software is furnished to do so, subject 
# to the following conditions:

# The above copyright notice and this permission notice shall be included in all 
# copies or substantial portions of the Software.

# 'THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
# INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A 
# PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT 
# HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF 
# CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE 
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

from tempfile import tempdir
import inkex
from pathlib import Path
from PIL import Image
from inkex.command import inkscape
from inkex.base import TempDirMixin
import os

class CreateIconFile (TempDirMixin, inkex.Effect):

    def __init__(self):
        inkex.Effect.__init__(self)

        self.arg_parser.add_argument('-t', '--iconname',
            type = str, dest = 'iconname', default = 'icon.ico',
            help = 'The selected icon name without path (will be created at same location as .svg)')

    def createIconFile(self, exportpar, icofilename):
        # Write the global header
        number_of_sources = 0
        for exportfilepar in exportpar:
            if (exportfilepar['ico']):
                number_of_sources = number_of_sources + 1
        data = bytes((0, 0, 1, 0, number_of_sources, 0))
        offset = 6 + number_of_sources * 16

        # Write the header entries for each individual image
        for exportfilepar in exportpar:
            if (exportfilepar['ico']):
                img = Image.open(exportfilepar['filename'])
                # inkex.errormsg("Width: " + str(img.width) + ", Height: " + str(img.height))
                if (img.width >= 256): # Icon max size 256 needs to set the size bytes to zero
                    data += bytes((0, 0, 0, 0, 1, 0, 32, 0, ))
                else:
                    data += bytes((img.width, img.height, 0, 0, 1, 0, 32, 0, ))
                bytesize = Path(exportfilepar['filename']).stat().st_size
                data += bytesize.to_bytes(4, byteorder="little")
                data += offset.to_bytes(4, byteorder="little")
                offset += bytesize
                img.close()

        # Write the image data to the icon file
        for exportfilepar in exportpar:
            if (exportfilepar['ico']):
                data += Path(exportfilepar['filename']).read_bytes()
        # Save the icon file
        Path(icofilename).write_bytes(data)

        return data

    def effect(self):
        try:
            svg = self.svg
            #inkex.utils.debug("start create icon: " + self.options.iconname)
            basename = os.path.splitext(self.options.iconname)[0]
            # prepend current file path if icon path is not absolute
            if basename[0] != '/' and basename[1] != ':':
                basename = os.path.join(self.svg_path(), basename)
                    
            # inkex.utils.debug("TempDir: " + self.tempdir)
            #inkex.utils.debug("svg.name: " + self.svg_path())
            #inkex.utils.debug("basename: " + basename)
            export = [
                {'filename': basename + "-16.png", 'size': 16, 'dpi': 96, 'ico': True},
                {'filename': basename + "-24.png", 'size': 24, 'dpi': 96, 'ico': True},
                {'filename': basename + "-32.png", 'size': 32, 'dpi': 96, 'ico': True},
                {'filename': basename + "-48.png", 'size': 48, 'dpi': 96, 'ico': True},
                {'filename': basename + "-64.png", 'size': 64, 'dpi': 96, 'ico': True},
                {'filename': basename + "-128.png", 'size': 128, 'dpi': 96, 'ico': True},
                {'filename': basename + "-256.png", 'size': 256, 'dpi': 96, 'ico': True},
                {'filename': basename + "-512.png", 'size': 512, 'dpi': 96, 'ico': False},
                {'filename': basename + "-1024.png", 'size': 1024, 'dpi': 96, 'ico': False},
                # iOS icons
                {'filename': basename + "-App-20x20@1x.png", 'size': 20, 'dpi': 72, 'ico': False},
                {'filename': basename + "-App-20x20@2x.png", 'size': 40, 'dpi': 144, 'ico': False},
                {'filename': basename + "-App-20x20@3x.png", 'size': 60, 'dpi': 216, 'ico': False},
                {'filename': basename + "-App-29x29@1x.png", 'size': 29, 'dpi': 72, 'ico': False},
                {'filename': basename + "-App-29x29@2x.png", 'size': 58, 'dpi': 144, 'ico': False},
                {'filename': basename + "-App-29x29@3x.png", 'size': 87, 'dpi': 216, 'ico': False},
                {'filename': basename + "-App-40x40@1x.png", 'size': 40, 'dpi': 72, 'ico': False},
                {'filename': basename + "-App-40x40@2x.png", 'size': 80, 'dpi': 144, 'ico': False},
                {'filename': basename + "-App-40x40@3x.png", 'size': 120, 'dpi': 216, 'ico': False},
                {'filename': basename + "-App-60x60@2x.png", 'size': 120, 'dpi': 144, 'ico': False},
                {'filename': basename + "-App-60x60@3x.png", 'size': 180, 'dpi': 216, 'ico': False},
                {'filename': basename + "-App-76x76@1x.png", 'size': 76, 'dpi': 72, 'ico': False},
                {'filename': basename + "-App-76x76@2x.png", 'size': 152, 'dpi': 144, 'ico': False},
                {'filename': basename + "-App-83.5x83.5@2x.png", 'size': 167, 'dpi': 144, 'ico': False},
                {'filename': basename + "-App-1024x1024@1x.png", 'size': 1024, 'dpi': 72, 'ico': False},
            ]

            for exportfilepar in export:
                inkscape(self.options.input_file, export_dpi=exportfilepar['dpi'], export_filename=exportfilepar['filename'], export_width=exportfilepar['size'], export_height=exportfilepar['size'])

            self.createIconFile(export, basename + ".ico")

            # inkex.utils.debug("finished")
        except Exception as e:
            inkex.errormsg("Exception occured!")

effect = CreateIconFile()
effect.run()
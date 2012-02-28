import os
from strange_case.nodes import FileNode
from PIL import Image
from shutil import copy2


class ImageNode(FileNode):
    """
    Copies a file to a destination
    """
    def generate(self, site):
        target_path = os.path.join(self.target_folder, self.target_name)
        if 'size' in self.config:
            image = Image.open(self.source_path)
            size = self.config['size']
            if isinstance(size, basestring):
                size = self.config['size'].split('x')
            # ensure working with ints - strings do nothing (no error, nothing!)
            size[0] = int(size[0])
            size[1] = int(size[1])
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(target_path)
        else:
            copy2(self.source_path, target_path)

        super(ImageNode, self).generate(site)

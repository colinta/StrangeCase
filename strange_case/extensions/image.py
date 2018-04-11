import sys
import os
from shutil import copy2
try:
    from PIL import Image
except ImportError:
    from strange_case import require_package
    require_package('Pillow')

from strange_case.nodes import AssetNode
from strange_case.registry import Registry
from strange_case.configurators import configurate


class ImageNode(AssetNode):
    """
    Copies the image, and optionally creates thumbnails for the image.
    The thumbnails are available as image_node.{thumbnail_name}
    """
    def generate_file(self, site, source_path, target_path):
        if 'size' in self.config:
            if not self['skip']:
                image = Image.open(source_path)
                size = self.config['size']

                if isinstance(size, str):
                    size = self.config['size'].split('x')
                    if len(size) == 1:
                        size = [size[0], size[0]]
                elif isinstance(size, int):
                    size = [size, size]

                # ensure working with ints - strings do nothing in Pillow (no
                # error, nothing!)
                size[0] = int(size[0])
                size[1] = int(size[1])
                image.thumbnail(size, Image.ANTIALIAS)
                image.save(target_path)
            elif self['__verbose']:
                sys.stderr.write("Skipping %s\n" % target_path)
        else:
            if not self['skip']:
                copy2(source_path, target_path)
            elif self['__verbose']:
                sys.stderr.write("Skipping %s\n" % target_path)
        self.files_tracked.append(source_path)
        self.files_written.append(target_path)


def processor(config, source_path, target_path):
    """
    If 'thumbnails' or 'thumbnail' has been set, thumbnails will be generated.

    Examples:
        thumbnail: 75x150  # one thumbnail, specifying width and height as a string
        thumbnails:  # multiple thumbnails, by name
            medium: [200, 200]  # array of [width, height]
            large: 1000         # max dimension for both width and height
        thumbnails:  # multiple thumbnails by index
            - 200  # this will be image_node.thumbnail
            - 1000  # this will be image_node.thumbnail_2
    """
    image_node = ImageNode(config, source_path, target_path)

    if 'thumbnail' in config and 'thumbnails' not in config:
        config['thumbnails'] = {'thumbnail': config['thumbnail']}

    if 'thumbnails' not in config:
        return (image_node,)

    thumbs = []
    thumb_index = 0
    for thumbnail in config['thumbnails']:
        if isinstance(config['thumbnails'], list):
            thumb_index += 1
            size = thumbnail
            thumbnail = thumb_index = 1 and 'thumbnail' or 'thumbnail_' + thumb_index
        else:
            size = config['thumbnails'][thumbnail]
        target_name, ext = os.path.splitext(image_node.target_name)
        target_name += '_' + thumbnail
        target_name += ext
        thumb_config = image_node.config_copy(name=thumbnail, target_name=target_name)
        thumb_config['size'] = size
        thumb_config['iterable'] = False
        thumb_config['is_thumbnail'] = True
        thumb_config['skip'] = config['skip']

        configurate(os.path.join(source_path, target_name), thumb_config)
        thumbnail_node = ImageNode(thumb_config, source_path, target_path)
        image_node.config[thumbnail] = thumbnail_node
        thumbs.append(thumbnail_node)
    return (image_node, ) + tuple(thumbs)

Registry.register('image', processor)
Registry.associate('image', ['*.png', '*.jpg', '*.jpeg', '*.gif',
                             '*.PNG', '*.JPG', '*.JPEG', '*.GIF'])

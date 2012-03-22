import os
from shutil import copy2
try:
    from PIL import Image
except ImportError:
    from strange_case import require_package
    require_package('PIL')

from strange_case.nodes import FileNode
from strange_case.registry import Registry


class ImageNode(FileNode):
    """
    Copies the image, and optionally creates thumbnails for the image.
    The thumbnails are available as image_node.{thumbnail_name}
    """
    def generate_file(self, site, source_path, target_path):
        if 'size' in self.config:
            image = Image.open(source_path)
            size = self.config['size']
            if isinstance(size, basestring):
                size = self.config['size'].split('x')
            # ensure working with ints - strings do nothing (no error, nothing!)
            size[0] = int(size[0])
            size[1] = int(size[1])
            image.thumbnail(size, Image.ANTIALIAS)
            image.save(target_path)
            self.files_written.append(target_path)
        else:
            copy2(source_path, target_path)
            self.files_written.append(target_path)


def processor(config, source_path, target_path):
    image_node = ImageNode(config, source_path, target_path)
    if 'thumbnails' not in config:
        return (image_node,)

    thumbs = []
    for thumbnail in config['thumbnails']:
        target_name, ext = os.path.splitext(image_node.target_name)
        target_name += '_' + thumbnail
        target_name += ext
        thumb_config = image_node.config_copy(name=thumbnail, target_name=target_name)
        thumb_config['size'] = config['thumbnails'][thumbnail]
        thumb_config['iterable'] = False
        thumb_config['is_thumbnail'] = True

        Registry.configurate(thumb_config, os.path.join(source_path, target_name))
        thumbnail_node = ImageNode(thumb_config, source_path, target_path)
        image_node.config[thumbnail] = thumbnail_node
        thumbs.append(thumbnail_node)
    return (image_node, ) + tuple(thumbs)

Registry.register('image', processor)
Registry.associate('image', ['*.png', '*.jpg', '*.jpeg', '*.gif'])

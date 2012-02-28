import os
from strange_case.nodes import ImageNode
from strange_case.registry import Registry


def image_processor(config, source_path, target_path):
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

        thumbnail_node = ImageNode(thumb_config, source_path, target_path)
        image_node.config[thumbnail] = thumbnail_node
        thumbs.append(thumbnail_node)
    return (image_node, ) + tuple(thumbs)


Registry.register('image', image_processor)

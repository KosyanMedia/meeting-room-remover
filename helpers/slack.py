def get_new_blocks(blocks):
    for block in blocks:
        # Replace in actions
        if block['type'] == 'actions':
            for element in block['elements']:
                if element['type'] == 'button' and element['action_id'] == 'cancel':
                    element['text']['text'] = element['text']['text'] + " :loading:"
                    if element.get('url') is not None:
                        del element['url']
        # replace in section
        elif block['type'] == 'section' and block.get('accessory') is not None:
            element = block.get('accessory')
            if element['type'] == 'button' and element['action_id'] == 'cancel':
                if element.get('url') is not None:
                    del element['url']

    return blocks

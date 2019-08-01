from tkinter import Tk, Canvas, mainloop

import math
import numpy as np


class Block(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rect = None

    def __repr__(self):
        return f'Block(w:{self.width}_h:{self.height}_rect:{bool(self.rect)})'


class Rect(object):
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.used = None
        self.down = None
        self.right = None

    def __repr__(self):
        return f'Rect(x:{self.x}_y:{self.y}_w:{self.width}_h:{self.height}_used:{bool(self.used)}_down:' \
            f'{bool(self.down)}_right:{bool(self.right)})'


def gen_blocks(num, min_width, max_width, min_height, max_height, mode=0):
    assert num > 0
    assert max_width > min_width
    assert max_height > min_height

    if mode == 0:
        widths = np.random.randint(min_width, max_width, num, dtype=np.int)
        heights = np.random.randint(min_width, max_width, num, dtype=np.int)
    elif mode == 1:
        widths = np.random.randint(min_width, max_width, num, dtype=np.int)
        heights = np.linspace(max_height, max_height, num, dtype=np.int)
    else:
        widths = np.linspace(min_width, max_width, num, dtype=np.int)
        heights = np.linspace(min_height, max_height, num, dtype=np.int)

    blocks = [Block(w, h) for w, h in zip(widths, heights)]
    return blocks


def get_sort_fun(sort_type):
    sort_types = dict()
    sort_types['width'] = lambda block: block.width
    sort_types['height'] = lambda block: block.height
    sort_types['area'] = lambda block: block.width * block.height
    sort_types['max_side'] = lambda block: (max(block.height, block.width), min(block.height, block.width))

    return sort_types[sort_type]


def sort_blocks(blocks, sort_type):
    sort_func = get_sort_fun(sort_type)
    blocks.sort(key=sort_func, reverse=True)

    return blocks


class RectPacking(object):
    def __init__(self, blocks, max_width=1e100, max_height=1e100):
        assert blocks
        block = blocks[0]
        self.max_width = max_width
        self.max_height = max_height

        self._root = Rect(0, 0, block.width, block.height)
        self._blocks = blocks

        self._pack()

    def _pack(self, show=True):
        for num, block in enumerate(self._blocks):
            rect = self._find_rect(self._root, block.width, block.height)
            if rect:
                block.rect = self._split_rect(rect, block.width, block.height)
            else:
                block.rect = self._grow_rect(block.width, block.height)
            if show:
                self.show(num + 1)

    def __repr__(self):
        return f'RectPacking(w:{self._root.width}_h:{self._root.height})'

    def box_size(self):
        width = self._root.width
        height = self._root.height

        width = math.pow(2, int(math.ceil(math.log(width, 2))))
        height = math.pow(2, int(math.ceil(math.log(height, 2))))
        return int(width), int(height)

    def show(self, num=0):
        width, height = self.box_size()
        master = Tk()
        w = Canvas(master, width=width, height=height, bg='red')
        for block in self._blocks[:num]:
            rect = block.rect
            x, y, width, height = rect.x, rect.y, rect.width, rect.height
            w.create_rectangle(x, y, x + width, y + height, fill="blue")
            w.create_rectangle(x, y, x + block.width, y + block.height, fill="green")
        w.pack()
        mainloop()

    def _find_rect(self, rect, width, height):
        if rect.used:
            return self._find_rect(rect.right, width, height) or self._find_rect(rect.down, width, height)
        elif width <= rect.width and height <= rect.height:
            return rect
        else:
            return None

    def _split_rect(self, rect, width, height):
        rect.used = True
        if height * rect.width < width * rect.height:
            rect.down = Rect(rect.x, rect.y + height, rect.width, rect.height - height)
            rect.right = Rect(rect.x + width, rect.y, rect.width - width, height)
        else:
            rect.down = Rect(rect.x, rect.y + height, width, rect.height - height)
            rect.right = Rect(rect.x + width, rect.y, rect.width - width, rect.height)
        return rect

    def _grow_rect(self, width, height):
        can_grow_down = (width <= self._root.width)
        can_grow_right = (height <= self._root.height)

        should_grow_right = can_grow_right and (self._root.height >= (self._root.width + width))
        should_grow_down = can_grow_down and (self._root.width >= (self._root.height + height))

        if should_grow_right:
            return self._grow_right(width, height)
        elif should_grow_down:
            return self._grow_down(width, height)
        elif can_grow_right:
            return self._grow_right(width, height)
        elif can_grow_down:
            return self._grow_down(width, height)
        else:
            raise Exception('error')

    def _grow_right(self, width, height):
        root = Rect(0, 0, self._root.width + width, self._root.height)
        root.used = True
        root.down = Rect(0, self._root.height, self._root.width + width, 0)
        root.right = Rect(self._root.width, 0, width, self._root.height)

        self._root = root
        rect = self._find_rect(self._root, width, height)
        if rect:
            return self._split_rect(rect, width, height)
        else:
            raise Exception('error')

    def _grow_down(self, width, height):
        root = Rect(0, 0, self._root.width, self._root.height + height)
        root.used = True
        root.down = Rect(0, self._root.height, self._root.width, height)
        root.right = Rect(self._root.width, 0, 0, self._root.height + height)

        self._root = root
        rect = self._find_rect(self._root, width, height)
        if rect:
            return self._split_rect(rect, width, height)
        else:
            raise Exception('error')


def main():
    blocks = gen_blocks(10, 10, 100, 10, 100, False)
    sort_blocks(blocks, 'max_side')
    RectPacking(blocks)


if __name__ == '__main__':
    main()

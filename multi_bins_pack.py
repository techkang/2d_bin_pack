from tkinter import Tk, Canvas, mainloop

import numpy as np


class Block(object):
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.index = -1
        self.rect = None

    def __repr__(self):
        return f'Block(w:{self.width}_h:{self.height}_rect:{bool(self.rect)}_index:{self.index})'


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
        self.max_width = max_width
        self.max_height = max_height
        self.max_index = 0
        self.shrink = 1.1

        self.roots = []
        self._blocks = blocks

        self._pack()

    def _pack(self, show=True):
        index = 0
        flag = True
        while flag:
            self._root = Rect(0, 0, self.max_width, self.max_height)
            flag = False
            for num, block in enumerate(self._blocks):
                if block.index != -1:
                    continue
                flag = True
                rect = self._find_rect(self._root, block.width, block.height)
                if rect:
                    block.rect = self._split_rect(rect, block.width, block.height)
                    block.index = index
                else:
                    continue
            self.roots.append(self._root)
            index += 1
        self.max_index = index - 1
        if show:
            self.show()

    def __repr__(self):
        return f'RectPacking(w:{self._root.width}_h:{self._root.height})'

    def box_size(self, root):
        width = root.width
        height = root.height

        width = 2 ** np.ceil(np.log2(width)).astype(np.int)
        height = 2 ** np.ceil(np.log2(height)).astype(np.int)
        return np.array([width, height], np.int)

    def show(self):
        master = Tk()
        w = Canvas(master, width=self.max_width * self.max_index * self.shrink, height=self.max_height, bg='red')

        coor = np.zeros(2, np.int)
        for i in range(self.max_index):
            w.create_rectangle(coor[0], 0, coor[0] + self.max_width, self.max_height, fill="white")
            for block in self._blocks:
                if block.index == i:
                    rect = block.rect
                    x, y, width, height = rect.x, rect.y, rect.width, rect.height
                    x += coor[0]
                    w.create_rectangle(x, y, x + width, y + height, fill="blue")
                    w.create_rectangle(x, y, x + block.width, y + block.height, fill="green")
            coor += (int(self.max_width * self.shrink), self.max_height)
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


def main():
    blocks = gen_blocks(20, 10, 100, 10, 100, mode=0)
    sort_blocks(blocks, 'max_side')
    RectPacking(blocks, 100, 100)


if __name__ == '__main__':
    main()

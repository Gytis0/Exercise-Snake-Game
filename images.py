WHITE = (255, 255, 255)
NO_LED = (0, 0, 0)

def five_img():
    W = WHITE; O = NO_LED
    return [O,O,W,W,W,W,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,W,W,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,W,W,W,W,O,O]

def four_img():
    W = WHITE; O = NO_LED
    return [O,O,W,O,O,O,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,O,W,O,O,O,
            O,O,W,W,W,W,O,O,
            O,O,O,O,W,O,O,O,
            O,O,O,O,W,O,O,O,
            O,O,O,O,W,O,O,O]

def three_img():
    W = WHITE; O = NO_LED
    return [O,O,W,W,W,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,W,W,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,W,W,W,W,O,O]

def two_img():
    W = WHITE; O = NO_LED
    return [O,O,W,W,W,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,O,O,O,W,O,O,
            O,O,W,W,W,W,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,O,O,O,O,O,
            O,O,W,W,W,W,O,O]

def one_img():
    W = WHITE; O = NO_LED
    return [O,O,O,O,W,O,O,O,
            O,O,O,W,W,O,O,O,
            O,O,W,O,W,O,O,O,
            O,O,O,O,W,O,O,O,
            O,O,O,O,W,O,O,O,
            O,O,O,O,W,O,O,O,
            O,O,O,O,W,O,O,O,
            O,O,O,W,W,W,O,O]

images = [five_img, four_img, three_img, two_img, one_img]
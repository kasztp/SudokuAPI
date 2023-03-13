import os
import cv2
import numpy as np
import pytesseract
from PIL import Image

test_images_dir = os.path.join(os.path.dirname(__file__)).replace("app/ocr", "tests/test_images/")
ocr_words_file = os.path.join(os.path.dirname(__file__)) + "/ocr_words.txt"
test_image = os.path.join(test_images_dir, "sudoku-wiki.jpg")
#test_image = os.path.join(test_images_dir, "distorted-sudoku.jpg")

verbose = False

# Load the Sudoku image
img = cv2.imread(test_image)

# Convert the image to grayscale
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

# Apply thresholding to create a binary image
thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

# Find the largest contour (assumed to be the Sudoku grid) and extract its corners
contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
approx = cv2.approxPolyDP(contours[0], 0.05 * cv2.arcLength(contours[0], True), True)
pts1 = np.float32([approx[0][0], approx[1][0], approx[2][0], approx[3][0]])

# Apply perspective transformation to warp the grid into a rectangular shape
pts2 = np.float32([[0, 0], [0, 450], [450, 450], [450, 0]])
M = cv2.getPerspectiveTransform(pts1, pts2)
warped = cv2.warpPerspective(img, M, (450, 450))

# Show the original and warped images
if verbose:
    cv2.imshow("Original", img)
    cv2.imshow("Warped", warped)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

# Divide the image into squares
square_size = warped.shape[0] // 9
squares = [[warped[y:y+square_size, x:x+square_size] for x in range(0, warped.shape[0], square_size)] for y in range(0, warped.shape[0], square_size)]

# Crop the middle square of each cell
squares = [[square[5:-5, 5:-5] for square in row] for row in squares]

# Show the squares as subplots
if verbose:
    import matplotlib.pyplot as plt
    fig, axs = plt.subplots(9, 9, figsize=(9, 9))
    for i in range(9):
        for j in range(9):
            axs[i, j].imshow(squares[i][j])
            axs[i, j].axis('off')
    plt.show()

# OCR each square
digits = []
for row in squares:
    row_digits = []
    for square in row:
        # Convert the image to grayscale
        gray = cv2.cvtColor(square, cv2.COLOR_BGR2GRAY)

        # Apply thresholding to create a binary image
        thresh = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY_INV, 11, 2)

        # Apply dilation to connect the broken lines
        kernel = np.ones((2, 2), np.uint8)
        thresh = cv2.dilate(thresh, kernel, iterations=1)

        # Find the contours
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        if len(contours) == 0:
            row_digits.append(0)
            continue

        # Find the largest contour and extract the digit
        contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
        x, y, w, h = cv2.boundingRect(contours[0])
        digit = thresh[y:y+h, x:x+w]

        # If no digit was found, but a contour was detected retry with a larger kernel
        if digit.size == 0:
            kernel = np.ones((4, 4), np.uint8)
            thresh = cv2.dilate(thresh, kernel, iterations=1)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            contours = sorted(contours, key=cv2.contourArea, reverse=True)[:1]
            x, y, w, h = cv2.boundingRect(contours[0])
            digit = thresh[y:y+h, x:x+w]

        # show the digit
        if verbose:
            cv2.imshow("Digit", digit)
            cv2.waitKey(0)

        # Resize the digit to 28x28 pixels
        # resized_digit = cv2.resize(digit, (28, 28), interpolation=cv2.INTER_AREA)

        # Apply OCR
        prediction = pytesseract.image_to_string(Image.fromarray(digit),
                                                 config=f"--psm 10 --oem 3 -c tessedit_char_whitelist=0123456789 --user-words {ocr_words_file}")
        if prediction == '':
            row_digits.append(0)
        else:
            row_digits.append(int(prediction))
    digits.append(row_digits)

# Print the result
print(digits)

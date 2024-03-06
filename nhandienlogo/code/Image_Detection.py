import cv2
import os
import concurrent.futures
import time
import tkinter as tk
from tkinter import filedialog
# Khởi tạo SIFT và Flann matcher ở mức global
sift = cv2.SIFT_create()
FLANN_INDEX_KDTREE = 0
index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=3)
search_params = dict(checks=100)
flann = cv2.FlannBasedMatcher(index_params, search_params)
# Định nghĩa image_templates trước khi gọi live_feed()
image_template_paths = ['D:/logo/Dr.Thanh.jpg', 'D:/logo/Hovan.PNG','D:/logo/Number1.webp', 'D:/logo/Wake-up-247.jpg','D:/logo/Vfresh.jpg','D:/logo/CocaCola.png', 'D:/logo/Fanta.png','D:/logo/RedBull.png', 'D:/logo/Sprite.webp','D:/logo/Sting.png']
image_templates = [cv2.imread(path, 0) for path in image_template_paths]
template_names = [os.path.splitext(os.path.basename(path))[0] for path in image_template_paths]

# Tối ưu hóa hàm sift_detector
def sift_detector(image1, image2):
    keypoints_1, descriptors_1 = sift.detectAndCompute(image1, None)
    keypoints_2, descriptors_2 = sift.detectAndCompute(image2, None)

    matches = flann.knnMatch(descriptors_1, descriptors_2, k=2)

    good_matches = []
    for m, n in matches:
        if m.distance < 0.7 * n.distance:
            good_matches.append(m)
    return len(good_matches)

# Các phần code khác không thay đổi

def process_template(template, cropped):
    return sift_detector(cropped, template)

def live_feed():
    cap = cv2.VideoCapture(0)
    start_time = time.time()
    frame_count = 0

    while True:
        ret, frame3 = cap.read()
        height, width = frame3.shape[:2]
        top_left_x = int(width / 3)
        top_left_y = int((height / 2) + (height / 4))
        bottom_right_x = int((width / 3) * 2)
        bottom_right_y = int((height / 2) - (height / 4))
        cv2.rectangle(frame3, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), 255, 3)
        cropped = frame3[bottom_right_y:top_left_y, top_left_x:bottom_right_x]
        
        best_match_name = None
        best_match_count = 0

        with concurrent.futures.ThreadPoolExecutor() as executor:  # Sử dụng ThreadPoolExecutor
            matches = executor.map(lambda t: process_template(t[0], t[1]), zip(image_templates, [cropped] * len(image_templates)))

        for i, match_count in enumerate(matches):
            if match_count > best_match_count:
                best_match_count = match_count
                best_match_name = template_names[i]

        threshold = 10
        if best_match_count > threshold:
            if (best_match_name=="Hovan"):
                best_match_name="Ho van"
            cv2.rectangle(frame3, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 0, 255), 3)
            cv2.putText(frame3, best_match_name, (100, 100), cv2.FONT_HERSHEY_COMPLEX, 2, (0, 0, 255), 2)

        frame_count += 1
        elapsed_time = time.time() - start_time
        fps = frame_count / elapsed_time

        cv2.putText(frame3, f"FPS: {fps:.2f}", (450, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 0, 255), 2)

        cv2.imshow('Live Feed', frame3)
        if cv2.waitKey(1) == 27:
            break

    cap.release()
    cv2.destroyAllWindows()



def video_process():
    coca = 0
    fanta = 0
    redbull = 0
    sprite = 0
    sting = 0
    skip_frames = 40  # Chỉ hiển thị mỗi 5 khung hình
    file_path = filedialog.askopenfilename()
    if file_path:
        
        cap = cv2.VideoCapture(file_path)
        start_time = time.time()
        frame_count = 0

        while True:
            ret, frame3 = cap.read()
            frame_count += 1
            if frame_count % skip_frames != 0:
                continue 
            height, width = frame3.shape[:2]
            top_left_x = int(width / 3)
            top_left_y = int((height / 2) + (height / 4))
            bottom_right_x = int((width / 3) * 2)
            bottom_right_y = int((height / 2) - (height / 4))
            cv2.rectangle(frame3, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), 255, 3)
            cropped = frame3[bottom_right_y:top_left_y, top_left_x:bottom_right_x]
            
            best_match_name = None
            best_match_count = 0

            with concurrent.futures.ThreadPoolExecutor() as executor:  # Sử dụng ThreadPoolExecutor
                matches = executor.map(lambda t: process_template(t[0], t[1]), zip(image_templates, [cropped] * len(image_templates)))

            for i, match_count in enumerate(matches):
                if match_count > best_match_count:
                    best_match_count = match_count
                    best_match_name = template_names[i]

            threshold = 10
            if best_match_count > threshold:
                cv2.rectangle(frame3, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), (0, 255, 0), 3)
                if(best_match_name=="CocaCola"):
                    coca = coca + 1
                elif(best_match_name=="Fanta"):
                    fanta = fanta + 1
                elif(best_match_name=="RedBull"):
                    redbull = redbull + 1
                elif(best_match_name=="Sprite"):
                    sprite = sprite + 1
                elif(best_match_name=="Sting"):
                    sting = sting + 1

                
            cv2.putText(frame3, "CocaCola: "+str(coca), (20, 50), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame3, "Fanta:    "+str(fanta), (20, 75), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame3, "RedBull:  "+str(redbull), (20, 100), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame3, "Sprite:   "+str(sprite), (20, 125), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)
            cv2.putText(frame3, "Sting:    "+str(sting), (20, 150), cv2.FONT_HERSHEY_COMPLEX, 0.5, (0, 0, 255), 2)
            frame_count += 1
            elapsed_time = time.time() - start_time
            fps = frame_count / elapsed_time

            cv2.putText(frame3, f"FPS: {fps:.2f}", (450, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)

            cv2.imshow('Video Process', frame3)
            if cv2.waitKey(1) == 27:
                break

        cap.release()
        cv2.destroyAllWindows()



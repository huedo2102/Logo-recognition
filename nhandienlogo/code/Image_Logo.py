import sys  # Import thư viện sys để làm việc với hệ thống
import cv2  # Import thư viện OpenCV để xử lý hình ảnh và video
import os   # Import thư viện os để làm việc với hệ thống tệp tin và thư mục
from PyQt5.QtGui import QImage, QPixmap  # Import các lớp QImage và QPixmap từ thư viện PyQt5
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QFileDialog, QTextBrowser ,QMessageBox # Import các lớp và tiện ích giao diện từ PyQt5
from PyQt5 import uic  # Import hàm uic từ PyQt5 để tải giao diện từ tệp .ui
from PyQt5.QtCore import Qt  # Import các lớp và chức năng core từ PyQt5
from Image_Detection import *
# Khởi tạo lớp chính (main window) cho ứng dụng
class MainWindow(QMainWindow):

    # Constructor của lớp MainWindow
    def __init__(self):
        super().__init__()  # Gọi constructor của lớp cha QMainWindow
        uic.loadUi("ui.ui", self)  # Tải giao diện từ tệp .ui và áp dụng nó cho cửa sổ chính
        self.pushButton.clicked.connect(self.select_image)  # Kết nối nút pushButton với phương thức select_image
        self.pushButton_2.clicked.connect(self.show_webcam)  # Kết nối nút pushButton_2 với phương thức process_image
        self.pushButton_5.clicked.connect(self.prev_image)
        self.pushButton_4.clicked.connect(self.next_image)
        self.filename = None  # Biến lưu trữ đường dẫn tệp hình ảnh được chọn
        self.filenames = []
        self.current_image_index = 0
        

    # Phương thức để phát hiện logo trong ảnh được chọn
    def detect_logo(self):
        
        input_image = cv2.imread(self.filename)  # Đọc ảnh đầu vào và chuyển nó thành ảnh grayscale
        a=input_image
        def sift_detector(new_image, image_template):
            image1 = cv2.cvtColor(new_image, cv2.COLOR_BGR2GRAY)
            image2 = image_template

            # Create SIFT detector object
            sift = cv2.SIFT_create()

            # Obtain the keypoints and descriptors using the SIFT function
            keypoints_1, descriptors_1 = sift.detectAndCompute(image1, None)
            keypoints_2, descriptors_2 = sift.detectAndCompute(image2, None)

            # Define parameters for the Flann Based Matcher
            FLANN_INDEX_KDTREE = 0
            index_params = dict(algorithm=FLANN_INDEX_KDTREE, trees=3)
            search_params = dict(checks=100)

            # Creating the Flann Matcher object
            flann = cv2.FlannBasedMatcher(index_params, search_params)

            #Computing number of similiar matches found in both the objects
            matches = flann.knnMatch(descriptors_1, descriptors_2, k=2)

            # Store the good matches using Lowe's ratio test
            good_matches = []
            for m, n in matches:
                if m.distance < 0.7 * n.distance:
                    good_matches.append(m)
            return len(good_matches)

        #Creating a list of refference images
        image_template_paths = ['D:/logo/Dr.Thanh.jpg', 'D:/logo/Hovan.PNG','D:/logo/Number1.webp', 'D:/logo/Wake-up-247.jpg','D:/logo/Vfresh.jpg','D:/logo/CocaCola.png', 'D:/logo/Fanta.png','D:/logo/RedBull.png', 'D:/logo/Sprite.webp','D:/logo/Sting.png']
        image_templates = [cv2.imread(path, 0) for path in image_template_paths]
        template_names = [os.path.splitext(os.path.basename(path))[0] for path in image_template_paths]

        # Obtaining height and width of webcam frame
        height, width = input_image.shape[:2]

        # Defining ROI Box Dimensions
        top_left_x = int(width / 3)
        top_left_y = int((height / 2) + (height / 4))
        bottom_right_x = int((width / 3) * 2)
        bottom_right_y = int((height / 2) - (height / 4))

        # Drawing a rectangular window for the region of interest
        cv2.rectangle(input_image, (top_left_x, top_left_y), (bottom_right_x, bottom_right_y), 255, 3)

        # Cropping window of observation we defined above
        cropped = input_image[bottom_right_y:top_left_y, top_left_x:bottom_right_x]

        # Flipping the frame orientation horizontally
        input_image = cv2.flip(input_image, 1)

        # Biến để theo dõi tên ảnh khớp nhất
        best_match_name = None
        best_match_count = 0

        for i, template in enumerate(image_templates):
            matches = sift_detector(cropped, template)
            
            # Update the name of the best matching image if a better match is found
            if matches > best_match_count:
                best_match_count = matches
                best_match_name = template_names[i]
                best_logo_image = image_templates[i]
        threshold = 10
        if best_match_count > threshold:
            if (best_match_name=="Hovan"):
                best_match_name="Hổ vằn"
            self.plainTextEdit_3.setPlainText(f"logo {best_match_name}")  # Hiển thị thông báo về logo
            
            keypoints_logo, descriptors_logo = cv2.SIFT_create().detectAndCompute(best_logo_image, None)  # Trích xuất đặc trưng từ logo tốt nhất
            keypoints_input, descriptors_input = cv2.SIFT_create().detectAndCompute(cropped, None)
            bf = cv2.BFMatcher()  # Tạo lại bộ so khớp
            matches = bf.knnMatch(descriptors_input, descriptors_logo, k=2)  # Tìm lại các khớp gần nhau
            good_matches = []
            for m, n in matches:
                if m.distance < 0.75 * n.distance:
                    good_matches.append(m)
            
            output_image = cv2.drawMatches(cropped, keypoints_input, best_logo_image, keypoints_logo, good_matches, None)  # Vẽ các khớp lên ảnh đầu vào và logo tốt nhất
            qimage = QImage(output_image.data, output_image.shape[1], output_image.shape[0], output_image.strides[0], QImage.Format_RGB888)  # Tạo QImage từ ảnh đầu ra
            pixmap2 = QPixmap.fromImage(qimage).scaled(self.label_3.width(), self.label_3.height(), Qt.KeepAspectRatio)  # Tạo QPixmap và thay đổi kích thước để hiển thị trên label_3
            self.label_3.setPixmap(pixmap2)  # Đặt pixmap lên label_3
        else:
            self.plainTextEdit_3.setPlainText("Không nhận diện được")  # Hiển thị thông báo khi không nhận diện được logo
    # Phương thức để chọn ảnh từ tệp tin
    def select_image(self):
        
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.ExistingFiles)
        file_dialog.setNameFilter("Tệp hình ảnh (*.png *.jpg *.bmp *.webp *.jpeg)")
        file_path, _ = file_dialog.getOpenFileNames(self, "Chọn ảnh", "", "Tệp hình ảnh (*.png *.jpg *.bmp *.webp *.jpeg)")
        if file_path:
            self.filename = file_path[0]  # Lấy đường dẫn của ảnh được chọn
            name = os.path.dirname(self.filename)
            self.filenames = [os.path.join(name, file) for file in os.listdir(name) if
                              file.lower().endswith(('.png', '.jpg', '.bmp', '.webp', '.jpeg'))]
            # Tìm chỉ số của self.filename trong self.filenames và gán cho self.current_image_index
            for index, file in enumerate(self.filenames):
                
                if os.path.basename(self.filename) == os.path.basename(file):
                    self.current_image_index = index
                    break  # Nếu tìm thấy, thoát khỏi vòng lặp
            
            self.show_image()  # Gọi phương thức để phát hiện logo trong ảnh
    def select_images(self):
        options = QFileDialog.Options()
        options |= QFileDialog.ReadOnly
        folder_dialog = QFileDialog()
        folder_dialog.setFileMode(QFileDialog.Directory)
        folder_dialog.setOption(QFileDialog.ShowDirsOnly, True)
        folder_path = folder_dialog.getExistingDirectory(self, "Chọn thư mục")
        if folder_path:
            self.filenames = [os.path.join(folder_path, file) for file in os.listdir(folder_path) if
                              file.lower().endswith(('.png', '.jpg', '.bmp', '.webp', '.jpeg'))]
            if self.filenames:
                self.current_image_index = 0
                self.show_image()

    def prev_image(self):
        if self.filenames == []:
            confirm = QMessageBox.question(self, "Cảnh báo", "Vui lòng chọn thư mục. Tiếp tục?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.No:
                return
            else:
                self.select_images()
        else:
            self.current_image_index -= 1
            if self.current_image_index < 0:
                self.current_image_index = len(self.filenames) - 1
            self.show_image()


            
    def next_image(self):
        if self.filenames == []:
            confirm = QMessageBox.question(self, "Cảnh báo", "Vui lòng chọn thư mục. Tiếp tục?", QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
            if confirm == QMessageBox.No:
                return
            else:
                self.select_images()
        else:
            self.current_image_index += 1
            if self.current_image_index >= len(self.filenames):
                self.current_image_index = 0
            self.show_image()

    def show_image(self):
        self.plainTextEdit_3.clear()
        self.label.clear()  # Xóa nội dung trên label để hiển thị ảnh mới
        self.label_3.clear()  # Xóa nội dung trên label_3 để hiển thị ảnh mới
        self.filename = self.filenames[self.current_image_index]
        pixmap = QPixmap(self.filename).scaled(self.label.width(), self.label.height(), Qt.KeepAspectRatio)
        self.label.setPixmap(pixmap)
        self.detect_logo()
    def show_webcam(self):
        self.plainTextEdit_3.clear()
        self.label.clear()  # Xóa nội dung trên label để hiển thị ảnh mới
        self.label_3.clear()  # Xóa nội dung trên label_3 để hiển thị ảnh mới
        live_feed()
# Hàm chính của chương trình
if __name__ == "__main__":
    app = QApplication(sys.argv)  # Tạo đối tượng ứng dụng QApplication
    mainWindow = MainWindow()  # Tạo đối tượng chính của ứng dụng MainWindow
    mainWindow.show()  # Hiển thị cửa sổ chính
    sys.exit(app.exec_())  # Khởi động ứng dụng và bắt đầu vòng lặp chính của ứng dụng

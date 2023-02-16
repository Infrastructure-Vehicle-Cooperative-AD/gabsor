# gabsor
Compress your rosbag

## Install

#### ROS Interface (Ubuntu)
```bash
pip install --extra-index-url https://rospypi.github.io/simple/ rospy rosbag
```
#### Python Library
```bash
pip install -r requirements.txt
```

#### Install gabsor
```bash
pip install -e .
```

## Usage

#### Compress rosbag
```python
from gabsor.ros_interface import ROSInterface

# Compress your rosbag
ROSInterface.compress_bag('input.bag', 'output_path')
```

#### Compress pcd and img files
```python
from gabsor.pcd import PCDReader
from gabsor.img import ImgReader

# Compress your pcd file to the zip file
PCDReader.compress_pcd('input.pcd', 'output.laz', debug_flag)
# Decompress the zip file to python dict
data_dict = PCDReader.read_compress_pcd('output.laz')

# Compress your image file to the numpy bytes array
ImgReader.compress_img('input.png', 'output.npy', debug_flag)
# Decompress the numpy bytes array to the numpy/opencv image
img = ImgReader.read_compress_img('output.npy')
```

### Compress Rate
* Image: about 23%
* PointCloud: about 19%
* Ros Bag: about 10%

ROS Bag (180G) -> Valid Data (74G) -> Compressed files (17G)

## TODO
- [ ] Transfer the compressed files to a ROS Bag
- [ ] Handle ROS Message array
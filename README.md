# gabsor
Compress your rosbag

## Usage

#### Compress pcd file
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

ROS Bag (180G) -> Valid Data (74G) -> Compressed files (17G)

## TODO
- [ ] Read and compress rosbag
- [ ] Compress other structured data 
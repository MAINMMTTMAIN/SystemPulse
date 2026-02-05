# SmartBatGuard

A lightweight system monitor built with Python that tracks CPU, RAM, battery, and GPU usage in real-time.

## Features
- Real-time stats with progress bars (Tkinter GUI)
- Desktop notifications for high usage or low battery
- Simple future usage prediction using linear regression
- Interactive real-time chart (Plotly)
- Weekly usage report export to PDF
- List of top CPU-consuming processes

## Requirements
- Python 3.8+
- See [requirements.txt](requirements.txt)

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/SmartBatGuard.git
cd SmartBatGuard
pip install -r requirements.txt
python main.py
```
## Usage Tips

GPU monitoring works best with NVIDIA graphics cards.
The weekly PDF report needs some accumulated data to show meaningful graphs.
Run the program for a while to collect enough logs.

## Contributing
Feel free to open issues or submit pull requests!
## License
MIT License – see LICENSE for details
Made with ❤️ in Python

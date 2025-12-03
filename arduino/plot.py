#!/usr/bin/env python3
import sys
import pyqtgraph as pg
from pyqtgraph.Qt import QtCore, QtWidgets
from collections import deque
import threading

class RealtimePlotter:
    def __init__(self):
        self.app = QtWidgets.QApplication(sys.argv)
        
        # Data storage (last 50 values)
        self.y_data = deque(maxlen=50)
        self.z_data = deque(maxlen=50)
        self.x_data = deque(maxlen=50)
        self.counter = 0
        
        # Create window with two plots
        self.win = pg.GraphicsLayoutWidget(show=True, title="Real-time Plotter")
        self.win.resize(800, 600)
        
        # Y plot
        self.plot_y = self.win.addPlot(title="Y Values")
        self.plot_y.setLabel('left', 'Y')
        self.plot_y.setLabel('bottom', 'Index')
        self.curve_y = self.plot_y.plot(pen='y')
        
        # Z plot (next row)
        self.win.nextRow()
        self.plot_z = self.win.addPlot(title="Z Values")
        self.plot_z.setLabel('left', 'Z')
        self.plot_z.setLabel('bottom', 'Index')
        self.curve_z = self.plot_z.plot(pen='c')
        
        # Set up timer for updating plots
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plots)
        self.timer.start(50)  # Update every 50ms
        
        # Start stdin reading thread
        self.running = True
        self.stdin_thread = threading.Thread(target=self.read_stdin, daemon=True)
        self.stdin_thread.start()
    
    def read_stdin(self):
        """Read from stdin in a separate thread"""
        for line in sys.stdin:
            if not self.running:
                break
            try:
                line = line.strip()
                if not line:
                    continue
                    
                y_str, z_str = line.split(',')
                y = float(y_str)
                z = float(z_str)
                
                self.y_data.append(y)
                self.z_data.append(z)
                self.x_data.append(self.counter)
                self.counter += 1
                
            except (ValueError, IndexError) as e:
                print(f"Error parsing line: {line} - {e}", file=sys.stderr)
    
    def update_plots(self):
        """Update the plots with current data"""
        if len(self.y_data) > 0:
            x = list(self.x_data)
            y = list(self.y_data)
            z = list(self.z_data)
            
            self.curve_y.setData(x, y)
            self.curve_z.setData(x, z)
    
    def run(self):
        """Start the application"""
        self.app.exec_()
        self.running = False

if __name__ == '__main__':
    plotter = RealtimePlotter()
    plotter.run()

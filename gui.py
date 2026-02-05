import tkinter as tk
from tkinter import ttk, messagebox
import plotly.graph_objects as go
from plotly.offline import plot
import threading
from monitor_core import start_monitoring, data_log  # data_log رو مستقیم ایمپورت کردیم
from utils import export_to_pdf, get_top_processes
import pandas as pd  # برای df در update_chart

class SystemMonitorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SmartBatGuard - System Monitor")
        self.root.geometry("700x500")
        
        # Labels for real-time stats
        self.cpu_label = ttk.Label(self.root, text="CPU: 0%")
        self.cpu_label.pack(pady=5)
        self.ram_label = ttk.Label(self.root, text="RAM: 0%")
        self.ram_label.pack(pady=5)
        self.bat_label = ttk.Label(self.root, text="Battery: N/A")
        self.bat_label.pack(pady=5)
        self.gpu_label = ttk.Label(self.root, text="GPU: N/A")
        self.gpu_label.pack(pady=5)
        
        # Progress bars
        self.cpu_progress = ttk.Progressbar(self.root, maximum=100, length=300)
        self.cpu_progress.pack(pady=5)
        self.ram_progress = ttk.Progressbar(self.root, maximum=100, length=300)
        self.ram_progress.pack(pady=5)
        
        # Buttons
        ttk.Button(self.root, text="Generate Weekly PDF Report", command=self.export_report).pack(pady=10)
        ttk.Button(self.root, text="Show Top CPU Processes", command=self.show_top_procs).pack(pady=5)
        
        # دکمه جدید برای نمودار
        ttk.Button(self.root, text="Show Live Usage Chart", command=self.update_chart).pack(pady=10)
        
        ttk.Label(self.root, text="Click the button above to view interactive chart (updates with recent data)").pack(pady=5)
        
        # Start monitoring in background thread
        threading.Thread(target=start_monitoring, args=(self.update_gui,), daemon=True).start()
        
        self.root.mainloop()
    
    def update_gui(self, stats):
        self.cpu_label.config(text=f"CPU: {stats['cpu']}%")
        self.ram_label.config(text=f"RAM: {stats['ram']}%")
        bat_text = f"Battery: {stats['battery']}%" if stats['battery'] else "Battery: N/A"
        bat_text += f" (Plugged: {'Yes' if stats['plugged'] else 'No'})"
        self.bat_label.config(text=bat_text)
        
        gpu_text = f"GPU: {stats['gpu_usage']}% (Temp: {stats['gpu_temp']}°C)" if stats['gpu_usage'] is not None else "GPU: N/A"
        self.gpu_label.config(text=gpu_text)
        
        self.cpu_progress['value'] = stats['cpu']
        self.ram_progress['value'] = stats['ram']
    
    def update_chart(self):
        df = pd.DataFrame(data_log[-120:])  # last ~20 minutes
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=df['time'], y=df['cpu'], mode='lines', name='CPU'))
        fig.add_trace(go.Scatter(x=df['time'], y=df['ram'], mode='lines', name='RAM'))
        if 'battery' in df.columns and df['battery'].notna().any():
            fig.add_trace(go.Scatter(x=df['time'], y=df['battery'], mode='lines', name='Battery'))
        if 'gpu_usage' in df.columns and df['gpu_usage'].notna().any():
            fig.add_trace(go.Scatter(x=df['time'], y=df['gpu_usage'], mode='lines', name='GPU'))
        fig.update_layout(title='Real-Time System Usage', xaxis_title='Time', yaxis_title='Usage (%)')
        fig.show()  # opens in default browser - best for tkinter compatibility
    
    def export_report(self):
        try:
            path = export_to_pdf('logs/system_log.csv')
            messagebox.showinfo("Report Ready", f"Weekly PDF saved at:\n{path}")
        except ValueError as ve:
            messagebox.showerror("Report Error", str(ve))
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate report:\n{str(e)}")
    
    def show_top_procs(self):
        top = get_top_processes(5)
        messagebox.showinfo("Top Processes", f"Top CPU consumers:\n{top}\n\nSuggestion: Kill unnecessary ones if needed.")
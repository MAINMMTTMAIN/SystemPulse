from plyer import notification
import psutil
import matplotlib.pyplot as plt
import pandas as pd
from tkinter import messagebox

def notify(title, message):
    notification.notify(title=title, message=message, timeout=10)

def get_top_processes(top_n=5):
    procs = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            cpu = proc.info['cpu_percent']
            if cpu > 0:
                procs.append((proc.info['name'], cpu))
        except:
            pass
    procs.sort(key=lambda x: x[1], reverse=True)
    return ', '.join([f"{name} ({cpu:.1f}%)" for name, cpu in procs[:top_n]])

def optimize_interval(current_interval):
    return max(30, current_interval)  

def export_to_pdf(log_file, period='weekly'):
    df = pd.read_csv(log_file)
    if len(df) < 10:  
        raise ValueError("Not enough data to generate report. Run the app longer!")
    
    df['time'] = pd.to_datetime(df['time'])
    df.set_index('time', inplace=True)  
    
    if period == 'weekly':
        df_period = df.resample('W').mean(numeric_only=True)
        if len(df_period) < 2:  
            raise ValueError("Not enough weeks of data. Collect data over multiple weeks!")
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df_period.index, df_period['cpu'], label='CPU')
    ax.plot(df_period.index, df_period['ram'], label='RAM')
    if 'battery' in df_period.columns:
        ax.plot(df_period.index, df_period['battery'], label='Battery')
    if 'gpu_usage' in df_period.columns:
        ax.plot(df_period.index, df_period['gpu_usage'], label='GPU Usage')
    ax.legend()
    ax.set_title('Weekly System Usage Report')
    ax.set_xlabel('Week')
    ax.set_ylabel('Usage (%)')
    ax.grid(True)
    
    pdf_path = 'logs/weekly_report.pdf'
    fig.savefig(pdf_path, bbox_inches='tight')
    plt.close(fig)

    return pdf_path

import psutil
import time
import schedule
import pandas as pd
from predictor import predict_usage
from utils import notify, get_top_processes, optimize_interval, export_to_pdf
import GPUtil  # برای GPU
import os

# تنظیمات اولیه
INTERVAL = 10  # ثانیه
THRESHOLD_CPU = 80
THRESHOLD_RAM = 80
THRESHOLD_BATTERY = 20
LOG_FILE = 'logs/system_log.csv'
data_log = []  # لیست برای داده‌ها (برای پیش‌بینی و لاگ)

def get_system_stats():
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    battery = psutil.sensors_battery()
    bat_percent = battery.percent if battery else None
    bat_power_plugged = battery.power_plugged if battery else None
    
    # GPU
    gpu_usage = None
    gpu_temp = None
    try:
        gpus = GPUtil.getGPUs()
        if gpus:
            gpu = gpus[0]  # اولین GPU
            gpu_usage = gpu.load * 100
            gpu_temp = gpu.temperature
    except:
        pass  # اگر GPU نبود، رد شو
    
    return {
        'time': time.strftime("%Y-%m-%d %H:%M:%S"),
        'cpu': cpu,
        'ram': ram,
        'battery': bat_percent,
        'plugged': bat_power_plugged,
        'gpu_usage': gpu_usage,
        'gpu_temp': gpu_temp
    }

def monitor_system(gui_update_callback=None):
    stats = get_system_stats()
    data_log.append(stats)
    
    # این دو خط جدید اضافه شدن تا فولدر logs اتوماتیک ساخته بشه
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    
    df = pd.DataFrame(data_log)
    df.to_csv(LOG_FILE, index=False)
    
    # چک threshold و اعلان
    if stats['cpu'] > THRESHOLD_CPU:
        notify("CPU Warning", f"CPU usage: {stats['cpu']}%")
    if stats['ram'] > THRESHOLD_RAM:
        notify("RAM Warning", f"RAM usage: {stats['ram']}%")
    if stats['battery'] and stats['battery'] < THRESHOLD_BATTERY:
        notify("Battery Warning", f"Battery: {stats['battery']}% – Plug in charger!")
    
    # پیش‌بینی (هر ۱۰ چک، یعنی حدود ۱-۲ دقیقه)
    if len(data_log) % 10 == 0:
        pred_cpu = predict_usage(data_log, 'cpu')
        pred_ram = predict_usage(data_log, 'ram')
        if pred_cpu > THRESHOLD_CPU:
            notify("CPU Prediction", f"Predicted CPU usage: {pred_cpu:.2f}% – Be careful!")
    
    # بهینه‌سازی باتری
    if stats['battery'] and stats['battery'] < 30 and not stats['plugged']:
        global INTERVAL
        INTERVAL = optimize_interval(INTERVAL)  # بیشتر کن
        top_procs = get_top_processes(5)
        notify("Battery Optimization", f"Low battery! Top consumers: {top_procs}\nSuggestion: Consider killing some processes")
    
    # آپدیت GUI اگر کال‌بک باشه
    if gui_update_callback:
        gui_update_callback(stats)

# اسکجول اولیه
def start_monitoring(gui_update_callback=None):
    schedule.every(INTERVAL).seconds.do(monitor_system, gui_update_callback)
    while True:
        schedule.run_pending()
        time.sleep(1)
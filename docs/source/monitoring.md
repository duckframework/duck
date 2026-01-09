# 📊 Duck System Monitor

Keep track of **real-time metrics** for your Duck processes with ease.  
Includes **per-process stats** and a **visual history table** to help you spot trends and potential bottlenecks.  

---

## 🌟 Key Features

- 🔄 Rolling history buffer for system metrics:  
  `cpu_total`, `ram_percent`, `disk_percent`, `net_up`, `net_down`  
- 📈 Visual table with **sparklines** showing min/max/avg/current values  
- ⚡ Configurable history length (default: 8 samples)  
- 🖥 Monitor Duck processes individually: CPU%, RAM%, Threads, Disk I/O, Network I/O  
- ✨ Wildcard support for process names, e.g., `duck*`  

---

## 🚀 Usage

Start monitoring Duck system metrics:

```py
duck monitor
```

You will see output similar to this image:  
[!](duck-monitor.png)

---

### 🔧 Parameters

| Parameter            | Type                  | Description                                                                 | Default       |
|----------------------|----------------------|-----------------------------------------------------------------------------|---------------|
| `interval`           | `float`              | Refresh interval in seconds                                                 | `1.0`         |
| `duck_process_name`  | `str`                | Process name pattern (supports wildcards `*` & `?`)                         | `"duck*"`     |
| `duck_pids`          | `Optional[List[int]]`| Specific process IDs to monitor                                             | `None`        |
| `sort_by`            | `str`                | Metric to sort processes by (`"cpu"` or `"ram"`)                             | `"cpu"`       |
| `cpu_warning`        | `float`              | CPU usage threshold (%) for warnings                                        | `80.0`        |
| `ram_warning`        | `float`              | RAM usage threshold (%) for warnings                                        | `80.0`        |
| `history_length`     | `int`                | Number of recent samples for visuals/history table                           | `8`           |

---

## ⚡ Notes

- Some metrics may require **root permissions**; run with `sudo` if needed.  
- Designed for Duck processes, but you can monitor other processes using wildcards or specific PIDs.  

---

✨ With Duck System Monitor, you can **see your system in action in real-time**, making it easier to detect and troubleshoot performance issues.

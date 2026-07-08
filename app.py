from flask import Flask, render_template_string, request, jsonify
import os
import json

app = Flask(__name__)
DATA_FILE = "devices.json"

def load_devices():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {
        "Smart Light A1": {"room": "Classroom A", "status": "online"},
        "Projector B2": {"room": "Classroom B", "status": "online"},
        "Thermostat C3": {"room": "Classroom C", "status": "online"},
        "Smart Board D1": {"room": "Classroom D", "status": "online"},
        "Camera E2": {"room": "Lab E", "status": "online"}
    }

def save_devices(devices):
    with open(DATA_FILE, "w") as f:
        json.dump(devices, f, indent=2)

devices = load_devices()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bright Minds Academy • Smart Device Manager</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Space+Grotesk:wght@500;600&display=swap');
        body { font-family: 'Inter', system_ui, sans-serif; }
        .logo-font { font-family: 'Space Grotesk', sans-serif; }
        .device-card { transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1); }
        .device-card:hover { transform: translateY(-4px); box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1); }
        .table-row { transition: all 0.2s ease; }
        .table-row:hover { background-color: #f8fafc; }
    </style>
</head>
<body class="bg-zinc-950 text-zinc-200">
    <div class="flex h-screen">
        <div class="w-72 bg-zinc-900 border-r border-zinc-800 flex flex-col">
            <div class="p-6 border-b border-zinc-800">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 bg-yellow-400 rounded-2xl flex items-center justify-center text-zinc-900 font-bold text-2xl">B</div>
                    <div><span class="logo-font text-2xl font-semibold tracking-tighter">BRIGHT MINDS</span></div>
                </div>
                <p class="text-xs text-zinc-500 mt-1">Academy • Smart Campus</p>
            </div>
            <div class="p-4">
                <div onclick="showSection('dashboard')" class="nav-item flex items-center gap-3 px-4 py-3 rounded-2xl hover:bg-zinc-800 cursor-pointer bg-zinc-800">
                    <i class="fa-solid fa-house w-5"></i><span class="font-medium">Dashboard</span>
                </div>
                <div onclick="showSection('devices')" class="nav-item flex items-center gap-3 px-4 py-3 rounded-2xl hover:bg-zinc-800 cursor-pointer mt-1">
                    <i class="fa-solid fa-lightbulb w-5"></i><span class="font-medium">All Devices</span>
                </div>
            </div>
        </div>

        <div class="flex-1 flex flex-col">
            <nav class="bg-zinc-900 border-b border-zinc-800 px-8 py-5 flex items-center justify-between">
                <h1 id="page-title" class="text-2xl font-semibold tracking-tight">Smart Device Manager</h1>
                <div class="flex items-center gap-6">
                    <div class="relative">
                        <input id="search-input" onkeyup="if(event.key === 'Enter') searchDevice()" type="text" placeholder="Search devices..." class="bg-zinc-800 border border-zinc-700 rounded-2xl pl-10 py-3 w-80 focus:outline-none focus:border-yellow-400">
                        <i class="fa-solid fa-magnifying-glass absolute left-4 top-3.5 text-zinc-500"></i>
                    </div>
                    <button onclick="showAddModal()" class="flex items-center gap-2 bg-yellow-400 hover:bg-yellow-300 text-zinc-900 px-6 py-3 rounded-2xl font-semibold">
                        <i class="fa-solid fa-plus"></i><span>Add Device</span>
                    </button>
                </div>
            </nav>

            <div id="dashboard-section" class="flex-1 p-8 overflow-auto">
                <div class="grid grid-cols-4 gap-6 mb-10">
                    <div class="bg-zinc-900 rounded-3xl p-6"><div class="flex justify-between"><div><p class="text-zinc-400 text-sm">Total Devices</p><p id="total-devices" class="text-5xl font-semibold mt-2">5</p></div><div class="w-12 h-12 bg-yellow-400/10 text-yellow-400 rounded-2xl flex items-center justify-center text-3xl">📟</div></div></div>
                    <div class="bg-zinc-900 rounded-3xl p-6"><div class="flex justify-between"><div><p class="text-zinc-400 text-sm">Online</p><p id="online-count" class="text-5xl font-semibold mt-2 text-emerald-400">5</p></div><div class="w-12 h-12 bg-emerald-400/10 text-emerald-400 rounded-2xl flex items-center justify-center text-3xl">✅</div></div></div>
                    <div class="bg-zinc-900 rounded-3xl p-6"><div class="flex justify-between"><div><p class="text-zinc-400 text-sm">Offline</p><p id="offline-count" class="text-5xl font-semibold mt-2 text-red-400">0</p></div><div class="w-12 h-12 bg-red-400/10 text-red-400 rounded-2xl flex items-center justify-center text-3xl">⭕</div></div></div>
                    <div class="bg-zinc-900 rounded-3xl p-6"><div class="flex justify-between"><div><p class="text-zinc-400 text-sm">Maintenance</p><p id="maintenance-count" class="text-5xl font-semibold mt-2 text-amber-400">0</p></div><div class="w-12 h-12 bg-amber-400/10 text-amber-400 rounded-2xl flex items-center justify-center text-3xl">🔧</div></div></div>
                </div>
                <h2 class="text-xl font-semibold mb-6">Live Devices</h2>
                <div id="live-devices-grid" class="grid grid-cols-3 gap-6"></div>
            </div>

            <div id="devices-section" class="flex-1 p-8 overflow-auto hidden">
                <div class="bg-zinc-900 rounded-3xl overflow-hidden">
                    <div class="px-8 py-6 border-b border-zinc-800 flex justify-between items-center">
                        <h2 class="text-xl font-semibold">All Devices</h2>
                        <button onclick="refreshDevices()" class="text-yellow-400 hover:text-yellow-300 flex items-center gap-2">
                            <i class="fa-solid fa-arrows-rotate"></i> Refresh
                        </button>
                    </div>
                    <table class="w-full">
                        <thead><tr class="border-b border-zinc-800">
                            <th class="text-left px-8 py-5 text-zinc-400">Device</th>
                            <th class="text-left px-8 py-5 text-zinc-400">Location</th>
                            <th class="text-left px-8 py-5 text-zinc-400">Status</th>
                            <th class="text-right px-8 py-5 text-zinc-400">Actions</th>
                        </tr></thead>
                        <tbody id="devices-table-body" class="divide-y divide-zinc-800"></tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>

    <!-- Modals (Add & Update) - Same as before -->
    <div id="add-modal" class="hidden fixed inset-0 bg-black/70 flex items-center justify-center z-50">
        <div class="bg-zinc-900 rounded-3xl w-full max-w-md mx-4">
            <div class="px-8 py-6 border-b border-zinc-800 flex justify-between">
                <h3 class="text-xl font-semibold">Add New Device</h3>
                <button onclick="hideAddModal()" class="text-3xl text-zinc-400 hover:text-white">×</button>
            </div>
            <div class="p-8 space-y-6">
                <div><label class="block text-sm text-zinc-400 mb-2">Device Name</label>
                <input id="add-name" type="text" class="w-full bg-zinc-800 border border-zinc-700 rounded-2xl px-5 py-4 focus:outline-none focus:border-yellow-400" placeholder="Smart Light F1"></div>
                <div><label class="block text-sm text-zinc-400 mb-2">Room / Location</label>
                <input id="add-room" type="text" class="w-full bg-zinc-800 border border-zinc-700 rounded-2xl px-5 py-4 focus:outline-none focus:border-yellow-400" placeholder="Classroom F"></div>
            </div>
            <div class="px-8 py-6 border-t border-zinc-800 flex gap-3">
                <button onclick="hideAddModal()" class="flex-1 py-4 rounded-2xl border border-zinc-700 hover:bg-zinc-800">Cancel</button>
                <button onclick="addDevice()" class="flex-1 py-4 bg-yellow-400 text-zinc-900 rounded-2xl font-semibold hover:bg-yellow-300">Add Device</button>
            </div>
        </div>
    </div>

    <div id="update-modal" class="hidden fixed inset-0 bg-black/70 flex items-center justify-center z-50">
        <div class="bg-zinc-900 rounded-3xl w-full max-w-md mx-4">
            <div class="px-8 py-6 border-b border-zinc-800">
                <h3 class="text-xl font-semibold">Update Status</h3>
                <p id="update-device-name" class="text-yellow-400"></p>
            </div>
            <div class="p-8 space-y-3">
                <button onclick="updateStatus('online')" class="w-full text-left px-6 py-5 rounded-2xl hover:bg-emerald-400/10 flex items-center gap-4"><div class="w-6 h-6 bg-emerald-400 rounded-xl flex items-center justify-center text-xs font-bold">ON</div><div><div class="font-medium">Online</div><div class="text-sm text-zinc-500">Working normally</div></div></button>
                <button onclick="updateStatus('offline')" class="w-full text-left px-6 py-5 rounded-2xl hover:bg-red-400/10 flex items-center gap-4"><div class="w-6 h-6 bg-red-400 rounded-xl flex items-center justify-center text-xs font-bold">OFF</div><div><div class="font-medium">Offline</div><div class="text-sm text-zinc-500">Not responding</div></div></button>
                <button onclick="updateStatus('maintenance')" class="w-full text-left px-6 py-5 rounded-2xl hover:bg-amber-400/10 flex items-center gap-4"><div class="w-6 h-6 bg-amber-400 rounded-xl flex items-center justify-center text-xs font-bold">M</div><div><div class="font-medium">Maintenance</div><div class="text-sm text-zinc-500">Under service</div></div></button>
            </div>
            <div class="px-8 py-6 border-t border-zinc-800">
                <button onclick="hideUpdateModal()" class="w-full py-4 rounded-2xl border border-zinc-700 hover:bg-zinc-800">Close</button>
            </div>
        </div>
    </div>

    <script>
        let currentDevices = {};
        let currentEditDevice = null;

        function loadDevices() {
            fetch('/api/devices').then(r => r.json()).then(data => {
                currentDevices = data;
                renderAll();
            });
        }

        function renderAll() {
            renderStats(); renderLiveGrid(); renderTable();
        }

        function renderStats() {
            const total = Object.keys(currentDevices).length;
            let online = 0, offline = 0, maint = 0;
            Object.values(currentDevices).forEach(d => {
                if (d.status === 'online') online++;
                else if (d.status === 'offline') offline++;
                else maint++;
            });
            document.getElementById('total-devices').textContent = total;
            document.getElementById('online-count').textContent = online;
            document.getElementById('offline-count').textContent = offline;
            document.getElementById('maintenance-count').textContent = maint;
        }

        function renderLiveGrid() {
            const container = document.getElementById('live-devices-grid');
            container.innerHTML = '';
            Object.entries(currentDevices).slice(0, 6).forEach(([name, info]) => {
                const statusClass = info.status === 'online' ? 'bg-emerald-500' : info.status === 'offline' ? 'bg-red-500' : 'bg-amber-500';
                const card = document.createElement('div');
                card.className = `device-card bg-zinc-900 rounded-3xl p-6 cursor-pointer`;
                card.innerHTML = `<div class="flex justify-between"><div><div class="font-semibold">${name}</div><div class="text-sm text-zinc-400">${info.room}</div></div><span class="${statusClass} text-xs px-4 py-1.5 rounded-2xl text-white">${info.status.toUpperCase()}</span></div><div onclick="editDevice('${name}');event.stopImmediatePropagation()" class="mt-6 text-yellow-400 text-sm flex items-center gap-2 cursor-pointer"><i class="fa-solid fa-pen"></i> Update Status</div>`;
                card.onclick = () => viewDevice(name);
                container.appendChild(card);
            });
        }

        function renderTable() {
            const tbody = document.getElementById('devices-table-body');
            tbody.innerHTML = '';
            Object.entries(currentDevices).forEach(([name, info]) => {
                const statusClass = info.status === 'online' ? 'bg-emerald-400 text-emerald-950' : info.status === 'offline' ? 'bg-red-400 text-white' : 'bg-amber-400 text-amber-950';
                const row = document.createElement('tr');
                row.className = 'table-row';
                row.innerHTML = `<td class="px-8 py-6 font-medium">${name}</td><td class="px-8 py-6 text-zinc-400">${info.room}</td><td class="px-8 py-6"><span class="px-5 py-1 rounded-3xl text-xs font-semibold ${statusClass}">${info.status.toUpperCase()}</span></td><td class="px-8 py-6 text-right"><button onclick="editDevice('${name}');event.stopImmediatePropagation()" class="text-yellow-400 hover:text-yellow-300 mr-6"><i class="fa-solid fa-pen"></i></button><button onclick="deleteDevice('${name}');event.stopImmediatePropagation()" class="text-red-400 hover:text-red-300"><i class="fa-solid fa-trash"></i></button></td>`;
                tbody.appendChild(row);
            });
        }

        function showSection(section) {
            document.getElementById('dashboard-section').classList.toggle('hidden', section !== 'dashboard');
            document.getElementById('devices-section').classList.toggle('hidden', section !== 'devices');
            document.getElementById('page-title').textContent = section === 'dashboard' ? 'Dashboard' : 'All Devices';
        }

        function showAddModal() { document.getElementById('add-modal').classList.remove('hidden'); }
        function hideAddModal() { document.getElementById('add-modal').classList.add('hidden'); }

        function addDevice() {
            const name = document.getElementById('add-name').value.trim();
            const room = document.getElementById('add-room').value.trim();
            if (!name || !room) return alert("All fields required");
            fetch('/api/devices', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({name, room})})
            .then(r => r.json()).then(data => { if (data.success) { hideAddModal(); loadDevices(); } else alert(data.message || "Failed"); });
        }

        function editDevice(name) {
            currentEditDevice = name;
            document.getElementById('update-device-name').textContent = name;
            document.getElementById('update-modal').classList.remove('hidden');
        }

        function hideUpdateModal() { document.getElementById('update-modal').classList.add('hidden'); }

        function updateStatus(status) {
            if (!currentEditDevice) return;
            fetch(`/api/devices/${encodeURIComponent(currentEditDevice)}`, {method: 'PUT', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({status})})
            .then(r => r.json()).then(data => { if (data.success) { hideUpdateModal(); loadDevices(); } });
        }

        function deleteDevice(name) {
            if (!confirm(`Delete ${name}?`)) return;
            fetch(`/api/devices/${encodeURIComponent(name)}`, { method: 'DELETE' })
            .then(r => r.json()).then(data => { if (data.success) loadDevices(); });
        }

        function viewDevice(name) {
            const d = currentDevices[name];
            alert(`Device: ${name}\nRoom: ${d.room}\nStatus: ${d.status.toUpperCase()}`);
        }

        function searchDevice() {
            const q = document.getElementById('search-input').value.toLowerCase().trim();
            if (!q) return renderTable();
            const filtered = Object.fromEntries(Object.entries(currentDevices).filter(([name, info]) => name.toLowerCase().includes(q) || info.room.toLowerCase().includes(q)));
            const tbody = document.getElementById('devices-table-body');
            tbody.innerHTML = '';
            Object.entries(filtered).forEach(([name, info]) => {
                const statusClass = info.status === 'online' ? 'bg-emerald-400 text-emerald-950' : info.status === 'offline' ? 'bg-red-400 text-white' : 'bg-amber-400 text-amber-950';
                const row = document.createElement('tr');
                row.className = 'table-row';
                row.innerHTML = `<td class="px-8 py-6 font-medium">${name}</td><td class="px-8 py-6 text-zinc-400">${info.room}</td><td class="px-8 py-6"><span class="px-5 py-1 rounded-3xl text-xs font-semibold ${statusClass}">${info.status.toUpperCase()}</span></td><td class="px-8 py-6 text-right"><button onclick="editDevice('${name}');event.stopImmediatePropagation()" class="text-yellow-400 hover:text-yellow-300 mr-6"><i class="fa-solid fa-pen"></i></button><button onclick="deleteDevice('${name}');event.stopImmediatePropagation()" class="text-red-400 hover:text-red-300"><i class="fa-solid fa-trash"></i></button></td>`;
                tbody.appendChild(row);
            });
        }

        function refreshDevices() { loadDevices(); }

        window.onload = () => { loadDevices(); showSection('dashboard'); };
    </script>
</body>
</html>"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/devices', methods=['GET'])
def get_devices():
    return jsonify(devices)

@app.route('/api/devices', methods=['POST'])
def add_device():
    global devices
    data = request.get_json()
    name = data.get('name')
    room = data.get('room')
    if not name or not room:
        return jsonify({"success": False, "message": "Name and room required"}), 400
    if name in devices:
        return jsonify({"success": False, "message": "Device already exists"}), 400
    devices[name] = {"room": room, "status": "online"}
    save_devices(devices)
    return jsonify({"success": True})

@app.route('/api/devices/<path:name>', methods=['PUT'])
def update_device(name):
    global devices
    if name not in devices:
        return jsonify({"success": False, "message": "Device not found"}), 404
    status = request.get_json().get('status')
    if status in ['online', 'offline', 'maintenance']:
        devices[name]['status'] = status
        save_devices(devices)
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Invalid status"}), 400

@app.route('/api/devices/<path:name>', methods=['DELETE'])
def delete_device(name):
    global devices
    if name in devices:
        del devices[name]
        save_devices(devices)
        return jsonify({"success": True})
    return jsonify({"success": False, "message": "Device not found"}), 404

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

#!/usr/bin/env python3
"""
Unified Mind System Startup Script

This script starts all components of the Mind system in the correct order:
1. Knowledge sharing API server (mind_bus_api.py)
2. Voice server (if Node.js dependencies are available)
3. Agent gateway (if configured)
4. Dashboard (if configured)

Usage:
    python mind_unified_startup.py [--port PORT] [--voice] [--dashboard] [--tunnel]
"""

import os
import sys
import time
import signal
import argparse
import subprocess
import threading
import socket
from pathlib import Path

class MindSystemManager:
    def __init__(self):
        self.processes = {}
        self.running = True
        
    def get_free_port(self):
        """Find a free port to use"""
        s = socket.socket()
        s.bind(('', 0))
        port = s.getsockname()[1]
        s.close()
        return port
    
    def is_port_free(self, port):
        """Check if a port is available"""
        try:
            s = socket.socket()
            s.bind(('', port))
            s.close()
            return True
        except OSError:
            return False
    
    def kill_port_processes(self, port):
        """Kill any processes using the specified port"""
        try:
            result = subprocess.run(['lsof', '-t', f'-i:{port}'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                pids = result.stdout.strip().split('\n')
                for pid in pids:
                    try:
                        subprocess.run(['kill', pid], check=False)
                        print(f"Killed process {pid} on port {port}")
                    except:
                        pass
                time.sleep(1)
        except FileNotFoundError:
            # lsof not available, skip
            pass
    
    def start_process(self, name, cmd, env=None, cwd=None):
        """Start a process and track it"""
        if name in self.processes:
            print(f"Process {name} is already running")
            return
            
        try:
            env_vars = os.environ.copy()
            if env:
                env_vars.update(env)
                
            proc = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                env=env_vars,
                cwd=cwd
            )
            self.processes[name] = proc
            
            # Start output monitoring thread
            def monitor_output():
                for line in proc.stdout:
                    if self.running:
                        print(f"[{name}] {line.rstrip()}")
                proc.wait()
                if name in self.processes:
                    del self.processes[name]
                    
            thread = threading.Thread(target=monitor_output, daemon=True)
            thread.start()
            
            print(f"Started {name} (PID: {proc.pid})")
            return proc
            
        except Exception as e:
            print(f"Failed to start {name}: {e}")
            return None
    
    def start_api_server(self, port=8000):
        """Start the main Mind API server"""
        print(f"Starting Mind API server on port {port}...")
        
        # Kill any existing processes on this port
        self.kill_port_processes(port)
        
        # Start the API server
        env = {"API_PORT": str(port)}
        return self.start_process(
            "api_server", 
            [sys.executable, "mind_bus_api.py"],
            env=env
        )
    
    def start_voice_server(self, port=8080):
        """Start the voice server if Node.js is available"""
        if not Path("package.json").exists():
            print("No package.json found, skipping voice server")
            return None
            
        try:
            subprocess.run(["node", "--version"], check=True, capture_output=True)
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("Node.js not found, skipping voice server")
            return None
            
        print(f"Starting voice server on port {port}...")
        self.kill_port_processes(port)
        
        # Install dependencies if needed
        if not Path("node_modules").exists():
            print("Installing Node.js dependencies...")
            subprocess.run(["npm", "install"], check=True)
        
        env = {"VOICE_PORT": str(port)}
        return self.start_process(
            "voice_server",
            ["node", "human_ai_voice_server.js"],
            env=env
        )
    
    def start_dashboard(self, port=8001):
        """Start the dashboard server"""
        if not Path("server.js").exists():
            print("Dashboard server not found, skipping")
            return None
            
        print(f"Starting dashboard on port {port}...")
        self.kill_port_processes(port)
        
        env = {"PORT": str(port)}
        return self.start_process(
            "dashboard",
            ["node", "server.js"],
            env=env
        )
    
    def setup_tunnel(self, port):
        """Setup localtunnel for public access"""
        try:
            subprocess.run(["npx", "localtunnel", "--version"], 
                          check=True, capture_output=True)
        except:
            print("Installing localtunnel...")
            subprocess.run(["npm", "install", "-g", "localtunnel"], check=True)
        
        print(f"Setting up tunnel for port {port}...")
        return self.start_process(
            "tunnel",
            ["npx", "localtunnel", "--port", str(port)]
        )
    
    def wait_for_server(self, port, timeout=30):
        """Wait for a server to be ready"""
        import urllib.request
        
        for i in range(timeout):
            try:
                urllib.request.urlopen(f"http://localhost:{port}/health", timeout=1)
                return True
            except:
                time.sleep(1)
        return False
    
    def shutdown(self):
        """Shutdown all processes"""
        print("\nShutting down Mind system...")
        self.running = False
        
        for name, proc in list(self.processes.items()):
            print(f"Stopping {name}...")
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait()
            except:
                pass
        
        self.processes.clear()
        print("Mind system shutdown complete")

def main():
    parser = argparse.ArgumentParser(description="Start the unified Mind system")
    parser.add_argument("--port", type=int, default=8000, 
                       help="Port for the main API server (default: 8000)")
    parser.add_argument("--voice", action="store_true", 
                       help="Start voice server")
    parser.add_argument("--dashboard", action="store_true", 
                       help="Start dashboard server")
    parser.add_argument("--tunnel", action="store_true", 
                       help="Setup public tunnel")
    parser.add_argument("--all", action="store_true",
                       help="Start all components")
    
    args = parser.parse_args()
    
    if args.all:
        args.voice = True
        args.dashboard = True
    
    manager = MindSystemManager()
    
    def signal_handler(signum, frame):
        manager.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("🧠 Starting Mind System...")
    print("=" * 50)
    
    # Start main API server
    api_proc = manager.start_api_server(args.port)
    if not api_proc:
        print("Failed to start API server, exiting")
        return 1
    
    # Wait for API server to be ready
    print("Waiting for API server to be ready...")
    if not manager.wait_for_server(args.port):
        print("API server failed to start properly")
        manager.shutdown()
        return 1
    
    print(f"✅ Mind API server ready at http://localhost:{args.port}")
    print(f"📚 Knowledge API available at http://localhost:{args.port}/docs")
    
    # Start optional components
    if args.voice:
        voice_port = 8080
        if manager.start_voice_server(voice_port):
            print(f"🎤 Voice server ready at ws://localhost:{voice_port}/speak")
    
    if args.dashboard:
        dashboard_port = 8001
        if manager.start_dashboard(dashboard_port):
            if manager.wait_for_server(dashboard_port):
                print(f"📊 Dashboard ready at http://localhost:{dashboard_port}")
    
    if args.tunnel:
        manager.setup_tunnel(args.port)
    
    print("\n" + "=" * 50)
    print("🚀 Mind System is ready!")
    print(f"📖 Main API: http://localhost:{args.port}")
    print(f"📚 Knowledge API docs: http://localhost:{args.port}/docs")
    print(f"🔧 API health check: http://localhost:{args.port}/health")
    
    if args.dashboard:
        print(f"📊 Dashboard: http://localhost:8001")
    if args.voice:
        print(f"🎤 Voice WebSocket: ws://localhost:8080/speak")
    
    print("\nPress Ctrl+C to stop all services")
    print("=" * 50)
    
    try:
        # Keep the main process alive
        while manager.running and manager.processes:
            time.sleep(1)
    except KeyboardInterrupt:
        pass
    finally:
        manager.shutdown()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
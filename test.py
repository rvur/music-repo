#!/usr/bin/env python3
"""
Music Server CLI - A terminal-based music player
Usage: python music_cli.py
"""

import requests
import os
import sys
import subprocess
import platform
from getpass import getpass

API_BASE = "http://192.168.1.93:5000/api"
session = requests.Session()

# ANSI color codes
class Colors:
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header(text):
    """Print a formatted header"""
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'=' * 60}{Colors.END}\n")

def print_success(text):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_error(text):
    """Print error message"""
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def format_time(seconds):
    """Format seconds to MM:SS"""
    if not seconds:
        return "0:00"
    mins = int(seconds) // 60
    secs = int(seconds) % 60
    return f"{mins}:{secs:02d}"

def login():
    """Login to the music server"""
    clear_screen()
    print_header("Music Server - Login")
    
    username = input(f"{Colors.CYAN}Username: {Colors.END}")
    password = getpass(f"{Colors.CYAN}Password: {Colors.END}")
    
    try:
        response = session.post(
            f"{API_BASE}/users/login",
            json={"username": username, "password": password}
        )
        
        if response.status_code == 200:
            print_success("Login successful!")
            return True
        else:
            error = response.json().get('error', 'Login failed')
            print_error(error)
            return False
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False

def register():
    """Register a new account"""
    clear_screen()
    print_header("Music Server - Register")
    
    username = input(f"{Colors.CYAN}Username: {Colors.END}")
    password = getpass(f"{Colors.CYAN}Password (min 8 chars): {Colors.END}")
    confirm = getpass(f"{Colors.CYAN}Confirm Password: {Colors.END}")
    
    if password != confirm:
        print_error("Passwords do not match!")
        return False
    
    if len(password) < 8:
        print_error("Password must be at least 8 characters!")
        return False
    
    try:
        response = session.post(
            f"{API_BASE}/users/register",
            json={"username": username, "password": password, "re_password": confirm}
        )
        
        if response.status_code == 201:
            print_success("Account created! Please login.")
            return True
        else:
            error = response.json().get('error', 'Registration failed')
            print_error(error)
            return False
    except Exception as e:
        print_error(f"Connection failed: {e}")
        return False

def get_songs():
    """Fetch all songs from the server"""
    try:
        response = session.get(f"{API_BASE}/music/")
        if response.status_code == 200:
            return response.json()
        return []
    except Exception as e:
        print_error(f"Failed to fetch songs: {e}")
        return []

def display_songs(songs):
    """Display the list of songs"""
    if not songs:
        print_info("No songs in your library")
        return
    
    print(f"\n{Colors.BOLD}{'#':<5} {'Title':<40} {'Size':<10} {'Duration':<10}{Colors.END}")
    print(f"{Colors.CYAN}{'-' * 70}{Colors.END}")
    
    for idx, song in enumerate(songs, 1):
        title = song.get('song_name', 'Unknown')[:38]
        size = f"{song.get('song_size', 0):.2f} MB"
        duration = format_time(song.get('length', 0))
        
        print(f"{Colors.YELLOW}{idx:<5}{Colors.END} {title:<40} {size:<10} {duration:<10}")
    
    print(f"\n{Colors.GREEN}Total: {len(songs)} songs{Colors.END}")

def search_songs(songs, query):
    """Search songs by name"""
    query = query.lower()
    results = [song for song in songs if query in song.get('song_name', '').lower()]
    return results

def play_song(song_id):
    """Stream and play a song"""
    try:
        # Get the audio stream
        response = session.get(f"{API_BASE}/music/stream/{song_id}", stream=True)
        
        if response.status_code != 200:
            print_error("Failed to stream song")
            return
        
        # Save to temporary file
        temp_file = "/tmp/music_server_temp.audio" if platform.system() != "Windows" else "music_server_temp.audio"
        
        print_info("Downloading song...")
        with open(temp_file, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        print_success("Playing song...")
        print_info("Press Ctrl+C to stop playback")
        
        # Play the audio file using system player
        if platform.system() == "Darwin":  # macOS
            subprocess.run(["afplay", temp_file])
        elif platform.system() == "Linux":
            # Try different players
            for player in ["mpg123", "ffplay", "vlc", "mplayer"]:
                try:
                    subprocess.run([player, temp_file], check=True)
                    break
                except (subprocess.CalledProcessError, FileNotFoundError):
                    continue
        elif platform.system() == "Windows":
            os.startfile(temp_file)
        
        # Cleanup
        try:
            os.remove(temp_file)
        except:
            pass
            
    except KeyboardInterrupt:
        print_info("\nPlayback stopped")
        try:
            os.remove(temp_file)
        except:
            pass
    except Exception as e:
        print_error(f"Playback failed: {e}")

def delete_song(song_id, song_name):
    """Delete a song"""
    confirm = input(f"{Colors.YELLOW}Delete '{song_name}'? (y/n): {Colors.END}")
    if confirm.lower() != 'y':
        print_info("Cancelled")
        return False
    
    try:
        response = session.delete(f"{API_BASE}/music/delete/{song_id}")
        if response.status_code == 200:
            print_success("Song deleted")
            return True
        else:
            print_error("Failed to delete song")
            return False
    except Exception as e:
        print_error(f"Delete failed: {e}")
        return False

def upload_file():
    """Upload a file to the server"""
    file_path = input(f"{Colors.CYAN}Enter file path: {Colors.END}").strip()
    
    if not os.path.exists(file_path):
        print_error("File not found!")
        return
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            print_info("Uploading...")
            response = session.post(f"{API_BASE}/music/", files=files)
            
            if response.status_code == 201:
                print_success("Upload successful!")
            else:
                print_error("Upload failed")
    except Exception as e:
        print_error(f"Upload failed: {e}")

def download_youtube():
    """Download from YouTube"""
    url = input(f"{Colors.CYAN}Enter YouTube URL: {Colors.END}").strip()
    
    if not url:
        print_error("URL cannot be empty!")
        return
    
    try:
        print_info("Downloading from YouTube...")
        response = session.post(
            f"{API_BASE}/music/yt",
            json={"yt_link": url}
        )
        
        if response.status_code == 201:
            print_success("Download successful!")
        else:
            error = response.json().get('error', 'Download failed')
            print_error(error)
    except Exception as e:
        print_error(f"Download failed: {e}")

def library_menu():
    """Main library menu"""
    while True:
        clear_screen()
        print_header("Music Server - Your Library")
        
        songs = get_songs()
        display_songs(songs)
        
        print(f"\n{Colors.BOLD}Options:{Colors.END}")
        print(f"{Colors.CYAN}[p]{Colors.END} Play song")
        print(f"{Colors.CYAN}[s]{Colors.END} Search")
        print(f"{Colors.CYAN}[u]{Colors.END} Upload file")
        print(f"{Colors.CYAN}[y]{Colors.END} Download from YouTube")
        print(f"{Colors.CYAN}[d]{Colors.END} Delete song")
        print(f"{Colors.CYAN}[r]{Colors.END} Refresh")
        print(f"{Colors.CYAN}[q]{Colors.END} Quit")
        
        choice = input(f"\n{Colors.GREEN}Enter your choice: {Colors.END}").lower().strip()
        
        if choice == 'p':
            if not songs:
                print_error("No songs available")
                input("\nPress Enter to continue...")
                continue
            
            try:
                song_num = int(input(f"{Colors.CYAN}Enter song number: {Colors.END}"))
                if 1 <= song_num <= len(songs):
                    song = songs[song_num - 1]
                    print(f"\n{Colors.BOLD}Now Playing: {song['song_name']}{Colors.END}")
                    play_song(song['id'])
                else:
                    print_error("Invalid song number")
            except ValueError:
                print_error("Please enter a valid number")
            except Exception as e:
                print_error(f"Error: {e}")
            
            input("\nPress Enter to continue...")
        
        elif choice == 's':
            query = input(f"{Colors.CYAN}Search: {Colors.END}").strip()
            if query:
                results = search_songs(songs, query)
                clear_screen()
                print_header(f"Search Results for '{query}'")
                display_songs(results)
                input("\nPress Enter to continue...")
        
        elif choice == 'u':
            upload_file()
            input("\nPress Enter to continue...")
        
        elif choice == 'y':
            download_youtube()
            input("\nPress Enter to continue...")
        
        elif choice == 'd':
            if not songs:
                print_error("No songs available")
                input("\nPress Enter to continue...")
                continue
            
            try:
                song_num = int(input(f"{Colors.CYAN}Enter song number to delete: {Colors.END}"))
                if 1 <= song_num <= len(songs):
                    song = songs[song_num - 1]
                    delete_song(song['id'], song['song_name'])
                else:
                    print_error("Invalid song number")
            except ValueError:
                print_error("Please enter a valid number")
            
            input("\nPress Enter to continue...")
        
        elif choice == 'r':
            continue
        
        elif choice == 'q':
            print_info("Goodbye!")
            sys.exit(0)
        
        else:
            print_error("Invalid choice")
            input("\nPress Enter to continue...")

def main():
    """Main function"""
    clear_screen()
    print_header("Welcome to Music Server CLI")
    
    print(f"{Colors.CYAN}[1]{Colors.END} Login")
    print(f"{Colors.CYAN}[2]{Colors.END} Register")
    print(f"{Colors.CYAN}[3]{Colors.END} Quit")
    
    choice = input(f"\n{Colors.GREEN}Enter your choice: {Colors.END}").strip()
    
    if choice == '1':
        if login():
            input("\nPress Enter to continue...")
            library_menu()
        else:
            input("\nPress Enter to continue...")
            main()
    
    elif choice == '2':
        if register():
            input("\nPress Enter to continue...")
            main()
        else:
            input("\nPress Enter to continue...")
            main()
    
    elif choice == '3':
        print_info("Goodbye!")
        sys.exit(0)
    
    else:
        print_error("Invalid choice")
        input("\nPress Enter to continue...")
        main()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_info("\n\nGoodbye!")
        sys.exit(0)
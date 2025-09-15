from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
import yt_dlp
import os
from threading import Thread

class YouTubeDownloaderApp(App):
    def build(self):
        # Create main layout (like arranging furniture in a room)
        main_layout = BoxLayout(orientation='vertical', padding=10, spacing=10)
        
        # Title label
        title = Label(
            text='YouTube Video/Audio Downloader', 
            size_hint=(1, 0.1),
            font_size='20sp'
        )
        main_layout.add_widget(title)
        
        # URL input field
        self.url_input = TextInput(
            hint_text='Paste YouTube URL here',
            size_hint=(1, 0.1),
            multiline=False
        )
        main_layout.add_widget(self.url_input)
        
        # Buttons layout
        button_layout = BoxLayout(orientation='horizontal', size_hint=(1, 0.1))
        
        # Video download button
        video_btn = Button(text='Download Video')
        video_btn.bind(on_press=self.download_video)
        button_layout.add_widget(video_btn)
        
        # Audio download button  
        audio_btn = Button(text='Download Audio Only')
        audio_btn.bind(on_press=self.download_audio)
        button_layout.add_widget(audio_btn)
        
        main_layout.add_widget(button_layout)
        
        # Progress bar
        self.progress = ProgressBar(max=100, size_hint=(1, 0.1))
        main_layout.add_widget(self.progress)
        
        # Status label
        self.status_label = Label(
            text='Ready to download', 
            size_hint=(1, 0.1)
        )
        main_layout.add_widget(self.status_label)
        
        return main_layout
    
    def download_video(self, instance):
        """Download full video"""
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = 'Please enter a URL'
            return
            
        # Start download in separate thread to not freeze UI
        thread = Thread(target=self._download, args=(url, 'video'))
        thread.daemon = True
        thread.start()
    
    def download_audio(self, instance):
        """Download audio only"""
        url = self.url_input.text.strip()
        if not url:
            self.status_label.text = 'Please enter a URL'
            return
            
        thread = Thread(target=self._download, args=(url, 'audio'))
        thread.daemon = True
        thread.start()
    
    def _download(self, url, format_type):
        """Actual download logic"""
        try:
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Starting download...'))
            
            # Create downloads folder
            download_path = '/storage/emulated/0/Download/YouTubeDownloader'
            os.makedirs(download_path, exist_ok=True)
            
            if format_type == 'video':
                ydl_opts = {
                    'format': 'best[height<=720]',  # Best quality up to 720p
                    'outtmpl': f'{download_path}/%(title)s.%(ext)s',
                    'progress_hooks': [self.progress_hook],
                }
            else:  # audio
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': f'{download_path}/%(title)s.%(ext)s',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                    'progress_hooks': [self.progress_hook],
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
                
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', 'Download completed!'))
            
        except Exception as e:
            error_msg = f'Error: {str(e)}'
            Clock.schedule_once(lambda dt: setattr(self.status_label, 'text', error_msg))
    
    def progress_hook(self, d):
        """Update progress bar"""
        if d['status'] == 'downloading':
            try:
                percent = float(d.get('_percent_str', '0').replace('%', ''))
                Clock.schedule_once(lambda dt: setattr(self.progress, 'value', percent))
            except:
                pass

if __name__ == '__main__':
    YouTubeDownloaderApp().run()

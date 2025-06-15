import os
import tempfile
import os
import wave
import struct
import math
from django.conf import settings
from django.core.files.base import ContentFile
import logging

try:
    from google.cloud import texttospeech
    GOOGLE_CLOUD_AVAILABLE = True
except ImportError:
    GOOGLE_CLOUD_AVAILABLE = False
    texttospeech = None

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False
    gTTS = None

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False
    pyttsx3 = None

logger = logging.getLogger(__name__)

class TextToSpeechService:
    """
    Google Cloud Text-to-Speech APIを使用して音声を生成するサービス
    """
    
    def __init__(self):
        self.client = None
        self.pyttsx3_engine = None
        self.use_mock = False
        
        # 1. gTTSを最優先で試行
        if GTTS_AVAILABLE:
            try:
                # gTTSの動作確認（簡単なテスト）
                test_tts = gTTS(text="test", lang='en')
                logger.info("gTTS engine available")
                self.gtts_available = True
                return
            except Exception as e:
                logger.error(f"gTTS engine not available: {e}")
                self.gtts_available = False
        else:
            self.gtts_available = False
        
        # 2. Google Cloud TTSを次に試行
        if GOOGLE_CLOUD_AVAILABLE:
            try:
                self.client = texttospeech.TextToSpeechClient()
                logger.info("Google Cloud Text-to-Speech client initialized successfully")
                return
            except Exception as e:
                logger.error(f"Failed to initialize Google Cloud Text-to-Speech client: {e}")
        
        # 3. pyttsx3を試行（問題があるため最後の選択肢）
        if PYTTSX3_AVAILABLE:
            try:
                # 初期化時はテスト用の一時エンジンを作成して確認
                test_engine = pyttsx3.init()
                test_engine.stop()
                logger.info("pyttsx3 TTS engine available")
                # 実際のエンジンは使用時に作成
                self.pyttsx3_engine = True  # フラグとして使用
                return
            except Exception as e:
                logger.error(f"pyttsx3 TTS engine not available: {e}")
                self.pyttsx3_engine = None
        
        # 4. どれも利用できない場合はモック機能を使用
        logger.info("No TTS engines available, using mock functionality")
        self.use_mock = True
    
    def synthesize_speech(self, text, language_code='en-US', voice_name='en-US-Wavenet-D'):
        """
        テキストを音声に変換する
        
        Args:
            text (str): 変換するテキスト
            language_code (str): 言語コード（例: 'en-US', 'ja-JP'）
            voice_name (str): 音声名
            
        Returns:
            bytes: WAV形式の音声データ
        """
        # 1. gTTSを優先使用
        if hasattr(self, 'gtts_available') and self.gtts_available:
            try:
                logger.info(f"Generating speech with gTTS for text: {text[:50]}...")
                return self._generate_gtts_audio(text, language_code)
            except Exception as e:
                logger.error(f"Error in gTTS speech synthesis: {e}")
                logger.info("Falling back to next available option")
        
        # 2. Google Cloud TTSを次に使用
        if self.client:
            try:
                # 音声合成リクエストを作成
                synthesis_input = texttospeech.SynthesisInput(text=text)
                
                # 音声設定
                voice = texttospeech.VoiceSelectionParams(
                    language_code=language_code,
                    name=voice_name
                )
                
                # オーディオ設定
                audio_config = texttospeech.AudioConfig(
                    audio_encoding=texttospeech.AudioEncoding.LINEAR16,
                    sample_rate_hertz=22050
                )
                
                # 音声合成を実行
                response = self.client.synthesize_speech(
                    input=synthesis_input,
                    voice=voice,
                    audio_config=audio_config
                )
                
                logger.info(f"Successfully synthesized speech with Google Cloud TTS for text: {text[:50]}...")
                return response.audio_content
                
            except Exception as e:
                logger.error(f"Error in Google Cloud TTS speech synthesis: {e}")
                logger.info("Falling back to next available option")
        
        # 3. pyttsx3を次に使用（問題があるため最後の選択肢）
        if self.pyttsx3_engine:
            try:
                logger.info(f"Generating speech with pyttsx3 for text: {text[:50]}...")
                return self._generate_pyttsx3_audio(text)
            except Exception as e:
                logger.error(f"Error in pyttsx3 speech synthesis: {e}")
                logger.info("Falling back to mock audio generation")
        
        # 4. 最後の手段としてモック音声を生成
        logger.info(f"Generating mock audio for text: {text[:50]}...")
        return self._generate_mock_audio(text)
    
    def get_available_voices(self, language_code='en-US'):
        """
        利用可能な音声リストを取得
        
        Args:
            language_code (str): 言語コード
        
        Returns:
            list: 利用可能な音声のリスト
        """
        if not self.client:
            return []
        
        try:
            voices = self.client.list_voices(language_code=language_code)
            return [
                {
                    'name': voice.name,
                    'gender': voice.ssml_gender.name,
                    'language_codes': list(voice.language_codes)
                }
                for voice in voices.voices
            ]
        except Exception as e:
            logger.error(f"Failed to get available voices: {e}")
            return []
    
    def create_audio_file(self, text, filename_prefix='listening_audio'):
        """
        テキストから音声ファイルを作成してContentFileとして返す
        
        Args:
            text (str): 音声に変換するテキスト
            filename_prefix (str): ファイル名のプレフィックス
        
        Returns:
            ContentFile: Django ContentFileオブジェクト
        """
        audio_content = self.synthesize_speech(text)
        
        if audio_content:
            return ContentFile(audio_content, name=f'{filename_prefix}.wav')
        return None
    
    def _generate_gtts_audio(self, text, language_code='en-US'):
        """
        gTTSを使用して音声を生成する
        
        Args:
            text (str): 変換するテキスト
            language_code (str): 言語コード
            
        Returns:
            bytes: WAV形式の音声データ
        """
        import tempfile
        import os
        import subprocess
        
        # 言語コードをgTTS形式に変換
        lang_map = {
            'en-US': 'en',
            'ja-JP': 'ja',
            'en': 'en',
            'ja': 'ja'
        }
        lang = lang_map.get(language_code, 'en')
        
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
            temp_mp3_filename = temp_mp3.name
        
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
            temp_wav_filename = temp_wav.name
        
        try:
            # gTTSで音声ファイルを生成（MP3形式）
            tts = gTTS(text=text, lang=lang, slow=False)
            tts.save(temp_mp3_filename)
            
            # ffmpegを使用してMP3をWAVに変換
            try:
                subprocess.run([
                    'ffmpeg', '-i', temp_mp3_filename, 
                    '-acodec', 'pcm_s16le', '-ar', '22050', 
                    temp_wav_filename, '-y'
                ], check=True, capture_output=True)
            except (subprocess.CalledProcessError, FileNotFoundError):
                # ffmpegが利用できない場合、MP3ファイルをそのまま返す
                # （ブラウザはMP3も再生可能）
                with open(temp_mp3_filename, 'rb') as f:
                    return f.read()
            
            # WAVファイルを読み込んでバイト列として返す
            with open(temp_wav_filename, 'rb') as f:
                audio_data = f.read()
            
            return audio_data
            
        finally:
            # 一時ファイルを削除
            for filename in [temp_mp3_filename, temp_wav_filename]:
                if os.path.exists(filename):
                    os.unlink(filename)
    
    def _generate_pyttsx3_audio(self, text):
        """
        pyttsx3を使用して音声を生成する
        
        Args:
            text (str): 変換するテキスト
            
        Returns:
            bytes: WAV形式の音声データ
        """
        import tempfile
        import os
        
        # 一時ファイルを作成
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_file:
            temp_filename = temp_file.name
        
        engine = None
        try:
            # 新しいエンジンインスタンスを作成
            engine = pyttsx3.init()
            
            # 既存のループが実行中の場合は終了
            if hasattr(engine, '_inLoop') and engine._inLoop:
                engine.endLoop()
            
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 0.9)
            
            # pyttsx3で音声ファイルを生成
            engine.save_to_file(text, temp_filename)
            engine.runAndWait()
            
            # ファイルを読み込んでバイト列として返す
            with open(temp_filename, 'rb') as f:
                audio_data = f.read()
            
            return audio_data
            
        except Exception as e:
            logger.error(f"pyttsx3 audio generation failed: {e}")
            raise
            
        finally:
            # エンジンのクリーンアップ
            if engine:
                try:
                    if hasattr(engine, '_inLoop') and engine._inLoop:
                        engine.endLoop()
                    engine.stop()
                except:
                    pass
            
            # 一時ファイルを削除
            if os.path.exists(temp_filename):
                os.unlink(temp_filename)
    
    def _generate_mock_audio(self, text):
        """
        開発用のモック音声データを生成（WAV形式）
        
        Args:
            text (str): テキスト（長さに基づいて音声の長さを決定）
        
        Returns:
            bytes: WAV形式の音声データ
        """
        try:
            # テキストの長さに基づいて音声の長さを決定（1文字あたり0.1秒）
            duration = max(2.0, len(text) * 0.1)  # 最低2秒
            sample_rate = 24000
            num_samples = int(duration * sample_rate)
            
            # 簡単なトーン音を生成（440Hz + 880Hz）
            audio_data = []
            for i in range(num_samples):
                t = i / sample_rate
                # 2つの周波数を混合してより自然な音に
                sample = 0.3 * math.sin(2 * math.pi * 440 * t) + 0.2 * math.sin(2 * math.pi * 880 * t)
                # フェードイン・フェードアウト効果
                fade_samples = sample_rate // 10  # 0.1秒のフェード
                if i < fade_samples:
                    sample *= i / fade_samples
                elif i > num_samples - fade_samples:
                    sample *= (num_samples - i) / fade_samples
                
                # 16ビット整数に変換
                audio_data.append(int(sample * 32767))
            
            # WAVファイルのヘッダーを作成
            import io
            wav_buffer = io.BytesIO()
            
            with wave.open(wav_buffer, 'wb') as wav_file:
                wav_file.setnchannels(1)  # モノラル
                wav_file.setsampwidth(2)  # 16ビット
                wav_file.setframerate(sample_rate)
                
                # 音声データを書き込み
                for sample in audio_data:
                    wav_file.writeframes(struct.pack('<h', sample))
            
            wav_buffer.seek(0)
            return wav_buffer.getvalue()
            
        except Exception as e:
            logger.error(f"Mock audio generation failed: {e}")
            # 最小限のWAVファイルを生成
            return self._generate_minimal_wav()
    
    def _generate_minimal_wav(self):
        """
        最小限のWAVファイルを生成（無音）
        """
        import io
        wav_buffer = io.BytesIO()
        
        with wave.open(wav_buffer, 'wb') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(24000)
            # 2秒の無音
            silence = [0] * (24000 * 2)
            for sample in silence:
                wav_file.writeframes(struct.pack('<h', sample))
        
        wav_buffer.seek(0)
        return wav_buffer.getvalue()

# TTSサービスのインスタンスを作成
tts_service = TextToSpeechService()
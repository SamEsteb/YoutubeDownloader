"""
Tests para el validador de URLs.
"""

import pytest

from core.validator import URLValidator, YouTubeURL, InvalidURLError


class TestURLValidator:
    """Tests para URLValidator."""
    
    def setup_method(self):
        """Setup para cada test."""
        self.validator = URLValidator()
    
    # Tests de URLs válidas
    def test_valid_youtube_watch_url(self):
        """URL estándar de YouTube debe ser válida."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert self.validator.validate(url) is True
    
    def test_valid_youtube_short_url(self):
        """URL corta de YouTube debe ser válida."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        assert self.validator.validate(url) is True
    
    def test_valid_youtube_shorts_url(self):
        """URL de YouTube Shorts debe ser válida."""
        url = "https://www.youtube.com/shorts/K6yCA9yN70U"
        assert self.validator.validate(url) is True
    
    def test_valid_youtube_playlist_url(self):
        """URL de playlist de YouTube debe ser válida."""
        url = "https://www.youtube.com/playlist?list=PL123456789"
        assert self.validator.validate(url) is True
    
    def test_valid_youtube_with_params(self):
        """URL con parámetros adicionales debe ser válida."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=60"
        assert self.validator.validate(url) is True
    
    # Tests de URLs inválidas
    def test_empty_url_raises_error(self):
        """URL vacía debe lanzar InvalidURLError."""
        with pytest.raises(InvalidURLError):
            self.validator.validate("")
    
    def test_empty_url_with_spaces_raises_error(self):
        """URL con solo espacios debe lanzar InvalidURLError."""
        with pytest.raises(InvalidURLError):
            self.validator.validate("   ")
    
    def test_invalid_url_raises_error(self):
        """URL inválida debe lanzar InvalidURLError."""
        with pytest.raises(InvalidURLError):
            self.validator.validate("not-a-url")
    
    def test_non_youtube_url_raises_error(self):
        """URL que no es de YouTube debe lanzar InvalidURLError."""
        with pytest.raises(InvalidURLError):
            self.validator.validate("https://vimeo.com/123456789")
    
    def test_random_string_raises_error(self):
        """String aleatorio debe lanzar InvalidURLError."""
        with pytest.raises(InvalidURLError):
            self.validator.validate("hello world")
    
    # Tests de parseo
    def test_parse_extracts_video_id(self):
        """Parse debe extraer el video ID."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        parsed = self.validator.parse(url)
        assert parsed.video_id == "dQw4w9WgXcQ"
    
    def test_parse_extracts_short_video_id(self):
        """Parse debe extraer el video ID de URL corta."""
        url = "https://youtu.be/dQw4w9WgXcQ"
        parsed = self.validator.parse(url)
        assert parsed.video_id == "dQw4w9WgXcQ"
    
    def test_parse_extracts_playlist_id(self):
        """Parse debe extraer el playlist ID."""
        url = "https://www.youtube.com/playlist?list=PL123456789"
        parsed = self.validator.parse(url)
        assert parsed.playlist_id == "PL123456789"
        assert parsed.is_playlist is True
    
    def test_parse_video_is_video(self):
        """URL de video debe ser detectada como video."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        parsed = self.validator.parse(url)
        assert parsed.is_video is True
        assert parsed.is_playlist is False
    
    # Tests de helpers
    def test_is_video(self):
        """is_video debe retornar True para videos."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert self.validator.is_video(url) is True
    
    def test_is_playlist(self):
        """is_playlist debe retornar True para playlists."""
        url = "https://www.youtube.com/playlist?list=PL123456789"
        assert self.validator.is_playlist(url) is True
    
    def test_get_video_id(self):
        """get_video_id debe retornar el ID del video."""
        url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        assert self.validator.get_video_id(url) == "dQw4w9WgXcQ"
    
    def test_get_playlist_id(self):
        """get_playlist_id debe retornar el ID de la playlist."""
        url = "https://www.youtube.com/playlist?list=PL123456789"
        assert self.validator.get_playlist_id(url) == "PL123456789"
    
    def test_invalid_url_returns_none_for_get_video_id(self):
        """get_video_id debe retornar None para URL inválida."""
        assert self.validator.get_video_id("invalid") is None


class TestYouTubeURL:
    """Tests para el dataclass YouTubeURL."""
    
    def test_create_youtube_url(self):
        """Crear YouTubeURL con datos."""
        url = YouTubeURL(
            url="https://www.youtube.com/watch?v=abc123",
            video_id="abc123",
            is_video=True,
        )
        assert url.url == "https://www.youtube.com/watch?v=abc123"
        assert url.video_id == "abc123"
        assert url.is_video is True
    
    def test_str_representation(self):
        """__str__ debe retornar la URL."""
        url = YouTubeURL(url="https://youtube.com/watch?v=test")
        assert str(url) == "https://youtube.com/watch?v=test"
